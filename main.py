import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot
import state
import os
import asyncio
from datetime import datetime, date, timezone, timedelta
import json
import secrets
import random
import typing
from discord.ext.commands import has_permissions
import qrcode
from asyncio import sleep, gather, wait_for, create_task
from PIL import Image
import requests
from email.message import EmailMessage
import ssl
import smtplib
import math
from discord import ui
from discord.ui import Modal, View, Select, Button, TextInput
import sys
from cogs.ticket_views import TicketButton, TicketChannelView, BuyPremium2
from cogs.views import *
import PyDictionary
from PyDictionary import PyDictionary
import googletrans
from googletrans import Translator
import wikipedia
import aiohttp
try:
    import fandom
except ModuleNotFoundError:
    fandom = None
from aiohttp import ClientSession
import re 
import time
import matplotlib.pyplot as plt
plt.set_loglevel("critical")
import numpy
import io
from captcha.image import ImageCaptcha                             
from discord.ext import tasks
from discord.utils import format_dt
import os, re, json, ast, time, uuid, string
from collections import deque, defaultdict
from typing import Dict, Any, List, Tuple, Optional, Literal
from io import BytesIO
import httpx
import asyncpg
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
email_password = os.getenv("email_password")
email_sender = os.getenv("email_sender")

os.makedirs("data", exist_ok=True)

intents = discord.Intents.default()

intents.members = True                      
intents.message_content = True
intents.presences = True              

                        
                                         

pending_alerts = {}

dictionary = PyDictionary()

BACKEND_URL = os.getenv("BACKEND_URL", "https://premiumbottesting.onrender.com")
_db_pool: Optional[asyncpg.Pool] = None

async def init_db_pool(min_size: int = 1, max_size: int = 5) -> None:
    global _db_pool
    if _db_pool is not None:
        return
    ssl_ctx = ssl.create_default_context()
    _db_pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"],
        min_size=min_size,
        max_size=max_size,
        ssl=ssl_ctx,
    )

async def close_db_pool() -> None:
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None



class PersistentViewBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents().all()
        super().__init__(command_prefix=commands.when_mentioned_or('/'), intents=discord.Intents.all())
        self.http_session = None
    async def setup_hook(self) -> None:
        self.http_session = ClientSession()
        await self.load_extension("cogs.events")
        await self.load_extension("cogs.automation")
        await self.load_extension("cogs.gacha")
        await self.load_extension("cogs.giveaway")
        await self.load_extension("cogs.moderation")
        await self.load_extension("cogs.premium")
        await self.load_extension("cogs.presence")
        await self.load_extension("cogs.reaction_roles")
        await self.load_extension("cogs.security")
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.utility")
        await self.load_extension("cogs.verification")
        self.add_view(TicketButton())
        self.add_view(TicketChannelView())
        self.add_view(VerifyButton())
        self.add_view(UpdateButton())
        self.add_view(rrSelectGames())
        self.add_view(rrSelectGender())
        self.add_view(rrSelectPing())
        self.add_view(rrSelectServer())
        self.add_view(PromptButtonView()) 

    async def close(self):
        from cogs.gacha import _flush_all as _gacha_flush
        await _gacha_flush()
        await close_db_pool()
        await self.http_session.close()
        await super().close()

STATS_FILE = "data/command_stats.json"
devs = [
    857932717681147954,
    1430719406022983740,
    661033986742550548,
]
IGNORED_USER_IDS = set(devs)                                       


client = PersistentViewBot()

                                                                                            

def check(interaction: discord.Interaction, m):
  return m.author.id == interaction.user.id

                                                                             

@client.tree.error
async def on_app_command_error(interaction, error):
  command = interaction.command.name
  if isinstance(error, app_commands.BotMissingPermissions):
    await interaction.response.send_message(embed=discord.Embed(title="I don't have required permission to do that!", description=f"```\n{error}\n```", color = 0xffffff))
  elif isinstance(error, app_commands.MissingPermissions):
    await interaction.response.send_message(embed=discord.Embed(title="Missing Permission", description=f"```\n{error}\n```", color = 0xffffff))
  elif isinstance(error, app_commands.CommandOnCooldown):
    remaining = 0
    if error.retry_after > 0 and error.retry_after < 59:
      remaining = f"{math.ceil(error.retry_after)} second(s)"
    elif error.retry_after > 59 and error.retry_after < 3600:
      remaining = f"{math.ceil(error.retry_after/60)} minute(s)"
    elif error.retry_after > 3600:
      remaining = f"{math.ceil(error.retry_after/3600)} hour(s)"  
    if command == "nsfw":
      embed=discord.Embed(title="You are being restricted", description=f"Normal nsfw command is only available to execute 10 times per hour.\nConsider buying our useful premium with lots of perks?\nUse </help:1242738769099231302> to check out our premium perks.", color = 0xffffff)
      embed.add_field(name=f"> Time left:", value=f"```Approximately {remaining}```", inline=False)
      await interaction.response.send_message(embed=embed, view=BuyPremium2())
    else:
      await interaction.response.send_message(embed=discord.Embed(title="Calm down...", description=f"```\nCommand {command} is on cooldown, please wait for {remaining}\n```", color = 0xffffff))
  else:
    raise error

                                                                                 

char1 = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0',]

client.monthly_codes = []
client.yearly_codes = []

client.monthly_user = []
client.yearly_user = []

def read_json(filename):
 try:
  with open(f"data/{filename}.json", "r") as file:
     data = json.load(file)
  return data
 except FileNotFoundError:
  data = {}
  write_json(data, filename)
  return data

def write_json(data, filename):
 with open(f"data/{filename}.json", "w") as file:
     json.dump(data, file, indent=4)

def refresh():
    monthly_data = read_json("monthcode")
    client.monthly_codes = monthly_data.get("monthlycodes", [])

    yearly_data = read_json("yearlycode")
    client.yearly_codes = yearly_data.get("yearlycodes", [])

    lifetime_data = read_json("lifetimecode")
    client.lifetime_codes = lifetime_data.get("lifetimecodes", [])

                                                                                  
    monthly_user_data = read_json("monthly_user")
    client.monthly_user = monthly_user_data.get("monthly_users", [])

    yearly_user_data = read_json("yearly_user")
    client.yearly_user = yearly_user_data.get("yearly_users", [])

async def is_premium(discord_id: int) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Mirrors db_user_is_active():
    returns (active, tier, expires_at_iso_or_none)
    """
    if _db_pool is None:
        return False, None, None

    now = datetime.now(timezone.utc)

    async with _db_pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT tier, expires_at
            FROM public.user_subscriptions
            WHERE discord_id = $1
            ORDER BY redeemed_at DESC
            LIMIT 1
            """,
            discord_id,  # int is fine if column is bigint
        )

    if not row:
        return False, None, None

    tier = row["tier"]
    expires = row["expires_at"]  # datetime or None

    # normalize tz (extra safety, mirrors your backend)
    if expires is not None and getattr(expires, "tzinfo", None) is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if tier == "lifetime" or expires is None:
        return True, tier, None

    active = expires > now
    return active, tier, expires.isoformat()

