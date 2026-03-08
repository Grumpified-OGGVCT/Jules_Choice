"""
Terminal rendering for Dungeon Forge.

Draws a scrolling viewport of the dungeon, a HUD panel on the right, and a
message log at the bottom.  All output uses ANSI escape codes; falls back to
plain text on non-colour terminals.
"""

from __future__ import annotations

import os
import shutil
import sys
from typing import TYPE_CHECKING, List, Set, Tuple

if TYPE_CHECKING:
    from dungeon_forge.game import GameState

from dungeon_forge.dungeon_gen import Tile


# ---------------------------------------------------------------------------
# ANSI helpers
# ---------------------------------------------------------------------------

class _C:
    """ANSI escape sequences."""
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"

    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def c(text: str, *codes: str) -> str:
    """Wrap *text* in ANSI colour codes (no-op if colour not supported)."""
    if not _supports_color():
        return text
    return "".join(codes) + text + _C.RESET


# ---------------------------------------------------------------------------
# ASCII title
# ---------------------------------------------------------------------------

TITLE_ART = c(r"""
 ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
 ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
 ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
 ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
 ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
 ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
          ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
          ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
          █████╗  ██║   ██║██████╔╝██║  ███╗█████╗
          ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
          ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
          ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
""", _C.BRIGHT_YELLOW, _C.BOLD)

SUBTITLE = c("        ⚔  A Procedural ASCII Dungeon Crawler  ⚔\n", _C.YELLOW)


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------

VIEWPORT_W = 40   # columns
VIEWPORT_H = 22   # rows
HUD_W = 22        # HUD panel width (characters)

# Tile glyphs & colours when visible / remembered
_TILE_VISIBLE = {
    Tile.WALL:     (c("█", _C.WHITE),           c("█", _C.DIM, _C.WHITE)),
    Tile.FLOOR:    (c(".", _C.WHITE),            c("·", _C.DIM)),
    Tile.CORRIDOR: (c("·", _C.WHITE),            c("·", _C.DIM)),
    Tile.ENTRANCE: (c("<", _C.BRIGHT_CYAN, _C.BOLD), c("<", _C.CYAN)),
    Tile.STAIRS:   (c(">", _C.BRIGHT_MAGENTA, _C.BOLD), c(">", _C.MAGENTA)),
}


def _bar(filled: int, total: int, char_full: str = "█", char_empty: str = "░") -> str:
    return char_full * filled + char_empty * (total - filled)


