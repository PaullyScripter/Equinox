"""Shared SQLite persistence for all non-premium features.

Replaces JSON file I/O with a single SQLite database (data/equinox.db)
using WAL mode for concurrent read/write safety.

All public functions are SYNCHRONOUS (same contract as the JSON functions
they replace). Async callers should offload via run_in_executor if needed.
"""

import sqlite3, time
import json
import os
import threading
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone

DB_PATH = "data/equinox.db"

_db_lock = threading.Lock()
_db_conn: sqlite3.Connection = None


def _conn():
    global _db_conn
    if _db_conn is None:
        _db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _db_conn.row_factory = sqlite3.Row
        _db_conn.execute("PRAGMA journal_mode=WAL")
        _db_conn.execute("PRAGMA foreign_keys=ON")
    return _db_conn


# ── Initialisation ──────────────────────────────────────────────

def init_db():
    with _db_lock:
        c = _conn()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS command_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                command TEXT NOT NULL,
                timestamp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS auto_ping (
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, channel_id)
            );
            CREATE TABLE IF NOT EXISTS auto_role (
                guild_id INTEGER PRIMARY KEY,
                role_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS privacy_settings (
                user_id INTEGER PRIMARY KEY,
                presence_disabled INTEGER NOT NULL DEFAULT 0,
                status_disabled INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS message_counter (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS message_counter_config (
                guild_id INTEGER PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 1,
                blacklisted_channels TEXT NOT NULL DEFAULT '[]',
                opted_out_users TEXT NOT NULL DEFAULT '[]'
            );
            CREATE TABLE IF NOT EXISTS gemini_servers (
                guild_id INTEGER PRIMARY KEY
            );
            CREATE TABLE IF NOT EXISTS audit_config (
                guild_id INTEGER PRIMARY KEY,
                enabled INTEGER NOT NULL DEFAULT 0,
                channel_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id INTEGER PRIMARY KEY,
                config_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS scam_actions (
                action_id TEXT PRIMARY KEY,
                guild_id INTEGER,
                author_id INTEGER,
                content TEXT,
                reasons TEXT,
                domains TEXT,
                timestamp TEXT
            );
            CREATE TABLE IF NOT EXISTS scam_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts INTEGER,
                label TEXT,
                data_json TEXT
            );
            CREATE TABLE IF NOT EXISTS pattern_weights (
                reason TEXT PRIMARY KEY,
                weight REAL NOT NULL DEFAULT 1.0,
                last_updated INTEGER
            );
            CREATE TABLE IF NOT EXISTS verify_config (
                guild_id INTEGER PRIMARY KEY,
                remove_role INTEGER,
                add_role INTEGER,
                url TEXT,
                message_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS user_verifying (
                guild_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS reaction_roles_main (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                template_name TEXT,
                roles_json TEXT,
                custom_id TEXT
            );
            CREATE TABLE IF NOT EXISTS reaction_roles_cog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                template_name TEXT,
                data_json TEXT
            );
            CREATE TABLE IF NOT EXISTS ticket_config (
                guild_id INTEGER PRIMARY KEY,
                msg_id INTEGER,
                category_id INTEGER,
                support_role INTEGER,
                ticket_count INTEGER DEFAULT 0,
                extra_json TEXT DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS ticket_active (
                channel_id INTEGER PRIMARY KEY,
                guild_id INTEGER NOT NULL,
                owner_id INTEGER NOT NULL,
                claimed_by INTEGER,
                topic TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ticket_archived (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER,
                guild_id INTEGER,
                owner_id INTEGER,
                transcript TEXT,
                closed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS ticket_archived_extra (
                channel_id INTEGER PRIMARY KEY,
                extra_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ticket_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                note TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS ticket_participants (
                channel_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (channel_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS ticket_server_info (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS giveaways (
                guild_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                prize TEXT,
                winners INTEGER DEFAULT 1,
                end_time TEXT,
                entries TEXT DEFAULT '[]',
                hosts TEXT DEFAULT '[]',
                roles TEXT DEFAULT '[]',
                data_json TEXT DEFAULT '{}',
                PRIMARY KEY (guild_id, message_id)
            );
        """)
        c.commit()
        _migrate_json(c)


def _migrate_json(c):
    """Idempotent migration from existing JSON files."""
    if c.execute("SELECT COUNT(*) FROM command_stats").fetchone()[0] > 0:
        return

    # 1. Command stats
    if os.path.exists("data/command_stats.json"):
        try:
            with open("data/command_stats.json", encoding="utf-8") as f:
                data = json.load(f)
            for ev in data.get("events", []):
                c.execute("INSERT INTO command_stats (user_id, command, timestamp) VALUES (?, ?, ?)",
                          (ev.get("user_id"), ev.get("command"), ev.get("timestamp")))
        except Exception:
            pass

    # 2. Auto-ping
    if os.path.isdir("autoping_data"):
        for fname in os.listdir("autoping_data"):
            if fname.startswith("autoping_") and fname.endswith(".json"):
                try:
                    gid = int(fname.replace("autoping_", "").replace(".json", ""))
                    with open(os.path.join("autoping_data", fname)) as f:
                        for cid in json.load(f):
                            c.execute("INSERT OR IGNORE INTO auto_ping (guild_id, channel_id) VALUES (?, ?)", (gid, cid))
                except Exception:
                    pass

    # 3. Auto-role
    if os.path.isdir("autorole_data"):
        for fname in os.listdir("autorole_data"):
            if fname.startswith("autorole_") and fname.endswith(".json"):
                try:
                    gid = int(fname.replace("autorole_", "").replace(".json", ""))
                    with open(os.path.join("autorole_data", fname)) as f:
                        rid = json.load(f)
                    if rid:
                        c.execute("INSERT OR IGNORE INTO auto_role (guild_id, role_id) VALUES (?, ?)", (gid, rid))
                except Exception:
                    pass

    # 4. Privacy
    if os.path.exists("data/privacy_settings.json"):
        try:
            with open("data/privacy_settings.json", encoding="utf-8") as f:
                priv = json.load(f)
            for uid_str, cats in priv.items():
                c.execute("INSERT OR IGNORE INTO privacy_settings (user_id, presence_disabled, status_disabled) VALUES (?, ?, ?)",
                          (int(uid_str), 1 if "presence" in cats else 0, 1 if "status" in cats else 0))
        except Exception:
            pass

    # 5. Message counter
    if os.path.isdir("messageCounterData"):
        for fname in os.listdir("messageCounterData"):
            if fname.startswith("messagecounter_") and fname.endswith(".json"):
                try:
                    gid = int(fname.replace("messagecounter_", "").replace(".json", ""))
                    with open(os.path.join("messageCounterData", fname)) as f:
                        data = json.load(f)
                    status_val = data.get("status", True)
                    enabled = 1 if (isinstance(status_val, str) and status_val == "enabled") or (not isinstance(status_val, str) and status_val) else 0
                    c.execute("INSERT OR IGNORE INTO message_counter_config (guild_id, enabled, blacklisted_channels, opted_out_users) VALUES (?, ?, ?, ?)",
                              (gid, enabled, json.dumps(data.get("blacklisted_channels", [])), json.dumps(data.get("opted_out_users", []))))
                    for uid_str, count in data.get("users", {}).items():
                        c.execute("INSERT OR IGNORE INTO message_counter (guild_id, user_id, count) VALUES (?, ?, ?)", (gid, int(uid_str), count))
                except Exception:
                    pass

    # 6. Gemini
    if os.path.exists("data/geminiServer.json"):
        try:
            with open("data/geminiServer.json") as f:
                gs = json.load(f)
            for sid in gs.get("servers", []):
                c.execute("INSERT OR IGNORE INTO gemini_servers (guild_id) VALUES (?)", (sid,))
        except Exception:
            pass

    # 7. Audit config
    if os.path.exists("data/audit_config.json"):
        try:
            with open("data/audit_config.json") as f:
                ac = json.load(f)
            for gid_str, cfg in ac.items():
                c.execute("INSERT OR IGNORE INTO audit_config (guild_id, enabled, channel_id) VALUES (?, ?, ?)",
                          (int(gid_str), 1 if cfg.get("enabled") else 0, cfg.get("channel")))
        except Exception:
            pass

    # 8. Guild config
    if os.path.exists("data/guild_config.json"):
        try:
            with open("data/guild_config.json", encoding="utf-8") as f:
                gc = json.load(f)
            for gid_str, cfg_data in gc.items():
                c.execute("INSERT OR IGNORE INTO guild_config (guild_id, config_json) VALUES (?, ?)",
                          (int(gid_str), json.dumps(cfg_data)))
        except Exception:
            pass

    # 9. Scam actions
    if os.path.exists("data/scam_actions.json"):
        try:
            with open("data/scam_actions.json", encoding="utf-8") as f:
                sa = json.load(f)
            for aid, ad in sa.items():
                c.execute("INSERT OR IGNORE INTO scam_actions (action_id, guild_id, author_id, content, reasons, domains, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (aid, ad.get("guild_id"), ad.get("author_id"), ad.get("content"),
                           json.dumps(ad.get("reasons", [])), json.dumps(ad.get("domains", [])), ad.get("timestamp")))
        except Exception:
            pass

    # 10. Scam feedback
    if os.path.exists("data/scam_feedback.jsonl"):
        try:
            with open("data/scam_feedback.jsonl", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    c.execute("INSERT INTO scam_feedback (ts, label, data_json) VALUES (?, ?, ?)",
                              (entry.get("ts"), entry.get("label"), json.dumps(entry)))
        except Exception:
            pass

    # 11. Verify config
    if os.path.exists("data/verify_system.json"):
        try:
            with open("data/verify_system.json") as f:
                vs = json.load(f)
            for g_entry in vs.get("guilds", []):
                c.execute("INSERT OR IGNORE INTO verify_config (guild_id, remove_role, add_role, url, message_id) VALUES (?, ?, ?, ?, ?)",
                          (g_entry["guildid"], g_entry.get("remove_role"), g_entry.get("add_role"), g_entry.get("url"), g_entry.get("messageid")))
        except Exception:
            pass

    # 12. User verifying
    if os.path.exists("data/user_verifying.json"):
        try:
            with open("data/user_verifying.json") as f:
                uv = json.load(f)
            for pair in uv.get("users", []):
                if isinstance(pair, list) and len(pair) == 2:
                    c.execute("INSERT OR IGNORE INTO user_verifying (guild_id, user_id) VALUES (?, ?)", (int(pair[0]), int(pair[1])))
        except Exception:
            pass

    # 13. Reaction roles (main)
    if os.path.exists("data/reaction_roles.json"):
        try:
            with open("data/reaction_roles.json") as f:
                rr = json.load(f)
            for guild_str, templates in rr.items():
                gid = int(guild_str)
                for tpl in templates if isinstance(templates, list) else []:
                    c.execute("INSERT OR IGNORE INTO reaction_roles_main (guild_id, template_name, roles_json, custom_id) VALUES (?, ?, ?, ?)",
                              (gid, tpl.get("name"), json.dumps(tpl.get("roles", [])), tpl.get("custom_id")))
        except Exception:
            pass

    # 14. Reaction roles (cog)
    if os.path.exists("data/reactionroles.json"):
        try:
            with open("data/reactionroles.json") as f:
                rrc = json.load(f)
            for guild_str, templates in rrc.items():
                gid = int(guild_str)
                for tpl in templates if isinstance(templates, list) else []:
                    c.execute("INSERT OR IGNORE INTO reaction_roles_cog (guild_id, template_name, data_json) VALUES (?, ?, ?)",
                              (gid, tpl.get("type") or tpl.get("name"), json.dumps(tpl)))
        except Exception:
            pass

    # 15. Giveaways
    if os.path.isdir("giveawayFolder"):
        for fname in os.listdir("giveawayFolder"):
            if fname.startswith("giveaways_") and fname.endswith(".json"):
                try:
                    gid = int(fname.replace("giveaways_", "").replace(".json", ""))
                    with open(os.path.join("giveawayFolder", fname)) as f:
                        gw = json.load(f)
                    for msg_id_str, gw_data in gw.items():
                        c.execute("INSERT OR IGNORE INTO giveaways (guild_id, message_id, prize, winners, end_time, entries, hosts, roles, data_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  (gid, int(msg_id_str), gw_data.get("prize"), gw_data.get("winners", 1), gw_data.get("end_time"),
                                   json.dumps(gw_data.get("entries", [])), json.dumps(gw_data.get("hosts", [])), json.dumps(gw_data.get("roles", [])), json.dumps(gw_data)))
                except Exception:
                    pass

    # 16. Ticket active
    if os.path.exists("ticket-json/active-tickets.json"):
        try:
            with open("ticket-json/active-tickets.json") as f:
                at = json.load(f)
            for cid_str, tdata in (at if isinstance(at, dict) else {}).items():
                if isinstance(tdata, dict):
                    c.execute("INSERT OR IGNORE INTO ticket_active (channel_id, guild_id, owner_id, claimed_by, topic, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                              (int(cid_str), tdata.get("guild_id"), tdata.get("owner_id"), tdata.get("claimed_by"), tdata.get("topic"), tdata.get("created_at", datetime.now(timezone.utc).isoformat())))
        except Exception:
            pass

    # 17. Ticket archived
    if os.path.exists("ticket-json/archived-tickets.json"):
        try:
            with open("ticket-json/archived-tickets.json") as f:
                ar = json.load(f)
            for cid_str, tdata in (ar if isinstance(ar, dict) else {}).items():
                if isinstance(tdata, dict):
                    c.execute("INSERT OR IGNORE INTO ticket_archived (channel_id, guild_id, owner_id, transcript, closed_at) VALUES (?, ?, ?, ?, ?)",
                              (int(cid_str), tdata.get("guild_id"), tdata.get("owner_id"), tdata.get("transcript"), tdata.get("closed_at")))
        except Exception:
            pass

    # 18. Ticket history
    if os.path.exists("ticket-json/ticket-history.json"):
        try:
            with open("ticket-json/ticket-history.json") as f:
                th = json.load(f)
            for cid_str, entries in (th if isinstance(th, dict) else {}).items():
                for entry in entries if isinstance(entries, list) else []:
                    c.execute("INSERT INTO ticket_history (channel_id, action, user_id, timestamp, note) VALUES (?, ?, ?, ?, ?)",
                              (int(cid_str), entry.get("action"), entry.get("user_id"), entry.get("at"), entry.get("note", "")))
        except Exception:
            pass

    # 19. Ticket participants
    if os.path.exists("ticket-json/ticket-participants.json"):
        try:
            with open("ticket-json/ticket-participants.json") as f:
                tp = json.load(f)
            for cid_str, uids in (tp if isinstance(tp, dict) else {}).items():
                for uid in uids if isinstance(uids, list) else []:
                    c.execute("INSERT OR IGNORE INTO ticket_participants (channel_id, user_id) VALUES (?, ?)", (int(cid_str), uid))
        except Exception:
            pass

    # 20. Ticket server info
    if os.path.exists("ticket-json/ticket-server.json"):
        try:
            with open("ticket-json/ticket-server.json") as f:
                ts = json.load(f)
            for k, v in (ts if isinstance(ts, dict) else {}).items():
                c.execute("INSERT OR IGNORE INTO ticket_server_info (key, value) VALUES (?, ?)", (k, json.dumps(v) if isinstance(v, (dict, list)) else str(v)))
        except Exception:
            pass

    # 21. Per-guild ticket configs
    if os.path.isdir("ticket-json"):
        for fname in os.listdir("ticket-json"):
            if fname.endswith("-ticket.json") and not any(x in fname for x in ("active", "archived", "ticket-")):
                try:
                    gid = int(fname.replace("-ticket.json", ""))
                    with open(os.path.join("ticket-json", fname)) as f:
                        tc = json.load(f)
                    msgs = tc.get("message", [])
                    c.execute("INSERT OR IGNORE INTO ticket_config (guild_id, msg_id, category_id, support_role, extra_json) VALUES (?, ?, ?, ?, ?)",
                              (gid, msgs[0].get("messageid") if msgs else None, tc.get("category"), tc.get("role"), json.dumps(tc)))
                except Exception:
                    pass

    c.commit()


# ══════════════════════════════════════════════════════════════════
# 1. COMMAND STATS
# ══════════════════════════════════════════════════════════════════

def load_stats() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT user_id, command, timestamp FROM command_stats ORDER BY id").fetchall()
        return {"events": [{"user_id": r["user_id"], "command": r["command"], "timestamp": r["timestamp"]} for r in rows]}


def save_stats(data: dict):
    with _db_lock:
        c = _conn()
        for ev in data.get("events", []):
            c.execute("INSERT INTO command_stats (user_id, command, timestamp) VALUES (?, ?, ?)",
                      (ev.get("user_id"), ev.get("command"), ev.get("timestamp")))
        c.commit()


def insert_command_stat(user_id: int, command: str, timestamp: str):
    with _db_lock:
        _conn().execute("INSERT INTO command_stats (user_id, command, timestamp) VALUES (?, ?, ?)",
                        (user_id, command, timestamp))
        _conn().commit()


# ══════════════════════════════════════════════════════════════════
# 2. AUTO-PING
# ══════════════════════════════════════════════════════════════════

def load_autoping_channels(guild_id: int) -> list:
    with _db_lock:
        rows = _conn().execute("SELECT channel_id FROM auto_ping WHERE guild_id = ?", (guild_id,)).fetchall()
        return [r["channel_id"] for r in rows]


def save_autoping_channels(guild_id: int, channels: list):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM auto_ping WHERE guild_id = ?", (guild_id,))
        for ch in channels:
            c.execute("INSERT INTO auto_ping (guild_id, channel_id) VALUES (?, ?)", (guild_id, ch))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 3. AUTO-ROLE
# ══════════════════════════════════════════════════════════════════

def load_autorole(guild_id: int):
    with _db_lock:
        row = _conn().execute("SELECT role_id FROM auto_role WHERE guild_id = ?", (guild_id,)).fetchone()
        return {"role_id": row["role_id"]} if row else None


def save_autorole(guild_id: int, role_id: int):
    with _db_lock:
        _conn().execute("INSERT OR REPLACE INTO auto_role (guild_id, role_id) VALUES (?, ?)", (guild_id, role_id))
        _conn().commit()


def remove_autorole(guild_id: int):
    with _db_lock:
        _conn().execute("DELETE FROM auto_role WHERE guild_id = ?", (guild_id,))
        _conn().commit()


# ══════════════════════════════════════════════════════════════════
# 4. PRIVACY SETTINGS
# ══════════════════════════════════════════════════════════════════

def load_privacy_settings() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM privacy_settings").fetchall()
        return {str(r["user_id"]): [k for k, v in (("presence", r["presence_disabled"]), ("status", r["status_disabled"])) if v] for r in rows}


def save_privacy_settings(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM privacy_settings")
        for uid_str, cats in data.items():
            c.execute("INSERT INTO privacy_settings (user_id, presence_disabled, status_disabled) VALUES (?, ?, ?)",
                      (int(uid_str), 1 if "presence" in cats else 0, 1 if "status" in cats else 0))
        c.commit()


# globally accessible sets populated at startup
PRIVACY_SET: set[int] = set()
STATUS_PRIVACY_SET: set[int] = set()


def reload_privacy_sets():
    global PRIVACY_SET, STATUS_PRIVACY_SET
    data = load_privacy_settings()
    PRIVACY_SET = {int(uid) for uid, cats in data.items() if "presence" in cats}
    STATUS_PRIVACY_SET = {int(uid) for uid, cats in data.items() if "status" in cats}


# ══════════════════════════════════════════════════════════════════
# 5. MESSAGE COUNTER
# ══════════════════════════════════════════════════════════════════

def load_server_data(guild_id: int):
    with _db_lock:
        c = _conn()
        cfg = c.execute("SELECT * FROM message_counter_config WHERE guild_id = ?", (guild_id,)).fetchone()
        if cfg is None:
            return None
        rows = c.execute("SELECT user_id, count FROM message_counter WHERE guild_id = ?", (guild_id,)).fetchall()
        return {
            "status": bool(cfg["enabled"]),
            "blacklisted_channels": json.loads(cfg["blacklisted_channels"]),
            "opted_out_users": json.loads(cfg["opted_out_users"]),
            "users": {str(r["user_id"]): r["count"] for r in rows},
        }


def save_server_data(guild_id: int, data: dict):
    with _db_lock:
        c = _conn()
        status_val = data.get("status", True)
        enabled = 1 if (isinstance(status_val, str) and status_val == "enabled") or (not isinstance(status_val, str) and status_val) else 0
        c.execute("INSERT OR REPLACE INTO message_counter_config (guild_id, enabled, blacklisted_channels, opted_out_users) VALUES (?, ?, ?, ?)",
                  (guild_id, enabled, json.dumps(data.get("blacklisted_channels", [])), json.dumps(data.get("opted_out_users", []))))
        c.execute("DELETE FROM message_counter WHERE guild_id = ?", (guild_id,))
        for uid_str, count in data.get("users", {}).items():
            c.execute("INSERT INTO message_counter (guild_id, user_id, count) VALUES (?, ?, ?)", (guild_id, int(uid_str), count))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 6. GEMINI SERVERS
# ══════════════════════════════════════════════════════════════════

def load_gemini_servers() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT guild_id FROM gemini_servers").fetchall()
        return {"servers": [r["guild_id"] for r in rows]}


def save_gemini_servers(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM gemini_servers")
        for sid in data.get("servers", []):
            c.execute("INSERT INTO gemini_servers (guild_id) VALUES (?)", (sid,))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 7. AUDIT CONFIG
# ══════════════════════════════════════════════════════════════════

def load_audit_config() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM audit_config").fetchall()
        return {str(r["guild_id"]): {"enabled": bool(r["enabled"]), "channel": r["channel_id"]} for r in rows}


def save_audit_config(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM audit_config")
        for gid_str, cfg in data.items():
            c.execute("INSERT INTO audit_config (guild_id, enabled, channel_id) VALUES (?, ?, ?)",
                      (int(gid_str), 1 if cfg.get("enabled") else 0, cfg.get("channel")))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 8. GUILD CONFIG (scam detection)
# ══════════════════════════════════════════════════════════════════

DEFAULTS = {
    "scam_channels": [],
    "codehelper_channels": [],
    "limited_role_id": None,
    "surge_threshold_per_minute": 10,
    "log_channel_id": None,
    "domain_allowlist": ["discord.com", "discord.gg", "steamcommunity.com", "github.com"],
    "shortener_allowlist": ["git.io"],
    "auto_whitelist_on_false_positive": True,
    "nitro_requires_url": True,
    "phrase_allowlist": [],
    "scam_user_whitelist": [],
    "scam_role_whitelist": [],
    "phrase_audit": {},
}


def get_guild_cfg(guild_id: int) -> dict:
    with _db_lock:
        c = _conn()
        row = c.execute("SELECT config_json FROM guild_config WHERE guild_id = ?", (guild_id,)).fetchone()
        if row is None:
            cfg = DEFAULTS.copy()
            c.execute("INSERT INTO guild_config (guild_id, config_json) VALUES (?, ?)", (guild_id, json.dumps(cfg)))
            c.commit()
            return cfg
        cfg = json.loads(row["config_json"])
        for k, v in DEFAULTS.items():
            cfg.setdefault(k, v)
        if "channel_allowlist" in cfg and cfg["channel_allowlist"]:
            olds = set(cfg.get("scam_channels") or [])
            cfg["scam_channels"] = sorted(olds | set(cfg["channel_allowlist"]))
            cfg["channel_allowlist"] = []
        return cfg


def update_guild_cfg(guild_id: int, **patch):
    with _db_lock:
        c = _conn()
        row = c.execute("SELECT config_json FROM guild_config WHERE guild_id = ?", (guild_id,)).fetchone()
        cfg = json.loads(row["config_json"]) if row else DEFAULTS.copy()
        cfg.update(patch)
        c.execute("INSERT OR REPLACE INTO guild_config (guild_id, config_json) VALUES (?, ?)", (guild_id, json.dumps(cfg)))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 9. SCAM ACTIONS
# ══════════════════════════════════════════════════════════════════

def load_actions() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM scam_actions").fetchall()
        return {r["action_id"]: {"guild_id": r["guild_id"], "author_id": r["author_id"], "content": r["content"],
                                 "reasons": json.loads(r["reasons"]) if r["reasons"] else [],
                                 "domains": json.loads(r["domains"]) if r["domains"] else [],
                                 "timestamp": r["timestamp"]} for r in rows}


def save_actions(data: dict):
    with _db_lock:
        c = _conn()
        for aid, ad in data.items():
            c.execute("INSERT OR REPLACE INTO scam_actions (action_id, guild_id, author_id, content, reasons, domains, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (aid, ad.get("guild_id"), ad.get("author_id"), ad.get("content"),
                       json.dumps(ad.get("reasons", [])), json.dumps(ad.get("domains", [])), ad.get("timestamp")))
        c.commit()


def insert_action(action_id: str, guild_id: int, author_id: int, content: str, reasons: list, domains: list, timestamp: int):
    with _db_lock:
        _conn().execute(
            "INSERT OR REPLACE INTO scam_actions (action_id, guild_id, author_id, content, reasons, domains, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (action_id, guild_id, author_id, content, json.dumps(reasons), json.dumps(domains), timestamp)
        )
        _conn().commit()


# ══════════════════════════════════════════════════════════════════
# 10. SCAM FEEDBACK
# ══════════════════════════════════════════════════════════════════

def append_feedback(entry: dict):
    with _db_lock:
        _conn().execute("INSERT INTO scam_feedback (ts, label, data_json) VALUES (?, ?, ?)",
                        (entry.get("ts"), entry.get("label"), json.dumps(entry)))
        _conn().commit()


def load_feedback_stats() -> dict:
    """Aggregate feedback into per-reason true/false positive counts."""
    with _db_lock:
        try:
            rows = _conn().execute("SELECT * FROM scam_feedback").fetchall()
        except sqlite3.OperationalError:
            _conn().execute("CREATE TABLE IF NOT EXISTS scam_feedback (id INTEGER PRIMARY KEY AUTOINCREMENT, ts INTEGER, label TEXT, data_json TEXT)")
            _conn().commit()
            rows = []
    stats = {}  # reason -> {"tp": int, "fp": int, "total": int}
    for r in rows:
        data = json.loads(r["data_json"])
        reasons = data.get("reasons") or []
        label = r["label"]
        for reason in reasons:
            s = stats.setdefault(reason, {"tp": 0, "fp": 0, "total": 0})
            if label == "true_positive":
                s["tp"] += 1
            elif label == "false_positive":
                s["fp"] += 1
            s["total"] += 1
    return stats


def get_pattern_confidence(reason: str, stats: dict = None) -> float:
    """Return a confidence score 0.0–1.0 for a given scam rule label.
    Uses Bayesian smoothing (2 pseudocounts each for TP/FP) so a single
    false positive doesn't crash confidence to minimum."""
    if stats is None:
        stats = load_feedback_stats()
    s = stats.get(reason, {"tp": 0, "fp": 0})
    tp = s["tp"] + 2
    fp = s["fp"] + 2
    ratio = tp / (tp + fp)
    if ratio >= 0.75:
        return 0.85
    if ratio >= 0.50:
        return 0.65
    if ratio >= 0.35:
        return 0.55
    return 0.35


def load_pattern_weights() -> dict:
    with _db_lock:
        try:
            rows = _conn().execute("SELECT reason, weight FROM pattern_weights").fetchall()
        except sqlite3.OperationalError:
            _conn().execute("CREATE TABLE IF NOT EXISTS pattern_weights (reason TEXT PRIMARY KEY, weight REAL NOT NULL DEFAULT 1.0, last_updated INTEGER)")
            _conn().commit()
            rows = []
    return {r["reason"]: r["weight"] for r in rows}


def save_pattern_weights(weights: dict):
    ts = int(time.time())
    with _db_lock:
        try:
            for reason, weight in weights.items():
                _conn().execute(
                    "INSERT OR REPLACE INTO pattern_weights (reason, weight, last_updated) VALUES (?, ?, ?)",
                    (reason, weight, ts)
                )
            _conn().commit()
        except sqlite3.OperationalError:
            _conn().execute("CREATE TABLE IF NOT EXISTS pattern_weights (reason TEXT PRIMARY KEY, weight REAL NOT NULL DEFAULT 1.0, last_updated INTEGER)")
            _conn().commit()
            for reason, weight in weights.items():
                _conn().execute(
                    "INSERT OR REPLACE INTO pattern_weights (reason, weight, last_updated) VALUES (?, ?, ?)",
                    (reason, weight, ts)
                )
            _conn().commit()


def degrade_pattern_weights(reasons: list):
    """Reduce confidence weight for each matched reason on false positive."""
    weights = load_pattern_weights()
    changed = False
    for r in reasons:
        old = weights.get(r, 1.0)
        new = max(0.3, old - 0.10)
        if new != old:
            weights[r] = new
            changed = True
    if changed:
        save_pattern_weights(weights)
    return weights


def compute_scan_confidence(reasons: list, stats: dict = None) -> (float, dict):
    """Compute overall scan confidence from per-reason weights and feedback."""
    weights = load_pattern_weights()
    if stats is None:
        stats = load_feedback_stats()
    scores = []
    details = {}
    for r in reasons:
        fb = stats.get(r, {"tp": 0, "fp": 0})
        fp_frac = fb["fp"] / max(fb["tp"] + fb["fp"], 1)
        base = get_pattern_confidence(r, stats)
        w = weights.get(r, 1.0)
        final = base * w
        if fp_frac > 0.5 and fb["fp"] >= 3:
            final *= 0.6
        scores.append(final)
        details[r] = {"weight": round(w, 3), "base": round(base, 3), "final": round(final, 3), "fp": fb["fp"], "tp": fb["tp"]}
    if not scores:
        return 0.0, details
    # harmonic-ish: primary score is max, but multiple hits boost
    best = max(scores)
    boost = 1.0 + (len(scores) - 1) * 0.1
    return min(1.0, best * boost), details


# ══════════════════════════════════════════════════════════════════
# 11. VERIFY CONFIG
# ══════════════════════════════════════════════════════════════════

def get_verify_configs() -> list:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM verify_config").fetchall()
        return [{"guildid": r["guild_id"], "remove_role": r["remove_role"], "add_role": r["add_role"],
                 "url": r["url"] or "", "messageid": r["message_id"]} for r in rows]


def get_verify_config(guild_id: int):
    with _db_lock:
        row = _conn().execute("SELECT * FROM verify_config WHERE guild_id = ?", (guild_id,)).fetchone()
        if row is None:
            return None
        return {"guildid": row["guild_id"], "remove_role": row["remove_role"], "add_role": row["add_role"],
                "url": row["url"] or "", "messageid": row["message_id"]}


def set_verify_config(guild_id: int, *, remove_role, add_role, url, message_id):
    with _db_lock:
        _conn().execute("INSERT OR REPLACE INTO verify_config (guild_id, remove_role, add_role, url, message_id) VALUES (?, ?, ?, ?, ?)",
                        (guild_id, remove_role, add_role, url, message_id))
        _conn().commit()


def delete_verify_config(guild_id: int):
    with _db_lock:
        _conn().execute("DELETE FROM verify_config WHERE guild_id = ?", (guild_id,))
        _conn().commit()


# ══════════════════════════════════════════════════════════════════
# 12. USER VERIFYING
# ══════════════════════════════════════════════════════════════════

def load_verifying_users() -> set:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM user_verifying").fetchall()
        return {(r["guild_id"], r["user_id"]) for r in rows}


def save_verifying_users(data: set):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM user_verifying")
        for gid, uid in data:
            c.execute("INSERT INTO user_verifying (guild_id, user_id) VALUES (?, ?)", (gid, uid))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 13. REACTION ROLES (main)
# ══════════════════════════════════════════════════════════════════

def load_reaction_roles() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM reaction_roles_main").fetchall()
        result = {}
        for r in rows:
            result.setdefault(r["guild_id"], []).append({"name": r["template_name"], "roles": json.loads(r["roles_json"]), "custom_id": r["custom_id"]})
        return result


def save_reaction_roles(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM reaction_roles_main")
        for gid_str, templates in data.items():
            for tpl in templates if isinstance(templates, list) else []:
                c.execute("INSERT INTO reaction_roles_main (guild_id, template_name, roles_json, custom_id) VALUES (?, ?, ?, ?)",
                          (int(gid_str), tpl.get("name"), json.dumps(tpl.get("roles", [])), tpl.get("custom_id")))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 14. REACTION ROLES (cog)
# ══════════════════════════════════════════════════════════════════

def load_reaction_roles_cog() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM reaction_roles_cog").fetchall()
        result = {}
        for r in rows:
            result.setdefault(r["guild_id"], []).append(json.loads(r["data_json"]))
        return result


def save_reaction_roles_cog(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM reaction_roles_cog")
        for gid_str, templates in data.items():
            for tpl in templates if isinstance(templates, list) else []:
                c.execute("INSERT INTO reaction_roles_cog (guild_id, template_name, data_json) VALUES (?, ?, ?)",
                          (int(gid_str), tpl.get("type") or tpl.get("name"), json.dumps(tpl)))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# 15. TICKETS
# ══════════════════════════════════════════════════════════════════

def load_active_tickets() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM ticket_active").fetchall()
        result = {}
        for r in rows:
            gid = str(r["guild_id"])
            uid = str(r["owner_id"])
            cid = int(r["channel_id"])
            result.setdefault(gid, {}).setdefault(uid, []).append(cid)
        return result


def save_active_tickets(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM ticket_active")
        now = datetime.now(timezone.utc).isoformat()
        for gid_str, users in data.items():
            for uid_str, channel_ids in users.items():
                for cid in channel_ids:
                    c.execute("INSERT INTO ticket_active (channel_id, guild_id, owner_id, created_at) VALUES (?, ?, ?, ?)",
                              (int(cid), int(gid_str), int(uid_str), now))
        c.commit()


def load_archived_tickets() -> dict:
    with _db_lock:
        c = _conn()
        rows = c.execute("SELECT * FROM ticket_archived").fetchall()
        extras = {r["channel_id"]: json.loads(r["extra_json"]) for r in c.execute("SELECT * FROM ticket_archived_extra").fetchall()}
        result = {}
        for r in rows:
            cid = r["channel_id"]
            entry = extras.get(cid, {})
            entry.update({"guild_id": r["guild_id"], "owner_id": r["owner_id"], "transcript": r["transcript"], "closed_at": r["closed_at"]})
            result[str(cid)] = entry
        return result


def save_archived_tickets(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM ticket_archived")
        c.execute("DELETE FROM ticket_archived_extra")
        for cid_str, tdata in data.items():
            if isinstance(tdata, dict):
                c.execute("INSERT INTO ticket_archived (channel_id, guild_id, owner_id, transcript, closed_at) VALUES (?, ?, ?, ?, ?)",
                          (int(cid_str), tdata.get("guild_id"), tdata.get("owner_id"), tdata.get("transcript"), tdata.get("closed_at")))
                extra = {k: v for k, v in tdata.items() if k not in ("guild_id", "owner_id", "transcript", "closed_at")}
                c.execute("INSERT OR REPLACE INTO ticket_archived_extra (channel_id, extra_json) VALUES (?, ?)",
                          (int(cid_str), json.dumps(extra)))
        c.commit()


def load_ticket_history() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM ticket_history ORDER BY id").fetchall()
        result = {}
        for r in rows:
            result.setdefault(str(r["channel_id"]), []).append({"action": r["action"], "user_id": r["user_id"], "at": r["timestamp"], "note": r["note"]})
        return result


def save_ticket_history(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM ticket_history")
        for cid_str, entries in data.items():
            for entry in entries if isinstance(entries, list) else []:
                c.execute("INSERT INTO ticket_history (channel_id, action, user_id, timestamp, note) VALUES (?, ?, ?, ?, ?)",
                          (int(cid_str), entry.get("action"), entry.get("user_id"), entry.get("at"), entry.get("note", "")))
        c.commit()


def append_ticket_history(channel_id: int, action: str, user_id: int, note: str = ""):
    with _db_lock:
        _conn().execute("INSERT INTO ticket_history (channel_id, action, user_id, timestamp, note) VALUES (?, ?, ?, ?, ?)",
                        (channel_id, action, user_id, datetime.now(timezone.utc).isoformat(), note))
        _conn().commit()


def load_ticket_participants() -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT channel_id, user_id FROM ticket_participants ORDER BY channel_id").fetchall()
        result = {}
        for r in rows:
            result.setdefault(str(r["channel_id"]), []).append(r["user_id"])
        return result


def save_ticket_participants(data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM ticket_participants")
        for cid_str, uids in data.items():
            for uid in uids if isinstance(uids, list) else []:
                c.execute("INSERT INTO ticket_participants (channel_id, user_id) VALUES (?, ?)", (int(cid_str), uid))
        c.commit()


def add_ticket_participant(channel_id: int, user_id: int):
    with _db_lock:
        _conn().execute("INSERT OR IGNORE INTO ticket_participants (channel_id, user_id) VALUES (?, ?)", (channel_id, user_id))
        _conn().commit()


def get_ticket_config(guild_id: int) -> dict:
    with _db_lock:
        row = _conn().execute("SELECT * FROM ticket_config WHERE guild_id = ?", (guild_id,)).fetchone()
        if row is None:
            return {"message": []}
        extra = json.loads(row["extra_json"]) if row["extra_json"] else {}
        extra.update({"category": row["category_id"], "role": row["support_role"]})
        return extra


def save_ticket_config(guild_id: int, data: dict):
    with _db_lock:
        msgs = data.get("message", [])
        _conn().execute("INSERT OR REPLACE INTO ticket_config (guild_id, msg_id, category_id, support_role, extra_json) VALUES (?, ?, ?, ?, ?)",
                        (guild_id, msgs[0].get("messageid") if msgs else None, data.get("category"), data.get("role"), json.dumps(data)))
        _conn().commit()


def get_ticket_server_info(key: str):
    with _db_lock:
        row = _conn().execute("SELECT value FROM ticket_server_info WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None


def set_ticket_server_info(key: str, value: str):
    with _db_lock:
        _conn().execute("INSERT OR REPLACE INTO ticket_server_info (key, value) VALUES (?, ?)", (key, value))
        _conn().commit()


# ══════════════════════════════════════════════════════════════════
# 16. GIVEAWAYS
# ══════════════════════════════════════════════════════════════════

def load_guild_giveaways(guild_id: int) -> dict:
    with _db_lock:
        rows = _conn().execute("SELECT * FROM giveaways WHERE guild_id = ?", (guild_id,)).fetchall()
        result = {}
        for r in rows:
            data_json = r["data_json"]
            if data_json and data_json != "{}":
                result[str(r["message_id"])] = json.loads(data_json)
            else:
                result[str(r["message_id"])] = {"prize": r["prize"], "winners": r["winners"], "end_time": r["end_time"],
                                                "entries": json.loads(r["entries"]), "hosts": json.loads(r["hosts"]), "roles": json.loads(r["roles"])}
        return result


def save_guild_giveaways(guild_id: int, data: dict):
    with _db_lock:
        c = _conn()
        c.execute("DELETE FROM giveaways WHERE guild_id = ?", (guild_id,))
        for msg_id_str, gw_data in data.items():
            c.execute("INSERT INTO giveaways (guild_id, message_id, prize, winners, end_time, entries, hosts, roles, data_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (guild_id, int(msg_id_str), gw_data.get("prize"), gw_data.get("winners", 1), gw_data.get("end_time"),
                       json.dumps(gw_data.get("entries", [])), json.dumps(gw_data.get("hosts", [])), json.dumps(gw_data.get("roles", [])), json.dumps(gw_data)))
        c.commit()


# ══════════════════════════════════════════════════════════════════
# CLEANUP
# ══════════════════════════════════════════════════════════════════

def close_db():
    global _db_conn
    with _db_lock:
        if _db_conn:
            _db_conn.close()
            _db_conn = None