MONTH_DAYS = 30                                              
YEAR_DAYS  = 365
SUB_FILES = {
        "monthly": "data/monthly_user.json",
        "yearly": "data/yearly_user.json",
        "lifetime": "data/lifetime_user.json",
}

def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()

def load_json(path):
    if not os.path.exists(path):
                                               
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"users": []}, f, indent=2)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _duration_days(tier: str) -> int | None:
    if tier == "monthly":  return 30                                            
    if tier == "yearly":   return 365
    if tier == "lifetime": return None                     
    return None

def _expires_at_for(tier: str, started_at_iso: str) -> str | None:
    days = _duration_days(tier)
    if days is None:
        return None
    started = datetime.fromisoformat(started_at_iso)
    return (started + timedelta(days=days)).isoformat()

def _ensure_objects_schema(file_path: str, legacy_key: str):
\
\
\
       
    with open(file_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, dict) and legacy_key in raw and isinstance(raw[legacy_key], list):
        migrated = {"users": [{"user_id": uid, "started_at": utcnow_iso(), "expires_at": None} for uid in raw[legacy_key]]}
        save_json(file_path, migrated)
        return migrated
    if isinstance(raw, dict) and "users" in raw and isinstance(raw["users"], list):
                            
        return raw
                              
    if isinstance(raw, list):
        migrated = {"users": [{"user_id": uid, "started_at": utcnow_iso(), "expires_at": None} for uid in raw]}
        save_json(file_path, migrated)
        return migrated
    return raw

def add_subscription(user_id: int, tier: str, code: str):
    file_path = SUB_FILES[tier]
                       
    legacy_key = f"{tier}_users"
    data = _ensure_objects_schema(file_path, legacy_key)
                               
    now_iso = utcnow_iso()
    exp_iso = _expires_at_for(tier, now_iso)
    found = next((u for u in data["users"] if u.get("user_id") == user_id), None)
    if found:
                                                      
        found["started_at"] = now_iso
        found["expires_at"] = exp_iso
        found["code"] = code
    else:
        data["users"].append({
            "user_id": user_id,
            "started_at": now_iso,
            "expires_at": exp_iso,
            "code": code
        })
    save_json(file_path, data)

def remove_subscription(user_id: int, tier: str):
    file_path = SUB_FILES[tier]
    data = load_json(file_path)
    data["users"] = [u for u in data.get("users", []) if u.get("user_id") != user_id]
    save_json(file_path, data)


def _coerce_dt(dt_val):
                                                                        
    if dt_val is None:
        return None
    if isinstance(dt_val, datetime):
        return dt_val if dt_val.tzinfo else dt_val.replace(tzinfo=timezone.utc)
    try:
        return datetime.fromisoformat(str(dt_val).replace("Z", "+00:00"))
    except Exception:
        return None

def _fmt_expiry(expires_at):
    dt = _coerce_dt(expires_at)
    if not dt:
        return "Never"
                                            
    try:
        return f"{dt.isoformat()} ({discord.utils.format_dt(dt, style='R')})"
    except Exception:
        return dt.isoformat()

                                        
                                                                                                                    


CODE_FILES: dict[str, str | tuple[str, str]] = {
    "monthly":  ("monthcode",   "monthlycodes"),
    "yearly":   ("yearlycode",  "yearlycodes"),
    "lifetime": ("lifetimecode","lifetimecodes"),
}

DEFAULT_CODE_KEYS = {
    "monthly":  "monthlycodes",
    "yearly":   "yearlycodes",
    "lifetime": "lifetimecodes",
}
def code_key_for_tier(tier: str) -> str:
    return {"monthly": "monthlycodes", "yearly": "yearlycodes", "lifetime": "lifetimecodes"}[tier]

def resolve_code_store(tier: str) -> tuple[str, str]:
\
\
\
       
    entry = CODE_FILES.get(tier)
    if entry is None:
        raise ValueError(f"Unknown tier: {tier}")
    if isinstance(entry, tuple):
        if len(entry) < 2:
            raise ValueError(f"CODE_FILES[{tier}] tuple must be (file_stub, key)")
        return str(entry[0]), str(entry[1])
                               
    return str(entry), DEFAULT_CODE_KEYS[tier]

def _random_code() -> str:
                                                          
    return "-".join("".join(random.choice(char1) for _ in range(4)) for __ in range(4))

def replenish_codes(tier: str, count: int = 5) -> list[str]:
                                                                         
    file_stub, key = resolve_code_store(tier)

    data = read_json(file_stub)
    existing = set(data.get(key, []))

    new_codes: list[str] = []
    while len(new_codes) < count:
        c = _random_code()
        if c not in existing:
            existing.add(c)
            new_codes.append(c)

    data[key] = list(existing)
    write_json(data, file_stub)

                                                                                           
    setattr(client, f"{tier}_codes", data[key])
    return new_codes

def _load_codes_for_tier(t: str) -> list[str]:
    file_stub, key = resolve_code_store(t)
    data = read_json(file_stub)
    return [str(c).strip() for c in data.get(key, []) if str(c).strip()]

def _as_txt_file(filename: str, codes: list[str]) -> Optional[discord.File]:
    if not codes:
        return None
    buf = io.BytesIO(("\n".join(codes) + "\n").encode("utf-8"))
    return discord.File(buf, filename=filename)

def load_stats() -> dict:
    if not os.path.exists(STATS_FILE):
        return {"events": []}
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {"events": []}


def save_stats(data: dict) -> None:
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _log_command(user_id: int, command_name: str) -> None:
    if user_id in IGNORED_USER_IDS:
        return

    data = load_stats()
    events = data.get("events", [])

    events.append({
        "user_id": int(user_id),
        "command": command_name,
        "ts": datetime.now(timezone.utc).isoformat()
    })

    data["events"] = events
    save_stats(data)


AUTOPING_FOLDER = "autoping_data"
os.makedirs(AUTOPING_FOLDER, exist_ok=True)

def get_autoping_path(guild_id):
    return os.path.join(AUTOPING_FOLDER, f"autoping_{guild_id}.json")

def load_autoping_channels(guild_id):
    path = get_autoping_path(guild_id)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_autoping_channels(guild_id, channels):
    path = get_autoping_path(guild_id)
    with open(path, "w") as f:
        json.dump(channels, f)

AUTOROLE_FOLDER = "autorole_data"
os.makedirs(AUTOROLE_FOLDER, exist_ok=True)

def get_autorole_path(guild_id):
    return os.path.join(AUTOROLE_FOLDER, f"autorole_{guild_id}.json")

def load_autorole(guild_id):
    path = get_autorole_path(guild_id)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def save_autorole(guild_id, role_id):
    path = get_autorole_path(guild_id)
    with open(path, "w") as f:
        json.dump(role_id, f)

