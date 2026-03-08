"""
Game state and main turn loop for Dungeon Forge.
"""

from __future__ import annotations

import math
import random
from collections import deque
from typing import Deque, List, Optional, Set, Tuple

from dungeon_forge.dungeon_gen import DungeonMap, Tile
from dungeon_forge.entities import Item, ItemType, Monster, Player


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PLAYER_START_HP = 30
PLAYER_START_ATK = 5
PLAYER_START_DEF = 1
VISION_RADIUS = 6          # tiles the player can see
MONSTERS_PER_ROOM = (1, 3) # min / max monsters spawned per room (except entrance)
ITEMS_PER_ROOM = (0, 2)


# ---------------------------------------------------------------------------
# GameState
# ---------------------------------------------------------------------------

class GameState:
    """Holds all mutable state for a single dungeon floor.

    Parameters
    ----------
    floor:
        Current dungeon depth (1-indexed).
    seed:
        Optional RNG seed for reproducible maps.
    player:
        Carry-over Player object from a previous floor (or None for a new game).
    """

    def __init__(
        self,
        floor: int = 1,
        seed: Optional[int] = None,
        player: Optional[Player] = None,
    ) -> None:
        self.floor = floor
        self.rng = random.Random(seed)

        # Generate map
        self.dungeon = DungeonMap(
            width=80,
            height=40,
            min_rooms=8,
            seed=seed,
        )

        # Player
        if player is None:
            px, py = self.dungeon.entrance
            self.player = Player(
                name="Adventurer",
                x=px, y=py,
                char="@",
                hp=PLAYER_START_HP,
                max_hp=PLAYER_START_HP,
                attack=PLAYER_START_ATK,
                defense=PLAYER_START_DEF,
            )
        else:
            player.x, player.y = self.dungeon.entrance
            self.player = player

        # Monsters & items
        self.monsters: List[Monster] = []
        self.floor_items: List[Item] = []
        self._populate()

        # Fog of war
        self.explored: Set[Tuple[int, int]] = set()
        self.visible: Set[Tuple[int, int]] = set()
        self._update_visibility()

        # Message log
        self._messages: Deque[str] = deque(maxlen=50)
        self.add_message("You descend into the dungeon…  Find the stairs (>) to go deeper!")

        # Helpers
        self.current_room: int = 0  # index of the room the player is currently in
        self.running: bool = True
        self.won: bool = False

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def recent_messages(self, n: int = 4) -> List[str]:
        msgs = list(self._messages)
        return msgs[-n:]

    def add_message(self, msg: str) -> None:
        self._messages.append(msg)

    def monster_at(self, x: int, y: int) -> Optional[Monster]:
        for m in self.monsters:
            if m.is_alive and m.x == x and m.y == y:
                return m
        return None

    def item_at(self, x: int, y: int) -> Optional[Item]:
        for item in self.floor_items:
            if item.x == x and item.y == y:
                return item
        return None

    # ------------------------------------------------------------------
    # Player actions
    # ------------------------------------------------------------------

    def move_player(self, dx: int, dy: int) -> None:
        """Attempt to move the player by (dx, dy).  Triggers combat if occupied."""
        nx, ny = self.player.x + dx, self.player.y + dy

        # Blocked by wall
        if not self.dungeon.is_walkable(nx, ny):
            return

        # Monster in the way → attack
        monster = self.monster_at(nx, ny)
        if monster:
            self._player_attack(monster)
            self._monster_turns()
            self._update_visibility()
            return

        # Move
        self.player.x, self.player.y = nx, ny
        self._update_visibility()
        self._check_stairs()
        self._update_current_room()
        self._monster_turns()

    def pickup_item(self) -> None:
        """Pick up an item at the player's current position."""
        item = self.item_at(self.player.x, self.player.y)
        if item is None:
            self.add_message("There is nothing here to pick up.")
            return

        self.floor_items.remove(item)

        if item.item_type == ItemType.GOLD:
            self.player.gold += item.value
            self.add_message(f"You scoop up {item.value} gold coins.")
        else:
            self.player.inventory.append(item)
            self.add_message(f"You pick up the {item.name}.")

        self._monster_turns()

    def use_item(self, index: int) -> str:
        """Use or equip the item at *index* in the player's inventory.

        Returns a message describing the outcome.
        """
        inv = self.player.inventory
        if index < 0 or index >= len(inv):
            return "Nothing there."
        item = inv[index]

        if item.item_type == ItemType.HEALTH_POTION:
            inv.pop(index)
            healed = self.player.heal(item.effect)
            return f"You drink the {item.name} and recover {healed} HP."

        if item.item_type in (ItemType.WEAPON, ItemType.ARMOR):
            self.player.equip(item)
            return f"You equip the {item.name}."

        return f"You can't use the {item.name} right now."

    # ------------------------------------------------------------------
    # Visibility
    # ------------------------------------------------------------------

    def _update_visibility(self) -> None:
        self.visible = self._compute_fov(self.player.x, self.player.y, VISION_RADIUS)
        self.explored |= self.visible

    def _compute_fov(
        self, origin_x: int, origin_y: int, radius: int
    ) -> Set[Tuple[int, int]]:
        """Compute field-of-view using shadow-casting (simplified octant scan)."""
        visible: Set[Tuple[int, int]] = {(origin_x, origin_y)}
        for angle_deg in range(0, 360, 2):
            angle = math.radians(angle_deg)
            rx, ry = math.cos(angle), math.sin(angle)
            px, py = float(origin_x), float(origin_y)
            for _ in range(radius):
                px += rx
                py += ry
                tile_x, tile_y = int(round(px)), int(round(py))
                visible.add((tile_x, tile_y))
                if self.dungeon.get_tile(tile_x, tile_y) == Tile.WALL:
                    break
        return visible

    # ------------------------------------------------------------------
    # Population
    # ------------------------------------------------------------------

    def _populate(self) -> None:
        """Scatter monsters and items across the dungeon rooms."""
        monster_types = Monster.types_for_floor(self.floor)

        for room_idx, room in enumerate(self.dungeon.rooms):
            is_entrance = room_idx == 0

            # Items in every room (skip entrance)
            if not is_entrance:
                n_items = self.rng.randint(*ITEMS_PER_ROOM)
                for _ in range(n_items):
                    pos = self._random_floor_pos(room)
                    if pos is None:
                        continue
                    ix, iy = pos
                    roll = self.rng.random()
                    if roll < 0.45:
                        item = Item.gold_pile(self.floor, ix, iy)
                    elif roll < 0.70:
                        item = Item.health_potion(self.floor, ix, iy)
                    elif roll < 0.85:
                        item = Item.weapon(self.floor, ix, iy)
                    else:
                        item = Item.armor(self.floor, ix, iy)
                    self.floor_items.append(item)

            # Monsters (skip entrance room)
            if not is_entrance:
                n_monsters = self.rng.randint(*MONSTERS_PER_ROOM)
                for _ in range(n_monsters):
                    pos = self._random_floor_pos(room)
                    if pos is None:
                        continue
                    mx, my = pos
                    mtype = self.rng.choice(monster_types)
                    self.monsters.append(Monster.create(mtype, mx, my, self.rng))

    def _random_floor_pos(
        self, room
    ) -> Optional[Tuple[int, int]]:
        """Return a random walkable, unoccupied position inside *room*."""
        occupied = {(m.x, m.y) for m in self.monsters}
        occupied |= {(i.x, i.y) for i in self.floor_items}
        occupied.add((self.player.x, self.player.y))
        occupied.add(self.dungeon.entrance)
        occupied.add(self.dungeon.exit)

        candidates = [
            (x, y)
            for y in range(room.y + 1, room.y2)
            for x in range(room.x + 1, room.x2)
            if (x, y) not in occupied
        ]
        if not candidates:
            return None
        return self.rng.choice(candidates)

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def _player_attack(self, monster: Monster) -> None:
        dmg = self.player.attack_roll()
        dealt = monster.take_damage(dmg)
        if monster.is_alive:
            self.add_message(
                f"You hit the {monster.name} for {dealt} damage. "
                f"({monster.hp}/{monster.max_hp} HP left)"
            )
        else:
            self.player.gold += monster.gold_value
            self.player.kills += 1
            leveled = self.player.gain_xp(monster.xp_value)
            self.add_message(
                f"You slay the {monster.name}! "
                f"+{monster.xp_value} XP, +{monster.gold_value} gold."
            )
            if leveled:
                self.add_message(
                    f"*** LEVEL UP!  You are now level {self.player.level}! ***"
                )

    def _monster_attack(self, monster: Monster) -> None:
        dmg = monster.attack_roll()
        dealt = self.player.take_damage(dmg)
        self.add_message(
            f"The {monster.name} hits you for {dealt} damage. "
            f"({self.player.hp}/{self.player.max_hp} HP)"
        )
        if not self.player.is_alive:
            self.add_message("You have been slain!")
            self.running = False

    def _monster_turns(self) -> None:
        """Each living monster takes its turn."""
        for monster in self.monsters:
            if not monster.is_alive:
                continue
            self._monster_act(monster)
            if not self.running:
                break

    def _monster_act(self, monster: Monster) -> None:
        px, py = self.player.x, self.player.y
        dist = math.hypot(px - monster.x, py - monster.y)

        # Can the monster see the player?
        if dist <= monster.vision_range and (monster.x, monster.y) in self.visible:
            monster.state = "chase"

        if monster.state == "chase":
            # One step toward the player (cardinal only, simple pathfinding)
            dx = 0 if px == monster.x else (1 if px > monster.x else -1)
            dy = 0 if py == monster.y else (1 if py > monster.y else -1)

            # Try horizontal then vertical step
            moved = False
            for ddx, ddy in [(dx, 0), (0, dy), (dx, dy)]:
                if ddx == 0 and ddy == 0:
                    continue
                nx, ny = monster.x + ddx, monster.y + ddy
                if nx == px and ny == py:
                    # Attack!
                    self._monster_attack(monster)
                    moved = True
                    break
                if (
                    self.dungeon.is_walkable(nx, ny)
                    and self.monster_at(nx, ny) is None
                ):
                    monster.x, monster.y = nx, ny
                    moved = True
                    break

            if not moved:
                monster.state = "idle"
        else:
            # Wander randomly
            dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.rng.shuffle(dirs)
            for ddx, ddy in dirs:
                nx, ny = monster.x + ddx, monster.y + ddy
                if (
                    self.dungeon.is_walkable(nx, ny)
                    and self.monster_at(nx, ny) is None
                    and not (nx == px and ny == py)
                ):
                    monster.x, monster.y = nx, ny
                    break

    # ------------------------------------------------------------------
    # Win condition
    # ------------------------------------------------------------------

    def _check_stairs(self) -> None:
        sx, sy = self.dungeon.exit
        if self.player.x == sx and self.player.y == sy:
            if self.floor >= 5:
                self.won = True
                self.running = False
                self.add_message("You reach the surface — YOU WIN!")
            else:
                self.add_message(
                    f"You descend to floor {self.floor + 1}…"
                )
                self.running = False  # caller will start a new floor

    def _update_current_room(self) -> None:
        for idx, room in enumerate(self.dungeon.rooms):
            if room.contains(self.player.x, self.player.y):
                self.current_room = idx
                break
