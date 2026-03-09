"""
Autonomous Model & Agent Registry — SQL persistence layer.

Uses stdlib sqlite3 (no ORM) to stay within the Layer 1 "4 GB RAM" constraint.
All tables are created with IF NOT EXISTS for idempotent init.
"""

from __future__ import annotations

import enum
import json
import sqlite3
import time
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

_DB_DIR = Path(__file__).parent.parent.parent / "data"
_DB_PATH = _DB_DIR / "registry.db"


def db_path() -> Path:
    return _DB_PATH


class ModelTier(enum.StrEnum):
    S = "S"
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    C = "C"
    D = "D"


TIER_MAP: dict[str, ModelTier] = {t.value: t for t in ModelTier}


class Provider(enum.StrEnum):
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"
    CLOUD = "cloud"


@contextmanager
def get_db(path: Path | str | None = None) -> Generator[sqlite3.Connection, None, None]:
    p = str(path or _DB_PATH)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_ts      TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    families    TEXT    NOT NULL DEFAULT '[]',
    model_count INTEGER NOT NULL DEFAULT 0,
    is_promoted INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS models (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id    INTEGER NOT NULL REFERENCES snapshots(id),
    model_id       TEXT    NOT NULL,
    family         TEXT    NOT NULL DEFAULT '',
    param_b        REAL    NOT NULL DEFAULT 0.0,
    quant          TEXT    NOT NULL DEFAULT '',
    raw_score      REAL    NOT NULL DEFAULT 0.0,
    tier           TEXT    NOT NULL DEFAULT 'D',
    context_length INTEGER NOT NULL DEFAULT 0,
    UNIQUE(snapshot_id, model_id)
);

CREATE TABLE IF NOT EXISTS model_tiers (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id       TEXT    NOT NULL,
    tier           TEXT    NOT NULL,
    effective_from TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    effective_to   TEXT
);

