# Equinox

Discord bot built with discord.py. Provides moderation, security, utility, gacha, giveaways, ticket systems, verification, premium subscriptions, and presence tracking.

- Dashboard: https://equinoxbot.netlify.app
- Documentation: https://equinoxbot.netlify.app/docs
- Invite: [Invite Equinox](https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=8&scope=bot) (Admin perms) | [Limited perms](https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=268494870&scope=bot)
- Support Server: https://discord.gg/Cu8JR7Vsvx
- License: GPL v3

---

## Features

| Category | Description |
|---|---|
| Scam Shield | Confidence-based scam detection with pattern weights, feedback training, domain analysis, fake Nitro detection, brand impersonation detection, and admin bypass |
| Gacha System | 10-tier rarity rolling with crafting recipes, inventory management, daily rewards, shop, and email-linked accounts |
| Ticket System | Persistent support tickets with role-based access, transcripts, premium perks, and add/revoke member access |
| Giveaways | Configurable giveaways with automatic winner selection, reroll, finalization, and role-based hosting permissions |
| Verification | Captcha-based member verification with configurable role assignment (remove role + add role) |
| Premium | Tiered subscriptions (Monthly / Yearly / Lifetime) with code generation, SellAuth export, email login, and gacha data reset |
| Presence Tracking | Server activity statistics, top games, now playing, per-user privacy opt-out, role-based presence stats |
| Gemini AI | Google Gemini integration for answering questions and AI-powered content moderation (ToS violation check) |
| Audit Logging | Configurable audit log capture with Discord audit event monitoring, downloadable exports (1–7 days), auto-rotation at 20MB |
| Event Guard | Join surge detection with automatic limited-role assignment for young accounts |
| Reaction Roles | Dropdown-based role selection with custom templates, multi-embed deployment, and embed editor |
| Automation | Auto-role assignment on join and configurable auto-ping channels |
| Code Helper | Inline Python syntax checking for codeblocks in designated channels |
| Message Counting | Per-server message tracking with leaderboards, transfers, channel blacklist, and opt-out |
| Utilities | Slash-based embed builder, translation, QR codes, polls, dictionary, Wikipedia, crypto/fiat exchange, blockchain transaction checking, math graphing, and more |
| Crypto/Fiat | Real-time exchange rates via ExchangeRate-API and blockchain transaction checking (BTC, ETH, LTC, DOGE) with confirmation alerts |

---

## Commands

### Scam Shield & Security
| Command | Description | Required Permissions |
|---|---|---|
| `/scam_enable` | Enable Anti-Scam in current channel | Manage Server / Administrator |
| `/scam_disable` | Disable Anti-Scam in current channel | Manage Server / Administrator |
| `/set_log_channel` | Set channel for scam alerts | Manage Server / Administrator |
| `/scan_test` | Test the scam scanner against custom text with confidence analysis | Anyone |
| `/scam_stats` | View per-pattern confidence bars, TP/FP counts, and overall accuracy | Anyone |
| `/scam_whitelist` | Add/remove users or roles from the scam shield whitelist, or list all | Manage Server / Administrator |
| `/whitelisted_phrase` | List, inspect, add, or remove whitelisted phrases (logged via Not a Scam feedback) | Manage Server / Administrator |
| `/block_ad` | Block Discord invite links (discord.gg, discord.com/invite) as spam | Administrator |
| `/youngest` | Show the youngest account and list all accounts younger than a duration (e.g. 1y, 30d, 1m) | Anyone |
| `/status` | Show current security and code-helper configuration for this server | Anyone |
| `/debug_safety` | Diagnose security readiness (intents, config, log channel) | Anyone |
| Review Content (context menu) | Right-click any message → Apps → Review Content to scan and mark as scam/not-scam | Manage Server / Administrator |
| `/auditlogsetup` | Toggle audit logging on or off | Administrator |
| `/auditlogchannel` | Set the channel for audit log entries | Administrator |
| `/auditlogdownload` | Download server audit logs (1-7 days) | Administrator |
| `/codehelper_enable` | Enable inline code helper in current channel | Manage Server / Administrator |
| `/codehelper_disable` | Disable inline code helper in current channel | Manage Server / Administrator |
| `/lint` | Check Python code for syntax errors (paste code in the command) | Anyone |

