# Handoff — Equinox Bot

## Goal
Port all changes from `main (2).py` (9061-line monolithic updated version) into the split cog-based codebase, then fix any runtime errors so the bot runs with no crashes and all 100+ commands working.

## Current State (June 21, 2026)

### Running
- Bot connects to Discord, syncs **101 commands**, no startup errors
- PostgreSQL premium checks via `is_premium()` (falls back to `(False, None, None)` when `DATABASE_URL` env var absent)
- `fandom` module optional; `/fandom` gives friendly message when missing

### Files
| File | Role | Lines |
|------|------|-------|
| `main.py` | Entry point — `PersistentViewBot`, all View classes, globals, helpers, `client.run()` | ~4770 |
| `cogs/events.py` | Event listeners (on_ready, on_member_join, etc.) | ~370 |
| `cogs/automation.py` | Automation cog | ~50 |
| `cogs/gacha.py` | Gacha/roll commands | ~700 |
| `cogs/giveaway.py` | Giveaway commands | ~320 |
| `cogs/moderation.py` | Moderation commands | ~80 |
| `cogs/premium.py` | Premium commands (redeem, nsfw) | ~495 |
| `cogs/presence.py` | Presence/role stats commands | ~200 |
| `cogs/reaction_roles.py` | Reaction role commands | ~195 |
| `cogs/security.py` | Security commands | ~150 |
| `cogs/tickets.py` | Ticket system commands | ~155 |
| `cogs/utility.py` | Utility commands | ~1265 |
| `cogs/verification.py` | Verification commands | ~100 |
| `.gitignore` | Ignores `.env`, `*.json`, `__pycache__`, etc. | 20 |
| `requirements.txt` | Pinned dependencies | 14 |
| `ticket-json/active-tickets.json` | Tracks user→channels for max-ticket enforcement | auto-created |
| `handoff.md` | This file | |

### Known Fixed Bugs (this session)
1. **`from asyncio import *` → explicit imports** — `main.py`: replaced wildcard import with `from asyncio import sleep, gather, wait_for, create_task`
2. **Duplicate bot instance** — `main.py:70`: removed second `client = commands.Bot(...)` (first existed at module level)
3. **Duplicate `devs` list** — `main.py:137-141`: removed second `devs` list (duplicate of lines 93-97)
4. **Duplicate `disable_buttons` method** — `main.py`: second definition removed; only the pattern-matching version kept
5. **Duplicate `BuyPremium2` class** — `main.py:1833`: removed second identical class
6. **4x `on_message` listeners → 1** — `cogs/events.py`: consolidated 4 separate `on_message` listeners into one that handles bot mention, message counting, @everyone/@here audit, scam detection, code helper, prefix logging, and calls `process_commands` exactly once
7. **`snowflake_time()` broken import** — `main.py`: fixed `date.datetime.utcfromtimestamp` → `datetime.utcfromtimestamp`
8. **`CODEBOBLOCK_CLOSED_RE` typo** — `cogs/events.py:171`: fixed to `CODEBLOCK_CLOSED_RE`
9. **`from main import FlexButton` → `sys.modules["__main__"]`** — `cogs/gacha.py` (2 places): replaced circular-import-prone direct import with lazy `sys.modules` pattern
10. **Duplicate `load_data`/`save_data` in reaction_roles.py** — `cogs/reaction_roles.py:234-242`: removed functions that duplicated lines 10-15
11. **Fandom input unsanitized** — `main.py:2336-2340`: added length & character-whitelist validation before passing to `fandom.set_wiki()`/`fandom.page()`
12. **`eval()` in graph functions** — `main.py:3739,3705`: added `SAFE_CHARS_RE` validation in `process_function()` and set `{"__builtins__": {}, ...}` in eval globals to restrict code injection
13. **Bare `except:` → `except Exception`** — `main.py` (11 occurrences in WikipediaButton class) + `cogs/utility.py:1252`: prevents catching `SystemExit`/`KeyboardInterrupt`
14. **`requests.get()` blocking event loop** — `cogs/premium.py:132,176`: replaced sync `requests.get()` with `async with aiohttp.ClientSession()` in 2 async nsfw commands
15. **Missing dependencies** — `requirements.txt`: added `python-dotenv`, `asyncpg`, `httpx`, `fandom`; pinned major versions
16. **`.gitignore` missing** — Created `.gitignore` to ignore `.env`, data `*.json` files, `__pycache__`, and `.gitkeep`

### Known Remaining Issues
- **Secrets not rotated**: Discord token, DB password, GEMINI_API_KEY, ETHERSCAN_API_KEY, email_password all as-is in `.env` (user must regenerate at each service)
- **Sync JSON I/O blocks event loop**: ~65 `json.load()`/`json.dump()` calls in async functions need `asyncio.to_thread()` or `aiofiles` wrapping
- **`main.py:2222`** — `fetch_word_example()` uses sync `requests.get()` called from async context in `cogs/utility.py:410`; wrap in `asyncio.to_thread()`
- **Premium codes logged in plaintext** — `cogs/premium.py:268-279`: codes sent to Discord channel; consider encrypting/hashing before logging

### Important Patterns
- Lazy imports via `_sys.modules["__main__"].X` in all cog files (avoids circular imports)
- `@app_commands.choices`/`@app_commands.autocomplete`/`@app_commands.describe` are **not used** in Cog methods (discord.py 2.6.4 `_extract_parameters_from_callback` misaligns params when `self` is present)
- `Choice[str]` annotations changed to plain `str`; `tier.value` → `tier` in bodies
- Explicit `from asyncio import sleep, gather, wait_for, create_task` (no wildcard imports)
- `eval()` in graph functions restricted via `SAFE_CHARS_RE` regex + empty `__builtins__` dict
- Bare `except:` never used; always `except Exception:` or specific exception types

### Config / Env
- `.env` file loaded at startup for `DISCORD_TOKEN`, `DATABASE_URL`, etc.
- `.gitignore` prevents `.env` and data `*.json` files from being committed
- Ticket JSON files in `ticket-json/` directory
- `active-tickets.json` structure: `{"guild_id": {"user_id": [channel_id, ...]}}`

## Next Step (if continuing)
1. Rotate all secrets at source (Discord, Neon, Google AI, Etherscan, Gmail)
2. `python -m pip install -r requirements.txt` to pick up new deps
3. Run `python main.py` and test `/nsfw`, `/graph` a math function like `x^2`, and verify Wikipedia buttons still work
4. Address remaining sync-JSON and `requests.get()` blocking issues

## Things That Failed / Rejected
- **Email creds from `main(2).py`**: Deliberately not ported — kept env-var approach for security
- **`import fandom`**: Not made a hard dependency; guarded with try/except
- **`redeem` command removed in `main(2).py`**: Kept in split codebase as extra 101st command (user wanted to preserve it)
- **Reusing `MessageComponent` in new `View()`**: Doesn't work in discord.py 2.6.4 (`_is_v2` error); fixed by clearing view entirely
- **Hardcoded channel IDs** (#15): Intentionally not fixed per user instruction
