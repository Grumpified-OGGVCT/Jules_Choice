"""
Procedural dungeon map generation using Binary Space Partitioning (BSP).

The dungeon is represented as a 2-D grid of Tiles.  The generator:
  1. Recursively splits the grid into BSP leaf regions.
  2. Places one room inside each leaf.
  3. Connects sibling rooms with L-shaped corridors.
  4. Marks the first room's centre as the entrance and the last as the exit.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# Tile types
# ---------------------------------------------------------------------------

class Tile(Enum):
    WALL = auto()
    FLOOR = auto()
    CORRIDOR = auto()
    ENTRANCE = auto()
    STAIRS = auto()


# ---------------------------------------------------------------------------
# Rect helper
# ---------------------------------------------------------------------------

@dataclass
class Rect:
    """Axis-aligned rectangle, defined by its top-left corner and size."""

    x: int
    y: int
    width: int
    height: int

    @property
    def x2(self) -> int:
        return self.x + self.width

    @property
    def y2(self) -> int:
        return self.y + self.height

    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    def contains(self, x: int, y: int) -> bool:
        """Return True if (x, y) is strictly inside the rectangle."""
        return self.x < x < self.x2 and self.y < y < self.y2

    def overlaps(self, other: "Rect", padding: int = 1) -> bool:
        """Return True if this rect overlaps *other* (with optional padding)."""
        return (
            self.x - padding < other.x2
            and self.x2 + padding > other.x
            and self.y - padding < other.y2
            and self.y2 + padding > other.y
        )


# ---------------------------------------------------------------------------
# BSP node
# ---------------------------------------------------------------------------

@dataclass
class BSPNode:
    """A node in the Binary Space Partition tree."""

    region: Rect
    left: Optional["BSPNode"] = field(default=None, repr=False)
    right: Optional["BSPNode"] = field(default=None, repr=False)
    room: Optional[Rect] = field(default=None)

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def get_room(self) -> Optional[Rect]:
        """Return the room for this node (delegates to children if not a leaf)."""
        if self.room:
            return self.room
        left_room = self.left.get_room() if self.left else None
        right_room = self.right.get_room() if self.right else None
        if left_room and right_room:
            return left_room
        return left_room or right_room


# ---------------------------------------------------------------------------
# Dungeon map
# ---------------------------------------------------------------------------

class DungeonMap:
    """A procedurally generated dungeon floor.

    Parameters
    ----------
    width, height:
        Dimensions of the tile grid (including outer walls).
    min_rooms:
        Minimum number of rooms to generate.  Actual count may vary.
    seed:
        Optional RNG seed for reproducible maps.
    """

    MIN_ROOM_SIZE = 4   # interior width/height (exclusive of walls)
    MAX_ROOM_SIZE = 10
    MIN_REGION_SIZE = MIN_ROOM_SIZE + 4

    def __init__(
        self,
        width: int = 80,
        height: int = 40,
        min_rooms: int = 8,
        seed: Optional[int] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.rng = random.Random(seed)

        # Tile grid — filled with walls initially
        self.tiles: List[List[Tile]] = [
            [Tile.WALL] * width for _ in range(height)
        ]
        self.rooms: List[Rect] = []
        self.entrance: Tuple[int, int] = (0, 0)
        self.exit: Tuple[int, int] = (0, 0)

        self._generate(min_rooms)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_tile(self, x: int, y: int) -> Tile:
        """Return the tile at (x, y), or WALL if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return Tile.WALL

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile

    def is_walkable(self, x: int, y: int) -> bool:
        return self.get_tile(x, y) != Tile.WALL

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def _generate(self, min_rooms: int) -> None:
        root = BSPNode(Rect(1, 1, self.width - 2, self.height - 2))
        self._split(root, depth=0, max_depth=5)

        self._place_rooms(root)

        # Retry if we got too few rooms
        if len(self.rooms) < min_rooms:
            self.tiles = [[Tile.WALL] * self.width for _ in range(self.height)]
            self.rooms.clear()
            self._generate(min_rooms)
            return

        self._connect_rooms(root)

        # Mark entrance (first room) and exit (last room)
        ex, ey = self.rooms[0].center
        sx, sy = self.rooms[-1].center
        self.entrance = (ex, ey)
        self.exit = (sx, sy)
        self.tiles[ey][ex] = Tile.ENTRANCE
        self.tiles[sy][sx] = Tile.STAIRS

    def _split(self, node: BSPNode, depth: int, max_depth: int) -> None:
        """Recursively split *node* into two children."""
        if depth >= max_depth:
            return

        region = node.region
        can_split_h = region.height >= 2 * self.MIN_REGION_SIZE
        can_split_v = region.width >= 2 * self.MIN_REGION_SIZE

        if not can_split_h and not can_split_v:
            return  # region too small to split

        # Choose split orientation
        if can_split_h and can_split_v:
            horizontal = self.rng.random() < 0.5
        else:
            horizontal = can_split_h

        if horizontal:
            split_at = self.rng.randint(
                region.y + self.MIN_REGION_SIZE,
                region.y2 - self.MIN_REGION_SIZE,
            )
            node.left = BSPNode(Rect(region.x, region.y, region.width, split_at - region.y))
            node.right = BSPNode(Rect(region.x, split_at, region.width, region.y2 - split_at))
        else:
            split_at = self.rng.randint(
                region.x + self.MIN_REGION_SIZE,
                region.x2 - self.MIN_REGION_SIZE,
            )
            node.left = BSPNode(Rect(region.x, region.y, split_at - region.x, region.height))
            node.right = BSPNode(Rect(split_at, region.y, region.x2 - split_at, region.height))

        self._split(node.left, depth + 1, max_depth)
        self._split(node.right, depth + 1, max_depth)

    def _place_rooms(self, node: BSPNode) -> None:
        """Place rooms in every leaf node."""
        if node.is_leaf:
            region = node.region
            # Random room size within the region
            max_w = min(self.MAX_ROOM_SIZE, region.width - 2)
            max_h = min(self.MAX_ROOM_SIZE, region.height - 2)
            if max_w < self.MIN_ROOM_SIZE or max_h < self.MIN_ROOM_SIZE:
                return
            rw = self.rng.randint(self.MIN_ROOM_SIZE, max_w)
            rh = self.rng.randint(self.MIN_ROOM_SIZE, max_h)
            rx = self.rng.randint(region.x + 1, region.x2 - rw - 1)
            ry = self.rng.randint(region.y + 1, region.y2 - rh - 1)
            room = Rect(rx, ry, rw, rh)
            node.room = room
            self.rooms.append(room)
            self._carve_room(room)
        else:
            if node.left:
                self._place_rooms(node.left)
            if node.right:
                self._place_rooms(node.right)

    def _connect_rooms(self, node: BSPNode) -> None:
        """Connect sibling rooms with corridors, bottom-up."""
        if node.is_leaf:
            return
        if node.left:
            self._connect_rooms(node.left)
        if node.right:
            self._connect_rooms(node.right)

        left_room = node.left.get_room() if node.left else None
        right_room = node.right.get_room() if node.right else None
        if left_room and right_room:
            self._carve_corridor(left_room.center, right_room.center)

    # ------------------------------------------------------------------
    # Carving helpers
    # ------------------------------------------------------------------

    def _carve_room(self, room: Rect) -> None:
        for y in range(room.y + 1, room.y2):
            for x in range(room.x + 1, room.x2):
                self.tiles[y][x] = Tile.FLOOR

    def _carve_corridor(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> None:
        """Carve an L-shaped corridor between two points."""
        x1, y1 = start
        x2, y2 = end
        if self.rng.random() < 0.5:
            self._carve_h_tunnel(x1, x2, y1)
            self._carve_v_tunnel(y1, y2, x2)
        else:
            self._carve_v_tunnel(y1, y2, x1)
            self._carve_h_tunnel(x1, x2, y2)

    def _carve_h_tunnel(self, x1: int, x2: int, y: int) -> None:
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.tiles[y][x] == Tile.WALL:
                self.tiles[y][x] = Tile.CORRIDOR

    def _carve_v_tunnel(self, y1: int, y2: int, x: int) -> None:
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.tiles[y][x] == Tile.WALL:
                self.tiles[y][x] = Tile.CORRIDOR