### Gacha & Economy
| Command | Description | Permissions |
|---|---|---|
| `/roll` | Roll for items across 10 rarity tiers (1/2 to 1/10,000) | Anyone |
| `/flex` | Display a member's gacha statistics | Anyone |
| `/inventory` | View your item inventory | Anyone |
| `/shop` | Browse the gacha shop | Anyone |
| `/daily` | Claim daily chest of potions | Anyone |
| `/craft` | Craft items from your inventory with predefined recipes | Anyone |

### Premium & Subscriptions
| Command | Description | Permissions |
|---|---|---|
| `/premium` | Check your premium subscription status | Anyone |
| `/is_premium` | Check premium status for yourself or another member | Anyone |
| `/redeem` | Redeem a premium code | Anyone |
| `/login` | Log in to your gacha database using email verification | Anyone |
| `/account` | View your account status (linked email, eligibility) | Anyone |
| `/unlink` | Unlink your email from the bot with verification | Anyone |
| `/reset` | Reset your gacha data (24h cooldown, requires email confirmation) | Anyone |
| `/prem_nsfw` | NSFW content (premium users only) | Premium |
| `/nsfw` | NSFW content (rate-limited for free users) | Anyone |
| `/email` | Send an email via the bot | Developer |
| `/gen_code` | Generate premium codes | Developer |
| `/remove_premium` | Remove premium from a user | Developer |
| `/export_codes` | Export premium codes to .txt for SellAuth | Developer |
| `/stats` | View bot statistics (guilds, users, commands, uptime) | Developer |

### Tickets
| Command | Description | Permissions |
|---|---|---|
| `/make_ticket` | Create a ticket system with a custom panel, category, and support role | Administrator |
| `/addmember` | Add a member to an open ticket | Ticket permissions |
| `/revmember` | Remove a member from a ticket | Ticket permissions |

### Giveaways
| Command | Description | Permissions |
|---|---|---|
| `/giveaway` | Create a giveaway with prize, winners, duration, and host roles | Anyone |
| `/giveaway_manage` | Reroll or finalize a giveaway by message ID | Host / Host Role |
| `/giveaway_console` | View all active giveaways in the server with pagination | Host / Host Role |

### Verification
| Command | Description | Permissions |
|---|---|---|
| `/make_verify` | Create a captcha-based verification system with role assignment | Administrator / Server Owner |

### Presence & Activity
| Command | Description | Permissions |
|---|---|---|
| `/server_member_activity` | View members by presence status (Online, DND, Idle, Offline) or summary stats | Anyone |
| `/server_member_stats` | Advanced member analytics: overview, top roles, and age distribution graph | Manage Server / Administrator |
| `/top_games` | Show the most played games in the server (top 10) | Anyone |
| `/now_playing` | View what a user is currently playing or doing (games, Spotify, custom status) | Anyone |
| `/role_presence_stats` | View presence breakdown (online/idle/dnd/offline) for a specific role | Anyone |
| `/privacy` | Opt out of presence tracking, status tracking, or both | Anyone |

### Automation
| Command | Description | Permissions |
|---|---|---|
| `/autoping_whitelist` | Add, remove, or view auto-ping channels for new members | Manage Messages |
| `/autorole` | Set, remove, or view auto-role configuration for new members | Manage Roles |