def remove_autorole(guild_id):
    path = get_autorole_path(guild_id)
    if os.path.exists(path):
        os.remove(path)

PREFIX = "/"

PRIVACY_FILE = "data/privacy_settings.json"

def load_privacy_settings() -> dict:
    if not os.path.exists(PRIVACY_FILE):
        return {}
    try:
        with open(PRIVACY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            new_data = {str(uid): ["presence", "status"] for uid in data}
            save_privacy_settings(new_data)
            return new_data
        return data
    except Exception:
        return {}

def save_privacy_settings(data: dict):
    with open(PRIVACY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

PRIVACY_SET: set[int] = set()
STATUS_PRIVACY_SET: set[int] = set()

def reload_privacy_sets():
    global PRIVACY_SET, STATUS_PRIVACY_SET
    data = load_privacy_settings()
    PRIVACY_SET = {int(uid) for uid, cats in data.items() if "presence" in cats}
    STATUS_PRIVACY_SET = {int(uid) for uid, cats in data.items() if "status" in cats}

reload_privacy_sets()

VERIFYING_USERS: set[tuple[int, int]] = set()
VERIFYING_FILE = "data/user_verifying.json"

VERIFYING_USERS = load_verifying_users()

def remove_code_from_pool(tier: str, code: str):
    if tier == "monthly":
        data = read_json("monthcode")
        if code in data.get("monthlycodes", []):
            data["monthlycodes"].remove(code)
            write_json(data, "monthcode")
        client.monthly_codes = read_json("monthcode").get("monthlycodes", [])

    elif tier == "yearly":
        data = read_json("yearlycode")
        if code in data.get("yearlycodes", []):
            data["yearlycodes"].remove(code)
            write_json(data, "yearlycode")
        client.yearly_codes = read_json("yearlycode").get("yearlycodes", [])

    elif tier == "lifetime":
        data = read_json("lifetimecode")
        if code in data.get("lifetimecodes", []):
            data["lifetimecodes"].remove(code)
            write_json(data, "lifetimecode")
                                                        
        client.lifetime_codes = read_json("lifetimecode").get("lifetimecodes", [])

_pending_auths: dict[int, dict] = {}
AUTH_CODE_EXPIRY = 300
AUTH_MAX_ATTEMPTS = 3


RESET_COOLDOWN = 86400  # 24 hours


language_dict = {}

for key, value in googletrans.LANGUAGES.items():
  if key in ['af', 'ar', 'hy', 'bs', 'bg', 'zh-cn', 'zh-tw', 'hr', 'nl', 'en', 'tl', 'fr', 'el', 'hi', 'id', 'ga', 'it', 'ja', 'ko', 'lo', 'ms', 'pt', 'es', 'th', 'vi']:
    language_dict[key] = value

async def fandom_query(interaction: discord.Interaction, search: str, category: str):
  if fandom is None:
    return await interaction.response.send_message("Fandom module is not installed.", ephemeral=True)
  await interaction.response.defer()
  if not search or len(search) > 200 or not category or len(category) > 100:
      return await interaction.followup.send("Invalid search or category length.", ephemeral=True)
  if not re.match(r'^[\w\s-]+$', search) or not re.match(r'^[\w\s-]+$', category):
      return await interaction.followup.send("Search and category must only contain letters, numbers, spaces, hyphens, and underscores.", ephemeral=True)
  search = search.title()
  category = category.lower()
  search_query = ""
  category_query = ""
  if len(search.split()) > 1:
    search_query = "_".join(search.split())
  else:
    search_query = search
  if len(category.split()) > 1:
    category_query = "-".join(category.split())
  else:
    category_query = category
  fandom.set_wiki(category_query)
  fandom_page = fandom.page(search_query)
  fandom_title = fandom_page.title
  fandom_url = fandom_page.url
  fandom_content = fandom.summary(search_query, category_query)
  embed=discord.Embed(color=0xffffff)
  embed.set_author(name=f"Fandom: {category.title()} Wiki", icon_url=client.user.avatar)
  embed.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/search-12-xxl.png")
  embed.add_field(name=f"> **{search.title()}**", value=f"```{fandom_content}```", inline=False)
  embed.set_footer(text=f"Powered by Fandom (fandom-py)", icon_url=interaction.user.avatar)
  view = FandomPageUrl(fandom_url)
  await interaction.followup.send(embed=embed, view=view)


update = "EV-5.1"
update_note = "```diff\n+Added giveaway command (Start a giveaway)\n\n+Added graph command.```"
API_URL = 'https://v6.exchangerate-api.com/v6/{}/latest/{}'

                                              
SYMBOL_TO_ID = {
    'btc': 'bitcoin',
    'eth': 'ethereum',
    'ltc': 'litecoin',
    'xrp': 'ripple',
    'bch': 'bitcoin-cash',
    'ada': 'cardano',
    'dot': 'polkadot',
    'link': 'chainlink',
    'xlm': 'stellar',
    'doge': 'dogecoin',
    'xmr': 'monero',
    'usdt': 'tether',
    'usdc': 'usd-coin',
    'bnb': 'binancecoin',
    'avax': 'avalanche-2',
    'shib': 'shiba-inu',
    'trx': 'tron',
    'sol': 'solana',
    'matic': 'matic-network',
    'near': 'near',
    'uni': 'uniswap',
    'ftm': 'fantom',
    'egld': 'elrond-erd-2',
    'cake': 'pancakeswap-token',
    'aave': 'aave',
    'sand': 'the-sandbox',
    'mana': 'decentraland',
    'atom': 'cosmos',
    'zec': 'zcash',
    'icp': 'internet-computer',
    'algo': 'algorand',
    'etc': 'ethereum-classic',
    'fil': 'filecoin',
    'grt': 'the-graph',
    'rune': 'thorchain',
    'chz': 'chiliz',
    'qtum': 'qtum',
    'bat': 'basic-attention-token'
}

SUPPORTED_FIAT = {
    'usd', 'eur', 'gbp', 'jpy', 'aud', 'cad', 'chf', 'cny', 'inr', 'brl',
    'nzd', 'sgd', 'hkd', 'krw', 'myr', 'thb', 'idr', 'php', 'vnd', 'bdt',
    'pkr', 'npr', 'aed', 'sar', 'ils', 'try', 'egp', 'zar', 'rub', 'mxn',
    'pln', 'czk', 'huf', 'ron', 'sek', 'nok', 'dkk', 'uah', 'ars', 'clp',
    'cop', 'pen', 'kes', 'twd', 'vuv', 'ngn', 'ghs', 'lkr', 'mad', 'tnd',
    'jod', 'omr', 'qar', 'kwd', 'bhd'
}


SUPPORTED_CHAINS = {"btc", "ltc", "doge", "eth"}

                             
async def fetch_tx_data(chain: str, txid: str):
    async with aiohttp.ClientSession() as session:
        if chain == "btc":
                                       
            tx_url = f"https://mempool.space/api/tx/{txid}"
            async with session.get(tx_url) as tx_resp:
                if tx_resp.status != 200:
                    return None, "Failed to fetch BTC tx."
                tx_data = await tx_resp.json()

            height_url = "https://mempool.space/api/blocks/tip/height"
            async with session.get(height_url) as h_resp:
                tip_height = int(await h_resp.text())

            block_height = tx_data.get("status", {}).get("block_height")
            confirmations = tip_height - block_height + 1 if block_height else 0
            tx_data["confirmations"] = confirmations
            return {"tx": tx_data}, None

        elif chain == "doge":
            net = chain.upper()
            url = f"https://sochain.com/api/v2/tx/{net}/{txid}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None, f"Failed to fetch {chain.upper()} tx."
                data = await resp.json()
                return {"tx": data["data"]}, None

        elif chain == "ltc":
            url = f"https://api.blockcypher.com/v1/ltc/main/txs/{txid}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None, "Failed to fetch LTC tx from BlockCypher."
                data = await resp.json()
                return {"tx": data}, None


        elif chain == "eth":
            url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={txid}&apikey={ETHERSCAN_API_KEY}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None, "Failed to fetch ETH tx."
                data = await resp.json()
                return {"tx": data.get("result")}, None

        return None, "Unsupported chain."

                          
def parse_tx_data(chain: str, data):
    tx = data["tx"]

    if chain == "btc":
        confirmations = tx["confirmations"]
        value_btc = sum(int(v["value"]) for v in tx.get("vout", [])) / 1e8
        explorer = f"https://mempool.space/tx/{tx['txid']}"
        embed = discord.Embed(title="🔍 BTC Transaction", color=0xf7931a, url=explorer)
        embed.add_field(name="TXID", value=tx["txid"], inline=False)
        embed.add_field(name="Confirmations", value=str(confirmations), inline=True)
        embed.add_field(name="Block Height", value=tx["status"].get("block_height", "Unconfirmed"), inline=True)
        embed.add_field(name="Total Output", value=f"{value_btc:.8f} BTC", inline=True)
        embed.add_field(name="Explorer", value=f"[View on mempool.space]({explorer})", inline=False)
        return embed, confirmations

    elif chain == "doge":
        confirmations = tx.get("confirmations", 0)
        value = tx.get("value", "0")
        fee = tx.get("fee", "0")

        explorer = f"https://sochain.com/tx/{chain.upper()}/{tx['txid']}"

        embed = discord.Embed(title=f"🔍 {chain.upper()} Transaction", color=0xff9900, url=explorer)
        embed.add_field(name="TXID", value=tx["txid"], inline=False)
        embed.add_field(name="Confirmations", value=str(confirmations), inline=True)
        embed.add_field(name="Block", value=tx.get("block_no", "Unconfirmed"), inline=True)
        embed.add_field(name="Value", value=f"{value} {chain.upper()}", inline=True)
        embed.add_field(name="Fee", value=f"{fee} {chain.upper()}", inline=True)
        embed.add_field(name="Explorer", value=f"[View on Explorer]({explorer})", inline=False)
        return embed, confirmations

    elif chain == "ltc":
        confirmations = tx.get("confirmations", 0)
        value = sum(output.get("value", 0) for output in tx.get("outputs", [])) / 1e8
        fee = tx.get("fees", 0) / 1e8
        block_height = tx.get("block_height", "Unconfirmed")
        txid = tx.get("hash", "N/A")
        explorer = f"https://litecoinspace.org/tx/{txid}"

        embed = discord.Embed(title="🔍 LTC Transaction", color=0xbfbbbb, url=explorer)
        embed.add_field(name="TXID", value=txid, inline=False)
        embed.add_field(name="Confirmations", value=str(confirmations), inline=True)
        embed.add_field(name="Block Height", value=str(block_height), inline=True)
        embed.add_field(name="Value", value=f"{value:.8f} LTC", inline=True)
        embed.add_field(name="Fee", value=f"{fee:.8f} LTC", inline=True)
        embed.add_field(name="Explorer", value=f"[View on LitecoinSpace]({explorer})", inline=False)
        return embed, confirmations

    elif chain == "eth":
        confirmations = 0                                                
        value_eth = int(tx.get("value", "0x0"), 16) / 1e18
        gas = int(tx.get("gas", "0x0"), 16)
        embed = discord.Embed(title="🔍 ETH Transaction", color=0x627eea,
                              url=f"https://etherscan.io/tx/{tx.get('hash')}")
        embed.add_field(name="TXID", value=tx.get("hash", "N/A"), inline=False)
        embed.add_field(name="From", value=tx.get("from", "N/A"), inline=True)
        embed.add_field(name="To", value=tx.get("to", "N/A"), inline=True)
        embed.add_field(name="Value", value=f"{value_eth:.6f} ETH", inline=True)
        embed.add_field(name="Gas Used", value=str(gas), inline=True)
        embed.add_field(name="Explorer", value=f"[View on Etherscan](https://etherscan.io/tx/{tx.get('hash')})", inline=False)
        return embed, confirmations

    return discord.Embed(title="Unsupported Chain", color=discord.Color.red()), 0

               
@tasks.loop(minutes=1)
async def monitor_confirmations():
    to_remove = []
    for (user_id, txid, chain), info in pending_alerts.items():
        data, error = await fetch_tx_data(chain, txid)
        if error:
            continue
        _, confirmations = parse_tx_data(chain, data)

        if confirmations >= info["target"]:
            user = await client.fetch_user(user_id)
            message = f"✅ Your `{chain.upper()}` transaction `{txid}` has reached **{confirmations} confirmations**."
            if info["channel"]:
                channel = client.get_channel(info["channel"])
                if channel:
                    await channel.send(f"{user.mention} {message}")
                else:
                    await user.send(message)
            else:
                await user.send(message)
            to_remove.append((user_id, txid, chain))

    for k in to_remove:
        del pending_alerts[k]



from typing import Literal

data_folder = "messageCounterData"
os.makedirs(data_folder, exist_ok=True)


def get_server_data_path(guild_id):
    return os.path.join(data_folder, f"messagecounter_{guild_id}.json")


def load_server_data(guild_id):
    path = get_server_data_path(guild_id)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_server_data(guild_id, data):
    path = get_server_data_path(guild_id)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

DEV_USER_ID = [857932717681147954]

async def ask_gemini(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            return await resp.json()

                      
async def violates_tos(text: str) -> bool:
    moderation_prompt = (
        "You're an AI content moderator. Respond ONLY with `true` or `false`.\n"
        "Does the following content clearly violate **any** of the following:\n"
        "- Discord's Terms of Service (e.g., illegal, violent, hateful, harmful, explicit NSFW)\n"
        "- Google's Gemini AI policy\n"
        "- Would this content be clearly inappropriate or harmful for a **general audience including minors**?\n"
        "If there's **any doubt or ambiguity**, respond with `false`.\n\n"
        f"Content:\n\"\"\"\n{text}\n\"\"\""
    )

    data = await ask_gemini(moderation_prompt)
    try:
        reply = data["candidates"][0]["content"]["parts"][0]["text"].strip().lower()
        return reply == "true"
    except Exception:
        return True

def load_gemini_servers():
    if not os.path.exists("data/geminiServer.json"):
        return {"servers": []}
    with open("data/geminiServer.json", "r") as f:
        return json.load(f)

def save_gemini_servers(data):
    with open("data/geminiServer.json", "w") as f:
        json.dump(data, f, indent=2)

                         
user_graph_data = {}                                           

SAFE_CHARS_RE = re.compile(r'^[\w\s+\-*/()\[\],.:=%!<>&|~^@]+$')

async def send_graph_embed(interaction: discord.Interaction, user_id):
                                                  
    graph_image = user_graph_data[user_id]["graph_image"]
    if graph_image is None:
        return await interaction.response.send_message("Failed to generate the graph.", ephemeral=True)

    embed = discord.Embed(title=None, description=None, color=0xffffff)
    embed.set_author(name=f"{interaction.user.name}'s Graph", icon_url=interaction.user.avatar)
    embed.set_image(url="attachment://graph.png")

                                                                    
    if "message" in user_graph_data[user_id] and user_graph_data[user_id]["message"]:
        try:
            old_message = user_graph_data[user_id]["message"]
            old_view = GraphView(user=interaction.user, message=old_message)
            for item in old_view.children:
                item.disabled = True                       

            await old_message.edit(view=old_view)                                        
        except (discord.NotFound, discord.HTTPException):
            pass                                       

                          
    view = GraphView(interaction.user)
    message = await interaction.channel.send(embed=embed, file=discord.File(graph_image, filename="graph.png"), view=view)

                                     
    user_graph_data[user_id]["message"] = message



data_file = 'data/reaction_roles.json'
if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(data_file, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

def load_audit_config():
    if not os.path.exists("data/audit_config.json"):
        return {}
    with open("data/audit_config.json", "r") as f:
        return json.load(f)

def save_audit_config(data):
    with open("data/audit_config.json", "w") as f:
        json.dump(data, f, indent=4)

def append_audit_log(guild_id: int, entry: str):
    os.makedirs("audit_logs", exist_ok=True)
    path = f"audit_logs/{guild_id}.txt"
    if os.path.exists(path) and os.path.getsize(path) > 20 * 1024 * 1024:
        base, ext = os.path.splitext(path)
        import shutil
        shutil.move(path, f"{base}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}{ext}")
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def read_audit_log(guild_id: int):
    path = f"audit_logs/{guild_id}.txt"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

CONFIG_PATH = "data/guild_config.json"
ACTIONS_PATH = "data/scam_actions.json"
FEEDBACK_PATH = "data/scam_feedback.jsonl"

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
    "phrase_audit": {}                                
}

                                          
def _load_json(path: str, default):
    if not os.path.exists(path): return default
    try:
        with open(path, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return default

def _save_json(path: str, data):
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2)

def load_all_config() -> Dict[str, Any]:
    data = _load_json(CONFIG_PATH, {})
    for _, cfg in list(data.items()):
        for k, v in DEFAULTS.items(): cfg.setdefault(k, v)

                                                              
        if "channel_allowlist" in cfg and cfg["channel_allowlist"]:
            olds = set(cfg.get("scam_channels") or [])
            cfg["scam_channels"] = sorted(olds | set(cfg["channel_allowlist"]))
            cfg["channel_allowlist"] = []                
    return data

def is_scam_whitelisted(member: discord.Member, cfg: dict) -> bool:
    users = set(cfg.get("scam_user_whitelist") or [])
    roles = set(cfg.get("scam_role_whitelist") or [])
    if member.id in users:
        return True
    if any(r.id in roles for r in getattr(member, "roles", [])):
        return True
    return False


def save_all_config(data: Dict[str, Any]): _save_json(CONFIG_PATH, data)

def get_guild_cfg(guild_id: int) -> Dict[str, Any]:
    data = load_all_config()
    g = str(guild_id)
    if g not in data:
        data[g] = DEFAULTS.copy()
        save_all_config(data)
    for k, v in DEFAULTS.items(): data[g].setdefault(k, v)
    return data[g]

def update_guild_cfg(guild_id: int, **patch):
    data = load_all_config()
    g = str(guild_id)
    if g not in data: data[g] = DEFAULTS.copy()
    data[g].update(patch)
    save_all_config(data)

                                                          
def load_actions() -> Dict[str, Any]: return _load_json(ACTIONS_PATH, {})
def save_actions(data: Dict[str, Any]): _save_json(ACTIONS_PATH, data)
def append_feedback(entry: Dict[str, Any]):
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

                                                        
COLOR_OK=0x57F287; COLOR_WARN=0xFEE75C; COLOR_BAD=0xED4245; COLOR_INFO=0xffffff
def embed_basic(title: str, description: str = "", color: int = COLOR_INFO) -> discord.Embed:
    e = discord.Embed(title=title, description=description, color=color)
    e.set_footer(text="Security & Utilities")
    return e

                                                         
def admin_or_manage_guild(interaction: discord.Interaction) -> bool:
    p = interaction.user.guild_permissions
    return p.administrator or p.manage_guild

def normalize_phrase(text: str) -> str:
    t = (text or "").lower()
    t = " ".join(t.split())
    return t.strip(string.punctuation + " ")

                               
MD_LINK_RE = re.compile(r"\[[^\]]*\]\((?P<url>[^)]+)\)")
ANGLED_RE  = re.compile(r"<(?P<url>https?://[^>]+)>", re.I)
SCHEME_RE  = re.compile(r"https?://(?P<host>[^/\s)]+)", re.I)
BARE_RE    = re.compile(r"\b(?P<host>(?:[a-z0-9-]+\.)+[a-z]{2,})(?:[/:?#][^\s]*)?\b", re.I)

def extract_domains(text: str) -> List[str]:
    text = text or ""; hosts: List[str] = []
    for m in MD_LINK_RE.finditer(text):
        url = m.group("url"); h = None
        ms = SCHEME_RE.search(url); h = ms.group("host") if ms else (BARE_RE.search(url).group("host") if BARE_RE.search(url) else None)
        if h: hosts.append(h.lower().rstrip(").,>}]"))
    for m in ANGLED_RE.finditer(text):
        h = SCHEME_RE.search(m.group("url")).group("host"); hosts.append(h.lower().rstrip(").,>}]"))
    for m in SCHEME_RE.finditer(text):
        hosts.append(m.group("host").lower().rstrip(").,>}]"))
    for m in BARE_RE.finditer(text):
        hosts.append(m.group("host").lower().rstrip(").,>}]"))
    seen, out = set(), []
    for h in hosts:
        if h not in seen: out.append(h); seen.add(h)
    return out

                                                         
                         
SCAM_RULES: List[Tuple[str, re.Pattern]] = [
    ("Fake Nitro", re.compile(r"(?:free|claim|gift).{0,20}\bnitro\b", re.I)),
    ("Wallet Connect / Verify Wallet", re.compile(r"\b(?:connect\s+wallet|wallet\s*connect|verify\s+wallet|sync\s+wallet)\b", re.I)),
    ("Seed Phrase / Private Key", re.compile(r"\b(?:seed\s+phrase|recovery\s+phrase|private\s+key|mnemonic|keystore)\b", re.I)),
    ("Crypto Airdrop", re.compile(r"\b(?:airdrop|claim\s+airdrop|retrodrop|season\s+\d+\s+airdrop)\b", re.I)),
    ("Mint Now / Gasless Mint", re.compile(r"\b(?:mint\s+now|gasless\s+mint|free\s+mint|stealth\s+mint|presale\s+mint)\b", re.I)),
    ("Giveaway / Double Your", re.compile(r"\bsend\s+\d+(?:\.\d+)?\s*(?:eth|btc|sol|usdt|usdc).{0,30}(?:get|receive)\s+\d+(?:\.\d+)?\s*(?:eth|btc|sol|usdt|usdc)\b", re.I)),
    ("Drainer Keywords", re.compile(r"\b(?:drainer|sweeper|web3\s*auth|sign\s+to\s+claim)\b", re.I)),
    ("Shortened Link", re.compile(r"https?://(?:bit\.ly|tinyurl\.com|t\.co|cutt\.ly|is\.gd|rb\.gy|linktr\.ee|links\.sh|goo\.gl)/\S*", re.I)),
    ("Crypto Address (ETH)", re.compile(r"\b0x[a-fA-F0-9]{40}\b")),
    ("Crypto Address (SOL-like)", re.compile(r"\b[1-9A-HJ-NP-Za-km-z]{32,48}\b")),
]
SUSPICIOUS_TLDS    = {"ru","tk","gq","cf","ml","xyz","zip","mov","top","cam","rest","guru","click","country"}
IMPERSONATION_ROOTS = {"discorcl","dlscord","disc0rd","steamcom","steamncommunity","steancommunity","faceb00k","go0gle"}

def domain_is_whitelisted(dom: str, allow: List[str]) -> bool:
    dom = dom.lower()
    for a in allow:
        if dom == a or dom.endswith("." + a): return True
    return False

def root_label(host: str) -> str:
    parts = host.split(".")
    return parts[-2] if len(parts) >= 2 else host

def scan_message_for_scams(content: str, cfg: dict) -> List[str]:
    hits: List[str] = []
    content = content or ""
    norm = normalize_phrase(content)

                      
    if norm in set(cfg.get("phrase_allowlist") or []): return []

    domains = extract_domains(content)
    allow = [d.lower() for d in (cfg.get("domain_allowlist") or [])]
    short_allow = [s.lower() for s in (cfg.get("shortener_allowlist") or [])]
    nitro_requires_url = bool(cfg.get("nitro_requires_url", True))

                   
    for label, pat in SCAM_RULES:
        if not pat.search(content): continue
        if label == "Fake Nitro" and nitro_requires_url and not domains: continue
        hits.append(label)

                  
    for host in domains:
        host = host.lower()
        if domain_is_whitelisted(host, allow): continue
        if any(host.endswith(s) for s in short_allow):                     
            continue
        if host.startswith("xn--"): hits.append("Punycode/IDN")
        tld = host.rsplit(".", 1)[-1] if "." in host else ""
        if tld in SUSPICIOUS_TLDS: hits.append("Suspicious TLD")
        if root_label(host) in IMPERSONATION_ROOTS: hits.append("Impersonation Domain")

                                              
    if hits and set(hits).issubset({"Crypto Address (ETH)", "Crypto Address (SOL-like)"}): return []

                             
    seen, out = set(), []
    for h in hits:
        if h not in seen: out.append(h); seen.add(h)
    return out

                                                         
CODEBLOCK_CLOSED_RE = re.compile(r"```(?P<lang>[a-zA-Z0-9_\-]*)\n(?P<code>[\s\S]*?)```", re.MULTILINE)
CODEBLOCK_UNTERMINATED_RE = re.compile(r"```(?P<lang>[a-zA-Z0-9_\-]*)\n(?P<code>[\s\S]*?)\Z", re.MULTILINE)

def try_python_syntax_check(code: str) -> Tuple[bool, str]:
    try:
        ast.parse(code); return True, "No syntax errors detected."
    except SyntaxError as e:
        pointer = ""
        if e.text:
            caret_pos = (e.offset or 1) - 1
            line_txt = e.text.rstrip("\n")
            pointer = f"\n{line_txt}\n{' ' * max(caret_pos,0)}^"
        return False, f"{e.msg} (line {e.lineno}, col {e.offset}){pointer}"

                                                         
JOIN_WINDOW_SECONDS = 60
join_windows: Dict[int, deque] = defaultdict(lambda: deque(maxlen=2500))
def record_join(guild_id: int):
    now = time.time(); dq = join_windows[guild_id]; dq.append(now)
    while dq and (now - dq[0] > JOIN_WINDOW_SECONDS): dq.popleft()
def joins_last_minute(guild_id: int) -> int:
    record_join(guild_id); dq = join_windows[guild_id]; now = time.time()
    return sum(1 for t in dq if now - t <= JOIN_WINDOW_SECONDS)

async def apply_limited_if_needed(member: discord.Member):
    cfg = get_guild_cfg(member.guild.id)
    threshold = int(cfg.get("surge_threshold_per_minute") or 10)
    limited_role_id = cfg.get("limited_role_id")
    count = joins_last_minute(member.guild.id)
    account_age_days = (discord.utils.utcnow() - member.created_at.replace(tzinfo=timezone.utc)).days
    if count >= threshold and limited_role_id and account_age_days < 7:
        role = member.guild.get_role(limited_role_id)
        if role:
            try:
                await member.add_roles(role, reason="Event Guard: join surge / young account")
                chan = member.guild.system_channel or next((c for c in member.guild.text_channels if c.permissions_for(member.guild.me).send_messages), None)
                if chan:
                    await chan.send(embed=embed_basic(
                        "Event Guard: Surge Protection Active",
                        f"Applied **{role.name}** to {member.mention} (joins/min: **{count}**, account age: **{account_age_days}d**)",
                        COLOR_WARN
                    ))
            except Exception: pass

                                                         
DURATION_RE = re.compile(r"^(\d+)(y|m|d|min)$", re.I)

def parse_duration_to_timedelta(s: str) -> Optional[float]:
\
\
\
       
    if not s:
        return None
    m = DURATION_RE.match(s.strip())
    if not m:
        return None
    qty = int(m.group(1))
    unit = m.group(2).lower()
    if qty <= 0:
        return None

    if unit == "y":                         
        return qty * 365 * 24 * 3600
    if unit == "m":                         
        return qty * 30 * 24 * 3600
    if unit == "d":
        return qty * 24 * 3600
    if unit == "min":
        return qty * 60
    return None

def fmt_discord_time(dt) -> tuple[str, str]:
\
\
       
    ts = int(dt.timestamp())
    return f"<t:{ts}:F>", f"<t:{ts}:R>"

                                                        
def _chunk_lines(lines, size=10):
    return [lines[i:i+size] for i in range(0, len(lines), size)] or [[]]

PAGE_SIZE = 20                               

def human_td(delta: timedelta) -> str:
    secs = int(delta.total_seconds())
    days, secs = divmod(secs, 86400)
    hours, secs = divmod(secs, 3600)
    minutes, _ = divmod(secs, 60)
    if days > 0: return f"{days}d {hours}h"
    if hours > 0: return f"{hours}h {minutes}m"
    return f"{minutes}m"

def bucketize_age(now: datetime, created_at: datetime) -> str:
    age = now - created_at
    if age <= timedelta(days=1): return "≤1d"
    if age <= timedelta(weeks=1): return "≤1w"
    if age <= timedelta(days=30): return "≤1m"
    if age <= timedelta(days=365): return "≤1y"
    if age <= timedelta(days=365*3): return "≤3y"
    return ">3y"

async def scan_inactive_members(guild: discord.Guild, members: list[discord.Member], history_days: int = 90) -> list[discord.Member]:
\
\
\
\
       
    now = discord.utils.utcnow()
    since_floor = now - timedelta(days=history_days)
                                                                                
    earliest: dict[int, datetime] = {}
    for m in members:
        if not m.bot:
            joined = (m.joined_at or now).replace(tzinfo=timezone.utc)
            earliest[m.id] = max(joined, since_floor)

                                                                           
    has_activity: set[int] = set()
    for channel in guild.text_channels:
        perms = channel.permissions_for(guild.me)
        if not (perms.read_messages and perms.read_message_history):
            continue
        try:
            async for msg in channel.history(limit=200, after=since_floor, oldest_first=True):
                mid = msg.author.id
                if mid in earliest and msg.created_at.replace(tzinfo=timezone.utc) >= earliest[mid]:
                    has_activity.add(mid)
                                                                     
                if len(has_activity) >= len(earliest):
                    break
        except (discord.Forbidden, discord.HTTPException):
            continue

    inactive = [m for m in members if (not m.bot) and (m.id in earliest) and (m.id not in has_activity)]
                                                           
    inactive.sort(key=lambda x: x.joined_at or now, reverse=True)
    return inactive

def build_overview_embed(guild: discord.Guild, members: list[discord.Member]) -> discord.Embed:
    now = discord.utils.utcnow()
    humans = [m for m in members if not m.bot and m.created_at is not None]
    if not humans:
        return embed_basic("Server Member Stats — Overview", "No human members found.", COLOR_INFO)

    ages = [now - m.created_at.replace(tzinfo=timezone.utc) for m in humans]
    avg_age = sum((a.total_seconds() for a in ages)) / len(ages)
    avg_td = timedelta(seconds=int(avg_age))

    youngest = max(humans, key=lambda m: m.created_at)
    oldest   = min(humans, key=lambda m: m.created_at)

                
    lt_1d = sum(1 for m in humans if now - m.created_at <= timedelta(days=1))
    lt_1w = sum(1 for m in humans if now - m.created_at <= timedelta(weeks=1))
    lt_1m = sum(1 for m in humans if now - m.created_at <= timedelta(days=30))
    lt_1y = sum(1 for m in humans if now - m.created_at <= timedelta(days=365))

    e = embed_basic("Server Member Stats — Overview", color=COLOR_INFO)
    e.add_field(name="Average account age", value=human_td(avg_td), inline=True)

    y_abs = f"<t:{int(youngest.created_at.replace(tzinfo=timezone.utc).timestamp())}:F>"
    y_rel = f"<t:{int(youngest.created_at.replace(tzinfo=timezone.utc).timestamp())}:R>"
    o_abs = f"<t:{int(oldest.created_at.replace(tzinfo=timezone.utc).timestamp())}:F>"
    o_rel = f"<t:{int(oldest.created_at.replace(tzinfo=timezone.utc).timestamp())}:R>"

    e.add_field(name="Youngest account", value=f"{youngest.mention} (`{youngest.id}`)\n{y_abs} ({y_rel})", inline=False)
    e.add_field(name="Oldest account",   value=f"{oldest.mention} (`{oldest.id}`)\n{o_abs} ({o_rel})", inline=False)
    e.add_field(name="Age distribution (counts)",
                value=f"≤1d: **{lt_1d}** | ≤1w: **{lt_1w}** | ≤1m: **{lt_1m}** | ≤1y: **{lt_1y}**",
                inline=False)
    e.set_footer(text=f"{guild.name} • Humans: {len(humans)}")
    return e

def build_top_roles_embed(guild: discord.Guild, members: list[discord.Member], page:int=0) -> tuple[discord.Embed,int]:
                                                
    counts: dict[int, int] = {}
    for m in members:
        for r in m.roles:
            if r.is_default():             
                continue
            counts[r.id] = counts.get(r.id, 0) + 1
    sorted_roles = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)

                         
    total_pages = max(1, math.ceil(len(sorted_roles)/PAGE_SIZE))
    page = max(0, min(page, total_pages-1))
    start = page*PAGE_SIZE
    chunk = sorted_roles[start:start+PAGE_SIZE]

    lines = []
    for rid, n in chunk:
        role = guild.get_role(rid)
        if role:
            lines.append(f"• {role.mention} — **{n}** members")

    e = embed_basic("Server Member Stats — Top Roles", color=COLOR_INFO)
    e.add_field(name=f"Most-equipped roles (page {page+1}/{total_pages})", value="\n".join(lines) or "No roles.", inline=False)
    return e, total_pages

def build_inactive_embed(inactive: list[discord.Member], page:int=0) -> tuple[discord.Embed,int]:
    total_pages = max(1, math.ceil(len(inactive)/PAGE_SIZE))
    page = max(0, min(page, total_pages-1))
    start = page*PAGE_SIZE
    chunk = inactive[start:start+PAGE_SIZE]

    lines = []
    for m in chunk:
        joined = m.joined_at or discord.utils.utcnow()
        lines.append(f"• {m.mention} (`{m.id}`) — joined <t:{int(joined.replace(tzinfo=timezone.utc).timestamp())}:R>")

    e = embed_basic("Server Member Stats — Inactive Since Joining", color=COLOR_INFO)
    e.add_field(name=f"Inactive members (page {page+1}/{total_pages})", value="\n".join(lines) or "None 🎉", inline=False)
    return e, total_pages

def build_age_graph(members: list[discord.Member]) -> io.BytesIO:
    now = discord.utils.utcnow()
    buckets = ["≤1d","≤1w","≤1m","≤1y","≤3y",">3y"]
    counts = {k:0 for k in buckets}
    for m in members:
        if m.bot or m.created_at is None: continue
        b = bucketize_age(now, m.created_at.replace(tzinfo=timezone.utc))
        counts[b] += 1

          
    fig, ax = plt.subplots(figsize=(6,3.2), dpi=180)
    ax.bar(buckets, [counts[k] for k in buckets])
    ax.set_xlabel("Account age")
    ax.set_ylabel("Members")
    ax.set_title("Account Age Distribution")
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

def format_expires(expires):
    # expires can be: None, datetime, or ISO string
    if not expires:
        return "Never"

    # If backend already returned an ISO string, just show it nicely
    if isinstance(expires, str):
        # Try to parse it for nicer display; fallback to raw string
        try:
            s = expires.replace("Z", "+00:00")
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            # Discord timestamp formatting
            return f"<t:{int(dt.timestamp())}:F> (<t:{int(dt.timestamp())}:R>)"
        except Exception:
            return expires  # show raw

    # If it’s a datetime object
    if isinstance(expires, datetime):
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return f"<t:{int(expires.timestamp())}:F> (<t:{int(expires.timestamp())}:R>)"

    # Unexpected type
    return str(expires)



@client.tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id in devs:
        synced = await client.tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} command(s)")
    else:
        await interaction.response.send_message('You must be the owner to use this command!')

_EMPTY_STRUCTURES = {
    "verify_system": {"guilds": []},
}
for _fname, _default in _EMPTY_STRUCTURES.items():
    if not os.path.exists(f"data/{_fname}.json"):
        write_json(_default, _fname)

# ── Populate shared state module ──
state.client = client
state.PREFIX = PREFIX
state.devs = devs
state.IGNORED_USER_IDS = IGNORED_USER_IDS
state.SUB_FILES = SUB_FILES
state.PRIVACY_SET = PRIVACY_SET
state.STATUS_PRIVACY_SET = STATUS_PRIVACY_SET
state.SUPPORTED_FIAT = SUPPORTED_FIAT
state.SYMBOL_TO_ID = SYMBOL_TO_ID
state.SUPPORTED_CHAINS = SUPPORTED_CHAINS
state.COLOR_OK = COLOR_OK
state.COLOR_WARN = COLOR_WARN
state.COLOR_BAD = COLOR_BAD
state.COLOR_INFO = COLOR_INFO
state.CODEBLOCK_CLOSED_RE = CODEBLOCK_CLOSED_RE
state.CODEBLOCK_UNTERMINATED_RE = CODEBLOCK_UNTERMINATED_RE
state.DURATION_RE = DURATION_RE
state.pending_alerts = pending_alerts
state.user_graph_data = user_graph_data
state.dictionary = dictionary
state.char1 = char1

# View / UI classes
state.FlexButton = FlexButton
state.BuyPremium = BuyPremium
state.DaysBetweenButton = DaysBetweenButton
state.myInvite = myInvite
state.Mymodal = Mymodal
state.AuthButton = AuthButton
state.LoginModal = LoginModal
state.ResetButton = ResetButton
state.NumbersButton = NumbersButton
state.VerifyButton = VerifyButton
state.DeleteVerifySystem = DeleteVerifySystem
state.EmailCheck = EmailCheck
state.EmailCode = EmailCode
state.UnbanButton = UnbanButton
state.DefineButton = DefineButton
state.RawCopyButton = RawCopyButton
state.WikipediaButton = WikipediaButton
state.CloneButton = CloneButton
state.rrSelectGames = rrSelectGames
state.rrSelectGender = rrSelectGender
state.rrSelectPing = rrSelectPing
state.rrSelectServer = rrSelectServer
state.Paginator = Paginator
state.mySelect = mySelect
state.CurrencyView = CurrencyView
state.PaginationView = PaginationView
state.PromptModal = PromptModal
state.PromptButtonView = PromptButtonView
state.GeminiView = GeminiView
state.RemoveGeminiView = RemoveGeminiView
state.DeployView = DeployView
state.DropView = DropView
state.GraphView = GraphView
state.FunctionInputModal = FunctionInputModal
state.DeleteFunctionModal = DeleteFunctionModal
state.ZoomModal = ZoomModal
state.UpdateButton = UpdateButton
state.ScamFeedbackView = ScamFeedbackView
state.YoungestView = YoungestView
state.MemberStatsView = MemberStatsView
state.PresencePaginator = PresencePaginator
state.ReactionRoleView = ReactionRoleView
state.BuyPremium2 = BuyPremium2

# Functions
state.read_json = read_json
state.write_json = write_json
state.refresh = refresh
state.is_premium = is_premium
state.format_expires = format_expires
state.load_json = load_json
state.save_json = save_json
state.load_stats = load_stats
state.save_stats = save_stats
state._log_command = _log_command
state.load_autoping_channels = load_autoping_channels
state.save_autoping_channels = save_autoping_channels
state.load_autorole = load_autorole
state.save_autorole = save_autorole
state.remove_autorole = remove_autorole
state.load_privacy_settings = load_privacy_settings
state.save_privacy_settings = save_privacy_settings
state.reload_privacy_sets = reload_privacy_sets
state.load_server_data = load_server_data
state.save_server_data = save_server_data
state.load_gemini_servers = load_gemini_servers
state.save_gemini_servers = save_gemini_servers
state.load_actions = load_actions
state.save_actions = save_actions
state.append_audit_log = append_audit_log
state.read_audit_log = read_audit_log
state.load_audit_config = load_audit_config
state.save_audit_config = save_audit_config
state.get_guild_cfg = get_guild_cfg
state.update_guild_cfg = update_guild_cfg
state.embed_basic = embed_basic
state.admin_or_manage_guild = admin_or_manage_guild
state.normalize_phrase = normalize_phrase
state.extract_domains = extract_domains
state.scan_message_for_scams = scan_message_for_scams
state.try_python_syntax_check = try_python_syntax_check
state.parse_duration_to_timedelta = parse_duration_to_timedelta
state.fmt_discord_time = fmt_discord_time
state._chunk_lines = _chunk_lines
state.build_overview_embed = build_overview_embed
state.is_scam_whitelisted = is_scam_whitelisted
state.fetch_tx_data = fetch_tx_data
state.parse_tx_data = parse_tx_data
state.fetch_word_example = fetch_word_example
state.generate_graph = generate_graph
state.replenish_codes = replenish_codes
state._load_codes_for_tier = _load_codes_for_tier
state._as_txt_file = _as_txt_file
state.remove_subscription = remove_subscription
state.add_subscription = add_subscription
state.build_top_roles_embed = build_top_roles_embed
state.build_age_graph = build_age_graph
state.init_db_pool = init_db_pool
state.load_data = load_data
state.update = update
state.random_color = random_color
state.update_note = update_note

client.run(os.getenv("DISCORD_TOKEN"))
  