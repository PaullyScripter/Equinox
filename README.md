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
| Scam Shield | Domain-based scam detection with allowlists, whitelists, and feedback logging |
| Gacha System | 10-tier rarity rolling with crafting, inventory management, daily rewards, and shop |
| Ticket System | Persistent support tickets with role-based access, transcripts, and premium perks |
| Giveaways | Configurable giveaways with reroll, finalization, and role-based hosting permissions |
| Verification | Captcha-based member verification with configurable role assignment |
| Premium | Tiered subscriptions (Monthly / Yearly / Lifetime) with code generation and SellAuth integration |
| Presence Tracking | Server activity statistics, top games, now playing, and per-user privacy opt-out |
| Gemini AI | Google Gemini integration for answering questions |
| Audit Logging | Configurable audit log capture with downloadable exports |
| Reaction Roles | Dropdown-based role selection with custom templates and embeds |
| Automation | Auto-role assignment on join and configurable auto-ping channels |
| Message Counting | Per-channel message tracking with leaderboards, transfers, and blacklist |
| Utilities | Translation, QR codes, polls, custom embeds, dictionary, Wikipedia, and more |
| Crypto/Fiat | Real-time currency exchange rates and blockchain transaction checking |

---

## Commands

### Scam Shield & Security
| Command | Description | Required Permissions |
|---|---|---|
| `/scam_enable` | Enable Anti-Scam in current channel | Manage Server / Administrator |
| `/scam_disable` | Disable Anti-Scam in current channel | Manage Server / Administrator |
| `/set_log_channel` | Set channel for scam alerts | Manage Server / Administrator |
| `/allowlist_phrase_add` | Add a phrase to the allowlist | Manage Server / Administrator |
| `/allowlist_phrase_remove` | Remove a phrase from the allowlist | Manage Server / Administrator |
| `/allowlist_phrase_list` | View all allowlisted phrases | Anyone |
| `/whitelisted_phrase` | Manage whitelisted phrases (add/remove/list) | Administrator |
| `/scam_whitelist` | Whitelist users or roles from scam checks | Manage Server / Administrator |
| `/scan_test` | Test the scam scanner against custom text | Anyone |
| `/debug_safety` | Diagnose security readiness and configuration | Anyone |
| `/status` | Show current security and code-helper configuration | Anyone |
| `/auditlogsetup` | Toggle audit logging on or off | Administrator |
| `/auditlogchannel` | Set the channel for audit log entries | Administrator |
| `/auditlogdownload` | Download server audit logs (1-7 days) | Administrator |
| `/codehelper_enable` | Enable inline code helper in current channel | Manage Server / Administrator |
| `/codehelper_disable` | Disable inline code helper in current channel | Manage Server / Administrator |
| `/lint` | Check Python code for syntax errors | Anyone |

### Gacha & Economy
| Command | Description | Required Permissions |
|---|---|---|
| `/roll` | Roll for items across 10 rarity tiers | Anyone |
| `/flex` | Display a member's gacha statistics | Anyone |
| `/inventory` | View your item inventory | Anyone |
| `/shop` | Browse the gacha shop | Anyone |
| `/daily` | Claim daily chest of potions | Anyone |
| `/craft` | Craft items from your inventory | Anyone |
| Gacha Stats (context menu) | Right-click any member to view their gacha stats | Anyone |

### Premium & Subscriptions
| Command | Description | Required Permissions |
|---|---|---|
| `/premium` | Check your premium subscription status | Anyone |
| `/is_premium` | Check premium status | Anyone |
| `/redeem` | Redeem a premium code | Anyone |
| `/login` | Log in to your database via email | Anyone |
| `/reset` | Reset your gacha data and credentials | Anyone |
| `/prem_nsfw` | NSFW content (premium users only) | Premium |
| `/nsfw` | NSFW content (rate-limited for free users) | Anyone |
| `/email` | Send an email | Developer |
| `/gen_code` | Generate premium codes | Developer |
| `/remove_premium` | Remove premium from a user | Developer |
| `/export_codes` | Export premium codes to .txt for SellAuth | Developer |
| `/stats` | View bot statistics | Developer |

### Tickets
| Command | Description | Required Permissions |
|---|---|---|
| `/make_ticket` | Create a ticket system with a custom panel | Administrator |
| `/addmember` | Add a member to an open ticket | Ticket Member |
| `/revmember` | Remove a member from a ticket | Ticket Member |

### Giveaways
| Command | Description | Required Permissions |
|---|---|---|
| `/giveaway_manage` | Reroll or finalize a giveaway by message ID | Host / Host Role |
| `/giveaway_console` | View all active giveaways in the server | Host / Host Role |

### Verification
| Command | Description | Required Permissions |
|---|---|---|
| `/make_verify` | Create a captcha-based verification system | Administrator / Server Owner |

### Presence & Activity
| Command | Description | Required Permissions |
|---|---|---|
| `/server_member_activity` | View members by presence status or summary statistics | Anyone |
| `/top_games` | Show the most played games in the server | Anyone |
| `/now_playing` | View what a user is currently playing or doing | Anyone |
| `/privacy` | Opt out of presence tracking | Anyone |