### Reaction Roles
| Command | Description | Permissions |
|---|---|---|
| `/rrgame` | Make a selection role (developer only) | Developer |
| `/reactionrolesetup` | Create or delete a reaction role template | Manage Roles |
| `/reactionroleedit` | Add or remove roles from a template | Manage Roles |
| `/reactionroleembed` | View or edit a template embed's appearance (title, description, color) | Manage Roles |
| `/reactionroledeploy` | Deploy a reaction role template to a channel | Manage Roles |

### Message Counting
| Command | Description | Permissions |
|---|---|---|
| `/messagecounter` | Enable or disable message counting in the server | Administrator |
| `/messagecount` | View a user's message count | Anyone |
| `/messagecountleaderboard` | Server message count leaderboard with pagination | Anyone |
| `/messagecountgive` | Transfer your message count to another user | Anyone |
| `/messagecountdeduct` | Deduct messages from a user | Administrator |
| `/messageblacklist` | Add or remove channels from the message counter blacklist | Administrator |
| `/messageblacklistview` | View blacklisted channels | Anyone |

### Moderation
| Command | Description | Permissions |
|---|---|---|
| `/purge` | Clear messages (2-50) with optional filters (bots, embeds, users, links) | Manage Messages |
| `/slowmode` | Set channel slowmode delay (0–21600 seconds) | Manage Channels |
| `/lockdown` | Lock a channel (prevent members from sending messages and reactions) | Manage Channels |
| `/unlockdown` | Unlock a previously locked channel | Manage Channels |
| `/private` | Hide a channel from @everyone | Manage Channels |
| `/unprivate` | Restore visibility to a hidden channel | Manage Channels |
| `/kick` | Kick a member from the server (with hierarchy validation) | Kick Members |
| `/ban` | Ban a member from the server (with unban button) | Ban Members |
| `/unban` | Unban a user by numeric ID | Ban Members |

### Utility
| Command | Description | Permissions |
|---|---|---|
| `/help` | Interactive help menu with category dropdown | Anyone |
| `/serverinfo` | Display detailed server information (owner, boosts, channels, roles) | Anyone |
| `/userinfo` | Display detailed user information (joined, created, roles, permissions) | Anyone |
| `/roleinfo` | Display detailed role information (color, position, permissions) | Anyone |
| `/avatar` | View a user's full-size avatar | Anyone |
| `/ping` | Check bot latency (WebSocket + REST round-trip) | Anyone |
| `/invite` | Get bot invite links (admin + limited perms) and support server | Anyone |
| `/embed` | Visual embed builder with interactive modals (title, desc, fields, author, footer, image, thumbnail, color) | Manage Messages |
| `/poll` | Start a poll with up to 3 options | Manage Messages |
| `/clone` | Clone the current channel (name, permissions, topic, NSFW, slowmode) | Manage Channels |
| `/qrcode` | Generate a QR code from text or URL | Anyone |
| `/translate` | Translate text to a target language with language selector | Anyone |
| `/def` | Look up the dictionary definition of a word | Anyone |
| `/wiki` | Search Wikipedia with category support (Fandom integration) | Anyone |
| `/daysbetween` | Calculate the number of days between two dates | Anyone |
| `/timedif` | Calculate the time difference between two message IDs | Anyone |
| `/steal` | Copy emojis from another server (animated + static supported) | Manage Emojis |
| `/exchange` | Convert between fiat and cryptocurrencies using real-time ExchangeRate-API rates | Anyone |
| `/check_tx` | Check blockchain transaction details (BTC, ETH, LTC, DOGE) with confirmation tracking | Anyone |
| `/graph` | Plot a mathematical function on a graph (with zoom controls) | Anyone |
| `/drop` | Start a drop game in the current channel (click to claim, random timer) | Anyone |
| `/update` | Post an Equinox update changelog embed | Developer |

### Gemini AI
| Command | Description | Permissions |
|---|---|---|
| `/ask_gemini` | Ask Google Gemini AI any question (with content moderation) | Administrator |

