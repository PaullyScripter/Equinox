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
| `/scam enable` | Enable Anti-Scam in current channel | Manage Server / Administrator |
| `/scam disable` | Disable Anti-Scam in current channel | Manage Server / Administrator |
| `/scam log` | Set channel for scam alerts | Manage Server / Administrator |
| `/scam test` | Test the scam scanner against custom text | Anyone |
| `/scam stats` | View per-pattern confidence stats | Anyone |
| `/scam debug` | Diagnose security readiness | Anyone |
| `/scam phrase` | Manage whitelisted phrases | Manage Server / Administrator |
| `/scam whitelist` | Manage scam shield whitelist | Manage Server / Administrator |
| `/scam status` | Show current security configuration | Anyone |
| `/block_ad` | Block Discord invite links as spam | Administrator |
| `/youngest` | Show youngest accounts younger than a duration | Anyone |
| `/auditlog toggle` | Toggle audit logging on or off | Administrator |
| `/auditlog set` | Set channel for audit log entries | Administrator |
| `/auditlog view` | Download server audit logs (1-7 days) | Administrator |
| `/codehelper enable` | Enable inline code helper in current channel | Manage Server / Administrator |
| `/codehelper disable` | Disable inline code helper in current channel | Manage Server / Administrator |
| `/lint` | Check Python code for syntax errors | Anyone |
| Review Content (context menu) | Right-click → Apps → Review Content | Manage Server / Administrator |

### Gacha & Economy
| Command | Description | Permissions |
|---|---|---|
| `/gacha roll` | Roll for items across 10 rarity tiers | Anyone |
| `/gacha flex` | Display a member's gacha statistics | Anyone |
| `/gacha inventory` | View a member's item inventory | Anyone |
| `/gacha shop` | Browse the gacha shop | Anyone |
| `/gacha craft` | Craft items from your inventory | Anyone |
| `/gacha daily` | Claim daily chest of potions | Premium |
| Gacha Stats (context menu) | Right-click a member → Apps → Gacha Stats | Anyone |

### Account & Premium
| Command | Description | Permissions |
|---|---|---|
| `/premium` | Check your premium subscription status | Anyone |
| `/nsfw` | NSFW content (rate-limited for free users) | Anyone |
| `/prem_nsfw` | NSFW content (premium users only) | Premium |
| `/account info` | View your account status | Anyone |
| `/account login` | Log in to your gacha database using email | Anyone |
| `/account unlink` | Unlink your email from the bot | Anyone |
| `/account redeem` | Redeem a premium code | Anyone |
| `/account reset` | Reset your gacha data (24h cooldown) | Anyone |
| `/email` | Send an email via the bot | Developer |
| `/gen_code` | Generate premium codes | Developer |
| `/remove_premium` | Remove premium from a user | Developer |
| `/export_codes` | Export premium codes to .txt | Developer |
| `/stats` | View bot statistics | Developer |

### Tickets & Verification
| Command | Description | Permissions |
|---|---|---|
| `/ticket create` | Create a ticket system | Administrator |
| `/ticket add` | Add a member to a ticket | Ticket permissions |
| `/ticket remove` | Remove a member from a ticket | Ticket permissions |
| `/make_verify` | Create a captcha-based verification system | Administrator / Owner |

### Giveaways
| Command | Description | Permissions |
|---|---|---|
| `/giveaway create` | Create a giveaway | Manage Messages |
| `/giveaway manage` | Reroll or finalize a giveaway | Host / Host Role |
| `/giveaway console` | View all active giveaways | Host / Host Role |

### Activity & Presence
| Command | Description | Permissions |
|---|---|---|
| `/activity status` | View members by presence status | Anyone |
| `/activity games` | Show the top played games | Anyone |
| `/activity now` | View what a user is currently doing | Anyone |
| `/activity role` | View presence breakdown for a role | Anyone |
| `/activity privacy` | Manage privacy and tracking settings | Anyone |
| `/activity members` | Advanced member analytics | Manage Server / Administrator |