### Automation
| Command | Description | Required Permissions |
|---|---|---|
| `/autoping_whitelist` | Manage auto-ping channels for new members | Manage Messages |
| `/autorole` | Set, remove, or view auto-role configuration | Manage Roles |

### Reaction Roles
| Command | Description | Required Permissions |
|---|---|---|
| `/reactionrolesetup` | Create or delete a reaction role template | Manage Roles |
| `/reactionroleedit` | Add or remove roles from a template | Manage Roles |
| `/reactionroleembed` | View or edit a template embed's appearance | Manage Roles |
| `/reactionroledeploy` | Deploy a reaction role template to a channel | Manage Roles |

### Message Counting
| Command | Description | Required Permissions |
|---|---|---|
| `/messagecounter` | Toggle message counting in a channel | Manage Messages |
| `/messagecount` | View a user's message count | Anyone |
| `/messageblacklistview` | View blacklisted channels | Anyone |
| `/messagecountdeduct` | Deduct messages from a user | Manage Messages |
| `/messagecountleaderboard` | Server message count leaderboard | Anyone |
| `/messagecountgive` | Transfer your message count to another user | Anyone |
| `/messageblacklist` | Add or remove channels from the message blacklist | Manage Messages |

### Moderation
| Command | Description | Required Permissions |
|---|---|---|
| `/slowmode` | Set channel slowmode delay | Manage Channels |
| `/lockdown` | Lock a channel (prevent members from sending messages) | Manage Channels |
| `/unlockdown` | Unlock a previously locked channel | Manage Channels |
| `/private` | Hide a channel from @everyone | Manage Channels |
| `/unprivate` | Restore visibility to a hidden channel | Manage Channels |
| `/kick` | Kick a member from the server | Kick Members |
| `/ban` | Ban a member from the server | Ban Members |
| `/unban` | Unban a user by ID | Ban Members |
| `/purge` | Clear messages (2-50) with optional filters (bots, embeds, users) | Manage Messages |

### Utility
| Command | Description | Required Permissions |
|---|---|---|
| `/help` | Interactive help menu | Anyone |
| `/serverinfo` | Display detailed server information | Anyone |
| `/userinfo` | Display detailed user information | Anyone |
| `/roleinfo` | Display detailed role information | Anyone |
| `/avatar` | View a user's full-size avatar | Anyone |
| `/ping` | Check bot latency | Anyone |
| `/invite` | Get bot invite links | Anyone |
| `/embed` | Create rich embeds with fields | Manage Messages |
| `/poll` | Start a poll with up to 3 options | Manage Messages |
| `/clone` | Clone the current channel | Manage Channels |
| `/qrcode` | Generate a QR code from text or a URL | Anyone |
| `/translate` | Translate text to a target language | Anyone |
| `/def` | Look up the definition of a word | Anyone |
| `/wiki` | Search Wikipedia | Anyone |
| `/daysbetween` | Calculate time between two dates | Anyone |
| `/timedif` | Calculate the time difference between two message IDs | Anyone |
| `/steal` | Copy emojis from another server | Manage Emojis |
| `/exchange` | Convert between fiat and cryptocurrencies using real-time rates | Anyone |
| `/check_tx` | Check blockchain transaction details across supported chains | Anyone |
| `/graph` | Plot a mathematical function | Anyone |
| `/drop` | Start a drop game in the current channel | Anyone |
| `/update` | Post an Equinox update embed | Developer |
| Translate (context menu) | Right-click any message to translate it | Anyone |

### Gemini AI
| Command | Description | Required Permissions |
|---|---|---|
| `/ask_gemini` | Ask Google Gemini AI any question | Anyone |

---

## Quick Start

### Prerequisites

- Python 3.11 or later
- Discord Bot Token
- PostgreSQL database (required for premium subscriptions)
- Google Gemini API Key (optional)

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

The bot creates all required data files with empty structures on first launch.

---

## Project Structure

```
Equinox/
  main.py                  Bot entry point, persistent views, core logic
  cogs/
    automation.py          Auto-role and auto-ping systems
    events.py              Startup events and code replenishment
    gacha.py               Gacha rolling, crafting, inventory management
    giveaway.py            Giveaway management
    giveaway_views.py      Giveaway UI components
    moderation.py          Slowmode, lockdown, ban, kick, purge
    premium.py             Premium subscriptions, code generation, NSFW
    presence.py            Activity tracking, top games, privacy controls
    reaction_roles.py      Dropdown-based role selection
    security.py            Scam shield, audit logging, code helper, lint
    ticket_views.py        Ticket UI components
    tickets.py             Ticket system
    utility.py             All utility commands (help, info, translate, etc.)
    verification.py        Captcha-based member verification
  assets/                  Static assets
  scripts/                 Utility scripts
  data/                    Runtime data (gitignored)
  .gitignore
  LICENSE                  GNU General Public License v3
  requirements.txt
```

---

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).

Copyright (C) 2025-2026 Equinox Team
