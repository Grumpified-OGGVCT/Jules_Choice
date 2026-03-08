"""
Game entities: Player, Monster, Item, and their data classes.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Item
# ---------------------------------------------------------------------------

class ItemType(Enum):
    HEALTH_POTION = auto()
    WEAPON = auto()
    ARMOR = auto()
    GOLD = auto()


@dataclass
class Item:
    """A floor item that the player can pick up."""

    name: str
    item_type: ItemType
    value: int          # gold value or gold amount
    effect: int         # healing, attack bonus, or defence bonus
    char: str           # glyph on the map
    x: int = 0
    y: int = 0

    # ------------------------------------------------------------------
    # Factories
    # ------------------------------------------------------------------

    @classmethod
    def health_potion(cls, level: int = 1, x: int = 0, y: int = 0) -> "Item":
        heal = level * 12 + random.randint(-3, 5)
        return cls("Health Potion", ItemType.HEALTH_POTION, 10, max(5, heal), "!", x, y)

    @classmethod
    def weapon(cls, level: int = 1, x: int = 0, y: int = 0) -> "Item":
        _weapons = [
            ("Rusty Dagger", 2),
            ("Short Sword", 4),
            ("Longsword", 7),
            ("Battle Axe", 10),
            ("Greatsword", 13),
        ]
        idx = min(level - 1, len(_weapons) - 1)
        name, base_dmg = _weapons[idx]
        dmg = base_dmg + random.randint(0, 2)
        return cls(name, ItemType.WEAPON, dmg * 3, dmg, "/", x, y)

    @classmethod
    def armor(cls, level: int = 1, x: int = 0, y: int = 0) -> "Item":
        _armors = [
            ("Leather Vest", 1),
            ("Chain Mail", 2),
            ("Plate Armour", 4),
        ]
        idx = min(level - 1, len(_armors) - 1)
        name, defence = _armors[idx]
        return cls(name, ItemType.ARMOR, defence * 5, defence, "]", x, y)

    @classmethod
    def gold_pile(cls, level: int = 1, x: int = 0, y: int = 0) -> "Item":
        amount = random.randint(level * 3, level * 15)
        return cls(f"{amount} Gold Coins", ItemType.GOLD, amount, amount, "$", x, y)


# ---------------------------------------------------------------------------
# Base entity
# ---------------------------------------------------------------------------

@dataclass
class Entity:
    name: str
    x: int
    y: int
    char: str
    hp: int
    max_hp: int
    attack: int
    defense: int

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, raw_damage: int) -> int:
        """Apply damage after mitigation.  Returns actual damage dealt."""
        actual = max(1, raw_damage - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------

@dataclass
class Player(Entity):
    level: int = 1
    xp: int = 0
    gold: int = 0
    kills: int = 0
    inventory: List[Item] = field(default_factory=list)
    weapon: Optional[Item] = None
    equipped_armor: Optional[Item] = None

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------

    def attack_roll(self) -> int:
        """Return a single random attack value."""
        base = self.attack + (self.weapon.effect if self.weapon else 0)
        return base + random.randint(0, max(1, base // 3))

    def effective_defense(self) -> int:
        bonus = self.equipped_armor.effect if self.equipped_armor else 0
        return self.defense + bonus

    def take_damage(self, raw_damage: int) -> int:  # type: ignore[override]
        actual = max(1, raw_damage - self.effective_defense())
        self.hp = max(0, self.hp - actual)
        return actual

    # ------------------------------------------------------------------
    # Healing
    # ------------------------------------------------------------------

    def heal(self, amount: int) -> int:
        """Heal up to max_hp.  Returns how much was actually healed."""
        healed = min(amount, self.max_hp - self.hp)
        self.hp += healed
        return healed

    # ------------------------------------------------------------------
    # Progression
    # ------------------------------------------------------------------

    def gain_xp(self, amount: int) -> bool:
        """Add XP; return True if this triggered a level-up."""
        self.xp += amount
        threshold = self.level * 50
        if self.xp >= threshold:
            self._level_up()
            return True
        return False

    def _level_up(self) -> None:
        self.level += 1
        self.max_hp += 10
        self.hp = min(self.hp + 10, self.max_hp)
        self.attack += 2
        self.defense += 1

    def xp_to_next(self) -> int:
        return self.level * 50

    # ------------------------------------------------------------------
    # Equipment
    # ------------------------------------------------------------------

    def equip(self, item: Item) -> Optional[Item]:
        """Equip an item.  Returns the previously equipped item (if any)."""
        if item.item_type == ItemType.WEAPON:
            old = self.weapon
            self.weapon = item
            if item in self.inventory:
                self.inventory.remove(item)
            if old:
                self.inventory.append(old)
            return old
        if item.item_type == ItemType.ARMOR:
            old = self.equipped_armor
            self.equipped_armor = item
            if item in self.inventory:
                self.inventory.remove(item)
            if old:
                self.inventory.append(old)
            return old
        return None


# ---------------------------------------------------------------------------
# Monster
# ---------------------------------------------------------------------------

_MONSTER_TEMPLATES = {
    "rat": {
        "names": ["Giant Rat", "Sewer Rat", "Plague Rat"],
        "char": "r",
        "hp": (4, 9),
        "atk": (2, 4),
        "def": 0,
        "xp": 5,
        "gold": (0, 3),
        "vision": 5,
    },
    "goblin": {
        "names": ["Goblin Scout", "Goblin Warrior", "Goblin Shaman"],
        "char": "g",
        "hp": (10, 18),
        "atk": (3, 6),
        "def": 1,
        "xp": 15,
        "gold": (2, 8),
        "vision": 7,
    },
    "orc": {
        "names": ["Orc Grunt", "Orc Berserker", "Orc Shaman"],
        "char": "o",
        "hp": (20, 35),
        "atk": (6, 11),
        "def": 2,
        "xp": 30,
        "gold": (5, 15),
        "vision": 6,
    },
    "troll": {
        "names": ["Cave Troll", "Bridge Troll"],
        "char": "T",
        "hp": (40, 65),
        "atk": (9, 16),
        "def": 3,
        "xp": 60,
        "gold": (10, 25),
        "vision": 5,
    },
    "lich": {
        "names": ["Ancient Lich", "Death Lich"],
        "char": "L",
        "hp": (80, 120),
        "atk": (15, 25),
        "def": 5,
        "xp": 200,
        "gold": (50, 120),
        "vision": 10,
    },
}


@dataclass
class Monster(Entity):
    xp_value: int = 10
    gold_value: int = 0
    monster_type: str = "goblin"
    vision_range: int = 7
    # Simple state: "idle" or "chase"
    state: str = "idle"

    @classmethod
    def create(
        cls,
        monster_type: str,
        x: int,
        y: int,
        rng: Optional[random.Random] = None,
    ) -> "Monster":
        if rng is None:
            rng = random.Random()
        tmpl = _MONSTER_TEMPLATES[monster_type]
        hp = rng.randint(*tmpl["hp"])
        atk = rng.randint(*tmpl["atk"])
        name = rng.choice(tmpl["names"])
        gold = rng.randint(*tmpl["gold"])
        return cls(
            name=name,
            x=x, y=y,
            char=tmpl["char"],
            hp=hp, max_hp=hp,
            attack=atk,
            defense=tmpl["def"],
            xp_value=tmpl["xp"],
            gold_value=gold,
            monster_type=monster_type,
            vision_range=tmpl["vision"],
        )

    def attack_roll(self) -> int:
        return self.attack + random.randint(0, max(1, self.attack // 4))

    @staticmethod
    def types_for_floor(floor: int) -> List[str]:
        """Return the monster types appropriate for the given floor depth."""
        if floor <= 2:
            return ["rat", "goblin"]
        if floor <= 4:
            return ["goblin", "orc"]
        if floor <= 6:
            return ["orc", "troll"]
        return ["troll", "lich"]