CREATE TABLE IF NOT EXISTS user_local_inventory (
    model_id        TEXT PRIMARY KEY,
    size_gb         REAL    NOT NULL DEFAULT 0.0,
    last_seen       TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now')),
    vram_required_mb INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS local_model_metadata (
    model_id           TEXT PRIMARY KEY,
    digest             TEXT    NOT NULL DEFAULT '',
    modified_at        TEXT    NOT NULL DEFAULT '',
    quantization_level TEXT    NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS agent_templates (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT    NOT NULL UNIQUE,
    required_tier     TEXT    NOT NULL DEFAULT 'D',
    system_prompt     TEXT    NOT NULL DEFAULT '',
    tools_json        TEXT    NOT NULL DEFAULT '[]',
    restrictions_json TEXT    NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS model_equivalents (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_id      TEXT    NOT NULL,
    provider          TEXT    NOT NULL,
    provider_model_id TEXT    NOT NULL,
    UNIQUE(canonical_id, provider)
);

CREATE TABLE IF NOT EXISTS policy_bundles (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    rules_json TEXT    NOT NULL DEFAULT '{}',
    active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS model_feedback (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id  TEXT    NOT NULL,
    rating    INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    context   TEXT    NOT NULL DEFAULT '',
    ts        TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S','now'))
);
"""


def init_db(path: Path | str | None = None) -> None:
    with get_db(path) as conn:
        conn.executescript(_SCHEMA_SQL)
        seed_aegis_templates(conn)


def create_snapshot(conn: sqlite3.Connection, families: list[str] | None = None) -> int:
    fam_json = json.dumps(families or [])
    cur = conn.execute("INSERT INTO snapshots (families) VALUES (?)", (fam_json,))
    return cur.lastrowid


def promote_snapshot(conn: sqlite3.Connection, snapshot_id: int) -> None:
    conn.execute("UPDATE snapshots SET is_promoted = 0 WHERE is_promoted = 1")
    conn.execute("UPDATE snapshots SET is_promoted = 1 WHERE id = ?", (snapshot_id,))


def get_active_snapshot(conn: sqlite3.Connection) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM snapshots WHERE is_promoted = 1 ORDER BY id DESC LIMIT 1").fetchone()


def update_snapshot_model_count(conn: sqlite3.Connection, snapshot_id: int, count: int) -> None:
    conn.execute("UPDATE snapshots SET model_count = ? WHERE id = ?", (count, snapshot_id))


def upsert_model(conn: sqlite3.Connection, snapshot_id: int, model_id: str, *, family: str = "", param_b: float = 0.0, quant: str = "", raw_score: float = 0.0, tier: str = "D", context_length: int = 0) -> int:
    cur = conn.execute(
        "INSERT INTO models (snapshot_id, model_id, family, param_b, quant, raw_score, tier, context_length) VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(snapshot_id, model_id) DO UPDATE SET family=excluded.family, param_b=excluded.param_b, quant=excluded.quant, raw_score=excluded.raw_score, tier=excluded.tier, context_length=excluded.context_length",
        (snapshot_id, model_id, family, param_b, quant, raw_score, tier, context_length),
    )
    return cur.lastrowid


def get_models_by_tier(conn: sqlite3.Connection, tier: str, snapshot_id: int | None = None) -> list[sqlite3.Row]:
    if snapshot_id is None:
        snap = get_active_snapshot(conn)
        if snap is None:
            return []
        snapshot_id = snap["id"]
    return conn.execute("SELECT * FROM models WHERE snapshot_id = ? AND tier = ? ORDER BY raw_score DESC", (snapshot_id, tier)).fetchall()


def get_all_models(conn: sqlite3.Connection, snapshot_id: int | None = None) -> list[sqlite3.Row]:
    if snapshot_id is None:
        snap = get_active_snapshot(conn)
        if snap is None:
            return []
        snapshot_id = snap["id"]
    return conn.execute("SELECT * FROM models WHERE snapshot_id = ? ORDER BY raw_score DESC", (snapshot_id,)).fetchall()


def upsert_local_inventory(conn: sqlite3.Connection, model_id: str, *, size_gb: float = 0.0, vram_required_mb: int = 0) -> None:
    now = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    conn.execute("INSERT INTO user_local_inventory (model_id, size_gb, last_seen, vram_required_mb) VALUES (?, ?, ?, ?) ON CONFLICT(model_id) DO UPDATE SET size_gb=excluded.size_gb, last_seen=excluded.last_seen, vram_required_mb=excluded.vram_required_mb", (model_id, size_gb, now, vram_required_mb))


def get_local_inventory(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM user_local_inventory ORDER BY last_seen DESC").fetchall()


def upsert_local_metadata(conn: sqlite3.Connection, model_id: str, *, digest: str = "", modified_at: str = "", quantization_level: str = "") -> None:
    conn.execute("INSERT INTO local_model_metadata (model_id, digest, modified_at, quantization_level) VALUES (?, ?, ?, ?) ON CONFLICT(model_id) DO UPDATE SET digest=excluded.digest, modified_at=excluded.modified_at, quantization_level=excluded.quantization_level", (model_id, digest, modified_at, quantization_level))


def upsert_agent_template(conn: sqlite3.Connection, name: str, *, required_tier: str = "D", system_prompt: str = "", tools: list[str] | None = None, restrictions: dict[str, Any] | None = None) -> int:
    cur = conn.execute("INSERT INTO agent_templates (name, required_tier, system_prompt, tools_json, restrictions_json) VALUES (?, ?, ?, ?, ?) ON CONFLICT(name) DO UPDATE SET required_tier=excluded.required_tier, system_prompt=excluded.system_prompt, tools_json=excluded.tools_json, restrictions_json=excluded.restrictions_json", (name, required_tier, system_prompt, json.dumps(tools or []), json.dumps(restrictions or {})))
    return cur.lastrowid


def get_agent_template(conn: sqlite3.Connection, name: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM agent_templates WHERE name = ?", (name,)).fetchone()


def upsert_model_equivalent(conn: sqlite3.Connection, canonical_id: str, provider: str, provider_model_id: str) -> None:
    conn.execute("INSERT INTO model_equivalents (canonical_id, provider, provider_model_id) VALUES (?, ?, ?) ON CONFLICT(canonical_id, provider) DO UPDATE SET provider_model_id=excluded.provider_model_id", (canonical_id, provider, provider_model_id))


def get_equivalents(conn: sqlite3.Connection, canonical_id: str) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM model_equivalents WHERE canonical_id = ?", (canonical_id,)).fetchall()


def upsert_policy_bundle(conn: sqlite3.Connection, name: str, *, rules: dict[str, Any] | None = None, active: bool = True) -> int:
    cur = conn.execute("INSERT INTO policy_bundles (name, rules_json, active) VALUES (?, ?, ?) ON CONFLICT(name) DO UPDATE SET rules_json=excluded.rules_json, active=excluded.active", (name, json.dumps(rules or {}), int(active)))
    return cur.lastrowid


def get_active_policies(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM policy_bundles WHERE active = 1").fetchall()


def add_feedback(conn: sqlite3.Connection, model_id: str, rating: int, context: str = "") -> int:
    cur = conn.execute("INSERT INTO model_feedback (model_id, rating, context) VALUES (?, ?, ?)", (model_id, rating, context))
    return cur.lastrowid


def get_feedback(conn: sqlite3.Connection, model_id: str, limit: int = 50) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM model_feedback WHERE model_id = ? ORDER BY ts DESC LIMIT ?", (model_id, limit)).fetchall()


def record_tier_change(conn: sqlite3.Connection, model_id: str, tier: str) -> None:
    now = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
    conn.execute("UPDATE model_tiers SET effective_to = ? WHERE model_id = ? AND effective_to IS NULL", (now, model_id))
    conn.execute("INSERT INTO model_tiers (model_id, tier, effective_from) VALUES (?, ?, ?)", (model_id, tier, now))


def get_current_tier(conn: sqlite3.Connection, model_id: str) -> str | None:
    row = conn.execute("SELECT tier FROM model_tiers WHERE model_id = ? AND effective_to IS NULL", (model_id,)).fetchone()
    return row["tier"] if row else None


def seed_aegis_templates(conn: sqlite3.Connection) -> None:
    upsert_agent_template(conn, "sentinel", required_tier="S", system_prompt="You are the Sentinel. Your primary goal is to ensure the security and integrity of the Sovereign OS. You scan all incoming intents for ALIGN policy violations and privilege escalation attempts.", tools=["READ"], restrictions={"max_gas": 50, "allow_network": False, "gas_per_scan": 1})
    upsert_agent_template(conn, "scribe", required_tier="A", system_prompt="You are the Scribe. You maintain the immutable ALS Merkle log of all system activities. You audit gas consumption and ensure that the global gas budget is not exceeded.", tools=["READ", "WRITE"], restrictions={"max_gas": 30, "allow_network": False, "budget_gate_pct": 0.8})
    upsert_agent_template(conn, "arbiter", required_tier="S", system_prompt="You are the Arbiter. You adjudicate security alerts and budget breaches reported by the Sentinel and Scribe. Your verdict is final. You can quarantine malicious agents and authorize emergency overrides.", tools=["READ", "WRITE"], restrictions={"max_gas": 100, "allow_network": True, "gas_per_adjudication": 2})