### Sync (Owner)
| Command | Description | Permissions |
|---|---|---|
| `/sync` | Force-sync all slash commands globally | Bot Owner |

---

## Quick Start

### Prerequisites

- Python 3.11 or later
- Discord Bot Token
- PostgreSQL database (required for premium subscriptions)
- Google Gemini API Key (optional)
- Etherscan API Key (optional, for ETH transaction checking)

### Installation

```
git clone https://github.com/PaullyScripter/Equinox.git
cd Equinox
pip install -r requirements.txt
```

### Configuration

Create a `.env` file with the following variables:

```
DISCORD_TOKEN=your_bot_token
API_KEY=your_api_key
ETHERSCAN_API_KEY=your_etherscan_key
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=postgresql://user:pass@host/db
email_password=your_email_password
email_sender=your_email@gmail.com
BACKEND_URL=https://your-backend.onrender.com
```

### Running

```
python main.py
```

The bot creates all required data files and SQLite tables on first launch.

---

## Project Structure

```
Equinox/
  main.py                  Bot entry point, persistent views, core logic (scam scanning, crypto, audit logs, state module population)
  state.py                 Shared state module — populated at runtime by main.py, imported by cogs
  cogs/
    automation.py          Auto-role and auto-ping systems
    database.py            SQLite persistence layer (WAL mode) for all non-premium features
    events.py              Startup initialization, event listeners (on_ready, on_message, on_member_join/remove, audit log entries)
    gacha.py               Gacha rolling, crafting, inventory management, email linking, SQLite + cache
    giveaway.py            Giveaway management, console, and creation
    giveaway_views.py      Giveaway UI components (views, modals, winner selection)
    moderation.py          Slowmode, lockdown, ban, kick, purge
    premium.py             Premium subscriptions, code generation, NSFW, email/auth system
    presence.py            Activity tracking, top games, privacy controls, role presence stats
    reaction_roles.py      Dropdown-based role selection with embed editing
    security.py            Scam shield, audit logging, code helper, lint, youngest account checker
    ticket_views.py        Ticket UI components (open, close, claim, etc.)
    tickets.py             Ticket system creation and management
    utility.py             All utility commands (help, info, translate, embed builder, etc.)
    verification.py        Captcha-based member verification
    views.py               All UI views and modals (auth, buttons, paginators, scam feedback, etc.)
  assets/                  Static assets
  scripts/                 Utility scripts
  data/                    Runtime data (gitignored) — equinox.db (SQLite), gacha.db (SQLite), JSON files
  tests/
    test_state.py          Pytest suite for state module initialization
  .gitignore
  .env                     Environment variables (gitignored)
  LICENSE                  GNU General Public License v3
  pyproject.toml           Ruff, mypy, and pytest configuration
  requirements.txt
  discloud.config          Discloud deployment configuration
```

---

## Architecture Notes

- **Database**: SQLite (`data/equinox.db`) with WAL mode and thread-safe locking for all non-premium features. Gacha uses a separate SQLite (`data/gacha.db`) with async locking and in-memory cache.
- **Premium**: PostgreSQL via asyncpg for subscription management, with a separate backend at `BACKEND_URL`.
- **State Module**: `state.py` is an empty module populated by `main.py` at startup with all shared functions and classes. Cogs import from it via `from state import ...`.
- **Scam Pipeline**: `on_message` → whitelist check → admin bypass → `scan_message_for_scams` → `compute_scan_confidence` → delete (≥50%) or flag → log embed with `ScamFeedbackView`.
- **Scam Feedback**: Persistent buttons on all flagged messages. True positives boost pattern weights (+0.1, max 1.0). False positives degrade weights (−0.10, min 0.3) and auto-whitelist domains/phrases.
- **Command Limit**: Current command count is 97 slash + 3 context menus (Review Content, Translate, Gacha Stats) = 99 (under Discord's 100 limit).

---

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).

Copyright (C) 2025-2026 Equinox Team
