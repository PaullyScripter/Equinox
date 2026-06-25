# Handoff Notes — Equinox

## Project Overview

Multipurpose Discord bot built with discord.py. Includes moderation, security (scam detection), gacha, giveaways, tickets, verification, premium subscriptions, presence tracking, utility commands, Gemini AI integration, and more.

Database: SQLite (`data/equinox.db`, gitignored). State shared via `state.py` module (populated at runtime by `main.py`).

**Current command count**: ~53 slash + 3 context menus = ~56 total (well under Discord's 100 limit).

## Session: Command Restructuring & Bug Fixes (June 24, 2026 — Round 2)

### Changes Made

#### 1. Slash Command Restructuring (97 → ~53)

All standalone commands were merged into `app_commands.Group` subcommand groups:

| Cog | Old Commands | New Structure |
|---|---|---|
| `giveaway.py` | `giveaway`, `giveaway_manage`, `giveaway_console` | `/giveaway create`, `/giveaway manage`, `/giveaway console` |
| `moderation.py` | `slowmode`, `lockdown`, `unlockdown`, `private`, `unprivate`, `kick`, `ban`, `unban` | `/channel slowmode/lockdown/unlockdown/private/unprivate/clone`, `/user kick/ban/unban` |
| `tickets.py` | `make_ticket`, `addmember`, `revmember` | `/ticket create`, `/ticket add`, `/ticket remove` |
| `security.py` | 17 standalone commands | `/scam` (10 subcommands: enable/disable/log/test/stats/debug/phrase/whitelist/status), `/auditlog` (3: toggle/set/view), `/codehelper` (2: enable/disable), standalone `lint`, `youngest`, `block_ad` |
| `premium.py` | `redeem`, `login`, `reset`, `account`, `unlink`, `premium`, `is_premium`, etc. | `/account info/login/unlink/redeem/reset`, `/premium` (optional `member` param merged from `/is_premium`), `/is_premium` deleted |
| `presence.py` | `server_member_activity`, `top_games`, `now_playing`, `role_presence_stats`, `privacy`, `server_member_stats` | `/activity status/games/now/role/privacy/members` |
| `gacha.py` | `roll`, `flex`, `inventory`, `shop`, `daily`, `craft` | `/gacha roll/flex/inventory/shop/daily/craft` |
| `reaction_roles.py` | `rrgame`, `reactionrolesetup`, `reactionroleedit`, `reactionroleembed`, `reactionroledeploy` | `/reactionrole game/template/edit/embed/deploy` |
| `utility.py` | 7 message counter commands + `clone` | `/messages` (7: count/toggle/leaderboard/deduct/give/blacklist/blacklist_view), `clone` moved to `moderation.py` `/channel clone` |
| `views.py` | Old `mySelect` help categories | 12 updated categories matching new group commands |
| `README.md` | Listed old command names | All tables updated with new grouped commands |

**`app_commands.Group` pattern used** (example from `giveaway.py`):
```python
class GiveawayCog(commands.Cog):
    giveaway = app_commands.Group(name="giveaway", description="Giveaway commands")

    @giveaway.command(name="create", description="Create a giveaway")
    async def giveaway_create(self, ...):
```

This registers `/giveaway create`, `/giveaway manage`, `/giveaway console` under one group slot.

#### 2. Ticket Owner Lookup Bug Fix

**Problem**: `CloseReasonModal.on_submit()` (and 3 other locations) parsed the ticket owner's user ID from the channel name via `channel.name.rsplit("-", 1)[-1]`. If the channel was renamed manually (e.g. by a mod), the split produced a non-numeric string, causing "Could not identify ticket owner."

**Fix**: Added `_lookup_ticket_owner(channel_id, guild_id)` helper in `ticket_views.py` that queries `load_active_tickets()` by channel ID + guild ID. Applied the lookup to all 4 locations:
- `generate_transcript()` (line ~654)
- `CloseReasonModal.on_submit()` (line ~862)
- `claim_ticket()` (line ~1002)
- `delete_ticket()` (line ~1121)

Fallback to channel name parsing preserved if the DB lookup fails.

#### 3. Audit Log Entry `vars()` Crash Fix

**Problem**: `_build_audit_embed()` in `events.py` called `vars(extra)` on the audit log entry's `extra` field. Some entry types return objects using `__slots__` (no `__dict__`), causing `TypeError: vars() argument must have __dict__ attribute`.

**Fix**: Changed the guard to `hasattr(extra, '__dict__')` and also handle plain `dict`:
```python
extra_dict = vars(extra) if hasattr(extra, '__dict__') else (extra if isinstance(extra, dict) else {})
```

#### 4. User-Facing Command References Updated
- `giveaway_views.py`: `</giveaway_manage:...>` mentions → `/giveaway manage`
- `security.py`: `/set_log_channel` error message → `/scam log`
- `utility.py`: All `use /messagecounter` error messages → `use /messages toggle`

### Architecture Notes

- **Help menu** (`views.py:mySelect`): Hardcoded embed fields listing each command. Must be kept in sync when commands change. Commands are shown as `</command>` without IDs (IDs change after `/sync`).
- **Context menus** (`gacha_stats`, `ctx_review_content`, `app_translate`): Registered via `bot.tree.add_command()` in their respective `setup()` functions. Cannot be nested under `app_commands.Group`.
- **Command ID references**: Old IDs like `</giveaway_manage:1370458427100368898>` were removed from user-facing strings since they become invalid after restructuring. A forced `/sync` is required on next restart to register the new command tree.

### Git State (as of this session)

- Branch: `lead`
- Remote: `origin` → https://github.com/PaullyScripter/Equinox.git
- Previous commit: `559754d` — "Security, production, and scalability hardening"

### Next Steps / Recommended Work

1. **Run `/sync` on next bot restart** to register all new command groups and unregister old command names
2. **Monitor for `Unknown command` errors** from users who may still have old command names cached in Discord client
3. **Consider removing `gacha_stats` context menu** if the `gacha flex` slash command covers the same functionality
4. **Consider merging `app_translate` context menu** into `/translate` slash command to free a context menu slot
5. **Ticketed channels may still have old permission overwrites** — the `_lookup_ticket_owner` fallback to channel name parsing handles legacy tickets
6. **Run a full lint/typecheck pass** after the restructuring to catch any missed references

### Changes Made

#### 1. Confidence-Based Scam Scoring
- **`cogs/database.py`**: Added `load_feedback_stats()`, `get_pattern_confidence()` with Bayesian smoothing (2 pseudocounts each for TP/FP), `load_pattern_weights()` / `save_pattern_weights()` / `degrade_pattern_weights()`, `compute_scan_confidence()`
- **`pattern_weights` table** in SQLite: per-reason weight starting at 1.0, degraded by −0.10 per false positive (floor 0.3)
- **`main.py`**: Wrapper functions for all new DB functions, registered on `state` module
- **`cogs/events.py`**: Scans now compute confidence. Messages ≥ 50% confidence are deleted; < 50% are flagged (log only). Buttons shown on ALL flags (not just deletions).

#### 2. Weight Decay / Boost on Feedback
- **Mark as Scam**: boosts matched pattern weights by +0.1 (up to 1.0) via `load_pattern_weights()` + `save_pattern_weights()`
- **Not a Scam**: degrades matched pattern weights by −0.10 (floor 0.3) via `degrade_pattern_weights()`, plus auto-whitelist domain/phrase. **Does NOT whitelist domains when reason is Brand Impersonation or Impersonation Domain** (fixes bug where `discord.awd` would be permanently allowlisted).

#### 3. Feedback UX
- **Buttons appear on all flagged messages** (not just deleted ones), so mods can train the system even on borderline detections
- **`ScamFeedbackView` disabled after one click** — greyed out via `_disable()` + `interaction.message.edit(view=self)`, preventing double-submission
- **Persistent view registration**: `bot.add_view(ScamFeedbackView())` in `main.py:setup_hook` so buttons survive restarts
- **`/scam_stats`**: shows per-pattern confidence bars (█░) with TP/FP counts and overall accuracy
- **`🔍 Review Content` context menu** (right-click → Apps on any message): scans the message, shows analysis, opens ScamFeedbackView — replaces two separate context menus to save command slots

#### 4. Admin/Owner Handling
- **`is_admin_bypass()`** in `main.py`: checks `guild_permissions.administrator`, `manage_guild`, or `guild.owner`
- Used in `cogs/events.py` to skip auto-deletion for admins (set `skip_delete = True`) but still scan, log, and show feedback buttons — so admins can test without getting their own messages deleted
- `is_scam_whitelisted()` reverted to only check config lists (user/role whitelist), not auto-skip admins

#### 5. Command Limit Compliance
- Discord's 100 global command limit was exceeded (103 total = 100 slash + 3 context menus)
- Removed `allowlist_phrase_add`, `allowlist_phrase_remove`, `allowlist_phrase_list` (replaced by `whitelisted_phrase` which handles add/remove/list)
- Removed `scam_review` slash command (replaced by context menu)
- **Current**: 97 slash + 3 context = 99 total (under limit)

#### 6. Bug Fixes
- **`_log_command` / `save_stats` key mismatch**: `_log_command` stored timestamp as `"ts"` but `save_stats` read `"timestamp"` → `NOT NULL constraint failed`. Fixed by changing `"ts"` → `"timestamp"` in `main.py:453`
- **Missing `uuid` and `time` imports** in `security.py` module-level context menu functions → added to top-level imports
- **`get_pattern_confidence` was too punitive**: 1 FP with 0 TP dropped base from 0.50 → 0.35. Bayesian prior (2 pseudocounts each) now keeps 1 FP at ~0.40 ratio → base stays 0.55
- **Weight degradation too aggressive**: Changed from −0.15 (floor 0.2) to −0.10 (floor 0.3)

### Architecture Notes

- **State module** (`state.py`): Empty module populated by `main.py` at startup with all shared functions/classes. Cogs access via `from state import ...` (lazy imports inside functions). This replaced the old `sys.modules["__main__"]` pattern.
- **Data persistence**: Dual system — JSON files in `data/` (legacy) + SQLite `data/equinox.db` for newer features. Scam feedback, pattern weights, guild config, actions, and audit logs use SQLite. Premium still uses PostgreSQL (asyncpg).
- **Scam pipeline**: `on_message` → `is_scam_whitelisted` → `scan_message_for_scams` → `compute_scan_confidence` → action (delete/flag) → log embed with `ScamFeedbackView`
- **`scan_message_for_scams`** returns `List[str]` reasons. The reasons are used for confidence calculation (per-reason weights + feedback stats) and displayed in log embeds.

### Known Issues / Challenges

1. **Brand Impersonation on non-standard TLDs**: The detection uses `_fuzzy_match(sld, BRAND_NAMES)` for TLDs outside `{com,net,org,io,co,app,dev}`. This catches `discord.awd`, `discord.htm`, etc. but also catches legitimate mentions like "my discord channel at discord.xyz". The feedback system helps train this out.

2. **No anti-spam for feedback buttons**: Multiple mods can click "Mark as Scam" / "Not a Scam" on the same message (though buttons disable per-viewer). The feedback system records each click as a separate data point, which is correct for training.

3. **Confidence cold start**: With no feedback data, all patterns start at 65% confidence (above 50% delete threshold). First-time false positives drop to ~50% borderline. This is by design so the system learns quickly.

4. **SQLite migration**: The `pattern_weights` and `scam_feedback` tables auto-create on first access via try/except `OperationalError` in `load_pattern_weights()` / `load_feedback_stats()`. Existing DBs from before this session get the new tables on first bot restart.

### Git State (as of last commit)

- Branch: `lead`
- Remote: `origin` → https://github.com/PaullyScripter/Equinox.git
- Last commit: `6227497` — "Smart feedback system: confidence scoring, pattern weight decay, context menu review, admin bypass rework"
- Working tree clean

### Next Steps / Recommended Work

1. Run a full lint/typecheck pass across all modified files
2. Consider a `/scam_confidence` command to let guild admins view per-pattern stats (currently only global stats in `/scam_stats`)
3. Add per-guild pattern weight overrides (so one guild's false positives don't affect others)
4. Consider adding a `scam_review` queued-modal or a `/scam_review` that lists recent flags for bulk review
5. Reset feedback data periodically or add a decay to old feedback entries so the system adapts to new scam patterns