### Automation
| Command | Description | Permissions |
|---|---|---|
| `/autoping_whitelist` | Manage auto-ping channels | Manage Messages |
| `/autorole` | Manage auto-role configuration | Manage Roles |

### Reaction Roles
| Command | Description | Permissions |
|---|---|---|
| `/reactionrole game` | Make a selection role | Developer |
| `/reactionrole template` | Create or delete a template | Manage Roles |
| `/reactionrole edit` | Add or remove roles from a template | Manage Roles |
| `/reactionrole embed` | View or edit template embed | Manage Roles |
| `/reactionrole deploy` | Deploy a template to a channel | Manage Roles |

### Messages
| Command | Description | Permissions |
|---|---|---|
| `/messages toggle` | Enable or disable message counting | Administrator |
| `/messages count` | View a user's message count | Anyone |
| `/messages leaderboard` | Server message count leaderboard | Anyone |
| `/messages give` | Transfer messages to another user | Anyone |
| `/messages deduct` | Deduct messages from a user | Administrator |
| `/messages blacklist` | Blacklist/unblacklist a channel | Administrator |
| `/messages blacklist_view` | View blacklisted channels | Anyone |

### Moderation
| Command | Description | Permissions |
|---|---|---|
| `/channel lockdown` | Lock a channel | Manage Channels |
| `/channel unlockdown` | Unlock a channel | Manage Channels |
| `/channel private` | Hide a channel from @everyone | Manage Channels |
| `/channel unprivate` | Restore visibility to a channel | Manage Channels |
| `/channel slowmode` | Set channel slowmode delay | Manage Channels |
| `/channel clone` | Clone the current channel | Manage Channels |
| `/user kick` | Kick a member | Kick Members |
| `/user ban` | Ban a member | Ban Members |
| `/user unban` | Unban a user by ID | Ban Members |
| `/purge` | Clear messages with filters | Manage Messages |

### Utility
| Command | Description | Permissions |
|---|---|---|
| `/help` | Interactive help menu | Anyone |
| `/serverinfo` | Display server information | Anyone |
| `/userinfo` | Display user information | Anyone |
| `/roleinfo` | Display role information | Anyone |
| `/avatar` | View a user's avatar | Anyone |
| `/ping` | Check bot latency | Anyone |
| `/invite` | Get bot invite links | Anyone |
| `/embed` | Visual embed builder | Manage Messages |
| `/poll` | Start a poll with 3 options | Manage Messages |
| `/qrcode` | Generate a QR code | Anyone |
| `/translate` | Translate text | Anyone |
| `/def` | Dictionary definition of a word | Anyone |
| `/wiki` | Search Wikipedia | Anyone |
| `/fandom` | Search Fandom pages | Anyone |
| `/daysbetween` | Calculate days between dates | Anyone |
| `/timedif` | Time difference between IDs | Anyone |
| `/steal` | Copy emojis from another server | Manage Emojis |
| `/graph` | Plot a mathematical function | Anyone |
| `/drop` | Start a drop game | Anyone |
| `/exchange` | Convert fiat ↔ crypto | Anyone |
| `/check_tx` | Check blockchain transactions | Anyone |
| `/ask_gemini` | Ask Google Gemini AI | Administrator |
| `/sync` | Sync slash commands | Bot Owner |

### Context Menus
| Command | Description | Permissions |
|---|---|---|
| Translate (right-click message) | Translate a message | Anyone |
| Review Content (right-click message) | Scan message for scams | Manage Server / Administrator |
| Gacha Stats (right-click member) | View gacha stats | Anyone |

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
- **Command Limit**: ~53 slash commands + 3 context menus (Review Content, Translate, Gacha Stats) = ~56 total (well under Discord's 100 limit).

---

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).

Copyright (C) 2025-2026 Equinox Team