class Renderer:
    """Renders the game state to stdout."""

    def __init__(self) -> None:
        self._color = _supports_color()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def render(self, state: "GameState") -> None:
        """Clear screen and draw the full game view."""
        self._clear()
        term_w, _ = shutil.get_terminal_size((80, 24))

        lines: List[str] = []

        # Header
        header = "⚔  DUNGEON FORGE  ⚔"
        lines.append(c(f" {header:^{term_w - 2}} ", _C.BRIGHT_YELLOW, _C.BOLD))
        lines.append(c("═" * term_w, _C.YELLOW))

        # Map + HUD side by side
        map_lines = self._render_map(state)
        hud_lines = self._render_hud(state)
        for i in range(max(len(map_lines), len(hud_lines))):
            ml = map_lines[i] if i < len(map_lines) else " " * VIEWPORT_W
            hl = hud_lines[i] if i < len(hud_lines) else ""
            lines.append(ml + "  " + hl)

        # Divider + messages
        lines.append(c("─" * term_w, _C.YELLOW))
        for msg in state.recent_messages(4):
            lines.append("  " + msg)

        # Controls hint
        lines.append("")
        lines.append(c(
            "  [WASD / ↑↓←→] Move   [G] Pick up   [I] Inventory   [Q] Quit",
            _C.DIM,
        ))

        print("\n".join(lines))

    def render_inventory(self, state: "GameState") -> None:
        self._clear()
        player = state.player
        print(c("╔══════════════════════════════════╗", _C.YELLOW, _C.BOLD))
        print(c("║           INVENTORY              ║", _C.YELLOW, _C.BOLD))
        print(c("╚══════════════════════════════════╝", _C.YELLOW, _C.BOLD))
        print()

        if not player.inventory and player.weapon is None and player.equipped_armor is None:
            print(c("  Your pack is empty.", _C.DIM))
        else:
            if player.weapon:
                print(
                    c(f"  [E] {player.weapon.name}", _C.CYAN)
                    + c(f" (ATK +{player.weapon.effect}) [equipped]", _C.GREEN)
                )
            if player.equipped_armor:
                print(
                    c(f"  [R] {player.equipped_armor.name}", _C.BLUE)
                    + c(f" (DEF +{player.equipped_armor.effect}) [equipped]", _C.GREEN)
                )
            print()
            for idx, item in enumerate(player.inventory):
                key = chr(ord("a") + idx)
                if item.item_type.name == "HEALTH_POTION":
                    print(
                        c(f"  [{key}] {item.name}", _C.BRIGHT_GREEN)
                        + c(f" (heals ~{item.effect} HP)", _C.GREEN)
                    )
                elif item.item_type.name == "WEAPON":
                    print(
                        c(f"  [{key}] {item.name}", _C.CYAN)
                        + c(f" (ATK +{item.effect})", _C.BRIGHT_CYAN)
                    )
                elif item.item_type.name == "ARMOR":
                    print(
                        c(f"  [{key}] {item.name}", _C.BLUE)
                        + c(f" (DEF +{item.effect})", _C.BRIGHT_BLUE)
                    )
                else:
                    print(c(f"  [{key}] {item.name}", _C.YELLOW))

        print()
        print(c("  Press a letter to use/equip, or any other key to close.", _C.DIM))

    def render_title(self) -> None:
        self._clear()
        print(TITLE_ART)
        print(SUBTITLE)
        print()
        print(c("  [N] New game    [Q] Quit\n", _C.WHITE))

    def render_game_over(self, state: "GameState", won: bool) -> None:
        self._clear()
        player = state.player
        if won:
            print(c("\n  ★  VICTORY!  You escaped the dungeon!  ★\n", _C.BRIGHT_YELLOW, _C.BOLD))
        else:
            print(c("\n  ✝  YOU DIED  ✝\n", _C.BRIGHT_RED, _C.BOLD))
            print(c("  The dungeon claims another soul…\n", _C.RED))

        print(c(f"  Floor reached : {state.floor}", _C.WHITE))
        print(c(f"  Level         : {player.level}", _C.BRIGHT_YELLOW))
        print(c(f"  XP earned     : {player.xp}", _C.CYAN))
        print(c(f"  Gold collected: {player.gold}", _C.YELLOW))
        print(c(f"  Enemies slain : {player.kills}", _C.RED))
        print()
        print(c("  Press any key to return to the main menu.", _C.DIM))

    # ------------------------------------------------------------------
    # Map rendering
    # ------------------------------------------------------------------

    def _render_map(self, state: "GameState") -> List[str]:
        dungeon = state.dungeon
        player = state.player
        monsters = {(m.x, m.y): m for m in state.monsters if m.is_alive}
        items = {(item.x, item.y): item for item in state.floor_items}
        fog: Set[Tuple[int, int]] = state.explored
        visible: Set[Tuple[int, int]] = state.visible

        # Camera centred on player, clamped to map bounds
        cam_x = max(0, min(player.x - VIEWPORT_W // 2, dungeon.width - VIEWPORT_W))
        cam_y = max(0, min(player.y - VIEWPORT_H // 2, dungeon.height - VIEWPORT_H))

        lines: List[str] = []
        for dy in range(VIEWPORT_H):
            row = ""
            for dx in range(VIEWPORT_W):
                wx, wy = cam_x + dx, cam_y + dy
                pos = (wx, wy)

                # Player
                if wx == player.x and wy == player.y:
                    row += c("@", _C.BRIGHT_GREEN, _C.BOLD)
                    continue

                # Unexplored
                if pos not in fog:
                    row += c(" ", _C.DIM)
                    continue

                is_vis = pos in visible

                # Monster (only shown when visible)
                if is_vis and pos in monsters:
                    m = monsters[pos]
                    row += c(m.char, _C.BRIGHT_RED, _C.BOLD)
                    continue

                # Item
                if pos in items:
                    item = items[pos]
                    glyph = c(item.char, _C.BRIGHT_YELLOW) if is_vis else c(item.char, _C.YELLOW)
                    row += glyph
                    continue

                # Tile
                tile = dungeon.get_tile(wx, wy)
                vis_glyph, mem_glyph = _TILE_VISIBLE.get(tile, (" ", " "))
                row += vis_glyph if is_vis else mem_glyph

            lines.append(row)
        return lines

    # ------------------------------------------------------------------
    # HUD rendering
    # ------------------------------------------------------------------

    def _render_hud(self, state: "GameState") -> List[str]:
        p = state.player
        W = HUD_W
        lines: List[str] = []

        def row(content: str = "") -> None:
            lines.append(c("║", _C.YELLOW) + f" {content:<{W - 2}} " + c("║", _C.YELLOW))

        def divider() -> None:
            lines.append(c("╠" + "═" * W + "╣", _C.YELLOW))

        lines.append(c("╔" + "═" * W + "╗", _C.YELLOW))
        row(c("ADVENTURER", _C.BRIGHT_WHITE, _C.BOLD))
        row(c(f"Level {p.level}", _C.BRIGHT_YELLOW))
        divider()

        # HP bar
        hp_pct = p.hp / p.max_hp
        bar_len = W - 8
        filled = round(bar_len * hp_pct)
        hp_col = (_C.BRIGHT_RED if hp_pct < 0.25 else
                  _C.YELLOW if hp_pct < 0.5 else
                  _C.BRIGHT_GREEN)
        row(c("HP  ", _C.WHITE) + c(_bar(filled, bar_len), hp_col))
        row(c(f"    {p.hp:3d} / {p.max_hp:3d}", _C.WHITE))

        # XP bar
        xp_needed = p.xp_to_next()
        xp_pct = min(1.0, p.xp / xp_needed)
        filled_xp = round(bar_len * xp_pct)
        row(c("XP  ", _C.WHITE) + c(_bar(filled_xp, bar_len), _C.BRIGHT_CYAN))
        row(c(f"    {p.xp:3d} / {xp_needed:3d}", _C.WHITE))

        divider()

        # Stats
        atk = p.attack + (p.weapon.effect if p.weapon else 0)
        def_ = p.effective_defense()
        row(c(f"ATK  {atk:<4}  DEF  {def_:<4}", _C.WHITE))
        row(c(f"Gold {p.gold:<6}  Kills {p.kills:<4}", _C.BRIGHT_YELLOW))

        divider()

        # Equipment
        wname = (p.weapon.name if p.weapon else "Bare Hands")[:W - 4]
        aname = (p.equipped_armor.name if p.equipped_armor else "No Armour")[:W - 4]
        row(c("Weapon:", _C.WHITE))
        row(c(f" {wname}", _C.CYAN))
        row(c("Armour:", _C.WHITE))
        row(c(f" {aname}", _C.BLUE))

        divider()
        row(c(f"Floor  {state.floor}", _C.MAGENTA))
        row(c(f"Room   {state.current_room + 1} / {len(state.dungeon.rooms)}", _C.DIM))
        lines.append(c("╚" + "═" * W + "╝", _C.YELLOW))

        # Pad to viewport height
        while len(lines) < VIEWPORT_H:
            lines.append("")
        return lines

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _clear() -> None:
        os.system("cls" if os.name == "nt" else "clear")
