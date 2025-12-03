import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Bot
import os
import asyncio
from datetime import datetime, date, timezone, timedelta
import json
import random
import typing
from typing import Optional
from discord.ext.commands import has_permissions
import qrcode
from asyncio import *
from PIL import Image
import requests
from email.message import EmailMessage
import ssl
import smtplib
import math
from discord import ui
from discord.ui import Modal, View, Select, Button, TextInput
import sys
import PyDictionary
from PyDictionary import PyDictionary
import googletrans
from googletrans import Translator
import wikipedia
import aiohttp
from aiohttp import ClientSession
import re 
import time
import matplotlib.pyplot as plt
plt.set_loglevel("critical")
import numpy
import io
from captcha.image import ImageCaptcha                             
from discord.ext import tasks
from typing import Literal
from discord.utils import format_dt
import os, re, json, ast, time, uuid, string
from collections import deque, defaultdict
from typing import Dict, Any, List, Tuple
from typing import Optional, Literal
import matplotlib.pyplot as plt
from io import BytesIO
import httpx
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
email_password = os.getenv("email_password")
email_sender = os.getenv("email_sender")

intents = discord.Intents.default()

intents.members = True                      
intents.message_content = True
intents.presences = True              

                        
                                         

client = commands.Bot(
    command_prefix="/",
    intents=intents
)


pending_alerts = {}

dictionary = PyDictionary()

BACKEND_URL = os.getenv("BACKEND_URL", "https://premiumbottesting.onrender.com")

class PersistentViewBot(commands.Bot):
  def __init__(self):
    intents = discord.Intents().all()
    super().__init__(command_prefix=commands.when_mentioned_or('/'), intents=discord.Intents.all())
    self.http_session = None
  async def setup_hook(self) -> None:
    self.http_session = ClientSession()
    self.add_view(TicketButton())
    self.add_view(DeleteTicketButton())
    self.add_view(VerifyButton())
    self.add_view(UpdateButton())
    self.add_view(rrSelectGames())
    self.add_view(rrSelectGender())
    self.add_view(rrSelectPing())
    self.add_view(rrSelectServer())
    self.add_view(PromptButtonView()) 

  async def close(self):
      await self.http_session.close()
      await super().close()

STATS_FILE = "command_stats.json"
devs = [
    857932717681147954,
    1430719406022983740,
    661033986742550548,
]
IGNORED_USER_IDS = set(devs)                                       


class ReactionRoleView(discord.ui.View):
    def __init__(self, roles, custom_id):
        super().__init__(timeout=None)
        self.add_item(ReactionRoleDropdown(roles, custom_id))

client = PersistentViewBot()

                                                                                            

def check(interaction: discord.Interaction, m):
  return m.author.id == interaction.user.id

                                                                             

class BuyPremium2(View):
  def __init__(self):
    super().__init__(timeout=None)
    button = discord.ui.Button(label='Buy Premium', style=discord.ButtonStyle.url, url='https://discord.gg/Cu8JR7Vsvx')
    self.add_item(button)

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

                                                                                 

devs = [857932717681147954, 953211569150525480, 886238665297264660]

char1 = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','1','2','3','4','5','6','7','8','9','0',]

client.monthly_codes = []
client.yearly_codes = []

client.monthly_user = []
client.yearly_user = []

def read_json(filename):
 with open(f"{filename}.json", "r") as file:
    data = json.load(file)
 return data

def write_json(data, filename):
 with open(f"{filename}.json", "w") as file:
     json.dump(data, file, indent=4)

def refresh():
    monthly_data = read_json("monthcode")
    client.monthly_codes = monthly_data.get("monthlycodes", [])

    yearly_data = read_json("yearlycode")
    client.yearly_codes = yearly_data.get("yearlycodes", [])

                          
    try:
        lifetime_data = read_json("lifetimecode")
    except FileNotFoundError:
        lifetime_data = {"lifetimecodes": []}
        write_json(lifetime_data, "lifetimecode")
    client.lifetime_codes = lifetime_data.get("lifetimecodes", [])

                                                                                  
    monthly_user_data = read_json("monthly_user")
    client.monthly_user = monthly_user_data.get("monthly_users", [])

    yearly_user_data = read_json("yearly_user")
    client.yearly_user = yearly_user_data.get("yearly_users", [])

async def is_premium(discord_id: int):
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{BACKEND_URL}/api/premium/{discord_id}")
            res.raise_for_status()
            data = res.json()
            return data.get("premium", False), data.get("tier"), data.get("expires_at")
    except Exception as e:
        print("Error checking premium:", e)
        return False, None, None

MONTH_DAYS = 30                                              
YEAR_DAYS  = 365
SUB_FILES = {
    "monthly":  "monthly_user.json",
    "yearly":   "yearly_user.json",
    "lifetime": "lifetime_user.json",
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

                                        
                                                                                                                    
def user_is_active(user_id: int):
\
\
\
       
    now = datetime.now(timezone.utc)

    for tier, path in SUB_FILES.items():                                                    
        data = load_json(path)
        for u in data.get("users", []):
            if str(u.get("user_id")) == str(user_id):
                exp_raw = u.get("expires_at")

                                       
                if exp_raw in (None, "", "null"):
                    return True, tier, None

                dt = _coerce_dt(exp_raw)
                if dt and dt > now:
                    return True, tier, dt                    
                else:
                    return False, tier, dt                     

                                
    return False, None, None

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


                                                                                            

client.ticket_configs = {}

@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name="/help me!")
    )
    client.add_view(ScamFeedbackView(action_id="dummy"))

               
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

                                                                        
    monthly_data      = await asyncio.to_thread(read_json, "monthcode")
    yearly_data       = await asyncio.to_thread(read_json, "yearlycode")
    try:
        lifetime_data  = await asyncio.to_thread(read_json, "lifetimecode")
    except FileNotFoundError:
        lifetime_data = {"lifetimecodes": []}
        await asyncio.to_thread(write_json, lifetime_data, "lifetimecode")

    client.monthly_codes  = monthly_data.get("monthlycodes", [])
    client.yearly_codes   = yearly_data.get("yearlycodes", [])
    client.lifetime_codes = lifetime_data.get("lifetimecodes", [])

                                                          
    monthly_user_data = await asyncio.to_thread(read_json, "monthly_user")
    yearly_user_data  = await asyncio.to_thread(read_json, "yearly_user")
    client.monthly_user = monthly_user_data.get("monthly_users", [])
    client.yearly_user  = yearly_user_data.get("yearly_users", [])

                                                                               
    async def generate_codes(filename: str, key: str, existing: list[str], target_min: int = 5):
        if len(existing) >= target_min:
            return
        data = await asyncio.to_thread(read_json, filename)
        need = target_min - len(existing)
        for _ in range(need):
                                 
            code = "-".join("".join(random.choice(char1) for _ in range(4)) for __ in range(4))
            data.setdefault(key, []).append(code)
        await asyncio.to_thread(write_json, data, filename)

    await asyncio.gather(
        generate_codes("monthcode", "monthlycodes", client.monthly_codes),
        generate_codes("yearlycode", "yearlycodes", client.yearly_codes),
        generate_codes("lifetimecode", "lifetimecodes", client.lifetime_codes),                                               
    )

                                                     
    if not prune_expired_subs.is_running():
        prune_expired_subs.start()                                                          
    if not monitor_confirmations.is_running():
        monitor_confirmations.start()

    print("Equinox is here!")

                                           
    data = load_data()
    for template_name, templates in data.items():
        for name, template in templates.items():
            if template.get("roles"):
                custom_id = f"reaction_role_dropdown:{name}"
                view = ReactionRoleView(template['roles'], custom_id)
                client.add_view(view)



def get_guild_giveaway_path(guild_id: int) -> str:
    return f"giveawayFolder/giveaways_{guild_id}.json"

def ensure_guild_json_file(guild_id: int):
    path = get_guild_giveaway_path(guild_id)
    if not os.path.isfile(path):
        with open(path, 'w') as f:
            json.dump({}, f)

def load_guild_giveaways(guild_id: int):
    path = get_guild_giveaway_path(guild_id)
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_guild_giveaways(guild_id: int, data: dict):
    path = get_guild_giveaway_path(guild_id)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

def remove_guild_giveaway(guild_id: int, message_id: int):
    giveaways = load_guild_giveaways(guild_id)
    if str(message_id) in giveaways:
        del giveaways[str(message_id)]
        with open(f'giveawayFolder/giveaways_{guild_id}.json', 'w') as f:
            json.dump(giveaways, f)



class GiveawayView(View):
    def __init__(self, client, giveaway_data):
        super().__init__(timeout=None)
        self.client = client
        self.giveaway_data = giveaway_data
        self.entries = set(giveaway_data["entries"])
        self.end_time = datetime.strptime(giveaway_data["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        self.message = None
        self.host_ids = giveaway_data["hosts"]
        self.role_ids = giveaway_data["roles"]
        self.original_winner = None
        self.previous_winners = set()                                               
        self.winner_message_id = None
        self.giveaway_ended = False
        self.timer_task = None                                    



    async def check_host_permission(self, interaction):
                                                                      
        if interaction.user.id in self.host_ids:
            return True
        
                                                                        
        member = interaction.guild.get_member(interaction.user.id)
        if member:
            for role_id in self.role_ids:
                if discord.utils.get(member.roles, id=role_id):
                    return True
        
        return False

    async def start_timer(self):
                                                                
        try:
            while True:
                current_time = datetime.now(timezone.utc)
                if current_time >= self.end_time:
                    await self.end_giveaway()                              
                    break
                await asyncio.sleep(1)              
        except asyncio.CancelledError:
                                                     
            pass

    async def end_giveaway(self, interaction: Optional[discord.Interaction] = None):
                                                 
        if interaction:
            await interaction.response.defer()
            if not await self.check_host_permission(interaction):
                await interaction.followup.send("You do not have permission to stop this giveaway.", ephemeral=True)
                return

        if self.giveaway_ended:
            if interaction:
                await interaction.followup.send("This giveaway has already been ended or canceled.", ephemeral=True)
            return

        self.giveaway_ended = True
        self.disable_buttons()

        if len(self.entries) > 0:
            self.original_winner = random.choice(list(self.entries))
            self.previous_winners.add(self.original_winner)

            winner = self.client.get_user(self.original_winner)
            if winner:
                embed = discord.Embed(title="Winner Announcement", color=0xffffff)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** {winner.mention}", inline=False)
                embed.add_field(name="<a:snow:1311099641932152903> </giveaway_manage:1370458427100368898>", value=f"", inline=False)

                winner_view = WinnerButtonView(self)
                winner_message = await self.message.channel.send(
                    f"Congratulations {winner.mention}! You won the giveaway!",
                    embed=embed,
                    view=winner_view
                )
                winner_view.message = winner_message
                self.winner_message_id = winner_message.id
            else:                
                await self.message.channel.send("The winner could not be found.")
                embed = discord.Embed(title="Winner Announcement", color=0xffffff)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** N/A", inline=False)
                embed.add_field(name="<a:snow:1311099641932152903> </giveaway_manage:1370458427100368898>", value=f"", inline=False)
        else:
            await self.message.channel.send("No entries were found for the giveaway.")
            embed = discord.Embed(title="Winner Announcement", color=0xffffff)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** N/A", inline=False)
            embed.add_field(name="<a:snow:1311099641932152903> </giveaway_manage:1370458427100368898>", value=f"", inline=False)

        guild_id = self.giveaway_data["guild_id"]
        giveaways = load_guild_giveaways(guild_id)
        giveaways[str(self.giveaway_data["message_id"])]["status"] = "On Going / Winner revealed"
        save_guild_giveaways(guild_id, giveaways)


                                                                        
        embed = self.message.embeds[0]
        embed.set_footer(text="Status: Ended")
        await self.message.edit(embed=embed)


    async def reroll(self, interaction: discord.Interaction):
                                         
        await interaction.response.defer()
        if not await self.check_host_permission(interaction):
            await interaction.followup.send("You do not have permission to reroll the winner.", ephemeral=True)
            return

        current_time = datetime.now(timezone.utc)
        giveaway_end_time = datetime.strptime(self.giveaway_data["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        if current_time < giveaway_end_time:
            await interaction.followup.send(
                "This giveaway has not ended yet. You can only reroll after it ends.",
                ephemeral=True
            )
            return

                                                      
        try:
            if self.winner_message_id:                                            
                prev_message = await interaction.channel.fetch_message(self.winner_message_id)
                if prev_message and prev_message.components:
                                                                 
                    disabled_view = View()
                    for component in prev_message.components[0].children:
                        component.disabled = True
                        disabled_view.add_item(component)
                    await prev_message.edit(view=disabled_view)
        except Exception as e:
            print(f"Error disabling buttons on previous winner embed: {e}")

                                                          
        eligible_entries = [entry for entry in self.entries if entry not in self.previous_winners]

        if not eligible_entries:
            await interaction.followup.send("No eligible entries left for rerolling.", ephemeral=True)
            return

                                                                 
        new_winner_id = random.choice(eligible_entries)
        new_winner = self.client.get_user(new_winner_id)

        if new_winner:
            self.previous_winners.add(new_winner_id)                                     

                                                    
            embed = discord.Embed(title="New Winner", color=0xffffff)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)

                                                                
            winner_view = View()

                           
            reroll_button = Button(label="Reroll", style=discord.ButtonStyle.primary)
            async def reroll_button_callback(interaction: discord.Interaction):
                await self.reroll(interaction)
            reroll_button.callback = reroll_button_callback

                                    
            finalize_button = Button(label="Finalize Winner", style=discord.ButtonStyle.secondary)
            async def finalize_button_callback(interaction: discord.Interaction):
                await self.finalize_winner(interaction)
            finalize_button.callback = finalize_button_callback

                                     
            winner_view.add_item(reroll_button)
            winner_view.add_item(finalize_button)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** {new_winner.mention}", inline=False)

                                              
            winner_message = await interaction.followup.send(
                f"Congratulations {new_winner.mention}! You are the new winner of the giveaway!",
                embed=embed,
                view=winner_view
            )
            self.winner_message_id = winner_message.id                            
        else:
            await interaction.followup.send("The new winner could not be found.", ephemeral=True)

    async def finalize_winner(self, interaction: discord.Interaction):
        messageExist = True
                                                                             
        await interaction.response.defer()

        if not await self.check_host_permission(interaction):
            await interaction.followup.send("You do not have permission to finalize the winner.", ephemeral=True)
            return
        
        current_time = datetime.now(timezone.utc)
        giveaway_end_time = datetime.strptime(self.giveaway_data["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        if current_time < giveaway_end_time:
            await interaction.followup.send(
                "This giveaway has not ended yet. You can only finalize after it ends.",
                ephemeral=True
            )
            return

                                                                       
        if not self.message:
            try:
                self.message = await interaction.channel.fetch_message(self.giveaway_data["message_id"])
            except Exception:
                messageExist = False
                pass

                                           
        if self.winner_message_id:
            try:
                winner_message = await interaction.channel.fetch_message(self.winner_message_id)
                await winner_message.edit(view=None)
            except Exception:
                pass                                         

                                                               
        guild_id = interaction.guild_id if interaction.guild else self.giveaway_data.get("guild_id")
        remove_guild_giveaway(guild_id, self.giveaway_data["message_id"])



        await interaction.followup.send("Winner has been finalized.", ephemeral=True)

        if (messageExist):
          embed = self.message.embeds[0]
          embed.set_footer(text="Status: Finalized")
          await self.message.edit(embed=embed)
        




    async def enter(self, interaction: discord.Interaction):
                                                             
        await interaction.response.defer()
        user_id = interaction.user.id
        guild_id = interaction.guild.id
        message_id = str(self.message.id)

        giveaways = load_guild_giveaways(guild_id)

        if user_id in self.entries:
            self.entries.remove(user_id)
            self.giveaway_data["entries"] = list(self.entries)

                         
            giveaways[message_id]["entries"] = list(self.entries)
            save_guild_giveaways(guild_id, giveaways)

            await asyncio.sleep(3)

            await interaction.followup.send("You've been successfully removed from this giveaway!", ephemeral=True)
            return

        self.entries.add(user_id)
        self.giveaway_data["entries"] = list(self.entries)

                     
        giveaways[message_id]["entries"] = list(self.entries)
        save_guild_giveaways(guild_id, giveaways)

        await asyncio.sleep(3)

        await interaction.followup.send("You've successfully entered the giveaway!", ephemeral=True)

    async def show_entries(self, interaction: discord.Interaction):
      await interaction.response.defer()
      embed = discord.Embed(title="Number of entries:", color=0xffffff)
      embed.add_field(name="", value=f"<a:snow:1311099641932152903> {str(len(self.entries))} user(s)", inline=False)
      await interaction.followup.send(embed=embed, ephemeral=True)
       


    async def cancel_giveaway(self, interaction: discord.Interaction):
                                                   
        if not await self.check_host_permission(interaction):
            await interaction.response.send_message("You do not have permission to cancel this giveaway.", ephemeral=True)
            return

        if self.giveaway_ended:
            await interaction.response.send_message("This giveaway has already been ended or canceled.", ephemeral=True)
            return

                                    
        self.giveaway_ended = True

                                          
        if self.timer_task is not None and not self.timer_task.done():
            self.timer_task.cancel()
            self.timer_task = None


                             
        self.disable_buttons()

                                   
        await interaction.response.send_message("The giveaway has been successfully canceled.")
        
                                                                     
        embed = self.message.embeds[0]
        embed.set_footer(text=f"Status: Canceled")
        await self.message.edit(embed=embed)

                                                
        remove_guild_giveaway(interaction.guild_id, self.message.id)


    def disable_buttons(self):
                                              
        for item in self.children:
            item.disabled = True

                                                     
        asyncio.run_coroutine_threadsafe(self.message.edit(view=self), self.client.loop)

    def disable_buttons(self):
                                              
        for item in self.children:
            item.disabled = True

                                                     
        asyncio.run_coroutine_threadsafe(self.message.edit(view=self), self.client.loop)

    async def stop_button_callback(self, interaction: discord.Interaction):
                                                    
        if not await self.check_host_permission(interaction):
            await interaction.response.send_message("You do not have permission to stop this giveaway.", ephemeral=True)
            return

        await self.end_giveaway(interaction)                              

    async def cancel_button_callback(self, interaction: discord.Interaction):
                                                      
        await self.cancel_giveaway(interaction)

    async def initialize_giveaway(self):
                                                          
        self.timer_task = asyncio.create_task(self.start_timer())                        

class WinnerButtonView(View):
    def __init__(self, giveaway_view: GiveawayView, timeout: float = 86400):                    
        super().__init__(timeout=timeout)
        self.giveaway_view = giveaway_view
        self.message = None                                  

                       
        reroll_button = Button(label="Reroll", style=discord.ButtonStyle.primary)
        async def reroll_button_callback(interaction: discord.Interaction):
            await self.giveaway_view.reroll(interaction)
        reroll_button.callback = reroll_button_callback
        self.add_item(reroll_button)

                                
        finalize_button = Button(label="Finalize Winner", style=discord.ButtonStyle.secondary)
        async def finalize_button_callback(interaction: discord.Interaction):
            await self.giveaway_view.finalize_winner(interaction)
        finalize_button.callback = finalize_button_callback
        self.add_item(finalize_button)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)


@client.tree.command(name="giveaway_manage", description="Reroll or finalize a giveaway by message ID.")
@app_commands.choices(action=[
    app_commands.Choice(name="Reroll", value="reroll"),
    app_commands.Choice(name="Finalize", value="finalize"),
])
@app_commands.describe(message_id="The message ID of the giveaway")
async def giveaway_manage(
    interaction: discord.Interaction,
    message_id: str,
    action: app_commands.Choice[str]
):
    guild_id = interaction.guild.id
    giveaways = load_guild_giveaways(guild_id)
    giveaway_data = giveaways.get(str(message_id))

    if not giveaway_data:
        return await interaction.response.send_message(
            embed=discord.Embed(title="No giveaway found with that message ID.", color=0xffffff),
            ephemeral=True
        )

    user_id = interaction.user.id
    user_roles = [role.id for role in interaction.user.roles]

    is_host = user_id in giveaway_data["hosts"]
    has_host_role = any(role_id in user_roles for role_id in giveaway_data["roles"])

    if not (is_host or has_host_role):
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="Permission Denied",
                description="You are not listed as a host or in an eligible host role for this giveaway.",
                color=0xffffff
            ),
            ephemeral=True
        )

    view = GiveawayView(client, giveaway_data)
    if action.value == "reroll":
        await view.reroll(interaction)
    elif action.value == "finalize":
        await view.finalize_winner(interaction)





@client.tree.command(name='giveaway', description='Create a giveaway')
@app_commands.describe(
    duration="Giveaway's duration (e.g., 1s, 2m, 3h, 4d)",
    prize="Giveaway's prize",
    hosts="Comma-separated list of host IDs (userID, roleID)"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def giveaway(interaction: discord.Interaction, duration: str, prize: str, hosts: str = None):
    await interaction.response.defer()

    guild_id = interaction.guild.id
    owner_id = interaction.guild.owner_id

    ensure_guild_json_file(guild_id)
    giveaways = load_guild_giveaways(guild_id)

                                             
    is_active, is_premium, expires_at = user_is_active(interaction.user.id)
    active_giveaways = [g for g in giveaways.values() if g.get("message_id")]

    if not is_premium and len(active_giveaways) >= 3:
        embed = discord.Embed(
            title="You are being restricted",
            description="Normal servers can only host **3 active giveaways**.\n"
                        "The server owner is **not a premium user**.\n\n"
                        "Consider finalizing an existing \ngiveaway using </giveaway_manage:1370458427100368898>\n"
                        "or upgrade to premium.",
            color=0xffffff
        )

        view = BuyPremium()
        for index, g in enumerate(active_giveaways, start=1):
            embed.add_field(
                name=f"Giveaway {index}: {g['message_id']}",
                value=f"",
                inline=False
            )
            button = Button(
                label=f"{index}",
                style=discord.ButtonStyle.link,
                url=f"https://discord.com/channels/{guild_id}/{interaction.channel.id}/{g['message_id']}"
            )
            view.add_item(button)

        return await interaction.followup.send(embed=embed, view=view, ephemeral=True)


                    
    duration_mapping = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    total_seconds = 0
    parts = duration.split()
    for part in parts:
        if len(part) < 2 or part[-1] not in duration_mapping:
            return await interaction.followup.send("Invalid duration format. Use s, m, h, or d.", ephemeral=True)
        try:
            value = int(part[:-1])
            if value < 1:
                return await interaction.followup.send("Duration values must be positive integers.", ephemeral=True)
            total_seconds += value * duration_mapping[part[-1]]
        except ValueError:
            return await interaction.followup.send("Invalid duration value. Use something like `1h 30m`.", ephemeral=True)

    if total_seconds >= 604800:
        return await interaction.followup.send("Duration must be less than `7` days.", ephemeral=True)
    elif total_seconds < 30:
        return await interaction.followup.send("Duration must be more than or equal to `30` seconds.", ephemeral=True)

    end_time = datetime.now(timezone.utc) + timedelta(seconds=total_seconds)

                    
    host_ids = [interaction.user.id]
    role_ids = []
    if hosts:
        input_ids = [host.strip() for host in hosts.split(",")]
        for host_id in input_ids:
            try:
                id_value = int(host_id)
                if interaction.guild.get_role(id_value):
                    role_ids.append(id_value)
                elif interaction.guild.get_member(id_value):
                    host_ids.append(id_value)
                else:
                    return await interaction.followup.send(f"Invalid ID: {host_id}", ephemeral=True)
            except ValueError:
                return await interaction.followup.send(f"Invalid ID format: {host_id}", ephemeral=True)

                          
    giveaway_data = {
        "prize": prize,
        "hosts": host_ids,
        "roles": role_ids,
        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "entries": [],
        "message_id": None,
        "status": "On Going / Winner not revealed",
        "guild_id": guild_id
    }


    embed = discord.Embed(title=prize, color=0x2b2d31)
    embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Ends in:** <t:{int(end_time.timestamp())}:R>", inline=False)
    embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Ends on:** <t:{int(end_time.timestamp())}:F>", inline=False)

                   
    host_mentions = [interaction.user.mention]
    for host_id in host_ids[1:]:
        user = interaction.guild.get_member(host_id)
        if user:
            host_mentions.append(user.mention)
    for role_id in role_ids:
        role = interaction.guild.get_role(role_id)
        if role:
            host_mentions.append(role.mention)

    embed.add_field(name="", value="<a:snow:1311099641932152903> **Host(s):** " + ", ".join(host_mentions), inline=False)
    embed.set_footer(text="Status: Ongoing")

    message = await interaction.followup.send(embed=embed)

    giveaway_data["message_id"] = message.id
    giveaways[str(message.id)] = giveaway_data
    save_guild_giveaways(guild_id, giveaways)

    view = GiveawayView(client, giveaway_data)
    view.message = message

    enter_button = Button(label="Enter Giveaway", style=discord.ButtonStyle.success)
    enter_button.callback = view.enter

    entries_button = Button(label="Entries", style=discord.ButtonStyle.blurple)
    entries_button.callback = view.show_entries    

    stop_button = Button(label="Get Winner", style=discord.ButtonStyle.secondary)
    stop_button.callback = view.stop_button_callback

    cancel_button = Button(label="Cancel Giveaway", style=discord.ButtonStyle.danger)
    cancel_button.callback = view.cancel_button_callback

    view.add_item(enter_button)
    view.add_item(entries_button) 
    view.add_item(stop_button)
    view.add_item(cancel_button)

    await message.edit(view=view)
    await view.start_timer()

@client.tree.command(name="giveaway_console", description="View all giveaways in this server.")
async def giveaway_console(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    guild_id = interaction.guild.id
    giveaways = load_guild_giveaways(guild_id)

    if not giveaways:
        return await interaction.followup.send(
            embed=discord.Embed(title="No giveaways found in this server.", color=0xffffff),
            ephemeral=True
        )

    giveaway_list = list(giveaways.values())
    giveaway_list.sort(key=lambda g: g["end_time"])                    

    def format_embed(start_idx: int):
        embed = discord.Embed(
            title=f"Giveaway Console (Page {start_idx // 3 + 1})",
            color=0x2b2d31
        )
        for i in range(start_idx, min(start_idx + 3, len(giveaway_list))):
            g = giveaway_list[i]
            prize = g["prize"]
            message_id = g["message_id"]
            end_time = datetime.strptime(g["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            now = datetime.now(datetime.timezone.utc)
            time_left = f"<t:{int(end_time.timestamp())}:R>"
            ends_on = f"<t:{int(end_time.timestamp())}:F>"

                                                          
            now = datetime.now(datetime.timezone.utc)
            end_time = datetime.strptime(g["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)

                                                             
            stored_status = g.get("status", "On Going / Winner not revealed")

            if now >= end_time:
                status = "Ended"
            elif stored_status == "On Going / Winner revealed":
                status = "Ongoing | Winner revealed"
            else:
                status = "Ongoing | Winner not revealed"

            msg_url = f"https://discord.com/channels/{guild_id}/{interaction.channel.id}/{message_id}"

                                 
            host_mentions = []
            for uid in g["hosts"]:
                user = interaction.guild.get_member(uid)
                if user:
                    host_mentions.append(user.mention)
            for rid in g["roles"]:
                role = interaction.guild.get_role(rid)
                if role:
                    host_mentions.append(role.mention)
            if not host_mentions:
                host_mentions.append("*None*")

            embed.add_field(
                name=f"<a:snow:1311099641932152903> {prize}",
                value=(
                    f"**Ends In:** {time_left}\n"
                    f"**Ends On:** {ends_on}\n"
                    f"**Message ID:** `{message_id}`\n"
                    f"[Jump to Message]({msg_url})\n"
                    f"**Status:** {status}\n"
                    f"**Hosts:** {', '.join(host_mentions)}"
                ),
                inline=False
            )
        embed.set_footer(text=f"Showing {start_idx + 1} - {min(start_idx + 3, len(giveaway_list))} of {len(giveaway_list)} giveaways")
        return embed


    class GiveawayConsoleView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.index = 0
            self.message = None

        async def update(self, interaction: discord.Interaction):
            embed = format_embed(self.index)
            await interaction.response.edit_message(embed=embed, view=self)

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
        async def previous(self, interaction: discord.Interaction, button: Button):
            if self.index >= 3:
                self.index -= 3
                await self.update(interaction)

        @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
        async def next(self, interaction: discord.Interaction, button: Button):
            if self.index + 3 < len(giveaway_list):
                self.index += 3
                await self.update(interaction)

        async def on_timeout(self):
            for item in self.children:
                item.disabled = True
            if self.message:
                await self.message.edit(view=self)

    view = GiveawayConsoleView()
    embed = format_embed(0)
    msg = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    view.message = msg

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

@client.event
async def on_member_join(member):
  if member.guild.id == 1243501449879752775:
    if not member.bot:
      guild = member.guild
      role =  guild.get_role(1244973833115533373)
      await member.add_roles(role)
      channel = guild.get_channel(1244983181006868480)
      msg = await channel.send(member.mention)
      await msg.delete()
  else:
    guild = member.guild
    channel_ids = load_autoping_channels(guild.id)
    
    for cid in channel_ids:
        channel = guild.get_channel(cid)
        if channel and channel.permissions_for(guild.me).send_messages:
            try:
                msg = await channel.send(f"{member.mention}")
                await msg.delete()
            except discord.Forbidden:
                continue
            
                                
    autorole_id = load_autorole(guild.id)
    if autorole_id:
        role = guild.get_role(autorole_id)
        if role and role < guild.me.top_role:
            try:
                await member.add_roles(role, reason="Auto-role on join")
            except discord.Forbidden:
                pass
     
@client.tree.command(name="autoping_whitelist", description="Manage auto-ping channels for new members.")
@app_commands.choices(action=[
    app_commands.Choice(name="Add", value="add"),
    app_commands.Choice(name="Remove", value="remove"),
    app_commands.Choice(name="View", value="view")
])
@app_commands.describe(action="Add, remove, or view whitelist", channel="The channel to modify")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_messages=True)
async def autoping_whitelist(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    channel: discord.TextChannel = None
):
    guild_id = interaction.guild.id
    current_channels = load_autoping_channels(guild_id)

    if action.value == "add":
        if not channel:
            return await interaction.response.send_message("You must specify a channel to add.", ephemeral=True)
        if channel.id in current_channels:
            return await interaction.response.send_message("Channel is already in the whitelist.", ephemeral=True)
        current_channels.append(channel.id)
        save_autoping_channels(guild_id, current_channels)
        return await interaction.response.send_message(f"✅ {channel.mention} added to the auto-ping whitelist.", ephemeral=True)

    elif action.value == "remove":
        if not channel:
            return await interaction.response.send_message("You must specify a channel to remove.", ephemeral=True)
        if channel.id not in current_channels:
            return await interaction.response.send_message("Channel is not in the whitelist.", ephemeral=True)
        current_channels.remove(channel.id)
        save_autoping_channels(guild_id, current_channels)
        return await interaction.response.send_message(f"❌ {channel.mention} removed from the auto-ping whitelist.", ephemeral=True)

    elif action.value == "view":
        if not current_channels:
            return await interaction.response.send_message("No channels are currently whitelisted for auto-ping.", ephemeral=True)
        channel_list = [f"<#{cid}>" for cid in current_channels]
        return await interaction.response.send_message(f"📋 Auto-ping channels:\n" + "\n".join(channel_list), ephemeral=True)

@client.tree.command(name="autorole", description="Manage the auto-role for new members.")
@app_commands.describe(action="Choose add, remove, or view", role="The role to assign")
@app_commands.choices(action=[
    app_commands.Choice(name="Add", value="add"),
    app_commands.Choice(name="Remove", value="remove"),
    app_commands.Choice(name="Console", value="console")
])
@app_commands.checks.has_permissions(manage_roles=True)
async def autorole(interaction: discord.Interaction, action: app_commands.Choice[str], role: discord.Role = None):
    guild = interaction.guild
    autorole_id = load_autorole(guild.id)

    if action.value == "add":
        if not role:
            return await interaction.response.send_message("You must specify a role to add.", ephemeral=True)

        if autorole_id:
            return await interaction.response.send_message("Auto-role already set. Remove it first to change.", ephemeral=True)

                                      
        if interaction.user.id != guild.owner_id:
            if role >= interaction.user.top_role:
                return await interaction.response.send_message("⚠️ You can't assign a role higher than or equal to your top role.", ephemeral=True)

        bot_member = guild.get_member(client.user.id)
        if not bot_member or role >= bot_member.top_role:
            return await interaction.response.send_message("⚠️ I can't assign that role because it’s higher than my top role.", ephemeral=True)

        save_autorole(guild.id, role.id)
        await interaction.response.send_message(f"✅ Auto-role set to {role.mention}.", ephemeral=True)

    elif action.value == "remove":
        if not autorole_id:
            return await interaction.response.send_message("No auto-role is currently set.", ephemeral=True)
        remove_autorole(guild.id)
        await interaction.response.send_message("❌ Auto-role removed.", ephemeral=True)

    elif action.value == "console":
        if not autorole_id:
            return await interaction.response.send_message("No auto-role is currently set.", ephemeral=True)
        role = guild.get_role(autorole_id)
        if not role:
            return await interaction.response.send_message("Stored role ID is invalid or deleted.", ephemeral=True)
        await interaction.response.send_message(f"📌 Current auto-role is {role.mention}", ephemeral=True)

@client.event
async def on_member_remove(member):
  if member.guild.id == 1243501449879752775:
    if not member.bot:
      guild = member.guild
      channel = guild.get_channel(1245008595066814474)
      await channel.send(embed=discord.Embed(title=f"Bye {member} 💀", description=f"> You have been here since: {member.joined_at.strftime('%A, %B %d %Y')}\n> {guild} now has {str(guild.member_count)} member(s)", color=0xffffff))

@client.event
async def on_app_command_completion(
    interaction: discord.Interaction,
    command: discord.app_commands.Command
):
    if interaction.user and not interaction.user.bot:
        _log_command(interaction.user.id, command.qualified_name)


PREFIX = "/"

@client.event
async def on_message(message):
  await client.process_commands(message)
  if client.user.mention in message.content.split():
    embed = discord.Embed(title=f"Equinox 🤍", description=f"I operate with slash commands, type **/** to see all available commands.", color = 0xffffff)
    await message.reply(embed=embed)
  if message.author.client or not message.guild:
      return

  guild_id = str(message.guild.id)
  data = load_server_data(guild_id)
  if not data or data.get("status") != "enabled":
      return

  if str(message.channel.id) in data.get("blacklisted_channels", []):
      return

  user_id = str(message.author.id)
  data["users"][user_id] = data["users"].get(user_id, 0) + 1
  save_server_data(guild_id, data)

                    
  if message.author.bot:
      return

                          
  if message.content.startswith(PREFIX):
      cmd_name = message.content[len(PREFIX):].split()[0].lower()
      _log_command(message.author.id, cmd_name)

                                        
  await client.process_commands(message)
  
@client.event
async def on_guild_join(guild):
  channel = client.get_channel(1242633669890277456)
  embed=discord.Embed(title=f"{client.user} was invited to a new guild!", description=f"```js\nGuild Name: {guild}\nGuild Membercount: {guild.member_count}\nClient Guilds: {len(client.guilds)}\nClient Users: {len(set(client.get_all_members()))}\n```", color =0xffffff)
  embed.set_thumbnail(url=guild.icon)
  msg = await channel.send(embed=embed)
                                                                                                   


                                                                       

@client.tree.command(name="roll", description="Gacha game")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.describe(item="The item you want to roll with")
@app_commands.choices(item=[
  discord.app_commands.Choice(name='Fortune Drink', value=1),
  discord.app_commands.Choice(name="Witch's Potion", value=2),
  discord.app_commands.Choice(name='Divine Fluid', value=3),
  discord.app_commands.Choice(name='Angel Dust', value=4),
  discord.app_commands.Choice(name='Me When Im Lucky', value=5),
  discord.app_commands.Choice(name='Touch of Divinity', value=6),
  discord.app_commands.Choice(name='Trio Charm', value=7),
])
async def roll(interaction: discord.Interaction, item: Optional[discord.app_commands.Choice[int]]):
  await interaction.response.defer()
  refresh()
  with open("userinventory.json") as f:
    users = json.load(f)
  userid_list = []
  for user in users["user"]:
    userid_list.append(user["userid"])
  if interaction.user.id not in userid_list:
    def add_json(new_data, filename='userinventory.json'):
      with open(filename,'r+') as file:
          file_data = json.load(file)
          file_data["user"].append(new_data)
          file.seek(0)
          json.dump(file_data, file, indent = 2)

    y = {
      "userid": interaction.user.id,
      "inventory": [
        {}
      ],
      "roll": 0
    }
    add_json(y)
  chances = []
  rarity_name = ["Common|(1/2)", "Uncommon|(1/3)", "Rare|(1/4)", "Epic|(1/10)", "Legendary|(1/100)", "Divine|(1/500)", "Myth in the Making|(1/1,000)", "Samantha|(1/10,000)", "Paully|(1/10,000)", "Tommy|(1/10,000)"]
  rarity_name_only = []
  for i in range(len(rarity_name)):
    rarity_name_only_split = rarity_name[i].split("|")
    rarity_name_only.append(rarity_name_only_split[0])
  rarity_probability = [1/2, 1/3, 1/4, 1/10, 1/100, 1/500, 1/1000, 1/10000, 1/10000, 1/10000]
  rarity_priority = 0
  probability = 1
  time = 5
  luck = 1
  refresh()
  is_active, is_premium, expires_at = user_is_active(interaction.user.id)
  if is_premium:
    time = random.randint(1,2)
    luck = 2
  else: 
    time = 5
    luck = 1
  luck_boost_index = []
  able_to_roll = False
  if item == None:
    rarity_priority = [0] 
    probability = 1
    able_to_roll = True
  elif item != None:
    roll_item = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]
    user_inventory_item = []
    with open("userinventory.json") as f:
      users = json.load(f)
    for user in users["user"]:
      if user["userid"] == interaction.user.id:
        for key in user["inventory"]:
          for inventory_roll_name in key:
            if inventory_roll_name in roll_item:
              user_inventory_item.append(inventory_roll_name)
    if item.name in user_inventory_item:
      def add_json(new_data, filename='userinventory.json'):
        with open(filename,'r+') as file:
            file_data = json.load(file)
            for users in file_data["user"]:
              if users["userid"] == interaction.user.id:
                for key in users["inventory"]:
                  return key[new_data]
            file.seek(0)
            json.dump(file_data, file, indent = 2)
      y = item.name
      if add_json(y) == 0:
        able_to_roll = False
      else:
        able_to_roll = True
        with open('userinventory.json', 'r') as f:
          json_data = json.load(f)

        index = 0
        for i in range(len(json_data['user'])):
          if json_data['user'][i]["userid"] == interaction.user.id:
            index = i 

        json_data['user'][index]['inventory'][0][item.name] -= 1

        with open('userinventory.json', 'w') as f:
          json.dump(json_data, f, indent=2)

        if item.name == "Fortune Drink":
          rarity_priority = [1]
          probability = 2
          able_to_roll = True
          luck_boost_index = [0,1]
        elif item.name == "Witch's Potion":
          rarity_priority = [2]
          probability = 3
          able_to_roll = True
          luck_boost_index = [1,2]
        elif item.name == "Divine Fluid":
          rarity_priority = [3]
          probability = 5
          able_to_roll = True
          luck_boost_index = [2,3]
        elif item.name == "Angel Dust":
          rarity_priority = [4]
          probability = 10
          able_to_roll = True
          luck_boost_index = [3,4]
        elif item.name == "Me When Im Lucky":
          rarity_priority = [5]
          probability = 50
          able_to_roll = True
          luck_boost_index = [4,5]
        elif item.name == "Touch of Divinity":
          rarity_priority = [6]
          probability = 100
          able_to_roll = True
          luck_boost_index = [4,5,6]
        elif item.name == "Trio Charm":
            rarity_priority = [7, 8, 9]
            probability = 500
            able_to_roll = True
            luck_boost_index = [7, 8, 9]
          
    else:
      able_to_roll = False
      
  for i in range(len(rarity_name)):
      if i in luck_boost_index:
          if i in rarity_priority:
                                                                                     
              for j in range(math.ceil(int(10000 * probability * luck / 2))):
                  chances.append(rarity_name[i])
          else:
                                                                                   
              for j in range(math.ceil(int(10000 * probability * luck / 1.5))):
                  chances.append(rarity_name[i])
      else:
                                                                                   
          for j in range(math.ceil(int(10000 * rarity_probability[i] * probability * luck))):
              chances.append(rarity_name[i])
  if able_to_roll == True:
    rolled = random.choice(chances)
    name = rolled.split("|")
    rolle_name = name[0]
    embed=discord.Embed(title="Rolling...", color = 0xffffff)
    roll_name_gif_name = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
    roll_name_gif = [
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXN2ZmhsdDE5ajFpamY4YmJ4cnBrM2F1OGczM3ZmODl2N3VmcGhtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dfAXMYZfSmUjYttjqM/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXE2ZHcxd3EwdDFwOGV6M3JxYmJwbzRyMGVhMjl6Ynl2d2hkcmplMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5EG56vzNYvfgJWldgS/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDNndGxyMXFsY3EzZ3djNWJrMHgwZ204aWE2NTA3eGdiNXBsd2l2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9f3OzkeQ6h0tbyKlTr/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXFkbm9wNmRkOXp4c2E1eTFiZ2FqZnZ1aHIxMjNhZnFqd2swNDA2OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/smZYhZ2Bwz8mPCwDPl/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXlza3gxYno2Z2I2NGNrdnNyMDlneGQwdmZicWxudGVzZmk3cTQ4NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mGl6JhTtCc0ukOugQ5/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3UxdWZrbDVvc281N2swc202cGR6Zmp4MGUyNmhuYjk0NWhvdXYyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cbhVQuTa5BFS5RlHFG/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDAxcm10MThzajBwbGYwOGhxMWdzZDYyazJ6OHg0dm05bWNpYW83NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FPjwcGYUkDO3kok4PP/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTRmYXA4YWl3NHdwY3k1ZGNrYjh2bzZxY2ZhZzY3eXp4a2p3eHoybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gsp2q6vt6KPZeyJgQd/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGNoa3FmYnNxc3M4Nm90ZTF0cDg4NTFpMjU0aWdndjN4ZXN2cHJzZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Xpb7aXuOuormG3MfnL/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ptYXg5Ymc2NHRuZmkzdDQ3YTJoN3JrZ3RiZXczMXdyd2tiZjRjbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jbsoD38dcXoEmjfNQQ/giphy.gif"
      ]
    roll_gif_url = ""
    roll_index = 0
    for i in range(len(roll_name_gif_name)):
      if rolle_name == roll_name_gif_name[i]:
        roll_index = i
        roll_gif_url = roll_name_gif[i]
    embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWJjMml0Y3B5dmsydmVkZGtmNHl6cTZ3OG1vczQ5OHB1aGZsdXNpZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eFgDbfks97Mq906D3A/giphy.gif")
    await interaction.followup.send(embed=embed)
    name = rolled.split("|")
    if roll_index > 3:
      e=discord.Embed(title="Rolling...???", color = 0xffffff)
      e.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW5yYjEwaGl2bzZ3cnNidDJtMnFscmkyNXY5MjVpZDZ4dXZpMTNkeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FJM4c4RYkb72qvAcBt/giphy.gif")
      await sleep(3)
      await interaction.edit_original_response(embed=e)
    if item != None:
      potion = item.name
    else:
      potion = "None"
    mbed=discord.Embed(title="You Rolled:", description = f"**{rolle_name}** with the probability of **{name[1]}**\nItem used: **{potion}**", color=0xffffff)
    if is_premium:
      mbed.add_field(name="Premium Perk:", value="**x2 Luck**")

    mbed.set_image(url=roll_gif_url)
    mbed.set_footer(text=f"Rolled by {interaction.user}", icon_url=interaction.user.avatar)
    await sleep(time)
    await interaction.edit_original_response(embed=mbed)
    with open(f'userinventory.json', 'r') as f:
      user_data = json.load(f)

    for user_data_index in range(len(user_data['user'])):
      if user_data['user'][user_data_index]['userid'] == interaction.user.id:
        user_data['user'][user_data_index]['roll'] += 1

    with open(f'userinventory.json', 'w') as f:
      json.dump(user_data, f, indent=2)      
    rolle_name = name[0]
    user_inventory_item = []
    with open("userinventory.json") as f:
      users = json.load(f)
    for user in users["user"]:
      if user["userid"] == interaction.user.id:
        for key in user["inventory"]:
          for inventory_roll_name in key:
            user_inventory_item.append(inventory_roll_name)
    if rolle_name not in user_inventory_item:
      def add_json(new_data, filename='userinventory.json'):
        with open(filename,'r+') as file:
            file_data = json.load(file)
            for users in file_data["user"]:
              if users["userid"] == interaction.user.id:
                for key in users["inventory"]:
                  key[new_data] = 1
            file.seek(0)
            json.dump(file_data, file, indent = 2)
      y = rolle_name
      add_json(y)
    else:
      def add_json(new_data, filename='userinventory.json'):
        with open(filename,'r+') as file:
            file_data = json.load(file)
            for users in file_data["user"]:
              if users["userid"] == interaction.user.id:
                for key in users["inventory"]:
                  key[new_data] += 1
            file.seek(0)
            json.dump(file_data, file, indent = 2)
      y = rolle_name
      add_json(y)
  else:
    embed=discord.Embed(title="Error in the rolling...", color=0xffffff)
    embed.add_field(name=f"{item.name}", value=f"> Missing: {item.name}", inline=False)
    await interaction.followup.send(embed=embed)

class FlexButton(discord.ui.View):
  def __init__(self, authorID, best_roll, best_item, all_roll, all_item, member, best_roll_gif, rarity):
    self.authorID = authorID
    self.best_roll = best_roll
    self.best_item = best_item
    self.all_roll = all_roll
    self.all_item = all_item
    self.member = member
    self.best_roll_gif = best_roll_gif
    self.rarity = rarity
    super().__init__(timeout=60)
  @discord.ui.button(label="Best Roll", style=discord.ButtonStyle.green)
  async def best_roll_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer(ephemeral=True)
      embed=discord.Embed(title=f"{self.member.name}'s Best Roll:", description=f"```{self.best_roll} with the probability of {self.rarity}```", color=0xffffff)
      embed.set_image(url=self.best_roll_gif)
      msg = await interaction.followup.send(embed=embed)
      await sleep(15)
      await msg.delete()
    else:
      await interaction.response.defer()

  @discord.ui.button(label="Best Item", style=discord.ButtonStyle.green)
  async def best_item_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      if self.best_item != None:
        await interaction.response.defer(ephemeral=True)
        embed=discord.Embed(title=f"{self.member.name}'s Best Crafted Item:", description=f"```{self.best_item}```", color=0xffffff)
        msg = await interaction.followup.send(embed=embed)
        await sleep(15)
        await msg.delete()
      else:
        await interaction.response.defer()
    else:
      await interaction.response.defer()

  @discord.ui.button(label="Acquired Roll", style=discord.ButtonStyle.green)
  async def acquired_roll_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer(ephemeral=True)
      embed=discord.Embed(title=f"All {self.member.name}'s Acquired Roll(s):", description=f"```{self.all_roll}```", color=0xffffff)
      msg =await interaction.followup.send(embed=embed)
      await sleep(15)
      await msg.delete()
    else:
      await interaction.response.defer()

  @discord.ui.button(label="Acquired Item", style=discord.ButtonStyle.green)
  async def acquired_item_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      if len(self.all_item) != 0:
        await interaction.response.defer()
        embed=discord.Embed(title=f"All {self.member.name}'s Acquired Item(s):", description=f"```{self.all_item}```", color=0xffffff)
        msg = await interaction.followup.send(embed=embed)
        await sleep(15)
        await msg.delete()
      else:
        await interaction.response.defer()
    else:
      await interaction.response.defer()

  async def on_timeout(self) -> None:
    best_roll_button_disable = discord.utils.get(self.children, label="Best Roll")
    best_roll_button_disable.disabled = True
    best_item_button_disable = discord.utils.get(self.children, label="Best Item")
    best_item_button_disable.disabled = True
    acquired_roll_button_disable = discord.utils.get(self.children, label="Acquired Roll")
    acquired_roll_button_disable.disabled = True
    acquired_item_button_disable = discord.utils.get(self.children, label="Acquired Item")
    acquired_item_button_disable.disabled = True
    await self.message.edit(view=self)

@client.tree.command(name="flex", description="Show a member's gacha stats")
@app_commands.checks.cooldown(1, 2, key=lambda i: (i.user.id))
async def flex(interaction: discord.Interaction, member: Optional[discord.Member]):
  await interaction.response.defer(ephemeral=True)
  msg = await interaction.followup.send("Retrieving your data please wait... <a:loading_symbol:1295113412564615249>")
  if member == None:
    member = interaction.user
  with open(f'userinventory.json', 'r') as f:
    user_data = json.load(f)

  userid = []

  for user_data_index in range(len(user_data['user'])):
    userid.append(user_data['user'][user_data_index]['userid'])

  if member.id not in userid:
    await msg.delete()
    await interaction.channel.send(embed=discord.Embed(title=f"{member.name} has no items to flex.", description="This user has no items\nIf this is you, you can start collecting items by running /roll", color = 0xffffff))
  else:
    roll_amount = 0
    best_roll = None
    best_item = None
    
    roll_name_gif_name = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
    roll_name_gif = [
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXN2ZmhsdDE5ajFpamY4YmJ4cnBrM2F1OGczM3ZmODl2N3VmcGhtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dfAXMYZfSmUjYttjqM/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXE2ZHcxd3EwdDFwOGV6M3JxYmJwbzRyMGVhMjl6Ynl2d2hkcmplMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5EG56vzNYvfgJWldgS/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDNndGxyMXFsY3EzZ3djNWJrMHgwZ204aWE2NTA3eGdiNXBsd2l2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9f3OzkeQ6h0tbyKlTr/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXFkbm9wNmRkOXp4c2E1eTFiZ2FqZnZ1aHIxMjNhZnFqd2swNDA2OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/smZYhZ2Bwz8mPCwDPl/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXlza3gxYno2Z2I2NGNrdnNyMDlneGQwdmZicWxudGVzZmk3cTQ4NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mGl6JhTtCc0ukOugQ5/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3UxdWZrbDVvc281N2swc202cGR6Zmp4MGUyNmhuYjk0NWhvdXYyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cbhVQuTa5BFS5RlHFG/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDAxcm10MThzajBwbGYwOGhxMWdzZDYyazJ6OHg0dm05bWNpYW83NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FPjwcGYUkDO3kok4PP/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTRmYXA4YWl3NHdwY3k1ZGNrYjh2bzZxY2ZhZzY3eXp4a2p3eHoybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gsp2q6vt6KPZeyJgQd/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGNoa3FmYnNxc3M4Nm90ZTF0cDg4NTFpMjU0aWdndjN4ZXN2cHJzZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Xpb7aXuOuormG3MfnL/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ptYXg5Ymc2NHRuZmkzdDQ3YTJoN3JrZ3RiZXczMXdyd2tiZjRjbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jbsoD38dcXoEmjfNQQ/giphy.gif"
      ]
    items = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]  
    rarity_name = ["1/2", "1/3", "1/4", "1/10", "1/100", "1/500", "1/1,000", "1/10,000", "1/10,000", "1/10,000"]
    user_rolls = []
    user_rolls_order = []
    user_items = []
    user_items_order = []
    gif = 0
    with open(f'userinventory.json', 'r') as f:
      user_data = json.load(f)

    for user_data_flex in range(len(user_data['user'])):
      if member.id == user_data['user'][user_data_flex]['userid']:
        roll_amount = user_data['user'][user_data_flex]['roll']
        for key in user_data['user'][user_data_flex]['inventory'][0]:
          if key in roll_name_gif_name:
            user_rolls.append(key)
          elif key in items:
            user_items.append(key)
    if len(user_rolls) != 0:
      for roll_name in range(len(roll_name_gif_name)):
        for user_roll_name in range(len(user_rolls)):
          if roll_name_gif_name[roll_name] == user_rolls[user_roll_name]:
            user_rolls_order.append(roll_name_gif_name[roll_name])
      best_roll = user_rolls_order[-1]
    if len(user_items) != 0:
      for item_name in range(len(items)):
        for user_item_name in range(len(user_items)):
          if items[item_name] == user_items[user_item_name]:
            user_items_order.append(items[item_name])
      best_item = user_items_order[-1]
    gif = roll_name_gif[roll_name_gif_name.index(best_roll)]
    roll_rarity = rarity_name[roll_name_gif_name.index(best_roll)]

    secs = roll_amount*4
    yrs,secs=divmod(secs,secs_per_year:=60*60*24*30.5*12)
    mth,secs=divmod(secs,secs_per_month:=60*60*24*30)
    days,secs=divmod(secs,secs_per_day:=60*60*24)
    hrs,secs=divmod(secs,secs_per_hr:=60*60)
    mins,secs=divmod(secs,secs_per_min:=60)
    secs=round(secs, 2)
    playtime='{} secs'.format(secs)
    
    if secs > 60 or mins > 0:
        playtime='{} minute(s) and {} second(s)'.format(int(mins),secs)
        if mins > 60 or hrs > 0:
            playtime='{} hour(s), {} minute(s) and {} second(s).'.format(int(hrs),int(mins),secs)
            if hrs > 24 or days > 0:
                playtime='{} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(days),int(hrs),int(mins),secs)
                if days > 30 or mth > 0:
                  playtime='{} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(mth),int(days),int(hrs),int(mins),secs)
                  if mth > 12 or yrs > 0:
                    playtime='{} year(s), {} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(yrs),int(mth),int(days),int(hrs),int(mins),secs)

    all_roll = ', '.join(user_rolls_order)
    all_item = ', '.join(user_items_order)
    embed = discord.Embed(title=f"🤍 {member.name}'s Gacha Stats", description="Items shown are virtual items,\nand could not possibly resell or trade with real items.", color=0xffffff)
    embed.add_field(name=f"> Rolling Stats:", value=f"```{member.name} has rolled {roll_amount} time(s)```", inline=False)
    embed.add_field(name=f"> Playtime:", value=f"```{playtime}```", inline=False)
    embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
    embed.set_thumbnail(url=member.avatar)
    await msg.delete()
    view = FlexButton(interaction.user.id, best_roll, best_item, all_roll, all_item, member, gif, roll_rarity)
    respond = await interaction.channel.send(embed=embed, view=view)
    view.message = respond
    
@client.tree.context_menu(name="Gacha Stats")
async def gacha_stats(interaction: discord.Interaction, member: discord.Member):
  await interaction.response.defer(ephemeral=True)
  msg = await interaction.followup.send("Retrieving your data please wait... <a:loading_symbol:1295113412564615249>")
  with open(f'userinventory.json', 'r') as f:
    user_data = json.load(f)

  userid = []

  for user_data_index in range(len(user_data['user'])):
    userid.append(user_data['user'][user_data_index]['userid'])

  if member.id not in userid:
    await msg.delete()
    await interaction.channel.send(embed=discord.Embed(title=f"{member.name} has no items to flex.", description="This user has no items\nIf this is you, you can start collecting items by running /roll", color = 0xffffff))
  else:
    roll_amount = 0
    best_roll = None
    best_item = None
    
    roll_name_gif_name = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
    roll_name_gif = [
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXN2ZmhsdDE5ajFpamY4YmJ4cnBrM2F1OGczM3ZmODl2N3VmcGhtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dfAXMYZfSmUjYttjqM/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXE2ZHcxd3EwdDFwOGV6M3JxYmJwbzRyMGVhMjl6Ynl2d2hkcmplMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5EG56vzNYvfgJWldgS/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDNndGxyMXFsY3EzZ3djNWJrMHgwZ204aWE2NTA3eGdiNXBsd2l2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9f3OzkeQ6h0tbyKlTr/giphy.gif", 
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXFkbm9wNmRkOXp4c2E1eTFiZ2FqZnZ1aHIxMjNhZnFqd2swNDA2OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/smZYhZ2Bwz8mPCwDPl/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXlza3gxYno2Z2I2NGNrdnNyMDlneGQwdmZicWxudGVzZmk3cTQ4NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mGl6JhTtCc0ukOugQ5/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3UxdWZrbDVvc281N2swc202cGR6Zmp4MGUyNmhuYjk0NWhvdXYyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cbhVQuTa5BFS5RlHFG/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDAxcm10MThzajBwbGYwOGhxMWdzZDYyazJ6OHg0dm05bWNpYW83NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FPjwcGYUkDO3kok4PP/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTRmYXA4YWl3NHdwY3k1ZGNrYjh2bzZxY2ZhZzY3eXp4a2p3eHoybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gsp2q6vt6KPZeyJgQd/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGNoa3FmYnNxc3M4Nm90ZTF0cDg4NTFpMjU0aWdndjN4ZXN2cHJzZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Xpb7aXuOuormG3MfnL/giphy.gif",
      "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ptYXg5Ymc2NHRuZmkzdDQ3YTJoN3JrZ3RiZXczMXdyd2tiZjRjbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jbsoD38dcXoEmjfNQQ/giphy.gif"
      ]
    items = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]  
    rarity_name = ["1/2", "1/3", "1/4", "1/10", "1/100", "1/500", "1/1,000", "1/10,000", "1/10,000", "1/10,000"]
    user_rolls = []
    user_rolls_order = []
    user_items = []
    user_items_order = []
    gif = 0
    with open(f'userinventory.json', 'r') as f:
      user_data = json.load(f)

    for user_data_flex in range(len(user_data['user'])):
      if member.id == user_data['user'][user_data_flex]['userid']:
        roll_amount = user_data['user'][user_data_flex]['roll']
        for key in user_data['user'][user_data_flex]['inventory'][0]:
          if key in roll_name_gif_name:
            user_rolls.append(key)
          elif key in items:
            user_items.append(key)
    if len(user_rolls) != 0:
      for roll_name in range(len(roll_name_gif_name)):
        for user_roll_name in range(len(user_rolls)):
          if roll_name_gif_name[roll_name] == user_rolls[user_roll_name]:
            user_rolls_order.append(roll_name_gif_name[roll_name])
      best_roll = user_rolls_order[-1]
    if len(user_items) != 0:
      for item_name in range(len(items)):
        for user_item_name in range(len(user_items)):
          if items[item_name] == user_items[user_item_name]:
            user_items_order.append(items[item_name])
      best_item = user_items_order[-1]
    gif = roll_name_gif[roll_name_gif_name.index(best_roll)]
    roll_rarity = rarity_name[roll_name_gif_name.index(best_roll)]

    secs = roll_amount*4
    yrs,secs=divmod(secs,secs_per_year:=60*60*24*30.5*12)
    mth,secs=divmod(secs,secs_per_month:=60*60*24*30)
    days,secs=divmod(secs,secs_per_day:=60*60*24)
    hrs,secs=divmod(secs,secs_per_hr:=60*60)
    mins,secs=divmod(secs,secs_per_min:=60)
    secs=round(secs, 2)
    playtime='{} secs'.format(secs)
    
    if secs > 60 or mins > 0:
        playtime='{} minute(s) and {} second(s)'.format(int(mins),secs)
        if mins > 60 or hrs > 0:
            playtime='{} hour(s), {} minute(s) and {} second(s).'.format(int(hrs),int(mins),secs)
            if hrs > 24 or days > 0:
                playtime='{} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(days),int(hrs),int(mins),secs)
                if days > 30 or mth > 0:
                  playtime='{} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(mth),int(days),int(hrs),int(mins),secs)
                  if mth > 12 or yrs > 0:
                    playtime='{} year(s), {} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(yrs),int(mth),int(days),int(hrs),int(mins),secs)

    all_roll = ', '.join(user_rolls_order)
    all_item = ', '.join(user_items_order)
    embed = discord.Embed(title=f"🤍 {member.name}'s Gacha Stats", description="Items shown are virtual items,\nand could not possibly resell or trade with real items.", color=0xffffff)
    embed.add_field(name=f"> Rolling Stats:", value=f"```{member.name} has rolled {roll_amount} time(s)```", inline=False)
    embed.add_field(name=f"> Playtime:", value=f"```{playtime}```", inline=False)
    embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
    embed.set_thumbnail(url=member.avatar)
    await msg.delete()
    view = FlexButton(interaction.user.id, best_roll, best_item, all_roll, all_item, member, gif, roll_rarity)
    respond = await interaction.channel.send(embed=embed, view=view)
    view.message = respond

@client.tree.command(name="inventory", description="Show a member's inventory")
@app_commands.checks.cooldown(1, 2, key=lambda i: (i.user.id))
@app_commands.choices(type=[
  discord.app_commands.Choice(name='Rolls', value=1),
  discord.app_commands.Choice(name="Items", value=2)
])
async def inventory(interaction: discord.Interaction, member: Optional[discord.Member], type: discord.app_commands.Choice[int]):

  rarity =  ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
  items = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]
  if member == None:
    member = interaction.user
  embed = discord.Embed(title=f"{member}'s {type.name} Inventory", description="Items shown are virtual items,\nand could not possibly resell or trade with real items.", color=0xffffff)
  embed.set_thumbnail(url=member.avatar)
  user_inventory_item = []
  with open("userinventory.json") as f:
    users = json.load(f)
  for user in users["user"]:
    if user["userid"] == member.id:
      for key in user["inventory"]:
        for inventory_roll_name in key:
          user_inventory_item.append(inventory_roll_name)
  with open('userinventory.json', 'r') as f:
          json_data = json.load(f)

  index = 0
  for i in range(len(json_data['user'])):
    if json_data['user'][i]["userid"] == interaction.user.id:
      index = i 

  for value in user_inventory_item:
    if json_data['user'][index]['inventory'][0][value] == 0:
      del json_data['user'][index]['inventory'][0][value]
      user_inventory_item.remove(value)

  with open('userinventory.json', 'w') as f:
    json.dump(json_data, f, indent=2)
  if len(user_inventory_item) == 0:
    await interaction.response.send_message(embed=discord.Embed(title=f"{member} has no items to show.", description="This user has no items\nIf this is you, you can start collecting items by running /roll", color = 0xffffff))
  else:
    if type.name == "Rolls":
      for rarity_items in rarity:
        if rarity_items in user_inventory_item:
          def add_json(new_data, filename='userinventory.json'):
            with open(filename,'r+') as file:
                file_data = json.load(file)
                for users in file_data["user"]:
                  if users["userid"] == interaction.user.id:
                    for key in users["inventory"]:
                      return key[new_data]
                file.seek(0)
                json.dump(file_data, file, indent = 2)
          y = rarity_items
          embed.add_field(name=f"🤍 {rarity_items}", value=f"> Amount: **{add_json(y)}**", inline=True)
    elif type.name == "Items":
      join_item = ""
      for craftable_items in items:
        if craftable_items in user_inventory_item:
          def add_json(new_data, filename='userinventory.json'):
            with open(filename,'r+') as file:
                file_data = json.load(file)
                for users in file_data["user"]:
                  if users["userid"] == interaction.user.id:
                    for key in users["inventory"]:
                      return key[new_data]
                file.seek(0)
                json.dump(file_data, file, indent = 2)
              
          y = craftable_items
          join_item += f"> {craftable_items} **(x{add_json(y)})**\n"
      if join_item != "":
        embed.add_field(name=f"🤍 Craftable Items", value=f"{join_item}", inline=True)
    await interaction.response.send_message(embed=embed)


@client.tree.command(name="shop", description="Show the gacha shop")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def shop(interaction: discord.Interaction):
  embed = discord.Embed(title="Equinox's Gacha Shop", description="Items shown are virtual items,\nand could not possibly resell or trade with real items.", color=0xffffff)
  embed.add_field(name=f"🤍 Fortune Drink", value=f"> Ingredients: **5 Commons, 3 Uncommons**\n> Stats: x2 Lucky", inline=True)
  embed.add_field(name=f"🤍 Witch's Potion", value=f"> Ingredients: **15 Commons, 10 Uncommons, 5 Rares**\n> Stats: x3 Lucky", inline=True)
  embed.add_field(name=f"🤍 Divine Fluid", value=f"> Ingredients: **30 Commons, 20 Uncommons, 10 Rares, 5 Epics**\n> Stats: x5 Lucky", inline=True)
  embed.add_field(name=f"🤍 Angel Dust", value=f"> Ingredients: **100 Commons, 70 Uncommons, 40 Rares, 20 Epics, 5 Legendaries**\n> Stats: x10 Lucky", inline=True)
  embed.add_field(name=f"🤍 Me When Im Lucky", value=f"> Ingredients: **250 Commons, 100 Uncommons, 70 Rares, 50 Epics, 25 Legendaries, 1 Divine**\n> Stats: x50 Lucky", inline=True)
  embed.add_field(name=f"🤍 Touch of Divinity", value=f"> Ingredients: **1000 Commons, 500 Uncommons, 400 Rares, 100 Epics, 70 Legendaries, 10 Divine**\n> Stats: x100 Lucky", inline=True)
  embed.add_field(name=f"🤍 Trio Charm", value=f"> Ingredients: **5000 Commons, 2500 Uncommons, 1000 Rares, 500 Epics, 300 Legendaries, 100 Divine, 10 Mythic in the Making**\n> Stats: x500 Lucky", inline=True)
  await interaction.response.send_message(embed=embed)

class BuyPremium(View):
  def __init__(self):
    super().__init__(timeout=60)
    button = discord.ui.Button(label='Buy Premium', style=discord.ButtonStyle.url, url='https://discord.gg/Cu8JR7Vsvx')
    self.add_item(button)


@client.tree.command(name="daily", description="Daily chest of potions")
@app_commands.checks.cooldown(1, 86400, key=lambda i: (i.user.id))
async def daily(interaction: discord.Interaction):
  refresh()
  is_active, is_premium, expires_at = user_is_active(interaction.user.id)
  if is_premium:
    with open('userinventory.json', 'r') as f:
      json_data = json.load(f)
    user_id = []
    index = 0
    for i in range(len(json_data['user'])):
        user_id.append(json_data['user'][i]['userid'])

    if interaction.user.id not in user_id:
      await interaction.response.send_message(embed=discord.Embed(title="Daily Error...", description="You do not have a paired database.\nCreate a database by rolling\nUse **/roll**", color=0xffffff))
    else:
      with open('userinventory.json', 'r') as f:
        json_data = json.load(f)  

      index = None
      for i in range(len(json_data['user'])):
        if json_data['user'][i]["userid"] == interaction.user.id:
          index = i

      item_list = ["Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Divine Fluid", "Divine Fluid", "Divine Fluid", "Divine Fluid", "Angel Dust", "Angel Dust","Angel Dust","Me When Im Lucky", "Me When Im Lucky"]
      user_daily_item = []
      user_item = []
      for i in range(3):
        user_daily_item.append(random.choice(item_list))

      for key in json_data['user'][index]['inventory'][0]:
        user_item.append(key)

      for i in range(len(user_daily_item)):
        for key in json_data['user'][index]['inventory'][0]:
          user_item.append(key)
        if user_daily_item[i] in user_item:
          json_data['user'][index]['inventory'][0][user_daily_item[i]] += 1
        elif user_daily_item[i] not in user_item:
          json_data['user'][index]['inventory'][0][user_daily_item[i]] = 1
        
      with open(f'userinventory.json', 'w') as f:
        json.dump(json_data, f, indent=2)
      await interaction.response.defer()
      msg = await interaction.followup.send(embed=discord.Embed(title="Opening Chest...", color=0xffffff))
      await sleep(5)
      embed1=discord.Embed(title="In the chest you got:", description=f"x1 **{user_daily_item[0]}**", color=0xffffff)
      await msg.edit(embed=embed1)
      await sleep(2)
      embed2=discord.Embed(title="In the chest you got:", description=f"x1 **{user_daily_item[0]}**\nx1 **{user_daily_item[1]}**", color=0xffffff)
      await msg.edit(embed=embed2)
      await sleep(2)
      embed3=discord.Embed(title="In the chest you got:", description=f"x1 **{user_daily_item[0]}**\nx1 **{user_daily_item[1]}**\nx1 **{user_daily_item[2]}**", color=0xffffff)
      await msg.edit(embed=embed3)
  else:
    await interaction.response.send_message(embed=discord.Embed(title="You are being restricted", description="Daily command is only available to our elite users.\nConsider buying our useful premium with lots of perks?\nUse </help:1242738769099231302> to check out our premium perks.", color=0xffffff), view=BuyPremium())



@client.tree.command(name="craft", description="Craft an item")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.describe(item="The item you want to craft")
@app_commands.choices(item=[
  discord.app_commands.Choice(name='Fortune Drink', value=1),
  discord.app_commands.Choice(name="Witch's Potion", value=2),
  discord.app_commands.Choice(name='Divine Fluid', value=3),
  discord.app_commands.Choice(name='Angel Dust', value=4),
  discord.app_commands.Choice(name='Me When Im Lucky', value=5),
  discord.app_commands.Choice(name='Touch of Divinity', value=6),
  discord.app_commands.Choice(name='Trio Charm', value=7),
])
async def craft(interaction: discord.Interaction, item: discord.app_commands.Choice[int], amount: Optional[int] = 1):
    if amount <= 0:
        amount = 1

                                       
    crafting_recipes = {
        "Fortune Drink": (["Common", "Uncommon"], [5, 3]),
        "Witch's Potion": (["Common", "Uncommon", "Rare"], [15, 10, 5]),
        "Divine Fluid": (["Common", "Uncommon", "Rare", "Epic"], [30, 20, 10, 5]),
        "Angel Dust": (["Common", "Uncommon", "Rare", "Epic", "Legendary"], [100, 70, 40, 20, 5]),
        "Me When Im Lucky": (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine"], [250, 100, 70, 50, 25, 1]),
        "Touch of Divinity": (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine"], [1000, 500, 400, 100, 70, 10]),
        "Trio Charm": (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Mythic in the Making"], [5000, 2500, 1000, 500, 300, 100, 10]),
    }

                                                          
    requirements, required_amount = crafting_recipes.get(item.name, ([], []))

                             
    with open("userinventory.json") as f:
        users = json.load(f)

                               
    user_inventory = next((user for user in users["user"] if user["userid"] == interaction.user.id), None)
    if not user_inventory:
        await interaction.response.send_message("User data not found!")
        return

                                    
    user_inventory_items = [inventory_item for inventory in user_inventory["inventory"] for inventory_item in inventory]

                                                        
    missing_requirements = []
    for i, requirement in enumerate(requirements):
        required = required_amount[i] * amount
        current_amount = user_inventory_items.count(requirement)
        missing = required - current_amount
        if missing > 0:
            missing_requirements.append((requirement, missing))

    if missing_requirements:
        embed = discord.Embed(title="Error in Crafting", color=0xffffff)
        for req, missing in missing_requirements:
            embed.add_field(name=req, value=f"Missing: {missing}", inline=False)
        await interaction.response.send_message(embed=embed)
        return

                                              
                                 
    for i, requirement in enumerate(requirements):
        required = required_amount[i] * amount
        for _ in range(required):
            user_inventory_items.remove(requirement)

                          
    for _ in range(amount):
        user_inventory_items.append(item.name)

                                                 
    with open("userinventory.json", 'r+') as file:
        file_data = json.load(file)
        for user in file_data["user"]:
            if user["userid"] == interaction.user.id:
                user["inventory"] = [dict(zip(user_inventory["inventory"][0].keys(), user_inventory_items))]
        file.seek(0)
        json.dump(file_data, file, indent=2)

                            
    embed = discord.Embed(title="🤍 Successfully Crafted", description=f"Item crafted: {item.name} (x{amount})", color=0xffffff)
    await interaction.response.send_message(embed=embed)

                                                                            

@client.tree.command(name="embed", description="Make an embed. (Manage messages required)")
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(title = "Title of the embed", description = "Description of the embed", color = "Color of side part of embed in rgb code ex: (0,0,0) without the parentheses", image="Largest media in embed in url", thumbnail="Smaller image usually located at top right in url")
async def embed(interaction: discord.Interaction, title: str, description: Optional[str], color: Optional[str], image: Optional[str], thumbnail: Optional[str], footer: Optional[str]):
  if color == None:
    color = "255,255,255"
  color_list = color.split(",")
  r = int(color_list[0])
  g = int(color_list[1])
  b = int(color_list[2])
  embed_2 = discord.Embed()
  if description == None:
    embed = discord.Embed(title=title, color=discord.Color.from_rgb(r, g, b))
  else:
    embed = discord.Embed(title=title, description=description, color=discord.Color.from_rgb(r, g, b))
  if image != None:
    embed.set_image(url=image)
  if thumbnail != None:
    embed.set_thumbnail(url=thumbnail)
  if footer == None:
    footer = f"Embed created by {interaction.user} | 🤍 Equinox Embeds"
  embed.set_footer(text=footer)
  await interaction.response.defer()
  await interaction.followup.send(file=discord.File("data_assets/embed_guide.png"), content="Embed's guide", ephemeral=True)
  msg_1 = await interaction.channel.send(f"{interaction.user.mention} How many fields does your embed need? (Answer in number, if not needed say 0)")
  msg_2 = await client.wait_for('message', check=lambda message: message.author == interaction.user)
  if int(msg_2.content) > 0:
    if msg_2 != None:
      await msg_2.delete()
      await msg_1.delete()
    for i in range(int(msg_2.content)):
      field_title = await interaction.channel.send(f"{interaction.user.mention} What is the content of the No: {i+1} field's title?")
      input_field_title = await client.wait_for('message', check=lambda message: message.author == interaction.user)
      if input_field_title != None:
        await input_field_title.delete()
        await field_title.delete()
      field_description = await interaction.channel.send(f"{interaction.user.mention} What is the content of the No: {i+1} field's description?")
      input_field_description = await client.wait_for('message', check=lambda message: message.author == interaction.user)
      if input_field_description != None:
        await input_field_description.delete()
        await field_description.delete()
      field_inline = await interaction.channel.send(f"{interaction.user.mention} No: {i+1} Field inline? (y/n) (if inline = y, then fields will be in row, if inline = n, then fields will stack on each other)")
      input_field_inline = await client.wait_for('message', check=lambda message: message.author == interaction.user)
      if input_field_inline != None:
        await input_field_inline.delete()
        await field_inline.delete()
        if input_field_inline.content.lower() == "y":
          embed.add_field(name=input_field_title.content, value=input_field_description.content, inline=True)
        elif input_field_inline.content.lower() == "n":
          embed.add_field(name=input_field_title.content, value=input_field_description.content, inline=False)
  else:
    await msg_1.delete()
  await interaction.channel.send(embed=embed)
    
@client.tree.command(name="purge", description="Clear messages. (Manage messages required)")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.checks.bot_has_permissions(manage_messages=True)
@app_commands.describe(amount="Number of messages to clear (less than 1000)")
async def purge(interaction: discord.Interaction, amount: int, bot_messages: bool = True, embed_messages: bool = True, user_messages: bool = True):
    if not (1 < amount <= 50):
        embed = discord.Embed(
            title=f"{interaction.user} 🤍 Error", 
            description="Amount of messages must be between 2 and 50. Consider using </clone:1250258069686849639> if you wish to clear all messages.",
            color=0xffffff
        )
        await interaction.response.send_message(content=interaction.user.mention, embed=embed)
        return
    
                                                   
    def check_message(message):
        if bot_messages and message.author.bot:
            return True
        if embed_messages and message.embeds:
            return True
        if user_messages and not message.author.bot:
            return True
        return False

                                           
    await interaction.response.defer(ephemeral=True)
    msg = await interaction.followup.send("Purging... <a:loading_symbol:1295113412564615249>")

                                                      
    deleted_messages = await interaction.channel.purge(limit=amount, check=check_message)

                                    
    botmessage = sum(1 for m in deleted_messages if m.author.bot)
    embedmessage = sum(1 for m in deleted_messages if m.embeds)
                                                                                    
    usermessage = sum(1 for m in deleted_messages if not m.author.bot)

                                             
    await msg.delete()                              

    embed = discord.Embed(
        title=f"Successfully deleted {len(deleted_messages)} message(s)",
        description=f"> **Logs:**\n```js\nBot Messages: {botmessage} message(s)\nEmbed Messages: {embedmessage} message(s)\nUser Messages: {usermessage} message(s)\n```",
        color=0xffffff
    )
    embed.set_footer(icon_url=interaction.user.avatar, text=f"Purged by {interaction.user}")
    await interaction.channel.send(embed=embed)



                                                                       
@client.tree.command(name="serverinfo", description="Shows information of the current server")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

                                                             
    await guild.chunk()

                                                     
    online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)

    description = str(guild.description) if guild.description else "No description"
    owner = str(guild.owner)
    guild_id = str(guild.id)
    member_count = str(guild.member_count)
    role_count = len(guild.roles)
    channel_count = len(guild.channels)
    boost_count = guild.premium_subscription_count
    boost_level = guild.premium_tier
    mfa_level = guild.mfa_level
    highest_role = guild.roles[-1]

    embed = discord.Embed(
        title=f"🤍 {guild.name}'s Information",
        description=f"Description: {description}",
        color=0xffffff
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="Owner", value=f"```{owner}```", inline=True)
    embed.add_field(name="Server ID", value=f"```{guild_id}```", inline=True)
    embed.add_field(name="Total Members", value=f"```{member_count}```", inline=True)
    embed.add_field(name="Online Members", value=f"```{online_members}```", inline=True)
    embed.add_field(name="Role Count", value=f"```{role_count}```", inline=True)
    embed.add_field(name="Highest Role", value=f"```{highest_role}```", inline=True)
    embed.add_field(name="Channel Count", value=f"```{channel_count}```", inline=True)
    embed.add_field(name="Verification Level", value=f"```{guild.verification_level}```", inline=True)
    embed.add_field(name="Boost Count", value=f"```{boost_count}```", inline=True)
    embed.add_field(name="Boost Level", value=f"```{boost_level}```", inline=True)
    embed.add_field(name="MFA Level", value=f"```{mfa_level}```", inline=True)
    embed.add_field(name="Created At", value=f"```{guild.created_at.strftime('%A, %B %d %Y')}```", inline=True)
    embed.add_field(name="Emoji Count", value=f"```{len(guild.emojis)}```", inline=True)
    embed.set_footer(text=f"Issued by {interaction.user}")

    await interaction.response.send_message(embed=embed)


PRIVACY_FILE = "privacy_settings.json"

                                 
def load_privacy_settings():
    if not os.path.exists(PRIVACY_FILE):
        with open(PRIVACY_FILE, "w") as f:
            json.dump([], f)
    with open(PRIVACY_FILE, "r") as f:
        return json.load(f)

def save_privacy_settings(data):
    with open(PRIVACY_FILE, "w") as f:
        json.dump(data, f, indent=2)

@client.tree.command(name="privacy", description="Opt-in or out of presence tracking (status & activity)")
@app_commands.describe(option="Turn presence visibility on or off")
async def privacy(interaction: discord.Interaction, option: Literal["on", "off"]):
    user_id = interaction.user.id
    settings = load_privacy_settings()

    if option == "on":
        if user_id not in settings:
            settings.append(user_id)
            save_privacy_settings(settings)
            await interaction.response.send_message("✅ You have opted out of presence tracking. Your status and activities will be hidden.")
        else:
            await interaction.response.send_message("ℹ️ You are already opted out.")
    else:
        if user_id in settings:
            settings.remove(user_id)
            save_privacy_settings(settings)
            await interaction.response.send_message("✅ You have opted back in. Your status and activities will now be visible.")
        else:
            await interaction.response.send_message("ℹ️ You were not opted out.")

@client.tree.command(name="userinfo", description="Shows information of a user")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def userinfo(interaction: discord.Interaction, member: Optional[discord.Member]):
    if member is None:
        member = interaction.user

    privacy_settings = load_privacy_settings()

    mbed = discord.Embed(
        title=f"🤍 {member.name}'s Information",
        description=f"{member.mention}",
        url=f"https://discordapp.com/users/{member.id}",
        color=0xffffff
    )

    mbed.add_field(name="Member ID", value=f"> {member.id}", inline=True)
    mbed.add_field(name="Joined Since", value=f"> {member.joined_at.strftime('%A, %B %d %Y')}", inline=False)
    mbed.add_field(name="Created Since", value=f"> {member.created_at.strftime('%A, %B %d %Y')}", inline=False)
    mbed.add_field(name="Display Name", value=f"> {member.display_name}", inline=False)
    mbed.add_field(name="Top Role", value=f"> {member.top_role.mention}", inline=False)

                             
    if member.id in privacy_settings:
        mbed.add_field(name="Current Status", value="> 🔒 Hidden (Privacy Opt-out)", inline=False)
        mbed.add_field(name="Activities", value="> 🔒 Hidden (Privacy Opt-out)", inline=False)
    else:
                
        mbed.add_field(name="Current Status", value=f"> {str(member.status).title()}", inline=False)

                    
        if member.activities:
            activity_list = []
            for activity in member.activities:
                if isinstance(activity, discord.Game):
                    activity_list.append(f"🎮 Playing: {activity.name}")
                elif isinstance(activity, discord.Streaming):
                    activity_list.append(f"📺 Streaming: [{activity.name}]({activity.url})")
                elif isinstance(activity, discord.Spotify):
                    activity_list.append(f"🎵 Listening to: {activity.title} by {activity.artist}")
                elif isinstance(activity, discord.CustomActivity):
                    activity_list.append(f"💬 Custom Status: {activity.state or '—'}")
                else:
                    activity_list.append(f"⚡ {activity.type.name.title()}: {activity.name}")
            mbed.add_field(name="Activities", value="\n".join(activity_list), inline=False)
        else:
            mbed.add_field(name="Activities", value="> None", inline=False)

    if member.premium_since:
        mbed.add_field(name="Boosting Since", value=f"> {member.premium_since.strftime('%A, %B %d %Y')}", inline=True)
    else:
        mbed.add_field(name="Boosting Since", value="> Not boosting", inline=True)

    mbed.add_field(name="Bot?", value=f"> {member.bot}", inline=False)
    mbed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    mbed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar.url)

    await interaction.response.send_message(embed=mbed)


@client.tree.command(name="roleinfo", description="Shows informations of a role")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def roleinfo(interaction: discord.Interaction, role: discord.Role = None):  
  mbed = discord.Embed(
  title=f"🤍 {role.name}'s Information",
  description=f"{role.mention}",
  color = 0xffffff
  )
  mbed.add_field(name="Role Id", value=f"> {role.id}", inline=False)
  mbed.add_field(name=f"Created Since", value=f"> {role.created_at.strftime('%A, %B %d %Y')}", inline=False)
  mbed.add_field(name=f"Position", value=f"> {role.position}", inline=False)
  mbed.add_field(name=f"Bot role?", value=f"> {role.is_bot_managed()}", inline=False)
  mbed.add_field(name=f"Displayed Seperately?", value=f"> {role.hoist}", inline=False)
  mbed.add_field(name=f"Mentionable?", value=f"> {role.mentionable}", inline=False)
  mbed.set_footer(icon_url = interaction.user.avatar, text = f"Issued by {interaction.user}")
  await interaction.response.send_message(embed=mbed)


@client.tree.command(name="avatar", description="Displays the image of a user's avatar")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def avatar(interaction: discord.Interaction, member: Optional[discord.Member]):
  if member == None:
    member = interaction.user
  embed = discord.Embed(title=f"{member}'s Avatar", url=f"{member.avatar}", color = 0xffffff)
  embed.set_image(url = member.avatar)
  embed.set_footer(icon_url = interaction.user.avatar, text = f"Issued by {interaction.user}")
  await interaction.response.send_message(embed=embed)
  
@client.tree.command(name="poll", description="Make a poll. (Manage messages required)")
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.describe(first_emoji = "First emoji", first_option = "First option", second_emoji = "Second emoji", second_option = "Second option", third_emoji = "Third emoji", third_option = "Third option")
async def poll(interaction: discord.Interaction, first_emoji: str, first_option: str, second_emoji: str, second_option: str, third_emoji: Optional[str], third_option: Optional[str]):
  if third_emoji != None or third_option != None:
    embed = discord.Embed(title="Poll Started 🤍", description=f"> {first_emoji}: **{first_option}**\n> {second_emoji}: **{second_option}**\n> {third_emoji}: **{third_option}**", color = 0xffffff)
  else:
    embed = discord.Embed(title="Poll Started 🤍", description=f"> {first_emoji}: **{first_option}**\n> {second_emoji}: **{second_option}**", color = 0xffffff)
  embed.set_footer(icon_url=interaction.user.avatar, text = f"Poll started by {interaction.user}")
  await interaction.response.defer()
  msg = await interaction.followup.send(embed=embed)
  await msg.add_reaction(f"{first_emoji}")
  await msg.add_reaction(f"{second_emoji}")
  if third_emoji != None or third_option != None:
    await msg.add_reaction(f"{third_emoji}")

@client.tree.command(name="qrcode", description="Generate qr-code from text, link, ...")
@app_commands.checks.cooldown(1, 69, key=lambda i: (i.user.id))
@app_commands.describe(parm = "Value of Qr-code")
async def qr(interaction: discord.Interaction, parm:str):
  qrim = qrcode.make(parm)
  qrim.save('data_assets/qrcode.png')
  with open('data_assets/qrcode.png', 'rb') as f:
      picture = discord.File(f)
  embed = discord.Embed(title='',color=0xffffff)
  embed.add_field(name=f'QR Code Maker',value=f'**Context**: `{parm}`')
  embed.set_image(url="attachment://qrcode.png")
  await interaction.response.send_message(file=discord.File('data_assets/qrcode.png'),embed=embed)

class DaysBetweenButton(discord.ui.View):
  def __init__(self, authorID, firstdate, seconddate):
    self.authorID = authorID
    self.firstdate = firstdate
    self.seconddate = seconddate
    super().__init__(timeout=60)
  @discord.ui.button(label="In Seconds", style=discord.ButtonStyle.green)
  async def second_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer()
      def calculate_days_between(input_date1, input_date2):
        day1, month1, year1 = input_date1.split('/')
        day2, month2, year2 = input_date2.split('/')

        date1 = datetime(int(year1), int(month1), int(day1))
        date2 = datetime(int(year2), int(month2), int(day2))
        if date2 < date1:
            date1, date2 = date2, date1
        return (date2 - date1).total_seconds()
      embed = discord.Embed(title=f"The second(s) between `{self.firstdate}` and `{self.seconddate}` is", description=f"{calculate_days_between(self.firstdate, self.seconddate)} second(s)!", color = 0xffffff)
      await interaction.followup.send(embed=embed, ephemeral=True)

  @discord.ui.button(label="In Minutes", style=discord.ButtonStyle.green)
  async def minute_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer()
      def calculate_days_between(input_date1, input_date2):
        day1, month1, year1 = input_date1.split('/')
        day2, month2, year2 = input_date2.split('/')

        date1 = datetime(int(year1), int(month1), int(day1))
        date2 = datetime(int(year2), int(month2), int(day2))
        if date2 < date1:
            date1, date2 = date2, date1
        return (date2 - date1).total_seconds()
      minute = round(calculate_days_between(self.firstdate, self.seconddate)/60)
      embed = discord.Embed(title=f"The minute(s) between `{self.firstdate}` and `{self.seconddate}` is roughly about:", description=f"{minute} minute(s)!", color = 0xffffff)
      await interaction.followup.send(embed=embed, ephemeral=True)

  @discord.ui.button(label="In Weeks", style=discord.ButtonStyle.green)
  async def week_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer()
      def calculate_days_between(input_date1, input_date2):
        day1, month1, year1 = input_date1.split('/')
        day2, month2, year2 = input_date2.split('/')

        date1 = datetime(int(year1), int(month1), int(day1))
        date2 = datetime(int(year2), int(month2), int(day2))
        if date2 < date1:
            date1, date2 = date2, date1
        return (date2 - date1).total_seconds()
      week = round(calculate_days_between(self.firstdate, self.seconddate)/604800)
      embed = discord.Embed(title=f"The week(s) between `{self.firstdate}` and `{self.seconddate}` is roughly about:", description=f"{week} week(s)!", color = 0xffffff)
      await interaction.followup.send(embed=embed, ephemeral=True)

  @discord.ui.button(label="In Months", style=discord.ButtonStyle.green)
  async def month_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer()
      def calculate_days_between(input_date1, input_date2):
        day1, month1, year1 = input_date1.split('/')
        day2, month2, year2 = input_date2.split('/')

        date1 = datetime(int(year1), int(month1), int(day1))
        date2 = datetime(int(year2), int(month2), int(day2))
        if date2 < date1:
            date1, date2 = date2, date1
        return (date2 - date1).total_seconds()
      month = round(calculate_days_between(self.firstdate, self.seconddate)/2629743.83)
      embed = discord.Embed(title=f"The month(s) between `{self.firstdate}` and `{self.seconddate}` is roughly about:", description=f"{month} month(s)!", color = 0xffffff)
      await interaction.followup.send(embed=embed, ephemeral=True)

  @discord.ui.button(label="In Years", style=discord.ButtonStyle.green)
  async def year_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer()
      def calculate_days_between(input_date1, input_date2):
        day1, month1, year1 = input_date1.split('/')
        day2, month2, year2 = input_date2.split('/')

        date1 = datetime(int(year1), int(month1), int(day1))
        date2 = datetime(int(year2), int(month2), int(day2))
        if date2 < date1:
            date1, date2 = date2, date1
        return (date2 - date1).total_seconds()
      year = round(calculate_days_between(self.firstdate, self.seconddate)/31556926)
      embed = discord.Embed(title=f"The year(s) between `{self.firstdate}` and `{self.seconddate}` is roughly about:", description=f"{year} year(s)!", color = 0xffffff)
      await interaction.followup.send(embed=embed, ephemeral=True)

  async def on_timeout(self) -> None:
    second_button = discord.utils.get(self.children, label="In Seconds")
    second_button.disabled = True
    minute_button = discord.utils.get(self.children, label="In Minutes")
    minute_button.disabled = True
    week_button = discord.utils.get(self.children, label="In Weeks")
    week_button.disabled = True
    month_button = discord.utils.get(self.children, label="In Months")
    month_button.disabled = True
    year_button = discord.utils.get(self.children, label="In Years")
    year_button.disabled = True
    await self.message.edit(view=self)

@client.tree.command(name="daysbetween", description="Find the days between a pair of day, month, and year")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.describe(firstdate = "The first date dd/mm/yy", seconddate = "The second date dd/mm/yy")
async def daysbetween(interaction: discord.Interaction, firstdate: str, seconddate: str):
  await interaction.response.defer()
  days_31 = [1,3,5,7,8,10,12]
  days_30 = [4,6,9,11]
  days_29_28 = [2]
  eligible = False
  firstdatesplit = firstdate.split("/")
  seconddatesplit = seconddate.split("/")
  if int(firstdatesplit[1]) > 0 and int(firstdatesplit[1]) < 13 and int(seconddatesplit[1]) > 0 and int(seconddatesplit[1]) < 13:
    if int(firstdatesplit[1]) in days_31 or int(seconddatesplit[1]) in days_31:
      if int(firstdatesplit[0]) > 0 and int(firstdatesplit[0]) < 32 and int(seconddatesplit[0]) > 0 and int(seconddatesplit[0]) < 32:
        eligible = True
    if int(firstdatesplit[1]) in days_30 or int(seconddatesplit[1]) in days_30:
      if int(firstdatesplit[0]) > 0 and int(firstdatesplit[0]) < 31 and int(seconddatesplit[0]) > 0 and int(seconddatesplit[0]) < 31:
        eligible = True
    if int(firstdatesplit[1]) in days_29_28 or int(seconddatesplit[1]) in days_29_28:
      if int(firstdatesplit[0]) > 0 and int(firstdatesplit[0]) < 30 and int(seconddatesplit[0]) > 0 and int(seconddatesplit[0]) < 30:
        eligible = True
  if int(firstdatesplit[2]) < 0 or int(seconddatesplit[2]) < 0:
    eligible = False

  if eligible == True:
    def calculate_days_between(input_date1, input_date2):
      day1, month1, year1 = input_date1.split('/')
      day2, month2, year2 = input_date2.split('/')

      date1 = datetime(int(year1), int(month1), int(day1))
      date2 = datetime(int(year2), int(month2), int(day2))
      if date2 < date1:
          date1, date2 = date2, date1
      return (date2 - date1).days
    embed = discord.Embed(title=f"The days between `{firstdate}` and `{seconddate}` is", description=f"{calculate_days_between(firstdate, seconddate)} day(s)!", color = 0xffffff)
    view = DaysBetweenButton(interaction.user.id, firstdate, seconddate)
    msg = await interaction.followup.send(embed=embed, view=view)
    view.message = msg
  else:
    embed = discord.Embed(title=f"Error in calculating...", description=f"Please check if whether your inputed dates are:\n- Days are not corresponding to months\n- Either day, month, year are below 0 and or above 31", color = 0xffffff)
    embed.add_field(name="> Months with 31 days:", value="```January(1), March(3), May(5), July(7), August(8), October(10), December(12).```", inline=False)
    embed.add_field(name="> Months with 30 days:", value="```April(4), June(6), September(9), November(11).```", inline=False)
    embed.add_field(name="> Months with 28-29 days:", value="```February(2).```", inline=False)
    await interaction.followup.send(embed=embed)

   

@client.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
  embed=discord.Embed(color = 0xffffff)
  embed.add_field(name="> 🤍 Client Ping", value=f"```{round(client.latency * 1000)}ms```")
  await interaction.response.send_message(embed=embed)


   

class myInvite(View):
  def __init__(self):
    super().__init__(timeout=60)
    button = discord.ui.Button(label='Admin Perms', style=discord.ButtonStyle.url, url='https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=8&scope=bot')
    button2 = discord.ui.Button(label='Limited Perms', style=discord.ButtonStyle.url, url='https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=268494870&scope=bot')
    self.add_item(button)
    self.add_item(button2)

@client.tree.command(name="invite", description="Invite Equinox")
async def invite(interaction: discord.Interaction):
  emb = discord.Embed(title="You're choosing the best bot for your server! :D",color = 0xffffff)
  await interaction.response.send_message(embed=emb, view=myInvite())

                                                                         

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

class Mymodal(ui.Modal, title="Be an elite user"):
    code = ui.TextInput(
        label="Enter code",
        placeholder="Include capitals and dashes.",
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = client.get_channel(1242633669890277456)
        msg = await channel.send(self.code)
        user_input = msg.content.strip()
        refresh()                                      

                                                              
        is_active, current_tier, _expires = user_is_active(interaction.user.id)
        if is_active:
            emb = discord.Embed(color=0xFFFFFF)
            emb.set_author(name="You're already a premium user")
            emb.add_field(
                name="Premium users must finish their current plan before buying again",
                value=f"Your current subscription: **{(current_tier or 'Unknown').title()}**",
                inline=False
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

                                        
        tier = None
        if user_input in getattr(client, "monthly_codes", []):
            tier = "monthly"
        elif user_input in getattr(client, "yearly_codes", []):
            tier = "yearly"
        elif hasattr(client, "lifetime_codes") and user_input in getattr(client, "lifetime_codes", []):
            tier = "lifetime"

        if tier is None:
            emb = discord.Embed(color=0xFFFFFF)
            emb.set_author(name="Invalid Code!")
            emb.add_field(
                name="Your code is not valid",
                value=(
                    "Please include **UPPERCASE letters** and **dashes** and try again.\n"
                    "It may also have already been used or not exist."
                ),
                inline=False
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            return

                                                             
        remove_code_from_pool(tier, user_input)
        add_subscription(interaction.user.id, tier, user_input)

                                                              
        try:
            replenish_codes(tier, 5)
        except Exception:
            pass

                          
        emb = discord.Embed(color=0xFFFFFF)
        emb.set_author(name="Valid Code!")
        emb.add_field(
            name="You have successfully redeemed a code",
            value=f"Your subscription plan: **{tier.title()}**",
            inline=False
        )
        await interaction.response.send_message(embed=emb, ephemeral=True)

                
        try:
            if channel:
                log = discord.Embed(
                    title=f"{interaction.user} has redeemed a code",
                    color=0xFFFFFF
                )
                log.add_field(name="> Code", value=f"```{user_input}```", inline=False)
                log.add_field(name="> Type", value=f"```{tier.title()}```", inline=False)
                log.add_field(name="> User Id", value=f"```{interaction.user.id}```", inline=False)
                if interaction.user.avatar:
                    log.set_thumbnail(url=interaction.user.avatar.url)
                await channel.send(embed=log)
        except Exception:
            pass
        
        await msg.delete()





@client.tree.command(name="redeem", description="Redeem a premium code")
async def redeem(interaction: discord.Interaction):
    await interaction.response.send_modal(Mymodal())


def _parse_iso_utc(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None
    
@tasks.loop(hours=24)
async def prune_expired_subs():
    await client.wait_until_ready()
    now = datetime.now(timezone.utc)

    for tier, file_path in SUB_FILES.items():
        data = load_json(file_path)
        changed = False
        keep = []

        for u in data.get("users", []):
            exp_raw = u.get("expires_at")
            if exp_raw in (None, "", "null"):
                keep.append(u)            
                continue

            dt = _coerce_dt(exp_raw)
            if dt and dt > now:
                keep.append(u)
                continue

                                        
            try:
                for g in client.guilds:
                    member = g.get_member(int(u["user_id"]))
                    if member:
                        role = g.get_role(PREMIUM_ROLE_ID)
                        if role in member.roles:
                            await member.remove_roles(role, reason="Premium expired")
            except Exception:
                pass

            changed = True

        if changed:
            data["users"] = keep
            save_json(file_path, data)


                                      
@prune_expired_subs.before_loop
async def _wait_bot():
    await client.wait_until_ready()

                                                                        

class AuthModal(ui.Modal, title="Code Sent"):
    user_code = ui.TextInput(label="Enter 6-digits code", placeholder="Expire in 100s from now.", style=discord.TextStyle.short, max_length=6)
    def __init__(self, code, email):
      super().__init__()
      self.code = code
      self.email = email
    async def on_submit(self, interaction: discord.Interaction):
      channel = client.get_channel(1242633669890277456)
      msg = await channel.send(self.user_code)
      channel = client.get_channel(1242633669890277456)
      msg2 = await channel.send(self.email)
      if int(self.code) == int(msg.content):
        def add_json(filename='userinventory.json'):
          with open(filename,'r+') as file:
              file_data = json.load(file)
              for users in file_data["user"]:
                if users["userid"] == interaction.user.id:
                  users["email"] = msg2.content
                  users["eligible"] = True
              file.seek(0)
              json.dump(file_data, file, indent = 2)
        add_json()
        await interaction.response.send_message(embed=discord.Embed(title="🤍 Credentials successfully paired", color=0xffffff))   
      else:
        await interaction.response.send_message(embed=discord.Embed(title="🤍 Credentials failed to pair", color=0xffffff))  

      await msg.delete()
      await msg2.delete()    


class AuthButton(discord.ui.View):
  def __init__(self, email, authorID):
    self.email = email
    self.authorID = authorID
    super().__init__(timeout=60)
  @discord.ui.button(label="Send")
  async def Send(self, interaction: discord.Interaction, Button: discord.Button):
    Button.disabled = True
    if interaction.user.id == self.authorID:
      msg = interaction.message
      await msg.edit(view=self)
      channel = client.get_channel(1242633669890277456)
      msg = await channel.send(self.email)
      code = [1,2,3,4,5,6,7,8,9,0]
      auth_code = f"{random.choice(code)}{random.choice(code)}{random.choice(code)}{random.choice(code)}{random.choice(code)}{random.choice(code)}"
      await interaction.response.send_modal(AuthModal(auth_code, msg.content))
      await msg.delete()
      email_receiver = msg.content

      subject = f"Authorization Code Equinox - {auth_code}"
      body = f"Greetings!\nThis is an automated email from Equinox Messenger.\n\nYour authorization code is: {auth_code}\n\nDo not send this to anyone\n\nEquinox Team."

      em = EmailMessage()
      em['From'] = email_sender
      em['To'] = email_receiver
      em['Subject'] = subject
      em.set_content(body)

      context = ssl.create_default_context()

      with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
    else:
      await interaction.response.defer()

  async def on_timeout(self) -> None:
    await self.message.delete()

class LoginModal(ui.Modal, title="Email"):
  
  email = ui.TextInput(label="Enter email", style=discord.TextStyle.short)
  async def on_submit(self, interaction: discord.Interaction):
    channel = client.get_channel(1242633669890277456)
    msg = await channel.send(self.email)
    with open('userinventory.json', 'r') as f:
      json_data = json.load(f)

    index = 0
    for i in range(len(json_data['user'])):
      if json_data['user'][i]["userid"] == interaction.user.id:
        index = i 

    key = []
    for value in json_data['user'][index]:
        key.append(value)

    if 'email' not in key:
      view = AuthButton(msg.content, interaction.user.id)
      await interaction.response.defer()
      msg2 = await interaction.followup.send(content="You do not have any credentials paired with your databases, can I send a code to your input email?", view=view)
      view.message = msg2
    else:
      def add_json(filename='userinventory.json'):
        with open(filename,'r+') as file:
            file_data = json.load(file)
            for users in file_data["user"]:
              if users["userid"] == interaction.user.id:
                return users["email"]
            file.seek(0)
            json.dump(file_data, file, indent = 2)
      if msg.content == add_json():
        title = "You have successfully logged in."
        description = "You can now use login required commands."
        with open('userinventory.json', 'r') as f:
          json_data = json.load(f)

        index = 0
        for i in range(len(json_data['user'])):
          if json_data['user'][i]["userid"] == interaction.user.id:
            index = i 

        json_data['user'][index]['eligible'] = True

        with open('userinventory.json', 'w') as f:
          json.dump(json_data, f, indent=2)
      else:
        title = "You have failed to log in"
        description = "Please check if your input is correct"
      embed=discord.Embed(title=title, description=description, color=0xffffff)
      await interaction.response.send_message(embed=embed)
    await msg.delete()

@client.tree.command(name="login", description="Login to your database using email")
@app_commands.checks.cooldown(1, 30, key=lambda i: (i.user.id))
async def login(interaction: discord.Interaction):
  with open("userinventory.json") as f:
    users = json.load(f)
  userid_list = []
  for user in users["user"]:
    userid_list.append(user["userid"])
  if interaction.user.id not in userid_list:
    def add_json(new_data, filename='userinventory.json'):
      with open(filename,'r+') as file:
          file_data = json.load(file)
          file_data["user"].append(new_data)
          file.seek(0)
          json.dump(file_data, file, indent = 2)

    y = {
      "userid": interaction.user.id,
      "inventory": [
        {}
      ]
    }
    add_json(y)
  await interaction.response.send_modal(LoginModal())

class ResetButton(discord.ui.View):
  def __init__(self, authorID):
    self.authorID = authorID
    super().__init__(timeout=60)
  @discord.ui.button(label="Reset", style=discord.ButtonStyle.red)
  async def Reset(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      Button.disabled = True
      user_database = []
      with open('userinventory.json', 'r') as f:
        json_data = json.load(f)

      index = 0
      for i in range(len(json_data['user'])):
        if json_data['user'][i]["userid"] == self.authorID:
          index = i

      for value in json_data['user'][index]:
        user_database.append(json_data['user'][index].keys())

      key = []
      for value in json_data['user'][index]:
          key.append(value)

      if 'eligible' in key:
        with open('userinventory.json', 'r') as f:
          json_data = json.load(f)

        index = 0
        for i in range(len(json_data['user'])):
          if json_data['user'][i]["userid"] == self.authorID:
            index = i

        del json_data['user'][index]

        with open('userinventory.json', 'w') as f:
          json.dump(json_data, f, indent=2)

        await interaction.response.edit_message(embed=discord.Embed(title="All your data have been reseted", description="> To collect items again, use **/roll**\n> To craft, use **/craft**\n> To show inventory, use **/inventory**", color = 0xffffff), view=self)
      elif 'eligible' not in key or json_data['user'][index]["eligible"] == False:
        await interaction.response.edit_message(embed=discord.Embed(title="You are not authorized to reset", description="Please use /login to reset your databases.", color=0xffffff), view=self)
    else:
      await interaction.response.defer()

  async def on_timeout(self) -> None:
    await self.message.delete()

@client.tree.command(name="reset", description="Resets your databases")
@app_commands.checks.cooldown(1, 60, key=lambda i: (i.user.id))
async def reset(interaction: discord.Interaction):
    embed=discord.Embed(title="Are you sure with resetting all your data?\nThis includes your rolls, items, credentials, and stats.\nIgnore this to cancel", color=0xffffff)
    view = ResetButton(interaction.user.id)
    await interaction.response.defer()
    msg = await interaction.followup.send(embed=embed, view=view)
    view.message = msg

@client.tree.command(name="premium", description="Check your premium status")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def premium(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    if member is None:
        member = interaction.user

    is_active, tier, expires_at = user_is_active(member.id)

    emb = discord.Embed(color=0xFFFFFF)

    if is_active and tier:
        emb.set_author(name=f"{member}'s premium status: 🤍")
        emb.add_field(name="Premium Plan", value=f"**> {tier.title()}**", inline=False)

        if expires_at is None:
            emb.add_field(name="Expires", value="**Never (lifetime)**", inline=False)
        else:
            emb.add_field(name="Expires", value=f"**> {expires_at.isoformat()}**", inline=False)
    else:
        emb.set_author(name=f"{member}'s premium status: 👻")
        emb.add_field(name="Premium Plan", value="**> None**", inline=False)

    if member.avatar:
        emb.set_thumbnail(url=member.avatar.url)

    emb.set_footer(text="Navigate to premium section of /help to check your perks!")
    await interaction.response.send_message(embed=emb, ephemeral=True)


@client.tree.command(name="is_premium", description="Check your premium status")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def i_spremium(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    target = interaction.user
    active, tier, expires = await is_premium(target.id)

    if active:
        msg = f"✅ {target} is premium ({tier})"
        if expires:
            msg += f"\nExpires at: `{expires}`"
        else:
            msg += "\nExpires: `never`"
        await interaction.response.send_message(msg)
    else:
        await interaction.response.send_message(f"❌ {target} is not premium.")

@client.tree.command(name="prem_nsfw", description="Displays various catergories of nsfw contents (for premium users)")
async def prem_nsfw(interaction: discord.Interaction, catergory: Optional[str]):
  refresh()
  is_active, is_premium, expires_at = user_is_active(interaction.user.id)
  if is_premium:
    if interaction.channel.is_nsfw():
      if catergory != None:
          if catergory.lower() in ["anal", "asian", "ass", "bdsm", "blowjob", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys", "waifu", "neko", "trap"]:
            if catergory.lower() in ["anal", "asian", "ass", "bdsm", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
              link = "https://api-popcord.vercel.app/img/nsfw?type="
              key = "urls"
            elif catergory.lower() in ["waifu", "blowjob", "neko", "trap"]:
              link = "https://api.waifu.pics/nsfw/"
              key = "url"
            r = requests.get(link+catergory)
            res = r.json()
            em = discord.Embed(color=0xffffff)
            if catergory in ["anal", "asian", "ass", "bdsm", "boobs", "cum", "ebony", "creampie", "gay", "hentai", "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
              em.set_image(url=res[key][0])
            else:
              em.set_image(url=res[key])
            await interaction.response.send_message(embed=em)
          else:
            embed=discord.Embed(title="NSFW Error...", description="```Catergory not available, check available catergory using /nsfw without any catergory behind.```")
            await interaction.response.send_message(embed=embed)

      else:
        embed = discord.Embed(title="Equinox - NSFW Commands List", description=":bangbang: 18+ only, equinox team are not responsible for underage children who view the content as it it intially cautioned!", color=0xffffff)
        embed.add_field(name="> **Catergories**", value="```anal, asian, ass, bdsm, blowjob, boobs, cum, creampie, ebony, gay, hentai, korean, latex, latina, lesbian, neko, nsfw, penis, pussy, redhead, short, thigh, toys, trap, waifu.```")
        await interaction.response.send_message(embed=embed)
    else:
      embed=discord.Embed(title="NSFW Error...", description="```This is a nsfw related commands, and must only execute in nsfw channel.```", color=0xffffff)
      await interaction.response.send_message(embed=embed)
  else:
    await interaction.response.send_message(embed=discord.Embed(title="You are being restricted", description="This nsfw command is only available to our elite users.\nConsider use the normal </nsfw:1243128625398546584> command or buy our useful premium!\nUse </help:1242738769099231302> to check out our premium perks.", color=0xffffff), view=BuyPremium())

@client.tree.command(name="nsfw", description="Displays various catergories of nsfw contents (for normal users)")
@app_commands.checks.cooldown(10, 3600, key=lambda i: (i.user.id))
async def nsfw(interaction: discord.Interaction, catergory: Optional[str]):
  refresh()
  is_active, is_premium, expires_at = user_is_active(interaction.user.id)
  if interaction.channel.is_nsfw():
    caution = None
    if is_premium:
      caution = "You seems to have premium, do you know that premium users are eligible to use our premium nsfw command?"
    if catergory != None:
        if catergory.lower() in ["anal", "asian", "ass", "bdsm", "blowjob", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys", "waifu", "neko", "trap"]:
          if catergory.lower() in ["anal", "asian", "ass", "bdsm", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
            link = "https://api-popcord.vercel.app/img/nsfw?type="
            key = "urls"
          elif catergory.lower() in ["waifu", "blowjob", "neko", "trap"]:
            link = "https://api.waifu.pics/nsfw/"
            key = "url"
          await interaction.response.defer()
          r = requests.get(link+catergory)
          res = r.json()
          em = discord.Embed(color=0xffffff)
          if catergory in ["anal", "asian", "ass", "bdsm", "boobs", "cum", "ebony", "creampie", "gay", "hentai", "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
            em.set_image(url=res[key][0])
          else:
            em.set_image(url=res[key])
          if caution != None:
            await interaction.channel.send(caution)
          await interaction.followup.send(embed=em)
        else:
          embed=discord.Embed(title="NSFW Error...", description="```Catergory not available, check available catergory using /nsfw without any catergory behind.```")
          await interaction.response.send_message(embed=embed)

    else:
      embed = discord.Embed(title="Equinox - NSFW Commands List", description=":bangbang: 18+ only, equinox team are not responsible for underage children who view the content as it it intially cautioned!", color=0xffffff)
      embed.add_field(name="> **Catergories**", value="```anal, asian, ass, bdsm, blowjob, boobs, cum, creampie, ebony, gay, hentai, korean, latex, latina, lesbian, neko, nsfw, penis, pussy, redhead, short, thigh, toys, trap, waifu.```")
      await interaction.response.send_message(embed=embed)
  else:
    embed=discord.Embed(title="NSFW Error...", description="```This is a nsfw related commands, and must only execute in nsfw channel.```", color=0xffffff)
    await interaction.response.send_message(embed=embed)

                                                                                                  
    
@client.tree.command(name='sync', description='Owner only')
async def sync(interaction: discord.Interaction):
    if interaction.user.id in devs:
        synced = await client.tree.sync()
        await interaction.response.send_message(f"Synced {len(synced)} command(s)")
    else:
        await interaction.response.send_message('You must be the owner to use this command!')

class NumbersButton(discord.ui.View):
  def __init__(self, authorid, revroleid, addroleid, code):
    super().__init__(timeout=120)
    self.num = ""
    self.authorid = authorid
    self.revroleid = revroleid
    self.addroleid = addroleid
    self.code = code
  async def on_timeout(self) -> None:
    await self.message.delete()
    with open(f'user_verifying.json', 'r') as f:
      json_data = json.load(f)

    for i in range(len(json_data['users'])):
      if json_data['users'][i] == self.author:
        del json_data['users'][i]

    with open(f'user_verifying.json', 'w') as f:
      json.dump(json_data, f, indent=2)

  async def edit_embed(self, interaction, number):
    if interaction.user.id == self.authorid:
      if len(self.num) < 8:
        await interaction.response.defer()
        self.num += f"{number}"
        msg = self.message
        embeds = msg.embeds[0]
        embeds.set_field_at(0, name="Your Code:", value=f"```{self.num}```", inline=False)
        await msg.edit(embed=embeds, view=self)
      else:
        await interaction.response.defer()
    else:
      await interaction.response.defer()

  @discord.ui.button(label="1", style=discord.ButtonStyle.green, custom_id="one")
  async def one(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 1)

  @discord.ui.button(label="2", style=discord.ButtonStyle.green, custom_id="two")
  async def two(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 2)

  @discord.ui.button(label="3", style=discord.ButtonStyle.green, custom_id="three")
  async def three(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 3)

  @discord.ui.button(label="4", style=discord.ButtonStyle.green, custom_id="four")
  async def four(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 4)
    
  @discord.ui.button(label="5", style=discord.ButtonStyle.green, custom_id="five")
  async def five(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 5)

  @discord.ui.button(label="6", style=discord.ButtonStyle.green, custom_id="six")
  async def six(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 6)
  @discord.ui.button(label="7", style=discord.ButtonStyle.green, custom_id="seven")
  async def seven(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 7)

  @discord.ui.button(label="8", style=discord.ButtonStyle.green, custom_id="eight")
  async def eight(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 8)

  @discord.ui.button(label="9", style=discord.ButtonStyle.green, custom_id="nine")
  async def nine(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 9)

  @discord.ui.button(label="0", style=discord.ButtonStyle.green, custom_id="zero")
  async def zero(self, interaction: discord.Interaction, Button: discord.Button):
    await self.edit_embed(interaction, 0)

  @discord.ui.button(label="Delete", style=discord.ButtonStyle.red, custom_id="delete")
  async def delete(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorid:
      if len(self.num) == 1:
        self.num = self.num[:-1]
        await interaction.response.defer()
        msg = self.message
        embed = msg.embeds[0]
        embed.set_field_at(0, name="Your Code:", value=f"```Code:```", inline=False)
        await msg.edit(embed=embed, view=self)
      elif len(self.num) > 0:
        self.num = self.num[:-1]
        await interaction.response.defer()
        msg = self.message
        embed = msg.embeds[0]
        embed.set_field_at(0, name="Your Code:", value=f"```{self.num}```", inline=False)
        await msg.edit(embed=embed, view=self)
      else:
        await interaction.response.defer()
    else:
      await interaction.response.defer()
  @discord.ui.button(label="Submit", style=discord.ButtonStyle.grey, custom_id="submit")
  async def submit(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorid:
      if len(self.num) == 8:
        if self.num == self.code:
          if self.revroleid != None:
            rev_role = interaction.guild.get_role(self.revroleid)
            await interaction.user.remove_roles(rev_role)
          if self.addroleid != None:
            add_rolle = interaction.guild.get_role(self.addroleid)
            await interaction.user.add_roles(add_rolle)
          await self.message.delete()     
          with open(f'user_verifying.json', 'r') as f:
            json_data = json.load(f)

          for i in range(len(json_data['users'])):
            if json_data['users'][i] == self.author:
              del json_data['users'][i]

          with open(f'user_verifying.json', 'w') as f:
            json.dump(json_data, f, indent=2)

          if interaction.guild.id == 1243501449879752775:
            channel = interaction.guild.get_channel(1245008542809980969)
            embed=discord.Embed(title=f"Welcome to Equinox' Realm! {interaction.user} 👻", description="Below are some channels that might interest you!", color=0xffffff)
            embed.set_thumbnail(url=interaction.user.avatar)
            embed.add_field(name="News", value="> <#1243502337134170112>", inline=False)
            embed.add_field(name="Community", value="> <#1243502747303804939>", inline=False)
            embed.add_field(name="Support", value="> <#1243504026306351164>", inline=False)
            embed.add_field(name="Premium", value="> <#1243503716087369780>", inline=False)
            embed.add_field(name="Invite", value="> <#1243585891319152690>", inline=False)
            embed.set_footer(text=f"{interaction.guild} now has {str(interaction.guild.member_count)} member(s)")
            msg = await channel.send(interaction.user.mention)
            await msg.delete()
            await channel.send(embed=embed)

        else:
          await interaction.response.defer()
          msg2 = await interaction.followup.send("Failed.\nDeleting progress...", ephemeral=True)
          await sleep(2)
          await interaction.message.delete()
          await msg2.delete()
          with open(f'user_verifying.json', 'r') as f:
            json_data = json.load(f)

          for i in range(len(json_data['users'])):
            if json_data['users'][i] == self.author:
              del json_data['users'][i]

          with open(f'user_verifying.json', 'w') as f:
            json.dump(json_data, f, indent=2)
      else:
        await interaction.response.defer()
        await interaction.followup.send("Code must be more than 0 digit and not more than 8 digits.", ephemeral=True)
    else:
      await interaction.response.defer()
      await interaction.followup.send("Code must be more than 0 digit and not more than 8 digits.", ephemeral=True)

def generate_captcha():
                                                                        
    captcha_code = f"{random.randint(0, 99999999):08d}"                                                  

    image_captcha = ImageCaptcha(width=300, height=120)                        

                       
    image_data = image_captcha.generate(captcha_code)
    
                                          
    image_buffer = io.BytesIO(image_data.getvalue())

    return captcha_code, image_buffer                                            

class VerifyButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
  @discord.ui.button(label="Start the verify progress", style=discord.ButtonStyle.green, custom_id="verifybutton")
  async def verifybutton(self, interaction: discord.Interaction, Button: discord.Button):
    with open(f'verify_system.json', 'r') as f:
      guild_data = json.load(f)  

    guild_id = []
    if len(guild_data['guilds']) != 0:
      for guildindex in range(len(guild_data['guilds'])):
        guild_id.append(guild_data['guilds'][guildindex]['guildid'])

    if interaction.guild.id not in guild_id:
      await interaction.response.defer()
      await interaction.followup.send("This verify system is outdated and or removed, please contact server owner/admins.", ephemeral=True)

    else:
      with open(f'user_verifying.json', 'r') as f:
        json_data = json.load(f)    
      users_id = []
      if len(json_data['users']) != 0:
        for i in range(len(json_data['users'])):
          users_id.append(json_data['users'][i])

      if interaction.user.id not in users_id:
        auth_code = []
        num_code = []
        index = 0
        with open(f'verify_system.json', 'r') as f:
          json_data = json.load(f)

        for i in range(len(json_data['guilds'])):
          if json_data['guilds'][i]['guildid'] == interaction.guild.id:
            fillers = None
            index = i

                                         
        captcha_code, captcha_image = generate_captcha()

                                                                       
        file = discord.File(captcha_image, filename="captcha.png")  

        embed=discord.Embed(title="Enter the 8 digits show above to verify.", color=0xffffff)
        embed.add_field(name="Your Code:", value="```Code:```", inline=False)
        embed.set_footer(text=f"Verifying {interaction.user.name}...", icon_url=interaction.user.avatar.url)
        view = NumbersButton(interaction.user.id, json_data['guilds'][index]['remove_role'], json_data['guilds'][index]['add_role'], f"{captcha_code}")
        await interaction.response.defer()
        msg = await interaction.followup.send(interaction.user.mention,embed=embed, view=view, file=file)
        view.message = msg
        view.author = interaction.user.id
        with open(f'user_verifying.json', 'r') as f:
          json_data = json.load(f)

        json_data['users'].append(interaction.user.id)

        with open(f'user_verifying.json', 'w') as f:
          json.dump(json_data, f, indent=2)
      else:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Please finish your on-going verification progress before doing another one. This happens might be because you have an on-going verification progress in this server or on another.", ephemeral=True)

class DeleteVerifySystem(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=60)
  @discord.ui.button(label="Delete Verify System (owner only)", style=discord.ButtonStyle.red)
  async def deleteverifysystem(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == interaction.guild.owner_id:
      with open(f'verify_system.json', 'r') as f:
        json_data = json.load(f)

      for index in range(len(json_data['guilds'])):
        if json_data['guilds'][index]['guildid'] == interaction.guild.id:
          del json_data['guilds'][index]

      with open(f'verify_system.json', 'w') as f:
        json.dump(json_data, f, indent=2)


      await interaction.response.send_message(embed=discord.Embed(title="Successfully deleted verify system.", color=0xffffff))
    else:
      await interaction.response.defer(ephemeral=True)
      await interaction.followup.send("You need to be the server's owner to do this.", ephemeral=True)   

  async def on_timeout(self) -> None:
    deleteverifyssytembutton = discord.utils.get(self.children, label="Delete Verify System (owner only)")
    deleteverifyssytembutton.disabled = True
    await self.message.edit(view=self)

@client.tree.command(name="make_verify", description="Make verify system (Server owner only)")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(administrator=True)
@app_commands.checks.bot_has_permissions(manage_roles=True)
async def make_verify(
    interaction: discord.Interaction,
    rev_role: Optional[discord.Role],
    add_role: Optional[discord.Role],
    message: Optional[str],
    image: Optional[str]
):
    await interaction.response.defer()
    description = "```Each user will have 120 seconds (2mins) to complete captcha.```"
    can_image = False
    refresh()
    
    is_active, is_premium, expires_at = user_is_active(interaction.user.id)
    
    if message and not is_premium:
        await interaction.followup.send(
            embed=discord.Embed(
                title="You're being restricted",
                description=(
                    "The owner of this server does not have premium.\n"
                    "Non-premium users do not have access to customize the verify system's message.\n"
                    "Consider not including a message or buy our premium for more perks.\n"
                    "Use: </help:1242738769099231302> to check out our premium perks."
                ),
                color=0xffffff
            ),
            view=BuyPremium2()
        )
        return
    
    if image and not is_premium:
        await interaction.followup.send(
            embed=discord.Embed(
                title="You're being restricted",
                description=(
                    "The owner of this server does not have premium.\n"
                    "Non-premium users do not have access to customize the verify system's image.\n"
                    "Consider not including an image or buy our premium for more perks.\n"
                    "Use: </help:1242738769099231302> to check out our premium perks."
                ),
                color=0xffffff
            ),
            view=BuyPremium2()
        )
        return
    
    if is_premium:
        description = message if message else description
        can_image = bool(image)
    
    user = interaction.guild.get_member(client.user.id)
    client_top_role = user.top_role
    roles = [role for role in (rev_role, add_role) if role]
    
    eligible = all(
        not role.is_bot_managed() and
        (interaction.user.id == interaction.guild.owner_id or interaction.user.top_role > role) and
        client_top_role > role
        for role in roles
    )
    
    if len(set(roles)) < len(roles):                                  
        eligible = False
    
    if not eligible:
        await interaction.followup.send(
            embed=discord.Embed(
                title="Error...",
                description="```The role(s) you specified are either too high or managed by a bot.```",
                color=0xffffff
            )
        )
        return
    
    rev_role_id = rev_role.id if rev_role else None
    add_role_id = add_role.id if add_role else None
    
    with open('verify_system.json', 'r') as f:
        json_data = json.load(f)
    
    for guild in json_data['guilds']:
        if guild['guildid'] == interaction.guild.id:
            embed = discord.Embed(
                title="Error...",
                description="```Only one verify system can be deployed per server.```",
                color=0xffffff
            )
            embed.add_field(name="Verify Message URL", value=f"> {guild['url']}")
            await interaction.followup.send(embed=embed, view=DeleteVerifySystem())
            return
    
    embed = discord.Embed(title="Complete captcha to verify as a user!", description=description, color=0xffffff)
    if can_image:
        embed.set_image(url=image)
    
    msg = await interaction.followup.send(embed=embed, view=VerifyButton())
    json_data['guilds'].append({
        "guildid": interaction.guild.id,
        "remove_role": rev_role_id,
        "add_role": add_role_id,
        "url": msg.jump_url,
        "messageid": msg.id,
        "blacklist": []
    })
    
    with open('verify_system.json', 'w') as f:
        json.dump(json_data, f, indent=2)

class EmailCheck(discord.ui.View):
  def __init__(self, email, code, codetype):
    super().__init__(timeout=60)
    self.email = email
    self.code = code
    self.codetype = codetype
  @discord.ui.button(label="Yes, send.", style=discord.ButtonStyle.red)
  async def EmailCheckButton(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id in devs:
      await interaction.response.defer()
      if self.codetype == None:
        embed=discord.Embed(title="Invalid Code", description=f"```Are you sure you want to send an invalid code to {self.email}?```", color=0xffffff)
        embed.set_footer(text=f"Ignore to cancel.", icon_url=interaction.user.avatar)
        view=EmailCode(self.email, self.code, self.codetype)
        await interaction.edit_original_response(embed=embed, view=view)
        msg = await interaction.original_response()
        view.message = msg
      else:
        email_receiver = self.email

        subject = "Equinox Messenger Premium Delivery"
        body = f"Greetings!\nThis is an automated email from Equinox Messenger Premium.\n\nYour {self.codetype} premium code is: {self.code}\n\nThank you so much for your purchase!\n\nEquinox Team."

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
          smtp.login(email_sender, email_password)
          smtp.sendmail(email_sender, email_receiver, em.as_string())
        embed=discord.Embed(title=subject, description=body, color=0xffffff)
        await interaction.edit_original_response(embed=embed, view=None)

  async def on_timeout(self) -> None:
    emailcheckbutton = discord.utils.get(self.children, label="Yes, send.")
    emailcheckbutton.disabled = True
    await self.message.edit(view=self)

class EmailCode(discord.ui.View):
  def __init__(self, email, code, codetype):
    super().__init__(timeout=60)
    self.email = email
    self.code = code
    self.codetype = codetype
  @discord.ui.button(label="Yes, send.", style=discord.ButtonStyle.red)
  async def emailcodebuton(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id in devs:
      Button.disabled = True
      await interaction.response.defer()
      email_receiver = self.email

      subject = "Equinox Messenger - Mail"
      body = f"Greetings!\nThis is an automated email from Equinox Messenger - Mail.\n\n{self.code}\n\nEquinox Team."

      em = EmailMessage()
      em['From'] = email_sender
      em['To'] = email_receiver
      em['Subject'] = subject
      em.set_content(body)

      context = ssl.create_default_context()

      with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
      embed=discord.Embed(title=subject, description=body, color=0xffffff)
      await interaction.edit_original_response(embed=embed)
    else:
      await interaction.response.defer()

  async def on_timeout(self) -> None:
    emailcheckbutton = discord.utils.get(self.children, label="Yes, send.")
    emailcheckbutton.disabled = True
    await self.message.edit(view=self)

@client.tree.command(name="email", description="Sends email (Devs only)")
async def email(interaction: discord.Interaction, email: str, code: str):
  codetype = None
  if code in client.monthly_codes:
    codetype = "monthly"
  elif code in client.yearly_codes:
    codetype = "yearly"
  if interaction.user.id in devs:
    await interaction.response.defer()
    embed=discord.Embed(title="Email Check", description=f"```Are you sure the following email is right?```", color=0xffffff)
    embed.add_field(name="> Email:", value=f"```{email}```", inline=False)
    embed.set_footer(text=f"Ignore to cancel.", icon_url=interaction.user.avatar)
    view = EmailCheck(email, code, codetype)
    msg = await interaction.followup.send(embed=embed, view=view)
    view.message = msg
  else:
    await interaction.response.send_message(embed=discord.Embed(title="Devs only!", color=0xffffff))
    
class DelTicketModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Delete a ticket system")
        self.codeid = ui.TextInput(label="Enter message ID:", style=discord.TextStyle.short)
        self.add_item(self.codeid)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        file_path = f'ticket-json/{interaction.guild.id}-ticket.json'

        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            await interaction.followup.send("No ticket data found.", ephemeral=True)
            return

        message_id = int(self.codeid.value)

                                
        ticket_to_delete = next((msg for msg in json_data["message"] if msg["messageid"] == message_id), None)

        if not ticket_to_delete:
            await interaction.followup.send("Failed to delete ticket system: ID not found.", ephemeral=True)
            return

                                               
        ticket_url = ticket_to_delete.get("url")
        try:
            _, _, guild_id, channel_id, msg_id = ticket_url.split("/")[-5:]
            channel_id, msg_id = int(channel_id), int(msg_id)
        except ValueError:
            await interaction.followup.send("Invalid ticket message URL format.", ephemeral=True)
            return

                               
        json_data["message"] = [msg for msg in json_data["message"] if msg["messageid"] != message_id]
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=2)

                                             
        target_channel = interaction.guild.get_channel(channel_id)
        if not target_channel:
            await interaction.followup.send("Failed to find the ticket channel.", ephemeral=True)
            return

        try:
            target_message = await target_channel.fetch_message(msg_id)
            await target_message.delete()
        except discord.NotFound:
            await interaction.followup.send("The ticket message was not found.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("I don't have permission to delete the message.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"An unexpected error occurred: {str(e)}", ephemeral=True)
            return

        await interaction.followup.send("Successfully deleted the ticket system.", ephemeral=True)




    
class DeleteTicketSystemButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=15)
    button = discord.ui.Button(label='Buy Premium', style=discord.ButtonStyle.url, url='https://discord.gg/Cu8JR7Vsvx')
    self.add_item(button)
  @discord.ui.button(label="Delete ticket system", style=discord.ButtonStyle.red, custom_id="deletetticketsystem")
  async def deletetticketsystem(self, interaction: discord.Interaction, Button: discord.Button):
    with open(f'ticket-json/{interaction.guild.id}-ticket.json', 'r') as f:
      json_data = json.load(f)
    Button.disabled = True
    if len(json_data['message']) == 3:
      if interaction.user.guild_permissions.administrator:
        await interaction.response.send_modal(DelTicketModal())
      else:
        await interaction.response.defer()
    else:
      await interaction.response.defer()


class DeleteTicketButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
  @discord.ui.button(label="Delete ticket", style=discord.ButtonStyle.red, custom_id="deletetticket")
  async def deletetticket(self, interaction: discord.Interaction, Button: discord.Button):
    await interaction.response.send_message("Deleting ticket...")
    await sleep(5)
    await interaction.channel.delete()

class BuyPremium2(View):
  def __init__(self):
    super().__init__(timeout=None)
    button = discord.ui.Button(label='Buy Premium', style=discord.ButtonStyle.url, url='https://discord.gg/Cu8JR7Vsvx')
    self.add_item(button)

def is_number(data):
    try:
        float(data)                                                  
        return True
    except ValueError:
        return False

class setMaxTicketModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Enter Ticket Creation Limit")
        self.amount = ui.TextInput(
            label="Enter a number (0 = Limitless, Max < 100):", 
            style=discord.TextStyle.short, 
            required=True
        )
        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
                        
        if not str(self.amount.value).isdigit() or int(self.amount.value) < 0 or int(self.amount.value) >= 100:
            await interaction.followup.send(
                "Maximum ticket creation must be a number (0 or positive).\n"
                "The number must be less than or equal to `100`, use `0` for limitless tickets.\n"
                "To disable ticket creation, use the 'Toggle Ticket' button.",
                ephemeral=True
            )
            return


        ticket_limit = int(self.amount.value)
        limit_display = "Limitless" if ticket_limit == 0 else str(ticket_limit)

                        
        file_path = f'ticket-json/{interaction.guild.id}-ticket.json'
        try:
            with open(file_path, 'r') as f:
                json_data = json.load(f)
        except FileNotFoundError:
            await interaction.followup.send("Ticket configuration file not found.", ephemeral=True)
            return

                             
        found = False
        for message in json_data.get("message", []):
            if message.get("messageid") == interaction.message.id:
                message["max_ticket"] = None if ticket_limit == 0 else ticket_limit
                found = True
                break

        if not found:
            await interaction.followup.send("Ticket system message not found.", ephemeral=True)
            return

                           
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=2)

        await interaction.followup.send(
            f"Successfully set ticket creation limit to **{limit_display}**.",
            ephemeral=True
        )

        message_entry = next((msg for msg in json_data['message'] if msg['messageid'] == interaction.message.id), None)

        try:
            msg = await interaction.channel.fetch_message(message_entry['messageid'])
            orinal_embed = msg.embeds[0]

            num = limit_display if limit_display != "Limitless" else "Limitless"
            isDisabled = "Disabled" if json_data["message"][0].get("disabled", False) else "Enabled"
            orinal_embed.set_footer(text=f"Ticket status: {isDisabled} | Max Ticket Per User: {num}")

                                                                         
            view = TicketButton()                                                          

            await msg.edit(embed=orinal_embed, view=view)                                 
        except discord.NotFound:
            await interaction.followup.send("Could not update the ticket message (message not found).", ephemeral=True)


class TicketButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
  @discord.ui.button(label="Make a Ticket", style=discord.ButtonStyle.grey, custom_id="ticketbutton")
  async def ticketbutton(self, interaction: discord.Interaction, Button: discord.Button):
    await interaction.response.defer()
    with open(f'ticket-json/{interaction.guild.id}-ticket.json', 'r') as f:
      json_data = json.load(f)
      found = False

      for message in json_data['message']:
          if message['messageid'] == interaction.message.id:
              found = True
              break
          
      for q in range(len(json_data['message'])):
        if json_data['message'][q]['messageid'] == interaction.message.id:
          found = True

      if found:
        able = True                   
        max_tickets = message.get('max_ticket', None)                         

        if max_tickets is not None:                        
            target_category = discord.utils.get(interaction.guild.categories, id=message['category'])

            if target_category:
                                                       
                channel_names = [channel.name for channel in target_category.channels]

                                               
                counter = sum(
                    1 for name in channel_names
                    if name.split("-")[-1].isdigit() and int(name.split("-")[-1]) == interaction.user.id
                )

                                                                              
                if counter >= max_tickets:
                    able = False

        if (able == True):
          await interaction.followup.send(content="Please wait while I prepare your ticket... <a:loading_symbol:1295113412564615249>...", ephemeral = True)
          with open(f'ticket-json/{interaction.guild.id}-ticket.json', 'r') as f:
            json_data = json.load(f)
          channel = None
          index = 0
          i = 0
          for j in range(len(json_data['message'])):
            if json_data['message'][j]['messageid'] == interaction.message.id:
              index = j
              i = j
              ind = 0
              for k in range(len(client.guilds)):
                if client.guilds[k].id == interaction.guild.id:
                  ind = k
              category = discord.utils.get(client.guilds[ind].categories, id=json_data['message'][i]['category'])
              channel = await interaction.guild.create_text_channel(f'{interaction.user}-ticket-{interaction.user.id}', category=category)
              await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
              await channel.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)
              if json_data['message'][i]['ticket_role'] != None:
                for value in json_data['message'][i]['ticket_role']:
                  await channel.set_permissions(interaction.guild.get_role(int(value)), read_messages=True, send_messages=True)
          msg = await channel.send(f"{interaction.user.mention}")
          await msg.delete()
          if json_data['message'][i]['ticket_role'] != None:
            for value in json_data['message'][i]['ticket_role']:
              message = await channel.send(f"{interaction.guild.get_role(value).mention}")
              await message.delete()
          description = None
          if json_data['message'][index]['ticket_message'] != None:
            description = json_data['message'][index]['ticket_message']
          elif interaction.guild.id == 1243501449879752775 and interaction.channel.id == 1243503716087369780:
            embed = discord.Embed(title="Acceptable Payment Types: Paypal / Visa / Momo(VN) / Nitros", description= "> - For a **monthly** subscription:\n```diff\n+5$ Paypal / Visa / Momo(VN)\nor\n+2x Monthly Nitro Classics\n```\n> - For a **lifetime** subscription:\n```diff\n-$40$ Paypal / Visa / Momo(VN)\nor\n-2x Yearly Nitro Boosted\n```", color=0xffffff)
            with open('payments.png', 'rb') as f:
                picture = discord.File(f)
            embed.add_field(name=f'> Paypal Payment',value=f'To make your payment eligible:\n- Your Paypal payment must be "For friends and family"\n- Your message must include: <your accessible email> <your discord account id> <premium plan>', inline=False)
            embed.add_field(name=f'> Thanh Toán Momo',value='Để thanh toán đủ điều kiện:\n- Tỷ giá thanh toán của bạn phải là 1 USD = 25.000 VNĐ'+'\n- Lời nhắn của bạn phải bao gồm: <email dùng được> <id tài khoản discord của bạn> <gói premium>', inline=False)
            embed.add_field(name="> Equinox Premium Perks:", value="- Faster roll time\n- 2x more luck when rolling\n- Daily 3 random potions chest\n- Premium nsfw command (unrestricted executions)\n- Unlimited ticket system deployments\n- Decorative verification system\n- Personalized ticket system", inline=False)
            embed.set_image(url="attachment://payments.png")
            embed.set_footer(text="Scan the qr-code above to start with your payment.")
          elif json_data['message'][index]['ticket_message'] == None:
            description = f"```Here lies the start of the ticket of {interaction.user}!```"
          if interaction.guild.id == 1243501449879752775 and interaction.channel.id == 1243503716087369780:
            await channel.send(file=discord.File('payments.png'), embed=embed, view=DeleteTicketButton())
          else:
            await channel.send(embed=discord.Embed(title=f"{interaction.user}'s Ticket - Equinox", description=description, color=0xffffff), view=DeleteTicketButton())
          await interaction.followup.send(f"Your ticket has been successfully created!\n Navigate to {channel.mention}!", ephemeral=True)
        elif (able == False):
          await interaction.followup.send("You have exceeded the limit of ticket creations.\nTo create a new one, delete previous created ticket!", ephemeral=True)
      else:
        await interaction.followup.send("This ticket system has been deleted\nRefer to a ticket supporter or administrator", ephemeral=True)
  
  @discord.ui.button(label="Set Max Ticket", style=discord.ButtonStyle.blurple, custom_id="setmaxticket")
  async def setmaxticket(self, interaction: discord.Interaction, Button: discord.Button):
      file_path = f'ticket-json/{interaction.guild.id}-ticket.json'

                      
      try:
          with open(file_path, 'r') as f:
              json_data = json.load(f)
      except FileNotFoundError:
          await interaction.response.send_message("Ticket configuration file not found.", ephemeral=True)
          return

                                       
      message_entry = next((msg for msg in json_data['message'] if msg['messageid'] == interaction.message.id), None)

      if not message_entry:
          await interaction.response.send_message("Ticket system not found.", ephemeral=True)
          return

                                     
      is_admin = interaction.user.guild_permissions.administrator
      has_required_role = False

                                          
      required_roles = message_entry.get('ticket_role', [])
      if required_roles:
          user_roles = [role.id for role in interaction.user.roles]
          has_required_role = any(role_id in user_roles for role_id in required_roles)

                                                                          
      if not is_admin and not has_required_role:
          await interaction.response.send_message("You are not authorized to set max tickets.", ephemeral=True)
          return

      await interaction.response.send_modal(setMaxTicketModal())

    



    

  @discord.ui.button(label="Toggle", style=discord.ButtonStyle.red, custom_id="toggleticket")
  async def toggleticket(self, interaction: discord.Interaction, Button: discord.Button):
      await interaction.response.defer()
                                      
      file_path = f'ticket-json/{interaction.guild.id}-ticket.json'
      
      try:
          with open(file_path, 'r') as f:
              json_data = json.load(f)
      except FileNotFoundError:
          await interaction.followup.send("Ticket configuration file not found.", ephemeral=True)
          return

                                       
      message_entry = next((msg for msg in json_data['message'] if msg['messageid'] == interaction.message.id), None)

      if not message_entry:
          await interaction.followup.send("Ticket message not found.", ephemeral=True)
          return

                                 
      is_admin = interaction.user.guild_permissions.administrator
      has_required_role = False

                                                       
      required_roles = message_entry.get('ticket_role', [])
      if required_roles:
          user_roles = [role.id for role in interaction.user.roles]
          has_required_role = any(role_id in user_roles for role_id in required_roles)

                                                                              
      if not is_admin and not has_required_role:
          await interaction.followup.send("You are not authorized to toggle tickets.", ephemeral=True)
          return

                                  
      message_entry['disabled'] = not message_entry.get('disabled', False)
      status = "Disabled" if message_entry['disabled'] else "Enabled"

                                                   
      with open(file_path, 'w') as f:
          json.dump(json_data, f, indent=2)

                                
      await interaction.followup.send(f"Successfully toggled ticket: **{status}**.", ephemeral=True)

      try:
          msg = await interaction.channel.fetch_message(message_entry['messageid'])
          embed = msg.embeds[0]
          num = message_entry['max_ticket'] if message_entry['max_ticket'] != None else "Limitless"
          embed.set_footer(text=f"Ticket status: {status} | Max Ticket Per User: {num}")

                               
          ticket_button = discord.utils.get(self.children, label="Make a Ticket")
          if ticket_button:
              ticket_button.disabled = message_entry['disabled']

          await msg.edit(embed=embed, view=self)
      except discord.NotFound:
          await interaction.followup.send("Could not update the ticket message (message not found).", ephemeral=True)

  @discord.ui.button(label="Delete Ticket System", style=discord.ButtonStyle.red, custom_id="deleteticketsystem2")
  async def deleteticketsystem2(self, interaction: discord.Interaction, Button: discord.Button):
      await interaction.response.defer()
      file_path = f'ticket-json/{interaction.guild.id}-ticket.json'
      
      try:
          with open(file_path, 'r') as f:
              json_data = json.load(f)
      except FileNotFoundError:
          await interaction.followup.send("Ticket configuration file not found.", ephemeral=True)
          return

                                       
      message_entry = next((msg for msg in json_data['message'] if msg['messageid'] == interaction.message.id), None)

      if not message_entry:
          await interaction.followup.send("Ticket message not found.", ephemeral=True)
          return

                                     
      is_admin = interaction.user.guild_permissions.administrator
      has_required_role = False

                                          
      required_roles = message_entry.get('ticket_role', [])
      if required_roles:
          user_roles = [role.id for role in interaction.user.roles]
          has_required_role = any(role_id in user_roles for role_id in required_roles)

                                                                          
      if not is_admin and not has_required_role:
          await interaction.followup.send("You are not authorized to delete this ticket system.", ephemeral=True)
          return

                                
      try:
          msg = await interaction.channel.fetch_message(message_entry['messageid'])
          await msg.delete()
      except discord.NotFound:
          await interaction.followup.send("Ticket message not found, but it will still be removed from the system.", ephemeral=True)

                                                   
      json_data['message'].remove(message_entry)

                              
      with open(file_path, 'w') as f:
          json.dump(json_data, f, indent=2)

                        
      await interaction.followup.send(embed=discord.Embed(title="Successfully deleted the ticket system.", color=0xffffff))
 
    
@client.tree.command(name="make_ticket", description="Make a ticket system. (Administrator required)")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.checks.bot_has_permissions(manage_channels=True, manage_roles=True)
@app_commands.describe(
    title="Configures ticket's embed title",
    description="Configures ticket's embed description",
    image="Set embed's image using link",
    category="Set ticket's channel",
    role='Role that will get access to the ticket (separate using ",")',
    ticket_message="Set message that users will get when making a ticket"
)
async def make_ticket(
    interaction: discord.Interaction,
    title: Optional[str],
    description: Optional[str],
    image: Optional[str],
    category: discord.CategoryChannel,
    role: Optional[str],
    ticket_message: Optional[str]
):
    refresh()
    guild_id = interaction.guild.id
    owner_id = interaction.guild.owner_id
    is_active, is_premium, expires_at = user_is_active(interaction.user.id)

    await interaction.response.defer()
    def load_json(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    
    def save_json(filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_server_to_json():
        servers = load_json("ticket-json/ticket-server.json")
        if guild_id not in servers["serverID"]:
            servers["serverID"].append(guild_id)
            save_json("ticket-json/ticket-server.json", servers)
    
    def update_ticket_json(new_data):
        filename = f"ticket-json/{guild_id}-ticket.json"
        try:
            file_data = load_json(filename)
            file_data["message"].append(new_data)
        except (FileNotFoundError, json.JSONDecodeError):
            file_data = {"message": [new_data]}
        save_json(filename, file_data)
    
    servers = load_json("ticket-json/ticket-server.json")
    ticket_data = load_json(f"ticket-json/{guild_id}-ticket.json") if guild_id in servers["serverID"] else {"message": []}
    
    if not is_premium:
        if image:
            await interaction.channel.send(
                embed=discord.Embed(
                    title="You're being restricted",
                    description=(
                        "The owner of this server does not have premium.\n"
                        "Non-premium users do not have access to ticket's image.\n"
                        "Consider not including an image or buy our useful premium with lots of perks.\n"
                        "Use: </help:1242738769099231302> to check out our premium perks."
                    ),
                    color=0xffffff
                ),
                view=BuyPremium2()
            )
            return
        
        if len(ticket_data["message"]) >= 3:
            embed = discord.Embed(
                title="You're being restricted",
                description=(
                    "The owner of this server does not have premium.\n"
                    "Non-premium users are only allowed to deploy 3 ticket systems into their server.\n"
                    "Consider deleting an existing ticket system below or buy our useful premium with lots of perks.\n"
                    "Use: </help:1242738769099231302> to check out our premium perks."
                ),
                color=0xffffff
            )
            for i, msg_data in enumerate(ticket_data['message']):
                embed.add_field(
                    name=f"No: 0{i+1} Ticket System:",
                    value=f"Url: {msg_data['url']}\nId: {msg_data['messageid']}",
                    inline=True
                )
            await interaction.channel.send(embed=embed, view=DeleteTicketSystemButton())
            return
    
    embed = discord.Embed(
        title=title or "Equinox Ticket",
        description=description or "```Click the gray button below to make a ticket```",
        color=0xffffff
    )
    embed.set_footer(text="Ticket status: Enabled | Max Ticket Per User: ∞")
    if image and is_premium:
        embed.set_image(url=image)
    
    msg = await interaction.original_response()
    view = TicketButton()
    ticket_msg = await interaction.followup.send(embed=embed, view=view)
    view.message = ticket_msg
    
    add_server_to_json()
    ticket_roles = [int(r) for r in role.split(",")] if role else None
    
    update_ticket_json({
        "messageid": msg.id,
        "category": category.id,
        "ticket_message": ticket_message,
        "ticket_role": ticket_roles,
        "url": msg.jump_url,
        "disabled": False,
        "max_ticket": None
    })

          
@client.tree.command(name="addmember", description="Add a member to the ticket. (Manage channels required)")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(administrator=True)
@app_commands.checks.bot_has_permissions(manage_channels=True)
@app_commands.describe(member="Add selected member to the ticket")
async def addmember(interaction: discord.Interaction, member: discord.Member):
  await interaction.channel.set_permissions(member, read_messages=True, send_messages=True, attach_files=True)
  await interaction.response.send_message(embed=discord.Embed(title=f"Successfully added {member.mention} to {interaction.channel.mention}", color=0xffffff))

@client.tree.command(name="revmember", description="Remove a member from a ticket. (Manage channels required)")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(administrator=True)
@app_commands.checks.bot_has_permissions(manage_channels=True)
@app_commands.describe(member="Remove selected member to the ticket")
async def revmember(interaction: discord.Interaction, member: discord.Member):
    await interaction.channel.set_permissions(member, view_channel=False)
    await interaction.response.send_message(embed=discord.Embed(title=f"Successfully remove {member} to {interaction.channel.mention}", color=0xffffff))

@client.tree.command(name="slowmode", description="Set slowmode for current channel. (Manage channels required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(manage_channels=True)
@app_commands.describe(slowmode="Set slowmode in second")
async def slowmode(interaction: discord.Interaction, slowmode: int):
  if slowmode < 0:
    await interaction.response.send_message(embed=discord.Embed(title="Failed...", description="```Slowmode input must be greater or equal to 0```", color=0xffffff))
  elif slowmode > 21600:
    await interaction.response.send_message(embed=discord.Embed(title="Failed...", description="```Slowmode input must be smaller or equal to 6 hours (21600 seconds)```", color=0xffffff))
  else:
    await interaction.channel.edit(slowmode_delay=slowmode)
    if slowmode < 60:
      time = f"{slowmode} second(s)"
    elif slowmode > 59 and slowmode < 3600:
      time = f"{slowmode/60} minute(s)"
    elif slowmode >= 3600:
      time = f"{slowmode/3600} hour(s)"
    await interaction.response.send_message(embed=discord.Embed(title=f"Sucessfully set {interaction.channel} slowmode to {time}", color=0xffffff))

@client.tree.command(name="lockdown", description="Lockdown a channel, not allowing members to chat. (Manage channels required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(manage_roles=True)
async def lockdown(interaction: discord.Interaction):
  await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False, add_reactions=False)
  await interaction.response.send_message(embed=discord.Embed(title=f"Successfully lockdown {interaction.channel.mention}", color=0xffffff))

@client.tree.command(name="unlockdown", description="Unlockdown a channel, allows members to chat. (Manage channels required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(manage_roles=True)
async def unlockdown(interaction: discord.Interaction):
  await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True, add_reactions=True)
  await interaction.response.send_message(embed=discord.Embed(title=f"Successfully unlock {interaction.channel.mention}", color=0xffffff))

@client.tree.command(name="private", description="Private a channel, not allowing members to see. (Manage channels required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(manage_roles=True)
async def private(interaction: discord.Interaction):
  await interaction.channel.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)
  await interaction.response.send_message(embed=discord.Embed(title=f"Successfully private {interaction.channel.mention}", color=0xffffff))

@client.tree.command(name="unprivate", description="Unprivate a channel, allows members to see. (Manage channels required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(manage_roles=True)
async def unprivate(interaction: discord.Interaction):
  await interaction.channel.set_permissions(interaction.guild.default_role, read_messages=True, send_messages=True)
  await interaction.response.send_message(embed=discord.Embed(title=f"Successfully unprivate {interaction.channel.mention}", color=0xffffff))

@client.tree.command(name="kick", description="Kick a member. (Kick members required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(kick_members=True)
@app_commands.checks.bot_has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str]):
  bot_user = interaction.guild.get_member(client.user.id)
  clienttop_role = bot_user.top_role
  if interaction.user.id == interaction.guild.owner_id:
    await interaction.guild.kick(user=member, reason=reason)
    await interaction.response.send_message(embed=discord.Embed(title=f"Successfully kicked {member.name}", description=f"**Reason:** {reason}", color=0xffffff))
  else:
    if interaction.user.top_role <= member.top_role or clienttop_role <= member.top_role or interaction.user.id == member.id or member.id == interaction.guild.owner.top_role:
      await interaction.response.send_message(embed=discord.Embed(title="Failed to kick, please check if the member's hierchy is:", description="> Higher than yours\n> Equals to yours\n> Higher than mine\n> Equals to mine\n> Is you\n> Is server's owner", color=0xffffff))
    else:
      await interaction.guild.kick(user=member, reason=reason)
      await interaction.response.send_message(embed=discord.Embed(title=f"Successfully kicked {member.name}", description=f"**Reason:** {reason}", color=0xffffff))

@client.tree.command(name="unban", description="Unban a user. (Ban members required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.checks.bot_has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, memberid: str):
    user = client.get_user(int(memberid))
    await interaction.guild.unban(user) 
    await interaction.response.send_message(embed=discord.Embed(title=f"Successfully unban {user}!", color=0xffffff))

class UnbanButton(discord.ui.View):
  def __init__(self, userID):
    super().__init__(timeout=60)
    self.userID = userID
  @discord.ui.button(label="Unban Member", style=discord.ButtonStyle.grey, custom_id="unban")
  async def unban(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.guild_permissions.ban_members:
      user = await client.fetch_user(self.userID)
      await interaction.guild.unban(user)
      Button.disabled = True
      await interaction.message.edit(view=self)
      await interaction.response.send_message(embed=discord.Embed(title=f"Successfully unban {user}", color=0xffffff))
    else:
      await interaction.response.defer()
    
  async def on_timeout(self) -> None:
    unban_button = discord.utils.get(self.children, label="Unban Member")
    unban_button.disabled = True
    await self.message.edit(view=self)

@client.tree.command(name="ban", description="Ban a member. (Ban members required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.checks.bot_has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str]):
  bot_user = interaction.guild.get_member(client.user.id)
  clienttop_role = bot_user.top_role
  if interaction.user.id == interaction.guild.owner_id:
    await interaction.guild.ban(user=member, reason=reason)
    view=UnbanButton(member.id)
    await interaction.response.defer()
    msg = await interaction.followup.send(embed=discord.Embed(title=f"Successfully banned {member.name}", description=f"**Reason:** {reason}", color=0xffffff), view=view)
    view.message = msg
  else:
    if interaction.user.top_role <= member.top_role or clienttop_role <= member.top_role or interaction.user.id == member.id or member.id == interaction.guild.owner.top_role:
      await interaction.response.send_message(embed=discord.Embed(title="Failed to ban, please check if the member's hierchy is:", description="> Higher than yours\n> Equals to yours\n> Higher than mine\n> Equals to mine\n> Is you\n> Is server's owner", color=0xffffff))
    else:
      await interaction.guild.ban(user=member, reason=reason)
      view=UnbanButton(member.id)
      await interaction.response.defer()
      msg = await interaction.followup.send(embed=discord.Embed(title=f"Successfully banned {member.name}", description=f"**Reason:** {reason}", color=0xffffff), view=view)
      view.message = msg


class DefineButton(discord.ui.View):
  def __init__(self, current_index, word, definitions, authorID):
      super().__init__(timeout=60)
      self.current_index = current_index
      self.word = word
      self.definitions = definitions
      self.authorID = authorID
  @discord.ui.button(label="< Previous Definition", style=discord.ButtonStyle.gray, custom_id="previous_definition_button")
  async def on_previous_definition(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == self.authorID:
        if self.current_index > 0:
            self.current_index -= 1
            definition = self.definitions[self.current_index]
            embed = interaction.message.embeds[0]
            embed.set_field_at(1, name=f"> Definition - {self.definitions.index(definition)+1}:", value=f"```{definition}```", inline=False)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()
      else:
        await interaction.response.defer()
  @discord.ui.button(label="Next Definition >", style=discord.ButtonStyle.gray, custom_id="next_definition_button")
  async def on_next_definition(self, interaction: discord.Interaction, button: discord.ui.Button):
      if interaction.user.id == self.authorID:
        if self.current_index < len(self.definitions) - 1:
            self.current_index += 1
            definition = self.definitions[self.current_index]
            embed = interaction.message.embeds[0]
            embed.set_field_at(1, name=f"> Definition - {self.definitions.index(definition)+1}:", value=f"```{definition}```", inline=False)
            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.defer()
      else:
        await interaction.response.defer()
  async def on_timeout(self) -> None:
    define_button_previous = discord.utils.get(self.children, label="< Previous Definition")
    define_button_next = discord.utils.get(self.children, label="Next Definition >")
    define_button_previous.disabled = True
    define_button_next.disabled = True
    await self.message.edit(view=self)
    

def fetch_word_example(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'meanings' in data[0] and 'definitions' in data[0]['meanings'][0] and 'example' in data[0]['meanings'][0]['definitions'][0]:
            example = data[0]['meanings'][0]['definitions'][0]['example']
            return example
    return None

@client.tree.command(name="def", description="Find a definition of a word")
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def define(interaction: discord.Interaction, word: str):
  await interaction.response.defer(ephemeral=True)
  msg2 = await interaction.followup.send("Wait for a few moments... <a:loading_symbol:1295113412564615249>")
  meaning = dictionary.meaning(word)
  if meaning != None:
    word_type = list(meaning.keys())[0]
    definition = meaning[word_type][0]
    definitions = meaning[word_type]
    example = fetch_word_example(word)
    embed=discord.Embed(title=f"{word.capitalize()} - Equinox Dictionary", description="Do not solely rely on Equinox's definition, please check other sources for verification if unsure about its meaning.",color=0xffffff)
    embed.add_field(name=f"> Type:", value=f"```{word_type}```", inline=False)
    embed.add_field(name=f"> Definition - 1:", value=f"```{definition}```", inline=False)
    embed.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/literature-xxl.png")
    if example != None:
      embed.add_field(name=f"> Example:", value=f"```{example}```", inline=False)
    if len(meaning[word_type]) != 1:
      embed.set_footer(text=f"Other meanings: {len(meaning[word_type])}")
    view = DefineButton(0, word, definitions, interaction.user.id)
    msg = await interaction.channel.send(embed=embed, view=view)
    await msg2.delete()
    view.message = msg
  else:
    await msg2.delete()
    await interaction.channel.send(embed=discord.Embed(title=f"No definition found for {word.capitalize()} :(", color=0xffffff))

class RawCopyButton(discord.ui.View):
  def __init__(self, translated_message, authorID):
    self.translated_message = translated_message
    self.authorID = authorID
    super().__init__(timeout=60)
  @discord.ui.button(label="Raw Copy")
  async def copy(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer()
      await interaction.followup.send(self.translated_message, ephemeral=True)
    else:
      await interaction.response.defer()
  async def on_timeout(self) -> None:
    translate_button = discord.utils.get(self.children, label="Raw Copy")
    translate_button.disabled = True
    await self.message.edit(view=self)
    

language_dict = {}

for key, value in googletrans.LANGUAGES.items():
  if key in ['af', 'ar', 'hy', 'bs', 'bg', 'zh-cn', 'zh-tw', 'hr', 'nl', 'en', 'tl', 'fr', 'el', 'hi', 'id', 'ga', 'it', 'ja', 'ko', 'lo', 'ms', 'pt', 'es', 'th', 'vi']:
    language_dict[key] = value

@client.tree.command(name="translate", description="Translate a text to a destinated language")
@app_commands.choices(
    lang=[
        discord.app_commands.Choice(name=language_name.capitalize(), value=language_code)
        for language_code, language_name in language_dict.items()
    ]
)
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
async def trans(interaction: discord.Interaction, args: str, lang: discord.app_commands.Choice[str]):
    t = Translator()
    a = t.translate(args, dest=lang.value)
    embe = discord.Embed(color = 0xffffff)
    sourcelang = googletrans.LANGUAGES[(a.src).lower()]
    translated_sourcelang = googletrans.LANGUAGES[(a.dest).lower()]
    embe.set_author(name="Equinox Translator", icon_url=client.user.avatar)
    embe.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/google-translate-xxl.png")
    embe.add_field(name=f"Original Text - {sourcelang.capitalize()}", value=args, inline=False)
    embe.add_field(name=f"Translated Text - {translated_sourcelang.capitalize()}", value=a.text, inline=False)
    embe.set_footer(text=f"Translated by {interaction.user}", icon_url=interaction.user.avatar)
    view = RawCopyButton(a.text, interaction.user.id)
    await interaction.response.defer()
    msg = await interaction.followup.send(embed=embe, view=view)
    view.message = msg

class translateSelect(View):
  def __init__(self, original_message, authorID, translated_message):
    super().__init__(timeout=60)
    self.original_message = original_message
    self.authorID = authorID
    self.translated_message = translated_message


  @discord.ui.select(placeholder= "Choose a destination language",
                     options=[
                        discord.SelectOption(label=language_name.capitalize(), value=language_code)
                        for language_code, language_name in language_dict.items()
                       ]
                     )
  async def translate_select_callback(self, interaction, select):
    if interaction.user.id == self.authorID:
      t = Translator()
      a = t.translate(self.original_message, dest=select.values[0])
      embe = discord.Embed(color = 0xffffff)
      sourcelang = googletrans.LANGUAGES[(a.src).lower()]
      translated_sourcelang = googletrans.LANGUAGES[(a.dest).lower()]
      embe.set_author(name="Equinox Translator", icon_url=client.user.avatar)
      embe.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/google-translate-xxl.png")
      embe.add_field(name=f"Original Text - {sourcelang.capitalize()}", value=self.original_message, inline=False)
      embe.add_field(name=f"Translated Text - {translated_sourcelang.capitalize()}", value=a.text, inline=False)
      embe.set_footer(text=f"Translated by {interaction.user}", icon_url=interaction.user.avatar)
      self.translated_message = a.text
      await interaction.response.edit_message(embed=embe, view=self)


  @discord.ui.button(label="Raw Copy")
  async def copy(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer()
      await interaction.followup.send(self.translated_message, ephemeral=True)
    else:
      await interaction.response.defer()

  async def on_timeout(self) -> None:
    for children in self.children:
      children.disabled = True
    await self.message.edit(view=self)

@client.tree.context_menu(name="Translate")
async def app_translate(interaction: discord.Interaction, message: discord.Message):
    t = Translator()
    a = t.translate(message.content, dest='en')
    embe = discord.Embed(color = 0xffffff)
    sourcelang = googletrans.LANGUAGES[(a.src).lower()]
    embe.set_author(name="Equinox Translator", icon_url=client.user.avatar)
    embe.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/google-translate-xxl.png")
    embe.add_field(name=f"Original Text - {sourcelang.capitalize()}", value=message.content, inline=False)
    embe.add_field(name=f"Translated Text - None", value="Please choose your destination language below.", inline=False)
    embe.set_footer(text=f"Translated by {interaction.user}", icon_url=interaction.user.avatar)
    view = translateSelect(message.content, interaction.user.id, "None")
    await interaction.response.defer()
    msg = await interaction.followup.send(embed=embe, view=view)
    view.message = msg

class FandomPageUrl(View):
  def __init__(self, url):
    super().__init__(timeout=None)
    self.url = url
    button = discord.ui.Button(label='Fandom Page', style=discord.ButtonStyle.url, url=self.url)
    self.add_item(button)





class wikipediaLink(View):
  def __init__(self, pageTitle):
    self.pageTitle = pageTitle
    super().__init__(timeout=None)
    wiki_url = self.pageTitle
    if len(self.pageTitle.split()) > 1:
      wiki_url = "_".join(self.pageTitle.split())
    button = discord.ui.Button(label='Wikipedia Page', style=discord.ButtonStyle.url, url=f'https://en.wikipedia.org/wiki/{wiki_url}')
    self.add_item(button)  

class WikipediaButton(discord.ui.View):
  def __init__(self, authorID, output):
    self.authorID = authorID
    self.output = output
    self.msg = None
    super().__init__(timeout=60)  

  @discord.ui.button(label="1")
  async def first(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        await interaction.response.defer()
        msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
        value_output = wikipedia.summary(self.output[0])
        split_value_output = len(value_output.split())
        content_output = value_output
        if split_value_output > 1999:
          content_output = value_output[:round(split_value_output/3)]
        elif split_value_output > 1000:
          content_output = value_output[:round(split_value_output/2)]
        elif split_value_output > 500:
          content_output = value_output[:round(split_value_output/1.5)]
        sentence = 1
        embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
        embed.set_footer(text=f"Passage Position: {sentence}")
        await msg.delete()
        if self.msg != None:
          msg2 = await interaction.channel.fetch_message(self.msg)
          await msg2.delete()
        view = wikipediaLink(self.output[0])
        msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
        self.msg = msg3.id
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))
    else:
      await interaction.response.defer() 
  @discord.ui.button(label="2")
  async def second(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 0:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[1])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[1]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[1])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))
    else:
      await interaction.response.defer()    
  @discord.ui.button(label="3")
  async def third(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 1:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[2])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[2]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[2])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))        
    else:
      await interaction.response.defer()     
  @discord.ui.button(label="4")
  async def forth(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 2:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[3])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[3]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[3])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))    
    else:
      await interaction.response.defer()     
  @discord.ui.button(label="5")
  async def fifth(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 3:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[4])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[4]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[4])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))    
    else:
      await interaction.response.defer()        
  @discord.ui.button(label="6")
  async def sixth(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 4:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[5])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[5]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[5])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))    
    else:
      await interaction.response.defer()  
  @discord.ui.button(label="7")
  async def seventh(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 5:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[6])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[6]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[6])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))    
    else:
      await interaction.response.defer()   
  @discord.ui.button(label="8")
  async def eighth(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 6:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[7])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[7]} - Wikipedia Result", description=f"```{content_output}...```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[7])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))    
    else:
      await interaction.response.defer()    
  @discord.ui.button(label="9")
  async def nineeth(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 7:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[8])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[8]} - Wikipedia Result", description=f"```{content_output}```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[8])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))    
    else:
      await interaction.response.defer()    
  @discord.ui.button(label="10")
  async def teneth(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      try:
        if len(self.output) > 8:
          await interaction.response.defer()
          msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
          value_output = wikipedia.summary(self.output[9])
          split_value_output = len(value_output.split())
          content_output = value_output
          if split_value_output > 1999:
            content_output = value_output[:round(split_value_output/3)]
          elif split_value_output > 1000:
            content_output = value_output[:round(split_value_output/2)]
          elif split_value_output > 500:
            content_output = value_output[:round(split_value_output/1.5)]
          sentence = 1
          embed=discord.Embed(title=f"{self.output[9]} - Wikipedia Result", description=f"```{content_output}```",color=0xffffff)
          embed.set_footer(text=f"Passage Position: {sentence}")
          await msg.delete()
          if self.msg != None:
            msg2 = await interaction.channel.fetch_message(self.msg)
            await msg2.delete()
          view = wikipediaLink(self.output[9])
          msg3 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          self.msg = msg3.id
        else:
          await interaction.response.defer()
      except:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))    
    else:
      await interaction.response.defer()  

  async def on_timeout(self) -> None:
    for children in self.children:
      children.disabled = True
    await self.message.edit(view=self)

  

@client.tree.command(name="wiki", description="Search anything from wikipedia")
async def wikipedia_query(interaction: discord.Interaction, search: str):
  await interaction.response.defer()
  msg = await interaction.followup.send("Please wait... <a:loading_symbol:1295113412564615249>")
  output = wikipedia.search(search)
  if len(output) > 0:
    if len(output) == 1:
      await interaction.followup.send(wikipedia.summary(search)[:1999])
    else:
      embed = discord.Embed(title=f"Wikipedia Search Results - {search.capitalize()}", color=0xffffff)
      embed.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/wikipedia-xxl.png")
      for i in range(len(output)):
        try:
          embed.add_field(name=f"{i+1} - {output[i]}", value=f"{wikipedia.summary(output[i])[:50]}...", inline=False)
        except:
          embed.add_field(name=f"{i+1} - {output[i]}", value=f"...", inline=False)
    view = WikipediaButton(interaction.user.id, output)
    await msg.delete()
    msg2 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
    view.message = msg2
  else:
    embed = discord.Embed(title=f"Wikipedia Search Results - {search.capitalize()}", description=f"No result(s) found for {search.capitalize()} :(", color=0xffffff)
    await interaction.channel.send(content=interaction.user.mention, embed=embed)

class CloneButton(discord.ui.View):
  def __init__(self, authorID, channel):
    self.authorID = authorID
    self.channel = channel
    super().__init__(timeout=60)
  @discord.ui.button(label="Clone & Delete", style=discord.ButtonStyle.red)
  async def clone_delete_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer(ephemeral=True)
      cloning_message = await interaction.followup.send(f"Cloning {self.channel} and deleting {self.channel} <a:loading_symbol:1295113412564615249>")
      cloned_channel = await self.channel.clone()
      await cloned_channel.edit(position=self.channel.position)
      msg = await cloned_channel.send(interaction.user.mention)
      await cloning_message.delete()
      await msg.delete()
      embed=discord.Embed(title=f"Successfully cloned {self.channel.name}", color=0xffffff)
      embed.set_footer(text=f"Cloned by {interaction.user}",icon_url=interaction.user.avatar)
      await cloned_channel.send(embed=embed)
      await self.channel.delete()
    else:
      await interaction.response.defer()

  @discord.ui.button(label="Clone Only", style=discord.ButtonStyle.red)
  async def clone_button(self, interaction: discord.Interaction, Button: discord.Button):
    if interaction.user.id == self.authorID:
      await interaction.response.defer(ephemeral=True)
      cloning_message = await interaction.followup.send(f"Cloning {self.channel} <a:loading_symbol:1295113412564615249>")
      cloned_channel = await self.channel.clone()
      await cloned_channel.edit(position=self.channel.position)
      msg = await cloned_channel.send(interaction.user.mention)
      await cloning_message.delete()
      await msg.delete()
      embed=discord.Embed(title=f"Successfully cloned {self.channel.name}", color=0xffffff)
      embed.set_footer(text=f"Cloned by {interaction.user}",icon_url=interaction.user.avatar)
      await cloned_channel.send(embed=embed)
    else:
      await interaction.response.defer()

  async def on_timeout(self) -> None:
    clone_del_button = discord.utils.get(self.children, label="Clone & Delete")
    clone_del_button.disabled = True
    clone_btn = discord.utils.get(self.children, label="Clone Only")
    clone_btn.disabled = True
    await self.message.edit(view=self)

@client.tree.command(name="clone", description="Clone current channel. (Manage channels required)")
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
@app_commands.checks.has_permissions(manage_channels=True)
@app_commands.checks.bot_has_permissions(manage_channels=True)
async def clone(interaction: discord.Interaction, channel: Optional[discord.TextChannel]):
  await interaction.response.defer()
  if channel == None:
    channel = interaction.channel
  view = CloneButton(interaction.user.id, channel)
  embed = discord.Embed(title="Cloning Caution ⚠️", description="```diff\nThe clone command allows you to either:\n+ Clone and delete channel\nor\n- Clone channel only\n```", color=0xffffff)
  embed.set_footer(text=f"Issued by {interaction.user} | Ignore to cancel", icon_url=interaction.user.avatar)
  msg = await interaction.followup.send(interaction.user.mention, embed=embed, view=view)
  view.message = msg


def snowflake_time(id):
    return date.datetime.utcfromtimestamp(((id >> 22) + 1420070400000) / 1000)


@client.tree.command(name="timedif", description="Find time differences between 2 message id.")
async def timedif(interaction: discord.Interaction, id1: str, id2: str):
    time1 = discord.utils.snowflake_time(int(id1))
    time2 = discord.utils.snowflake_time(int(id2))
    ts_diff = time2 - time1
    secs = abs(ts_diff.total_seconds())
    yrs,secs=divmod(secs,secs_per_year:=60*60*24*30.5*12)
    mth,secs=divmod(secs,secs_per_month:=60*60*24*30)
    days,secs=divmod(secs,secs_per_day:=60*60*24)
    hrs,secs=divmod(secs,secs_per_hr:=60*60)
    mins,secs=divmod(secs,secs_per_min:=60)
    secs=round(secs, 2)
    answer='{} secs'.format(secs)
    
    if secs > 60 or mins > 0:
        answer='{} minute(s) and {} second(s)'.format(int(mins),secs)
        if mins > 60 or hrs > 0:
            answer='{} hour(s), {} minute(s) and {} second(s).'.format(int(hrs),int(mins),secs)
            if hrs > 24 or days > 0:
                answer='{} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(days),int(hrs),int(mins),secs)
                if days > 30 or mth > 0:
                  answer='{} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(mth),int(days),int(hrs),int(mins),secs)
                  if mth > 12 or yrs > 0:
                    answer='{} year(s), {} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(yrs),int(mth),int(days),int(hrs),int(mins),secs)
    
    embed = discord.Embed(title=f"Time Difference - Snowflake", color=0xffffff)
    embed.add_field(name=f"> Time Difference:", value=f"```{answer}```", inline=False)
    embed.add_field(name=f"> First Id: <t:{round(time1.timestamp())}:F>", value=f"```{id1}\n```", inline=False)
    embed.add_field(name=f"> Second Id: <t:{round(time2.timestamp())}:F>", value=f"```{id2}\n```", inline=False)
    await interaction.response.send_message(embed=embed) 

class rrSelectGames(View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.select(placeholder= "Click here to choose a game!",
                     options=[
                       discord.SelectOption(label="Genshin Impact", value="1", description="Genshin Impact", emoji="<:GI1Primogem:1265298846880370691>"),
                       discord.SelectOption(label="Honkai: Star Rail", value="2", description="Honkai: Star Rail", emoji="<:HSR1Stellarjade:1265292394459299975>"),
                       discord.SelectOption(label="Zenless Zone Zero", value="3", description="Zenless Zone Zero", emoji="<:ZZZ1Polychrome:1265304068662759517>"),
                       discord.SelectOption(label="Wuthering Waves", value="4", description="Wuthering Waves", emoji="<:Astrite:1265305744480276603>")
                       ],
                      custom_id= "rrSelectGamesSelection"
                     )
  async def select_callback(self, interaction, select):
    if select.values[0] == "1":
      role = interaction.guild.get_role(1265210842794688595)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} from you!", ephemeral=True)
    elif select.values[0] == "2":
      role = interaction.guild.get_role(1265210791766917171)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} from you!", ephemeral=True)
    elif select.values[0] == "3":
      role = interaction.guild.get_role(1265210889364181002)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} from you!", ephemeral=True)
    elif select.values[0] == "4":
      role = interaction.guild.get_role(1265210921169457256)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} from you!", ephemeral=True)

      
class rrSelectGender(View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.select(placeholder= "Click here to choose a pronoun!",
                     options=[
                       discord.SelectOption(label="She/Her", value="1", description="She/Her", emoji="🩷"),
                       discord.SelectOption(label="He/Him", value="2", description="He/Him", emoji="💙"),
                       discord.SelectOption(label="They/Them", value="3", description="They/Them", emoji="🖤"),
                       discord.SelectOption(label="Other Pronouns", value="4", description="Other Pronouns", emoji="🤍")
                       ],
                      custom_id= "rrSelectGenderSelection"
                     )
  async def select_callback(self, interaction, select):
    if select.values[0] == "1":
      role = interaction.guild.get_role(1265210663429603359)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "2":
      role = interaction.guild.get_role(1265210697395208245)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "3":
      role = interaction.guild.get_role(1265210723827449896)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "4":
      role = interaction.guild.get_role(1265210752134807645)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)

class rrSelectPing(View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.select(placeholder= "Click here to choose a ping role!",
                     options=[
                       discord.SelectOption(label="Announcement Ping", value="1", description="Announcement Ping", emoji="✉️"),
                       discord.SelectOption(label="Giveaway Ping", value="2", description="Giveaway Ping", emoji="🎉"),
                       discord.SelectOption(label="Events Ping", value="3", description="Events Ping", emoji="🔊"),
                       discord.SelectOption(label="Dead Chat Ping", value="4", description="Dead Chat Ping", emoji="💬")
                       ],
                      custom_id= "rrSelectPingSelection"
                     )
  async def select_callback(self, interaction, select):
    if select.values[0] == "1":
      role = interaction.guild.get_role(1265210956682629182)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "2":
      role = interaction.guild.get_role(1265210991764045895)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "3":
      role = interaction.guild.get_role(1265285805023432704)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "4":
      role = interaction.guild.get_role(1265364117238059119)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)

class rrSelectServer(View):
  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.select(placeholder= "Click here to choose a server role!",
                     options=[
                       discord.SelectOption(label="NA Server", value="1", description="NA Server", emoji="🌎"),
                       discord.SelectOption(label="EU Server", value="2", description="EU Server", emoji="🌍"),
                       discord.SelectOption(label="Asia Server", value="3", description="Asia Server", emoji="🌏")
                       ],
                      custom_id= "rrSelectServerSelection"
                     )
  async def select_callback(self, interaction, select):
    if select.values[0] == "1":
      role = interaction.guild.get_role(1265211423911448636)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "2":
      role = interaction.guild.get_role(1265216089839763486)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)
    elif select.values[0] == "3":
      role = interaction.guild.get_role(1265216164683059352)
      if role in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.remove_roles(role)
        await interaction.followup.send(f"Successfully removed the role {role.name} from you!", ephemeral=True)
      elif role not in interaction.user.roles:
        await interaction.response.defer()
        await interaction.user.add_roles(role)
        await interaction.followup.send(f"Successfully added the role {role.name} to you!", ephemeral=True)

@client.tree.command(name="rrgame", description="Make a selection role (Dev only)")
async def rr(interaction: discord.Interaction):
  if interaction.user.id in devs:
    games_embed=discord.Embed(title="・What game(s) do you play? ⚝", color=0x2c2d35)
    games_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTE2MnY1bW44anhmZ3VxbjYzc2Zjb3B1cDlzcWVrbHR0aXRyczd2OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/IBYvXiE7xtYHB4DHS1/giphy.gif")
    games_view = rrSelectGames()
    gender_embed=discord.Embed(title="・What is your preferred pronoun(s)? ⚝", color=0x2c2d35)
    gender_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTE2MnY1bW44anhmZ3VxbjYzc2Zjb3B1cDlzcWVrbHR0aXRyczd2OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/IBYvXiE7xtYHB4DHS1/giphy.gif")
    gender_view = rrSelectGender()
    ping_embed=discord.Embed(title="・What ping(s) would you like to get? ⚝", color=0x2c2d35)
    ping_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTE2MnY1bW44anhmZ3VxbjYzc2Zjb3B1cDlzcWVrbHR0aXRyczd2OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/IBYvXiE7xtYHB4DHS1/giphy.gif")
    ping_view = rrSelectPing()
    server_embed=discord.Embed(title="・What server(s) do you play on? ⚝", color=0x2c2d35)
    server_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExeTE2MnY1bW44anhmZ3VxbjYzc2Zjb3B1cDlzcWVrbHR0aXRyczd2OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/IBYvXiE7xtYHB4DHS1/giphy.gif")
    server_view = rrSelectServer()
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send(content="Successfully set up selection role")
    await interaction.channel.send(embed=games_embed, view=games_view)
    await interaction.channel.send(embed=gender_embed, view=gender_view)
    await interaction.channel.send(embed=ping_embed, view=ping_view)
    await interaction.channel.send(embed=server_embed, view=server_view)
  else:
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Devs only!")


class Paginator(discord.ui.View):
    def __init__(self, pages: list[discord.Embed], timeout=60):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current = 0

    async def update(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = False
        if self.current == 0:
            self.first.disabled = True
            self.prev.disabled = True
        if self.current == len(self.pages) - 1:
            self.next.disabled = True
            self.last.disabled = True
        await interaction.response.edit_message(embed=self.pages[self.current], view=self)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.grey)
    async def first(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = 0
        await self.update(interaction)

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current -= 1
        await self.update(interaction)

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current += 1
        await self.update(interaction)

    @discord.ui.button(label=">>", style=discord.ButtonStyle.grey)
    async def last(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current = len(self.pages) - 1
        await self.update(interaction)


@client.tree.command(name="steal", description="Steal multiple emojis from another server")
@app_commands.describe(emojis="The emojis to steal", names="Optional new names for the emojis, separated by spaces")
@app_commands.checks.has_permissions(manage_emojis_and_stickers=True)
async def steal(interaction: discord.Interaction, emojis: str, names: str = None):
    await interaction.response.defer()
    guild = interaction.guild
    if not guild:
        await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
        return

    emoji_list = re.findall(r'<a?:\w+:\d+>', emojis)
    name_list = names.split() if names else []

    results = []

    for i, emoji in enumerate(emoji_list):
        emoji_match = re.match(r'<(a?):(\w+):(\d+)>', emoji)
        if not emoji_match:
            results.append(f"Invalid format for {emoji}")
            continue

        is_animated = emoji_match.group(1) == 'a'
        original_name = emoji_match.group(2)
        emoji_id = emoji_match.group(3)
        emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{'gif' if is_animated else 'png'}"

        emoji_name = name_list[i] if i < len(name_list) else original_name

        async with client.http_session.get(emoji_url) as response:
            if response.status != 200:
                results.append(f"Failed to fetch {emoji_name}")
                continue
            emoji_data = await response.read()

        try:
            new_emoji = await guild.create_custom_emoji(name=emoji_name, image=emoji_data)
            results.append(f"Emoji {new_emoji}: `{new_emoji.name}` added successfully!")
        except discord.HTTPException as e:
            results.append(f"Failed to add {emoji_name}: {e}")

                
    per_page = 10
    total_pages = math.ceil(len(results) / per_page)
    pages = []

    for i in range(total_pages):
        chunk = results[i * per_page:(i + 1) * per_page]
        embed = discord.Embed(title="> 🤍 Emoji Upload Logs", color=0xffffff)
        embed.add_field(name="Result(s)", value="\n".join(chunk), inline=False)
        embed.set_footer(text=f"Page {i+1}/{total_pages}")
        pages.append(embed)

    if not pages:
        await interaction.followup.send("No valid emojis were provided.", ephemeral=True)
    elif len(pages) == 1:
        await interaction.followup.send(embed=pages[0])
    else:
        await interaction.followup.send(embed=pages[0], view=Paginator(pages))


update = "EV-5.1"
update_note = "```diff\n+Added giveaway command (Start a giveaway)\n\n+Added graph command.```"
update_note_content  = "```diff\n+Added giveaway command\n  > Start a giveaway.\n\n+Added graph command. (Premium only)\n  > Create a graph with a function.```"

class mySelect(View):
  def __init__(self, authorID):
    super().__init__(timeout=60)
    self.authorID = authorID
    button = discord.ui.Button(label='Invite Me', style=discord.ButtonStyle.url, url='https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=8&scope=bot')
    button2 = discord.ui.Button(label='Privacy Policy', style=discord.ButtonStyle.url, url='https://gist.github.com/PaullyScripter/c6ed57ac20fcc54dcf01adac78e6f712')
    button3 = discord.ui.Button(label='Support Server', style=discord.ButtonStyle.url, url='https://discord.gg/wAqVkf3MmG')
    button4 = discord.ui.Button(label='Website', style=discord.ButtonStyle.url, url='https://equinoxbot.netlify.app')
    self.add_item(button)
    self.add_item(button2)
    self.add_item(button3)
    self.add_item(button4)

  @discord.ui.select(placeholder= "Choose a catergory",
                     options=[
                       discord.SelectOption(label="Utilities", value="1", description="Shows bot's utilities commands", emoji="🤍"),
                       discord.SelectOption(label="Decorations", value="2", description="Shows bot's decorations commands", emoji="🍙"),
                       discord.SelectOption(label="Managements", value="3", description="Shows bot's management commands", emoji="⚙️"),
                       discord.SelectOption(label="Gacha", value="4", description="Shows bot's gacha commands", emoji="🎱"),
                       discord.SelectOption(label="Premium", value="5", description="Shows bot's premium commands", emoji="💎"),
                       discord.SelectOption(label="NSFW", value="6", description="Shows bot's nsfw commands", emoji="🔞"),
                       discord.SelectOption(label="Ticket & Verification", value="7", description="Shows bot's ticket and verify commands", emoji="📠"),
                       discord.SelectOption(label="Giveaway", value="8", description="Shows bot's giveaway command", emoji="🎉"),
                       discord.SelectOption(label="Messages", value="11", description="Shows bot's message counter command", emoji="💬"),
                       discord.SelectOption(label="Equinox", value="10", description="Shows bot's information", emoji="🌗"),
                       discord.SelectOption(label="Home", value="9", description="Returns home", emoji="🏠")
                       ]
                     )
  async def select_callback(self, interaction, select):
    if interaction.user.id == self.authorID:
      if select.values[0] == "1":
        em = discord.Embed(title="Equinox Navigator - Utilities", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
        em.set_author(name="Utilities Commands List", icon_url=client.user.avatar)
        em.add_field(name="> </ping:1238388376047059025>", value="```Shows bot's latency.```", inline=False)
        em.add_field(name="> </invite:1238507175299780689>", value="```Shows bot's invite.```", inline=False)
        em.add_field(name="> </help:1242738769099231302>", value="```Display this message.```", inline=False)
        em.add_field(name="> </qrcode:1238725889160646708> `<parm>`", value="```Make a qr-code from link, text, or emoji.```", inline=False)
        em.add_field(name="> </daysbetween:1238380307976028261> `<mm/yy>` `<mm/yy>`", value="```Calculte the day(s) between two date (dd/mm/yy).```", inline=False)
        em.add_field(name="> </poll:1239073953226559530> `first_emoji` `first_option` `second_emoji` `second_option` `third_emoji` `third_option`", value="```Make a poll from 3 emojis and 3 options. (Manage messages required)```", inline=False)
        em.add_field(name="> </def:1247731923854557205> `<word>`", value="```Shows word's type, definition, and example if there is any.```", inline=False)
        em.add_field(name="> </translate:1248240686600421397> `<arg>` `<lang>`", value="```Translate a text to another language (25 languages available).```", inline=False)
        em.add_field(name="> </fandom:1248623133263528128> `<search>` `<category>`", value="```Shows summary of a fandom page of a search from a category (still in beta).```", inline=False)
        em.add_field(name="> </timedif:1251229664333271070> `<id1>` `<id2>`", value="```Shows the differences between two relevant ids (message, guild, channels, ect).```", inline=False)
        em.add_field(name="> </wiki:1259879320411701311> `<query>`", value="```Find information on wikipedia.```", inline=False)
        em.add_field(name="> </steal:1295642758081417276> `<emoji>` `<name>`", value="```Steal an emoji from another server.```", inline=False)
        em.add_field(name="> __</graph:1337205925060149248>__ `<function>`", value="```Create a graph with a function.```", inline=False)
        em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self)
      if select.values[0] == "2":
        em = discord.Embed(title="Equinox Navigator - Decorations", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
        em.set_author(name="Decorations Commands List", icon_url=interaction.user.avatar)
        em.add_field(name="> </embed:1240567987606392834> `<title>` `[description]` `[color(ex. 0,0,0)]` `[image(link)]` `[thumbnail(link)]` `[footer]`", value="```Make instant embed to decorate your server, or to make announcement.```", inline=False)
        em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self)
      if select.values[0] == "3":
        em = discord.Embed(title="Equinox Navigator - Managements", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
        em.set_author(name="Managements Commands List", icon_url=interaction.user.avatar)
        em.add_field(name="> </kick:1244283319257006160> `<member>`", value="```Kick a member from the server (kick members required and can't kick yourself).```", inline=False)
        em.add_field(name="> </ban:1244290662971740301> `<member>`", value="```Ban a member from the server (ban members required and can't ban yourself).```", inline=False)
        em.add_field(name="> </lockdown:1243953621763358882>", value="```Lockdown a channel (manage channels required).```", inline=False)
        em.add_field(name="> </unlockdown:1243953621763358883>", value="```Unlock a channel (manage channels required).```", inline=False)
        em.add_field(name="> </private:1244902055345131565>", value="```Private a channel (manage channels required).```", inline=False)
        em.add_field(name="> </unprivate:1244902055345131566>", value="```Unprivate a channel (manage channels required).```", inline=False)
        em.add_field(name="> </purge:1238751918210285641> `<bot_messages>` `<embed_messages>` `<user_messages>`", value="```Purge messages in a channel (manage messages required).```", inline=False)
        em.add_field(name="> </slowmode:1247374983014125598> `<slowmode>`", value="```Set slowmode in current channel in seconds (manage channels required).```", inline=False)
        em.add_field(name="> </clone:1250258069686849639> `[channel]`", value="```Clone a channel and delete the original channel (manage channels required).```", inline=False)
        em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self)
      if select.values[0] == "4":
        em = discord.Embed(title="Equinox Navigator - Gacha", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
        em.set_author(name="Managements Gacha List", icon_url=interaction.user.avatar)
        em.add_field(name="> </roll:1240904743639973945> `item`", value="```Roll to get a title, boost luck with items.```", inline=False)
        em.add_field(name="> </craft:1241057341344845926> `<item>` `amount`", value="```Craft items using ingredients```", inline=False)
        em.add_field(name="> </login:1242639169579253931>", value="```Login to reset databases.```", inline=False)
        em.add_field(name="> </reset:1242686814255583262>", value="```Reset your databases.```", inline=False)
        em.add_field(name="> __</daily:1244877735541866497>__", value="```Open a daily chest container 3 random potions.```", inline=False)
        em.add_field(name="> </flex:1252120365778468935>", value="```Shows user's their gacha stats.```", inline=False)
        em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self)
      if select.values[0] == "5":
        refresh()
        member = interaction.user
        is_active, tier, expires_at = user_is_active(member.id)
        em = discord.Embed(title="Equinox Navigator - Premium", description=f"Your premium status: **{tier}**", color=0xffffff)
        em.set_author(name=f"Greetings! {interaction.user}.", icon_url=interaction.user.avatar)
        if tier:
          em.add_field(name="Thank you again for being one of our elite users!", value="Here are your perks! Additionally, you can check for more perks [here](https://equinoxbot.netlify.app/premium)", inline=False)
        em.add_field(name="> More Lucky", value="```You get 2x more lucky when rolling!```", inline=False)
        em.add_field(name="> Daily Potions Chest", value="```You get a chest of 3 random potion daily!```", inline=False)
        em.add_field(name="> Little time rolling", value="```Roll time are reduce to 2-3s!```", inline=False)
        em.add_field(name="> Daily potions", value="```Premium users are granted each day a chest of 3 random potions!```", inline=False)
        em.add_field(name="> No restriction on NSFW", value="```Subscriber are able to execute our nsfw commands unrestrictedly and anytime!```", inline=False)
        em.add_field(name="> Unlimited ticket system", value="```Elite users can deploy unlimited ticket system into their server!```", inline=False)
        em.add_field(name="> Customizable ticket system", value="```With premium, you can fully personalize your ticket systen!```", inline=False)
        em.add_field(name="> Personalized verification", value="```Beautiful verification system are to be seen on all premium users' server!```", inline=False)
        em.set_footer(text="Equinox Premium Panel", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self)
      if select.values[0] == "9":
        await interaction.response.edit_message(embed=self.embed, view=self)     
      if select.values[0] == "7":
        em = discord.Embed(title="Equinox Navigator - Ticket & Verification", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
        em.set_author(name="Ticket & Verification Commands List", icon_url=interaction.user.avatar)
        em.add_field(name="> </make_ticket:1243822562916565142> `<category>` `[title]` `[description]` __`[image]`__ `[role]` `[ticket_message]`", value="```Make a ticket system, category is ticket's channel, title, description, image(premium) is ticket's embed, role is ticket moderator, ticket_message is ticket's message```", inline=False)
        em.add_field(name="> </addmember:1243579023674708050> `<member>`", value="```Add a member to a ticket```", inline=False)
        em.add_field(name="> </revmember:1243579023674708051> `<member>`", value="```Remove a member from a ticket```", inline=False)
        em.add_field(name="> </make_verify:1245216089038782485> `[rev_role]` `[add_role]` __`[message]`__ __`[image]`__", value="```Make verification system, either remove role from user or add or both.```", inline=False)
        em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self) 
      if select.values[0] == "8":
        em = discord.Embed(title="Equinox Navigator - Giveaway", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
        em.set_author(name="Giveaway Commands List", icon_url=interaction.user.avatar)
        em.add_field(name="> </giveaway:1296022630800818218> `<duration>` `<prize>` `[hosts]`", value="```Start a giveaway, duration must be less than 7 days or a week, hosts can be roleid or userid or both.```", inline=False)
        em.add_field(name="> </giveaway_manage:1370458427100368898> `<message_id>` `<action>`", value="```Either reroll or finalize a giveaway.```", inline=False)
        em.add_field(name="> </giveaway_console:1370533191127142431>", value="```Show all giveaway(s) within the server.```", inline=False)
        em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self)
      if select.values[0] == "6":
        if interaction.channel.is_nsfw():
          em = discord.Embed(title="Equinox Navigator - NSFW", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
          em.set_author(name="Nsfw Commands List", icon_url=interaction.user.avatar)
          em.add_field(name="> </nsfw:1243128625398546584> `[category]`", value="```Shows available nsfw category if category is not argued. (normal)```", inline=False)
          em.add_field(name="> __</prem_nsfw:1250043405904379934>__ `[category]`", value="```Shows unrestricted premium available nsfw category if category is not argued.```", inline=False)
          em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
          await interaction.response.edit_message(embed=em, view=self)
        else:
          await interaction.response.defer()
      if select.values[0] == "11":
        em = discord.Embed(title="Equinox Navigator - Message Counter", description="<> = Required Arguement(s)\n[] = Optional Arguement(s)\n __underlined__ = Premium", color=0xffffff)
        em.set_author(name="Message Counter Commands List", icon_url=interaction.user.avatar)
        em.add_field(name="> </messagecount:1372799044098854923> `[user]`", value="```Shows a user's their message counts```", inline=False)
        em.add_field(name="> </messagecounter:1372799044098854922> `<option>`", value="```Enable/disable the server's message counter system.```", inline=False)
        em.add_field(name="> </messagecountleaderboard:1372799044098854925>`", value="```Shows top users with the most messages.```", inline=False)
        em.add_field(name="> </messagecountdeduct:1372799044098854924> `<user>` `<amount>`", value="```Remove an amount of messages from a user.```", inline=False)
        em.add_field(name="> </messagecountgive:1373135879060848701> `<from_user>` `<to_user>` `<amount>`", value="```Transfer an amount of messages from a user to another user.```", inline=False)
        em.add_field(name="> </messageblacklist:1373135879060848702> `<action>` `<channel>`", value="```Whitelist/blacklist a channel from the message counter system.```", inline=False)
        em.add_field(name="> </messageblacklistview:1373142859028496535>", value="```View blacklisted channels.```", inline=False)
        em.set_footer(text="Equinoxxxx <3", icon_url=f'{interaction.user.avatar}')
        await interaction.response.edit_message(embed=em, view=self)
      if select.values[0] == "10":
        embed=discord.Embed(title="Equinox Information", color=0xffffff)
        embed.set_author(name="Black or White, Equinox.", icon_url=client.user.avatar)
        embed.add_field(name="My Creators", value="> 🤍 **paullyzzz**: **Bot Developer**\n> 🌸 **rozmyosotis**: **Bot Decorator**\n> 🙊 **david220807**: **Bot Tester**", inline=False)
        embed.add_field(name=f"Thanks.", value="> Thank you for adding me!\n> Support us by purchasing our premium!", inline=False)
        embed.add_field(name=f"Rate Me", value="> [Upvote me here](https://top.gg/bot/1237992032715280385)", inline=False)
        embed.add_field(name=f"Privacy Policy", value="> [We never sell your data.](https://gist.github.com/PaullyScripter/6229b36372697feaf9c51292aaec9bc8)", inline=False)
        embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
        await interaction.response.edit_message(embed=embed, view=self)            
    else:
      await interaction.response.defer()

  async def on_timeout(self) -> None:
    help_select = discord.utils.get(self.children, placeholder="Choose a catergory")
    help_select.disabled = True
    await self.message.edit(view=self)

@client.tree.command(name="help", description="Shows a selectable drow down menu of available commands")
@app_commands.checks.cooldown(1, 20, key=lambda i: (i.user.id))
async def help(interaction: discord.Interaction):
  embed=discord.Embed(title="Equinox Navigator | /equinox", description="```Currently only operable with slash prefix.```", color=0xffffff)
  embed.set_author(name="Equinox' Commands List", icon_url=client.user.avatar)
  embed.add_field(name="My Categories", value="```Search through drop down menu down below.```", inline=False)
  embed.add_field(name=f"Updates {update}", value=update_note, inline=False)
  embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
  view = mySelect(interaction.user.id)
  await interaction.response.defer()
  msg = await interaction.followup.send(embed=embed, view=view)
  view.message = msg
  view.embed = embed

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


class CurrencyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Supported Currencies", style=discord.ButtonStyle.grey, custom_id="supported_currencies")
    async def supported_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        fiat_list = ", ".join(sorted(SUPPORTED_FIAT))
        crypto_list = ", ".join(sorted(SYMBOL_TO_ID.keys()))
        embed = discord.Embed(title="Supported Currencies", color=0xffffff)
        embed.add_field(name="Fiat", value=fiat_list, inline=False)
        embed.add_field(name="Crypto", value=crypto_list, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="exchange", description="Convert fiat <-> crypto <-> fiat using real-time rates")
@app_commands.describe(
    from_currency="Currency or crypto you're converting from (e.g. usd, btc, ltc)",
    amount="Amount to convert",
    to_currency="Currency or crypto you're converting to (e.g. vnd, xmr, eur)"
)
async def exchange(
    interaction: discord.Interaction,
    from_currency: str,
    amount: float,
    to_currency: str
):
    await interaction.response.defer()
    from_currency = from_currency.lower()
    to_currency = to_currency.lower()

    is_from_crypto = from_currency in SYMBOL_TO_ID
    is_to_crypto = to_currency in SYMBOL_TO_ID

    timestamp = int(datetime.now(timezone.utc).timestamp())

    async with aiohttp.ClientSession() as session:
        try:
            if is_from_crypto:
                ids = SYMBOL_TO_ID[from_currency]
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={to_currency}"
                async with session.get(url) as resp:
                    data = await resp.json()
                rate = data[ids][to_currency]
                converted = amount * rate

            elif is_to_crypto:
                ids = SYMBOL_TO_ID[to_currency]
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies={from_currency}"
                async with session.get(url) as resp:
                    data = await resp.json()
                rate = data[ids][from_currency]
                converted = amount / rate

            elif from_currency in SUPPORTED_FIAT and to_currency in SUPPORTED_FIAT:
                url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={from_currency},{to_currency}"
                async with session.get(url) as resp:
                    data = await resp.json()
                btc_to_from = data["bitcoin"][from_currency]
                btc_to_to = data["bitcoin"][to_currency]
                rate = btc_to_to / btc_to_from
                converted = amount * rate
            else:
                embed = discord.Embed(title="Supported Currencies", color=discord.Color.red())
                embed.add_field(name="Fiat", value=", ".join(sorted(SUPPORTED_FIAT)), inline=False)
                embed.add_field(name="Crypto", value=", ".join(sorted(SYMBOL_TO_ID.keys())), inline=False)
                await interaction.followup.send("One or both currencies are invalid.", embed=embed, ephemeral=True)
                return
        except Exception:
            await interaction.followup.send("Failed to fetch exchange rate. Try again later.", ephemeral=True)
            return

    embed = discord.Embed(title="💱 Currency Exchange", color=0xffffff)
    embed.add_field(name="From", value=f"`{amount}` `{from_currency.upper()}`", inline=True)
    embed.add_field(name="To", value=f"`{converted:.4f}` `{to_currency.upper()}`", inline=True)

    if is_from_crypto or (not is_from_crypto and not is_to_crypto):
        rate_display = f"1 {from_currency.upper()} = {rate:.6f} {to_currency.upper()}"
    else:
        rate_display = f"1 {from_currency.upper()} = {(1/rate):.6f} {to_currency.upper()}"

    embed.add_field(name="", value=f"Rate: {rate_display}", inline=False)
    embed.add_field(name="", value=f"Requested: <t:{timestamp}:R>", inline=False)                                           

    embed.set_footer(text="Rates may vary slightly in real exchanges.")

    await interaction.followup.send(embed=embed, view=CurrencyView())

                                        

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

               
@client.tree.command(name="check_tx", description="Check transaction details across chains")
@app_commands.describe(
    txid="Transaction ID/hash",
    chain="Blockchain to check (btc, ltc, doge, eth)",
    min_confirmations="Notify when this confirmation count is reached (max 11)"
)
async def check_tx(interaction: discord.Interaction, txid: str, chain: str, min_confirmations: int = None):
    await interaction.response.defer()
    chain = chain.lower()

    if chain not in SUPPORTED_CHAINS:
        await interaction.followup.send(f"❌ Unsupported chain. Supported: {', '.join(SUPPORTED_CHAINS)}", ephemeral=True)
        return

    if min_confirmations is not None and not (1 <= min_confirmations <= 11):
        await interaction.followup.send("❌ min_confirmations must be between 1 and 11", ephemeral=True)
        return

    data, error = await fetch_tx_data(chain, txid)
    if error:
        await interaction.followup.send(f"❌ Error: {error}", ephemeral=True)
        return

    embed, confirmations = parse_tx_data(chain, data)
    await interaction.followup.send(embed=embed)

    if min_confirmations and confirmations < min_confirmations:
        pending_alerts[(interaction.user.id, txid, chain)] = {
            "target": min_confirmations,
            "channel": interaction.channel.id if interaction.guild else None
        }
        await interaction.followup.send(f"⏳ You will be notified when this transaction reaches {min_confirmations} confirmations.", ephemeral=True)

                                                        
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

@client.tree.command(name="optout", description="Opt in or out of message tracking.")
@app_commands.describe(option="Choose whether to opt in or out of message tracking")
async def optout(interaction: discord.Interaction, option: Literal["in", "out"]):
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    data = load_server_data(guild_id)
    if not data:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Opt-Out",
                description="```\nMessage counter has not been set up for this server.\n```",
                color=0xffffff
            ),
            ephemeral=True
        )
        return

    if "opted_out_users" not in data:
        data["opted_out_users"] = []

    if option == "out":
        if user_id in data["opted_out_users"]:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Already Opted Out",
                    description="```\nYou are already opted out of message tracking.\n```",
                    color=0xffffff
                ),
                ephemeral=True
            )
            return
        data["opted_out_users"].append(user_id)
        save_server_data(guild_id, data)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Opt-Out Successful",
                description="```\nYou have opted out. Your messages will no longer be counted.\n```",
                color=0xffffff
            ),
            ephemeral=True
        )

    elif option == "in":
        if user_id not in data["opted_out_users"]:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Opted Out",
                    description="```\nYou were not opted out of message tracking.\n```",
                    color=0xffffff
                ),
                ephemeral=True
            )
            return
        data["opted_out_users"].remove(user_id)
        save_server_data(guild_id, data)
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Opt-In Successful",
                description="```\nYou have opted back in. Your messages will now be counted.\n```",
                color=0xffffff
            ),
            ephemeral=True
        )



@client.tree.command(name="messagecounter")
@app_commands.describe(option="Enable or disable the message counter")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(option=[
    app_commands.Choice(name="Enable", value="enable"),
    app_commands.Choice(name="Disable", value="disable")
])
async def messagecounter(interaction: discord.Interaction, option: app_commands.Choice[str]):

    guild_id = str(interaction.guild.id)
    data = load_server_data(guild_id) or {
        "guild_id": guild_id,
        "status": "disabled",
        "users": {},
        "blacklisted_channels": []
    }

    if option.value == "enable":
        if "opted_out_users" not in data:
            data["opted_out_users"] = []
        data["status"] = "enabled"
        save_server_data(guild_id, data)
        await interaction.response.send_message(embed=discord.Embed(title="Message Counter", description=f"```js\nStatus: Enabled.\n```", color = 0xffffff), ephemeral=True)
        
    elif option.value == "disable":
        data["status"] = "disabled"
        save_server_data(guild_id, data)
        await interaction.response.send_message(embed=discord.Embed(title="Message Counter", description=f"```js\nStatus: Disabled.\n```", color = 0xffffff), ephemeral=True)

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

@client.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    data = load_server_data(guild_id)
    if not data or data.get("status") != "enabled":
        return

    if str(message.channel.id) in data.get("blacklisted_channels", []):
        return

    if user_id in data.get("opted_out_users", []):
        return

    data["users"][user_id] = data["users"].get(user_id, 0) + 1
    save_server_data(guild_id, data)




@client.tree.command(name="messagecount")
@app_commands.describe(user="User to check message count for")
async def messagecount(interaction: discord.Interaction, user: discord.User = None):
    user = user or interaction.user
    guild_id = str(interaction.guild.id)
    data = load_server_data(guild_id)
    if not data:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Message Counter",
                description="```\nMessage counter has not been set up for this server, use /messagecounter.\n```",
                color=0xffffff
            ),
            ephemeral=True
        )
        return

    opted_out = str(user.id) in data.get("opted_out_users", [])

    if opted_out:
        embed = discord.Embed(
            title="Message Count",
            description=f"🔒 {user.mention} has opted out of message tracking.",
            color=0xffffff
        )
    else:
        count = data["users"].get(str(user.id), 0)
        embed = discord.Embed(
            title="Message Count",
            description=f"{user.mention} has {count} message(s).",
            color=0xffffff
        )

    embed.set_footer(text=f"Message Counter: {data.get('status', 'unknown')}")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    
    
@client.tree.command(name="messageblacklistview")
async def messageblacklistview(interaction: discord.Interaction):

    guild_id = str(interaction.guild.id)
    data = load_server_data(guild_id)
    if not data:
        await interaction.response.send_message(embed=discord.Embed(title="Message Counter Blacklist", description=f"```\nMessage counter has not been set up for this server, use /messagecounter.\n```", color = 0xffffff), ephemeral=True)
        return

    blacklisted_ids = data.get("blacklisted_channels", [])
    if not blacklisted_ids:
        await interaction.response.send_message(embed=discord.Embed(title="Message Counter Blacklist", description=f"```\nThere are no blacklisted channels.\n```", color = 0xffffff), ephemeral=True)
        return

    mentions = []
    for cid in blacklisted_ids:
        channel = interaction.guild.get_channel(int(cid))
        if channel:
            mentions.append(channel.mention)
        else:
            mentions.append(f"<# {cid}>")

    desc = "\n".join(mentions)
    embed = discord.Embed(title="Blacklisted Channels", description=desc, color = 0xffffff)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="messagecountdeduct")
@app_commands.describe(user="User to deduct message count from", amount="Amount to deduct")
@app_commands.checks.has_permissions(administrator=True)
async def messagecountdeduct(interaction: discord.Interaction, user: discord.User, amount: int):

    guild_id = str(interaction.guild.id)
    data = load_server_data(guild_id)
    if not data:
        await interaction.response.send_message(embed=discord.Embed(title="Message Counter", description=f"```\nMessage counter has not been set up for this server, use /messagecounter.\n```", color = 0xffffff), ephemeral=True)
        return

    uid = str(user.id)
    current = data["users"].get(uid, 0)
    if amount > current:
        await interaction.response.send_message(embed=discord.Embed(title="Message Deduction", description=f"```\nYour input amount is more than the user's message count(s).\n```", color = 0xffffff), ephemeral=True)
        return

    data["users"][uid] = current - amount
    save_server_data(guild_id, data)
    await interaction.response.send_message(embed=discord.Embed(title="Message Deducted", description=f"\nSuccessfully deducted {amount} message(s) from {user.mention}.\n", color = 0xffffff), ephemeral=True)


@client.tree.command(name="messagecountleaderboard")
async def messagecountleaderboard(interaction: discord.Interaction):
    guild_id = str(interaction.guild.id)
    data = load_server_data(guild_id)
    if not data:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Message Counter",
                description="```\nMessage counter has not been set up for this server, use /messagecounter.\n```",
                color=0xffffff
            ),
            ephemeral=True
        )
        return

    sorted_users = sorted(data["users"].items(), key=lambda item: item[1], reverse=True)
    pages = [sorted_users[i:i + 10] for i in range(0, min(len(sorted_users), 20), 10)]

    if not pages:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Message Leaderboard",
                description="```\nNo data available.\n```",
                color=0xffffff
            ),
            ephemeral=True
        )
        return

    embeds = []
    for idx, page in enumerate(pages):
        desc = ""
        for user_id, count in page:
            is_opted_out = user_id in data.get("opted_out_users", [])
            user = interaction.guild.get_member(int(user_id))
            if not user:
                continue

            if is_opted_out:
                desc += f"{user.mention} 🔒 This user has opted out\n"
            else:
                desc += f"{user.mention} - {count} messages\n"

        embed = discord.Embed(title=f"Message Leaderboard - Page {idx + 1}", description=desc, color=0xffffff)
        embed.set_footer(text="/optout to not have your messages counted.")
        embeds.append(embed)

    current_page = 0
    await interaction.response.send_message(embed=embeds[current_page], ephemeral=False)
    message = await interaction.original_response()

    if len(embeds) > 1:
        await message.edit(view=PaginationView(embeds))

@client.tree.command(name="messagecountgive", description="Transfer your message count to another user.")
@app_commands.describe(to_user="User to give messages to", amount="Amount to transfer")
async def messagecountgive(interaction: discord.Interaction, to_user: discord.User, amount: int):
    from_user = interaction.user

    if from_user.id == to_user.id:
        embed = discord.Embed(
            title="Message Count Transfer",
            description="```Cannot transfer messages to yourself.```",
            color=0xffffff
        )
        await interaction.response.send_message(embed=embed)
        return

    guild_id = str(interaction.guild.id)
    data = load_server_data(guild_id)
    if not data:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Message Count Transfer",
                description="```\nMessage counter has not been set up for this server, use /messagecounter.\n```",
                color=0xffffff
            ),
            ephemeral=True
        )
        return

    from_id = str(from_user.id)
    to_id = str(to_user.id)

    if data["users"].get(from_id, 0) < amount:
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Message Count Transfer",
                description="```\nInsufficient message count(s) to transfer.```",
                color=0xffffff
            )
        )
        return

    data["users"][from_id] -= amount
    data["users"][to_id] = data["users"].get(to_id, 0) + amount
    save_server_data(guild_id, data)

    await interaction.response.send_message(
        embed=discord.Embed(
            title="Message Count Transfer",
            description=f"Transferred {amount} messages from {from_user.mention} to {to_user.mention}.",
            color=0xffffff
        )
    )


@client.tree.command(name="messageblacklist")
@app_commands.describe(action="Add or remove a blacklisted channel", channel="Channel to blacklist/unblacklist")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(action=[
    app_commands.Choice(name="Add", value="add"),
    app_commands.Choice(name="Remove", value="remove")
])
async def messageblacklist(interaction: discord.Interaction, action: app_commands.Choice[str], channel: discord.TextChannel):

    guild_id = str(interaction.guild.id)
    data = load_server_data(guild_id)
    if not data:
        await interaction.response.send_message(embed=discord.Embed(title="Message Counter Blacklist", description=f"```\nMessage counter has not been set up for this server, use /messagecounter.\n```", color = 0xffffff), ephemeral=True)
        return

    channel_id = str(channel.id)
    blacklist = data.get("blacklisted_channels", [])

    if action.value == "add":
        if channel_id not in blacklist:
            blacklist.append(channel_id)
            data["blacklisted_channels"] = blacklist
            save_server_data(guild_id, data)
            await interaction.response.send_message(embed=discord.Embed(title="Message Counter Blacklist", description=f"Channel {channel.mention} has been blacklisted.", color = 0xffffff), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Message Counter Blacklist", description=f"Channel {channel.mention} has already been blacklisted.", color = 0xffffff), ephemeral=True)
    elif action.value == "remove":
        if channel_id in blacklist:
            blacklist.remove(channel_id)
            data["blacklisted_channels"] = blacklist
            save_server_data(guild_id, data)
            await interaction.response.send_message(embed=discord.Embed(title="Message Counter Blacklist", description=f"Channel {channel.mention} has been unblacklisted.", color = 0xffffff), ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Message Counter Blacklist", description=f"Channel {channel.mention} isn't blacklisted.", color = 0xffffff), ephemeral=True)

class PaginationView(discord.ui.View):
    def __init__(self, embeds):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.embeds[self.current_page])

DEV_USER_ID = [857932717681147954]

class PromptModal(discord.ui.Modal, title="Prompt Gemini AI"):
    prompt_input = discord.ui.TextInput(
        label="Your prompt",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000
    )

    dev_field = discord.ui.TextInput(
        label="Dev? (y/n)",
        placeholder="Leave blank or type 'n' for user mode, 'y' for dev mode",
        required=False,
        max_length=1
    )

    def __init__(self, original_interaction: discord.Interaction):
        super().__init__()
        self.original_interaction = original_interaction

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        prompt = self.prompt_input.value
        dev_answer = self.dev_field.value.lower().strip() if self.dev_field.value else "n"

                        
        if dev_answer == "y":
            if interaction.user.id not in DEV_USER_ID:
                await interaction.followup.send("❌ You are not authorized for Dev mode.", ephemeral=True)
                return
            bypass_filter = True
        else:
            bypass_filter = False

                                   
        if not bypass_filter and await violates_tos(prompt):
            await interaction.followup.send("❌ You can not prompt that!", ephemeral=True)
            return

        response_data = await ask_gemini(prompt)
        try:
            answer = response_data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            await interaction.followup.send("❌ Error retrieving response from Gemini.", ephemeral=True)
            return

        if not bypass_filter and await violates_tos(answer):
            await interaction.followup.send("❌ You can not prompt that!", ephemeral=True)
            return

        words = answer.split()
        word_limit = 250
        if len(words) > word_limit:
            pages = [' '.join(words[i:i+word_limit]) for i in range(0, len(words), word_limit)]
            embed = discord.Embed(
                title="> Gemini said...",
                description=pages[0],
                color=0xFFFFFF
            )
            embed.set_footer(
                text=f"Page -/- | Gemini AI 2.0 Flash",
                icon_url=interaction.user.display_avatar.url
            )
            view = GeminiView(pages, interaction)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        else:
            embed = discord.Embed(
                title="> Gemini said...",
                description=answer,
                color=0xFFFFFF
            )
            embed.set_footer(
                text=f"Gemini AI 2.0 Flash",
                icon_url=interaction.user.display_avatar.url
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

                       
class PromptButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Prompt", style=discord.ButtonStyle.primary, custom_id="prompt_button")
    async def prompt_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gemini_data = load_gemini_servers()
        if str(interaction.guild.id) not in gemini_data["servers"]:
            await interaction.response.send_message("❌ This Gemini implementation is outdated. Ask an admin to reinitialize it.", ephemeral=True)
            return

        await interaction.response.send_modal(PromptModal(interaction))


                           
class GeminiView(discord.ui.View):
    def __init__(self, pages, interactor: discord.Interaction):
        super().__init__(timeout=300)
        self.pages = pages
        self.current = 0
        self.interactor = interactor

    async def update_embed(self, interaction):
        embed = discord.Embed(
            title="> AI said...",
            description=self.pages[self.current],
            color=0xFFFFFF
        )
        embed.set_footer(
            text=f"Page {self.current + 1}/{len(self.pages)} | Gemini AI 2.0 Flash",
            icon_url=self.interactor.user.display_avatar.url
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current > 0:
            self.current -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current < len(self.pages) - 1:
            self.current += 1
            await self.update_embed(interaction)

                              
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

class RemoveGeminiView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = str(guild_id)

    @discord.ui.button(label="Remove Gemini", style=discord.ButtonStyle.danger, custom_id="remove_gemini_button")
    async def remove_gemini(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only administrators can remove Gemini implementation.", ephemeral=True)
            return

        gemini_data = load_gemini_servers()
        if self.guild_id in gemini_data["servers"]:
            gemini_data["servers"].remove(self.guild_id)
            save_gemini_servers(gemini_data)
            await interaction.response.send_message("✅ Gemini implementation removed for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ This server isn't registered with Gemini.", ephemeral=True)


def load_gemini_servers():
    if not os.path.exists("geminiServer.json"):
        return {"servers": []}
    with open("geminiServer.json", "r") as f:
        return json.load(f)

def save_gemini_servers(data):
    with open("geminiServer.json", "w") as f:
        json.dump(data, f, indent=2)

                         
@client.tree.command(name="ask_gemini", description="Ask Gemini AI any question")
@app_commands.checks.has_permissions(administrator=True)
async def ask_gemini_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    guild = interaction.guild
    if not guild:
        await interaction.followup.send("❌ This command must be used in a server.", ephemeral=True)
        return

    owner_id = guild.owner_id

    is_active, is_premium, expires_at = user_is_active(owner_id)

    if not is_premium:
        await interaction.followup.send(
            embed=discord.Embed(
                title="You are being restricted",
                description="Gemini command is only available to our elite users. And the server's owner does not have our premium.\nConsider buying our useful premium with lots of perks?\nUse </help:1242738769099231302> to check out our premium perks.",
                color=0xffffff
            ),
            view=BuyPremium()
        )
        return

    gemini_data = load_gemini_servers()
    guild_id_str = str(guild.id)

    if guild_id_str in gemini_data["servers"]:
        await interaction.followup.send("⚠️ This server has already used the Gemini command.", ephemeral=True, view=RemoveGeminiView(guild.id))
        return

    gemini_data["servers"].append(guild_id_str)
    save_gemini_servers(gemini_data)

    embed = discord.Embed(
        title="> Ask Gemini",
        description=None,
        color=0xFFFFFF
    )
    embed.set_image(url="attachment://Gemini.png")
    embed.add_field(name="<:gemini:1364105172011454485> Model", value="- Gemini 2.0 Flash", inline=True)
    embed.add_field(
        name="⚠️ Terms",
        value="- [Discord ToS.](https://discord.com/terms)\n- [Gemini API ToS.](https://ai.google.dev/gemini-api/terms)",
        inline=True
    )

    await interaction.channel.send(embed=embed, view=PromptButtonView())

    await interaction.followup.send("✅ Successfully sent Gemini playground!", ephemeral=True)

class DeployButton(discord.ui.Button):
    def __init__(self, author: discord.User, callback_fn, parent_view):
        super().__init__(label="Deploy Drop", style=discord.ButtonStyle.success)
        self.author = author
        self.callback_fn = callback_fn
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Only the drop creator can deploy this.", ephemeral=True)
            return

        self.disabled = True
        await interaction.response.edit_message(view=self.parent_view)                             
        await self.callback_fn(interaction)



class DeployView(discord.ui.View):
    def __init__(self, author: discord.User, callback_fn):
        super().__init__(timeout=60)
        self.add_item(DeployButton(author, callback_fn, self))



class ColorButton(discord.ui.Button):
    def __init__(self, color_name, custom_id, correct_color, drop_view):
        style_map = {
            "red": discord.ButtonStyle.danger,
            "green": discord.ButtonStyle.success,
            "blue": discord.ButtonStyle.primary,
            "grey": discord.ButtonStyle.secondary
        }
        super().__init__(label=color_name.title(), style=style_map[color_name], custom_id=custom_id, disabled=True)
        self.color_name = color_name
        self.correct_color = correct_color
        self.drop_view = drop_view

    async def callback(self, interaction: discord.Interaction):
        async with self.drop_view.lock:
            if self.drop_view.winner_found:
                await interaction.response.send_message("This drop is already claimed!", ephemeral=True)
                return

            if self.color_name == self.correct_color:
                self.drop_view.winner_found = True
                for child in self.drop_view.children:
                    child.disabled = True
                await interaction.response.edit_message(view=self.drop_view)
                await interaction.followup.send(f"🎉 {interaction.user.mention} clicked the correct button and won **{self.drop_view.prize}**!")
            else:
                await interaction.response.send_message("❌ You got the wrong one!", ephemeral=True)


class DropView(discord.ui.View):
    def __init__(self, correct_color, prize):
        super().__init__(timeout=300)
        self.correct_color = correct_color
        self.prize = prize
        self.winner_found = False
        self.lock = asyncio.Lock()
        self.color_options = ["red", "green", "blue", "grey"]
        random.shuffle(self.color_options)

        for i, color in enumerate(self.color_options):
            self.add_item(ColorButton(color, f"drop_btn_{i}", self.correct_color, self))
    async def on_timeout(self):
        if not self.winner_found and self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(content="Time's up! No one clicked the correct button in time.", view=self)
            except discord.NotFound:
                pass




@client.tree.command(name="drop", description="Start a drop game.")
@app_commands.describe(prize="The prize for the drop", reaction="Add participation reaction (🤚)?")
async def drop(interaction: discord.Interaction, prize: str, reaction: bool = False):
    await interaction.response.defer()

    async def deploy_callback(deploy_interaction: discord.Interaction):

        correct_color = random.choice(["red", "green", "blue", "grey"])
        view = DropView(correct_color, prize)

        drop_embed = discord.Embed(
            title="Drop Challenge",
            description=f"The first person to click the right one wins **{prize}**!",
            color=0x000000
        )
        drop_embed.set_footer(text="Dropping in between 5–10 seconds...")

        view.message = await deploy_interaction.followup.send(embed=drop_embed, view=view)

        await asyncio.sleep(random.randint(5, 10))

        await interaction.followup.send(f"# CLICK THE **{correct_color.upper()}** BUTTON NOW!")

        for item in view.children:
            item.disabled = False
        await view.message.edit(view=view)


                                           
    instruction_embed = discord.Embed(
        title="Get Ready!",
        description=(
                "- **When announced**, click the correct colored button in the next embed.\n"
                f"- The first person to click the right one wins **{prize}**!"
            ),
        color=0x000000
    )
    instruction_embed.set_footer(text="Only the drop creator can deploy it.")

    view = DeployView(interaction.user, deploy_callback)
    deploy_message = await interaction.followup.send(embed=instruction_embed, view=view)

    if reaction:
        await deploy_message.add_reaction("🤚")




user_graph_data = {}                                           

def random_color():
                                                
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def process_function(func):
                                                    
    func = func.strip()

                                                       
    if re.match(r"^\(\d+,\d+\)$", func):
        return None                            

    func = func.replace("^", "**")
    func = func.replace("sqrt", "numpy.sqrt")
    func = re.sub(r'\by\s*=\s*', "", func)                            

                                       
    func = re.sub(r'(\d)(x)', r'\1*x', func)             
    func = re.sub(r'(x)(\d)', r'x*\2', func)             

    return func

def is_valid_function(func):
                                                                             
    try:
        if not func:
            return False                              

        x = numpy.linspace(-10, 10, 100)
        safe_func = process_function(func)
        if not safe_func:
            return False                  

                            
        test_x = numpy.linspace(0, 10, 100) if "sqrt" in safe_func else x

        y = eval(safe_func, {"numpy": numpy, "x": test_x})
        return y.shape == x.shape                           
    except Exception:
        return False


def generate_graph(user_id, zoom_factor=1.0):
                                                                                      
    try:
        if user_id not in user_graph_data:
            raise ValueError("No functions or points to plot.")

        if 'zoom' not in user_graph_data[user_id]:
            user_graph_data[user_id]['zoom'] = 1.0                    

        user_graph_data[user_id]['zoom'] *= zoom_factor                     
        
        zoom = user_graph_data[user_id]['zoom']
        x_min, x_max = -10 * zoom, 10 * zoom
        y_min, y_max = -10 * zoom, 10 * zoom
        x = numpy.linspace(x_min, x_max, 400)  

        plt.figure(figsize=(6, 6))  

                        
        for func, color in user_graph_data[user_id].get('functions', []):
            try:
                valid_func = process_function(func)
                safe_x = numpy.copy(x)
                
                                                              
                if "numpy.sqrt" in valid_func:
                    safe_x = numpy.where(safe_x >= 0, safe_x, numpy.nan)
                
                y = eval(valid_func, {"numpy": numpy, "x": safe_x}) 
                plt.plot(x, y, label=func, color=color)
            except Exception as e:
                raise ValueError(f"Invalid function '{func}'. Error: {e}")
        
                                  
        for point in user_graph_data[user_id].get('points', []):
            plt.scatter(*point, color='red', label=f"Point {point}")

        plt.xlim([x_min, x_max])  
        plt.ylim([y_min, y_max])  
        plt.axhline(0, color='black', linewidth=1)
        plt.axvline(0, color='black', linewidth=1)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.legend()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        user_graph_data[user_id]['graph_image'] = buf                        

        plt.clf()
    except Exception as e:
        user_graph_data[user_id]['graph_image'] = None  
        raise





class GraphView(discord.ui.View):
                                                   
    def __init__(self, user, message=None):
        super().__init__(timeout=120)                     
        self.user = user  
        self.message = message                           

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
                                                        
        if interaction.user != self.user:
            await interaction.response.send_message("You can't interact with this graph.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
                                                
        for item in self.children:
            item.disabled = True                       
        if self.message:
            try:
                await self.message.edit(view=self)                                        
            except discord.NotFound:
                pass                                  

    @discord.ui.button(label="Add Graph", style=discord.ButtonStyle.primary)
    async def add_graph(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(FunctionInputModal(self.user.id))

    @discord.ui.button(label="Delete Function", style=discord.ButtonStyle.danger)
    async def delete_function(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DeleteFunctionModal(self.user.id))

    @discord.ui.button(label="All Functions", style=discord.ButtonStyle.secondary)
    async def all_functions(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = self.user.id
        functions = user_graph_data.get(user_id, {}).get('functions', [])
        function_list = "\n".join([f"{i+1}. {func} - Color: {color}" for i, (func, color) in enumerate(functions)]) or "No functions added yet."
        embed = discord.Embed(title="Functions in the Graph", description=function_list, color=0xffffff)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="Zoom In/Out", style=discord.ButtonStyle.secondary)
    async def zoom_graph(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ZoomModal(self.user.id))

class FunctionInputModal(discord.ui.Modal):
                                    
    def __init__(self, user_id):
        super().__init__(title="Add Function")
        self.user_id = user_id
        self.function_input = discord.ui.TextInput(label="Enter Function (e.g., np.sin(x))", required=True)
        self.add_item(self.function_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = self.user_id
        function = self.function_input.value.strip()
        if not is_valid_function(function):
            await interaction.followup.send(f"The function `{function}` is invalid and was not added.", ephemeral=True)
            return
        user_graph_data.setdefault(user_id, {"functions": [], "graph_image": None})  
        user_graph_data[user_id]["functions"].append((self.function_input.value.strip(), random_color()))
        generate_graph(user_id)
        msg = await interaction.followup.send(content=f"Adding {self.function_input.value.strip()} to graph... <a:loading_symbol:1295113412564615249>")
        await send_graph_embed(interaction, user_id)
        await msg.delete()

class DeleteFunctionModal(discord.ui.Modal):
                                     
    def __init__(self, user_id):
        super().__init__(title="Delete Function")
        self.user_id = user_id
        self.function_index = discord.ui.TextInput(label="Enter function number to delete", required=True)
        self.add_item(self.function_index)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.user_id
        try:
                                                
            if len(user_graph_data[user_id]["functions"]) == 1:
                return await interaction.response.send_message("You cannot delete the last function.", ephemeral=True)

            index = int(self.function_index.value) - 1
            if 0 <= index < len(user_graph_data[user_id]["functions"]):
                await interaction.response.defer()
                removed_function = user_graph_data[user_id]["functions"].pop(index)
                generate_graph(user_id)

                msg = await interaction.channel.send(content=f"Deleting `{removed_function[0]}`... <a:loading_symbol:1295113412564615249>")
                                               
                await send_graph_embed(interaction, user_id)
                await msg.delete()
                                                                    
                await interaction.followup.send(f"Function `{removed_function[0]}` removed.", ephemeral=True)
            else:
                await interaction.response.send_message("Invalid function index.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number.", ephemeral=True)

class ZoomModal(discord.ui.Modal):
                               
    def __init__(self, user_id):
        super().__init__(title="Zoom Graph")
        self.user_id = user_id
        self.zoom_input = discord.ui.TextInput(label="Zoom factor", required=True)
        self.add_item(self.zoom_input)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.user_id
        try:
            zoom_factor = float(self.zoom_input.value)
            if zoom_factor <= 0:
                return await interaction.response.send_message("Zoom factor must be greater than zero.", ephemeral=True)
            await interaction.response.defer()
            generate_graph(user_id, zoom_factor)
            msg = await interaction.channel.send(content=f"Zooming the graph {self.zoom_input.value} times... <a:loading_symbol:1295113412564615249>")
            await send_graph_embed(interaction, user_id)
            await msg.delete()
            await interaction.followup.send(content=f"Zoomed the graph {self.zoom_input.value} times.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Invalid input. Please enter a valid number.", ephemeral=True)


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



@client.tree.command(name="graph", description="Create a graph with a function")
async def graph_command(interaction: discord.Interaction, function: str):
  is_active, is_premium, expires_at = user_is_active(interaction.user.id)
  if is_premium:
    await interaction.response.defer()
    msg = await interaction.followup.send(content="Please wait while your graph is generating... <a:loading_symbol:1295113412564615249>")
    user_id = interaction.user.id
    user_graph_data.setdefault(user_id, {"functions": [], "graph_image": None, "message": None})

    user_graph_data[user_id]["functions"].append((function, random_color()))
    generate_graph(user_id)

                                       
    if "message" in user_graph_data[user_id] and user_graph_data[user_id]["message"]:
        try:
            await user_graph_data[user_id]["message"].delete()
        except (discord.NotFound, discord.HTTPException):
            pass                             

    embed = discord.Embed(title=None, description=None, color=0xffffff)
    embed.set_author(name=f"{interaction.user.name}'s Graph", icon_url=interaction.user.avatar)
    embed.set_image(url="attachment://graph.png")

    view = GraphView(interaction.user)
    message = await interaction.channel.send(embed=embed, file=discord.File(user_graph_data[user_id]["graph_image"], filename="graph.png"), view=view)
    await msg.delete()

                                     
    user_graph_data[user_id]["message"] = message
  else:
    await interaction.response.send_message(embed=discord.Embed(title="You are being restricted", description="Graph command is only available to our elite users.\nConsider buying our useful premium with lots of perks?\nUse </help:1242738769099231302> to check out our premium perks.", color=0xffffff), view=BuyPremium())

class UpdateButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
  @discord.ui.button(label="Check update", style=discord.ButtonStyle.green, custom_id="update_check")
  async def update_check(self, interaction: discord.Interaction, Button: discord.Button):
    await interaction.response.defer()
    embed = discord.Embed(title=f"Equinox's Update - {update}", description=update_note_content, color=0xffffff)
    await interaction.followup.send(embed=embed, ephemeral=True)

@client.tree.command(name="update", description="Setup a Equinox' updates (Devs only, users use /help)")
async def update_setup(interaction: discord.Interaction):
  if interaction.user.id in devs:
    embed = discord.Embed(title=f"Equinox's Updates Checker", description="```Please click the button if you wish to check Equinox' update(s)```", color=0xffffff)
    await interaction.response.send_message(embed=embed, view=UpdateButton())
  else:
    await interaction.response.defer(ephemeral=True)
    await interaction.followup.send("Devs only")

                                                                              



@client.tree.command(name="gen_code", description="Generate premium code(s) (Devs only)")
@app_commands.describe(
    tier="Choose the premium tier",
    amount="How many codes to generate (default 1, no limit)"
)
@app_commands.choices(tier=[
    discord.app_commands.Choice(name="Monthly",  value="monthly"),
    discord.app_commands.Choice(name="Yearly",   value="yearly"),
    discord.app_commands.Choice(name="Lifetime", value="lifetime"),
])
async def gen_code(
    interaction: discord.Interaction,
    tier: discord.app_commands.Choice[str],
    amount: Optional[int] = 1
):
    if interaction.user.id not in devs:
        return await interaction.response.send_message("Devs only.", ephemeral=True)

    tier_value = tier.value.lower()
    count = 1 if amount is None else max(1, int(amount))

    await interaction.response.defer(ephemeral=True)

                        
    try:
        new_codes = replenish_codes(tier_value, count)
    except Exception as e:
        return await interaction.followup.send(f"Error: {e}", ephemeral=True)

                                 
    if len(new_codes) > 10:
        buf = io.BytesIO(("\n".join(new_codes) + "\n").encode("utf-8"))
        file = discord.File(buf, filename=f"{tier_value}_codes_{len(new_codes)}.txt")
        await interaction.followup.send(
            content=f"✅ Generated **{len(new_codes)}** {tier_value.title()} code(s). See attachment.",
            file=file,
            ephemeral=True
        )
    else:
        emb = discord.Embed(
            title=f"✅ Generated {len(new_codes)} {tier_value.title()} code(s)",
            color=0xFFFFFF
        )
        for i, c in enumerate(new_codes, 1):
            emb.add_field(name=str(i), value=f"```{c}```", inline=False)
        await interaction.followup.send(embed=emb, ephemeral=True)

                                       
    try:
        log_channel = client.get_channel(1242633669890277456)
        if log_channel:
            msg = discord.Embed(
                title=f"{interaction.user} generated {len(new_codes)} {tier_value.title()} code(s)",
                color=0xFFFFFF
            )
            preview = "\n".join(f"`{c}`" for c in new_codes[:50])
            if preview:
                msg.description = preview if len(new_codes) <= 50 else (preview + f"\n…(+{len(new_codes)-50} more)")
            await log_channel.send(embed=msg)
    except Exception:
        pass


@client.tree.command(name="remove_premium", description="Remove premium from users (Devs only)")
async def remove_premium(interaction: discord.Interaction, member: discord.Member):
    if interaction.user.id not in devs:
        return await interaction.response.send_message("Devs only.", ephemeral=True)

    removed_tier = None
    for tier, file_path in SUB_FILES.items():
        data = load_json(file_path)
        users = data.get("users", [])
        if any(u.get("user_id") == member.id for u in users):
            remove_subscription(member.id, tier)
            removed_tier = tier
            break

    if removed_tier:
        embed = discord.Embed(color=0xFFFFFF)
        embed.set_author(name=f"Successfully removed premium from {member}")
        embed.add_field(name="Premium Plan", value=f"**> {removed_tier.title()}**", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(color=0xFFFFFF)
        embed.set_author(name=f"{member} has no active premium plan")
        embed.add_field(name="Premium Plan", value=f"**> None**", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="export_codes", description="Export premium codes to .txt for SellAuth (Devs only)")
@app_commands.choices(tier=[
    discord.app_commands.Choice(name="Monthly",  value="monthly"),
    discord.app_commands.Choice(name="Yearly",   value="yearly"),
    discord.app_commands.Choice(name="Lifetime", value="lifetime"),
    discord.app_commands.Choice(name="All",      value="all"),
])
async def export_codes(interaction: discord.Interaction, tier: discord.app_commands.Choice[str]):
    if interaction.user.id not in devs:
        return await interaction.response.send_message("Devs only.", ephemeral=True)

    await interaction.response.defer(ephemeral=True)

    tiers = ("monthly", "yearly", "lifetime") if tier.value == "all" else (tier.value,)

    files: list[discord.File] = []
    summary_lines: list[str] = []
    empty_tiers: list[str] = []

    for t in tiers:
                                                   
        codes = _load_codes_for_tier(t)
        if codes:
            files.append(_as_txt_file(f"{t}_codes.txt", codes))
            summary_lines.append(f"- {t.title()}: {len(codes)} code(s)")
        else:
            empty_tiers.append(t)
            summary_lines.append(f"- {t.title()}: 0 code(s)")

    if not files:
        return await interaction.followup.send(
            "No available codes found for the requested tier(s).",
            ephemeral=True
        )

    await interaction.followup.send(
        content="Here are the current code lists for SellAuth:\n" + "\n".join(summary_lines),
        files=files,
        ephemeral=True
    )

@client.tree.command(name="stats", description="Shows Equinox' stats (Devs only)")
async def stats(interaction: discord.Interaction):
    if interaction.user.id not in devs:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Devs only.")
        return

    data = load_stats()
    events = data.get("events", [])

                                 
    now = datetime.now(timezone.utc)
    day_ago   = now - timedelta(days=1)
    week_ago  = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    year_ago  = now - timedelta(days=365)

    count_day = count_week = count_month = count_year = 0
    unique_users: set[int] = set()
    per_command: dict[str, int] = {}
    per_day: dict[str, int] = {}                          

    for e in events:
        try:
            ts_raw = e.get("ts")
            user_id = int(e.get("user_id"))
            cmd = str(e.get("command"))
            ts = datetime.fromisoformat(ts_raw)
        except Exception:
            continue

                                                              
        if user_id in IGNORED_USER_IDS:
            continue

        unique_users.add(user_id)

                           
        if ts >= day_ago:
            count_day += 1
        if ts >= week_ago:
            count_week += 1
        if ts >= month_ago:
            count_month += 1
        if ts >= year_ago:
            count_year += 1

                     
        per_command[cmd] = per_command.get(cmd, 0) + 1

                                    
        day_key = ts.date().isoformat()
        per_day[day_key] = per_day.get(day_key, 0) + 1

                       
    if per_command:
        top_cmd, top_count = max(per_command.items(), key=lambda kv: kv[1])
    else:
        top_cmd, top_count = "None", 0

                                                
    ticket = 'ticket-json'
    try:
        with open("verify_system.json", encoding="utf-8") as f:
            verify_json = json.load(f)
        verify_count = len(verify_json.get("guilds", []))
    except FileNotFoundError:
        verify_count = 0

    guild_count  = len(client.guilds)
    user_count   = len(set(client.get_all_members()))
    py_version   = sys.version.split()[0]
    ticket_count = max(
        0,
        len([n for n in os.listdir(ticket)
             if os.path.isfile(os.path.join(ticket, n))]) - 1
    )

                           
    desc = (
        "```js\n"
        f"Guilds: {guild_count}\n"
        f"Users (cached): {user_count}\n"
        f"Python Version: {py_version}\n"
        f"Guild Ticket Deployed: {ticket_count}\n"
        f"Verify System Deployed: {verify_count}\n"
        "-------------------------\n"
        f"Commands (last 24h): {count_day}\n"
        f"Commands (last 7d):  {count_week}\n"
        f"Commands (last 30d): {count_month}\n"
        f"Commands (last 365d): {count_year}\n"
        f"Unique users (all time, non-dev): {len(unique_users)}\n"
        f"Top command: {top_cmd} ({top_count} uses)\n"
        "```"
    )

    embed = discord.Embed(
        title="🤍 Equinox Stats",
        description=desc,
        color=0xFFFFFF
    )
    embed.set_footer(text="Command analytics (dev-only, devs excluded from stats)")

                                            
                                    
    last_30_days = [(now.date() - timedelta(days=i)).isoformat()
                    for i in range(29, -1, -1)]
    counts = [per_day.get(d, 0) for d in last_30_days]

                                                     
    file = None
    if any(counts):
        plt.figure(figsize=(9, 4))
        plt.plot(last_30_days, counts, marker="o")
        plt.xticks(rotation=45, ha="right", fontsize=7)
        plt.ylabel("Commands")
        plt.xlabel("Date")
        plt.title("Commands per day (last 30 days)")
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        file = discord.File(buf, filename="commands_over_time.png")
        embed.set_image(url="attachment://commands_over_time.png")

                    
    if file:
        await interaction.response.send_message(embed=embed, file=file)
    else:
        await interaction.response.send_message(embed=embed)


data_file = 'reaction_roles.json'
if not os.path.exists(data_file):
    with open(data_file, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(data_file, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(data_file, 'w') as f:
        json.dump(data, f, indent=4)

class ReactionRoleDropdown(discord.ui.Select):
    def __init__(self, roles, custom_id):
        options = [discord.SelectOption(label=role['name'], emoji=role.get('emoji')) for role in roles]
        super().__init__(
            placeholder="Choose your roles...",
            min_values=0,
            max_values=len(options),
            options=options,
            custom_id=custom_id                               
        )
        self.role_ids = [role['id'] for role in roles]
        self.role_map = {role['name']: role['id'] for role in roles}

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        if not self.values:
            data = load_data()
            gid = str(interaction.guild_id)
            user_roles = [role.id for role in user.roles]
            matching_by_template = []

            for template in data.get(gid, {}).values():
                matching_roles = [r['name'] for r in template['roles'] if int(r['id']) in user_roles]
                if matching_roles:
                    color = int(template.get("color", "#000000").replace("#", ""), 16)
                    matching_by_template.append((matching_roles, color))

            if not matching_by_template:
                await interaction.response.send_message("You don't have any roles from the reaction role system.", ephemeral=True)
                return

            embeds = []
            current_embed = discord.Embed(title="Your Roles from Reaction Role", description="", color=discord.Color.blue())
            field_count = 0
            current_color = None

            for role_list, color in matching_by_template:
                for role_name in role_list:
                    if len(current_embed.description) + len(role_name) + 1 > 4000 or field_count >= 25:
                        embeds.append(current_embed)
                        current_embed = discord.Embed(title="Your Roles from Reaction Role (continued)", description="", color=color)
                        field_count = 0

                    if current_color is None:
                        current_embed.color = color
                        current_color = color

                    current_embed.description += f"{role_name}\n"
                    field_count += 1

            embeds.append(current_embed)
            await interaction.response.send_message(embeds=embeds, ephemeral=True)
            return

        selected_ids = [self.role_map[opt.label] for opt in self.options if opt.label in self.values]
        selected_ids_int = [int(rid) for rid in selected_ids]
        all_role_ids = [int(rid) for rid in self.role_ids]

        added_roles = []
        removed_roles = []

        new_roles = [role for role in user.roles if role.id not in all_role_ids]

        for rid in selected_ids_int:
            role = guild.get_role(rid)
            if role in user.roles:
                new_roles = [r for r in new_roles if r.id != role.id]
                removed_roles.append(role)
            else:
                new_roles.append(role)
                added_roles.append(role)

        try:
            await user.edit(roles=new_roles)
        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to modify your roles.", ephemeral=True)
            return

        log_message = "✅ **Roles Updated**\n"
        if added_roles:
            log_message += "**Added:** " + ", ".join([r.name for r in added_roles]) + "\n"
        if removed_roles:
            log_message += "**Removed:** " + ", ".join([r.name for r in removed_roles]) + "\n"
        if not added_roles and not removed_roles:
            log_message += "No changes made."

        await interaction.response.send_message(log_message, ephemeral=True)

        for option in self.options:
            option.default = False




@client.tree.command(name="reactionrolesetup", description="Add or remove a reaction role template.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(name="Name of the template", action="Choose whether to add or remove the template")
async def reactionrolesetup(
    interaction: discord.Interaction,
    name: str,
    action: Literal["Add", "Remove"]                                     
):

    data = load_data()
    gid = str(interaction.guild_id)
    if gid not in data:
        data[gid] = {}
    templates = data[gid]

    if action == "Add":
        if name in templates:
            await interaction.response.send_message("Template already exists.", ephemeral=True)
            return
        if len(templates) >= 3:
            is_active, is_premium, expires_at = user_is_active(interaction.guild.owner_id)
            if not is_premium:
              await interaction.response.send_message(embed=discord.Embed(title="You are being restricted", description="The owner of this guild is not a premium user. \nPremium users can add unlimited reaction role templates!\nUse </help:1242738769099231302> to check out our premium perks.", color=0xffffff), view=BuyPremium())
              return
        templates[name] = {"description": "Choose your role!", "color": "#ffffff", "roles": []}
        save_data(data)
        await interaction.response.send_message(f"Template `{name}` added.", ephemeral=True)

    elif action == "Remove":
        if name not in templates:
            await interaction.response.send_message("Template not found.", ephemeral=True)
            return

        view = discord.ui.View(timeout=30)

        async def confirm_callback(i):
            if i.user != interaction.user:
                await i.response.send_message("Only the command user can confirm.", ephemeral=True)
                return
            del data[gid][name]
            save_data(data)
            await i.response.edit_message(content=f"Template `{name}` removed.", view=None)

        button = discord.ui.Button(label="Confirm Delete", style=discord.ButtonStyle.danger)
        button.callback = confirm_callback
        view.add_item(button)
        await interaction.response.send_message(f"Are you sure you want to delete `{name}`?", view=view, ephemeral=True)

@client.tree.command(name="reactionroleedit", description="Add or remove roles from a template.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(name="Template name", role="Role to add or remove", action="Add or Remove", emoji="Optional default emoji")
async def reactionroleedit(
    interaction: discord.Interaction,
    name: str,
    role: discord.Role,
    action: Literal["Add", "Remove"],
    emoji: str = None
):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You lack permission to manage roles.", ephemeral=True)
        return

    data = load_data()
    gid = str(interaction.guild_id)
    templates = data.get(gid, {})

    if name not in templates:
        await interaction.response.send_message("Template not found.", ephemeral=True)
        return

    roles = templates[name]['roles']
    if action == "Add":
        if any(r['id'] == str(role.id) for r in roles):
            await interaction.response.send_message("Role already in template.", ephemeral=True)
            return
        roles.append({"id": str(role.id), "name": role.name, "emoji": emoji})
    elif action == "Remove":
        roles = [r for r in roles if r['id'] != str(role.id)]
        templates[name]['roles'] = roles

    save_data(data)
    await interaction.response.send_message(f"Role `{role.name}` {action.lower()}ed in template `{name}`.", ephemeral=True)


@client.tree.command(name="reactionroleembed", description="View or edit embed of a reaction role template.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(name="Template name", title="New embed title", color="New embed color in HEX")
async def reactionroleembed(
    interaction: discord.Interaction,
    name: str = None,
    title: str = None,
    color: str = None
):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You lack permission to manage roles.", ephemeral=True)
        return

    data = load_data()
    gid = str(interaction.guild_id)
    templates = data.get(gid, {})

    if not name:
        if not templates:
            await interaction.response.send_message("No templates available.", ephemeral=True)
            return
        await interaction.response.send_message("Templates: " + ", ".join(templates.keys()), ephemeral=True)
        return

    if name not in templates:
        await interaction.response.send_message("Template not found.", ephemeral=True)
        return

    if title:
        templates[name]['description'] = title
    if color:
        templates[name]['color'] = color if color.startswith("#") else f"#{color}"
    save_data(data)

    if not title and not color:
        info = templates[name]
        embed_color = int(info.get("color", "#000000").replace("#", ""), 16)
        embed = discord.Embed(title=f"Reaction Role Template: {name}", color=embed_color)
        embed.add_field(name="Title", value=info.get("description", "None"), inline=False)
        embed.add_field(name="Color", value=info.get("color", "#000000"), inline=False)

        roles_text = ""
        for r in info['roles']:
            emoji = f"{r['emoji']} " if r.get('emoji') else ""
            roles_text += f"{emoji}`{r['name']}` (`{r['id']}`)\n"

        embed.add_field(name="Roles", value=roles_text if roles_text else "None", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        await interaction.response.send_message(f"Updated template `{name}`.", ephemeral=True)


@client.tree.command(name="reactionroledeploy", description="Deploy a reaction role template to a channel.")
@app_commands.checks.has_permissions(manage_roles=True)
@app_commands.describe(name="Template name", channel="Optional channel to send to")
async def reactionroledeploy(
    interaction: discord.Interaction,
    name: str,
    channel: discord.TextChannel = None
):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("You lack permission to manage roles.", ephemeral=True)
        return

    data = load_data()
    gid = str(interaction.guild_id)
    templates = data.get(gid, {})

    if name not in templates:
        await interaction.response.send_message("Template not found.", ephemeral=True)
        return

    info = templates[name]
    embed = discord.Embed(title=info['description'], color=int(info['color'].replace("#", ""), 16))
    custom_id = f"reaction_role_dropdown:{name}"
    view = ReactionRoleView(info['roles'], custom_id)
    target_channel = channel or interaction.channel

    await target_channel.send(embed=embed, view=view)
    await interaction.response.send_message("Reaction role deployed.", ephemeral=True)

@reactionroleedit.autocomplete('name')
@reactionroleembed.autocomplete('name')
@reactionroledeploy.autocomplete('name')
async def template_name_autocomplete(interaction: discord.Interaction, current: str):
    data = load_data()
    gid = str(interaction.guild_id)
    templates = data.get(gid, {})

    return [
        app_commands.Choice(name=key, value=key)
        for key in templates.keys()
        if current.lower() in key.lower()
    ][:25]                  



def load_audit_config():
    if not os.path.exists("audit_config.json"):
        return {}
    with open("audit_config.json", "r") as f:
        return json.load(f)

def save_audit_config(data):
    with open("audit_config.json", "w") as f:
        json.dump(data, f, indent=4)

def append_audit_log(guild_id: int, entry: str):
    os.makedirs("audit_logs", exist_ok=True)
    with open(f"audit_logs/{guild_id}.txt", "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def read_audit_log(guild_id: int):
    path = f"audit_logs/{guild_id}.txt"
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()

@client.tree.command(name="auditlogsetup", description="Enable or disable audit logging.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(state="Turn audit logging on or off")
async def auditlogsetup(interaction: discord.Interaction, state: Literal["on", "off"]):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need admin permissions.", ephemeral=True)
        return

    config = load_audit_config()
    gid = str(interaction.guild_id)

    if gid not in config:
        config[gid] = {}

    config[gid]["enabled"] = state == "on"
    save_audit_config(config)

    await interaction.response.send_message(f"Audit logging has been turned **{state}**.", ephemeral=True)

@client.tree.command(name="auditlogchannel", description="Set a channel to receive audit log entries.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(channel="Channel to send audit logs to")
async def auditlogchannel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You need admin permissions.", ephemeral=True)
        return

    config = load_audit_config()
    gid = str(interaction.guild_id)

    if gid not in config:
        config[gid] = {}

    config[gid]["channel"] = channel.id
    save_audit_config(config)

    await interaction.response.send_message(f"Audit log channel set to {channel.mention}.", ephemeral=True)

@client.tree.command(name="auditlogdownload", description="Download server audit logs for the past X days.")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(duration="Number of days (1-7)")
async def auditlogdownload(interaction: discord.Interaction, duration: app_commands.Range[int, 1, 7]):
    config = load_audit_config()
    gid = str(interaction.guild_id)

    if not config.get(gid, {}).get("enabled", False):
        await interaction.response.send_message("Audit logging is currently **off**.", ephemeral=True)
        return

    now = datetime.now(timezone.utc)

    cutoff = now - timedelta(days=duration)

    logs = read_audit_log(interaction.guild_id)
    filtered = [line for line in logs if line.strip() and datetime.fromisoformat(line.split(" | ")[0]).replace(tzinfo=timezone.utc) >= cutoff]

    if not filtered:
        await interaction.response.send_message("No logs found in that duration.", ephemeral=True)
        return

    path = f"audit_logs/{interaction.guild_id}.txt"
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(filtered)

    await interaction.response.send_message("Here are the logs:", ephemeral=True)
    await interaction.followup.send(file=discord.File(path), ephemeral=True)


CONFIG_PATH   = "guild_config.json"                          
ACTIONS_PATH  = "scam_actions.json"                              
FEEDBACK_PATH = "scam_feedback.jsonl"                                 

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

                                                         
class ScamFeedbackView(discord.ui.View):
    def __init__(self, action_id: str):
        super().__init__(timeout=None)              
        self.action_id = action_id

    @discord.ui.button(label="Mark as Scam", style=discord.ButtonStyle.success, custom_id="scamfb:tp")
    async def mark_scam(self, interaction: discord.Interaction, button: discord.ui.Button):
        actions = load_actions(); payload = actions.get(self.action_id)
        if not payload: return await interaction.response.send_message("Action not found or expired.", ephemeral=True)
        append_feedback({
            "ts": int(time.time()), "label": "true_positive",
            "guild_id": payload["guild_id"], "moderator_id": interaction.user.id,
            "message_author_id": payload["author_id"], "reasons": payload["reasons"],
            "content": payload["content"], "domains": payload.get("domains", []),
        })
        await interaction.response.send_message(embed=embed_basic("Logged: Marked as Scam ✅", "Thanks!"), ephemeral=True)

    @discord.ui.button(label="Not a Scam", style=discord.ButtonStyle.danger, custom_id="scamfb:fp")
    async def mark_not_scam(self, interaction: discord.Interaction, button: discord.ui.Button):
        actions = load_actions(); payload = actions.get(self.action_id)
        if not payload: return await interaction.response.send_message("Action not found or expired.", ephemeral=True)
        cfg = get_guild_cfg(payload["guild_id"]); updated = False
        domains = payload.get("domains", []) or []; content = payload.get("content", "") or ""
        if cfg.get("auto_whitelist_on_false_positive", True) and domains:
            wl = set(cfg.get("domain_allowlist") or [])
            for d in domains:
                if not d.startswith("xn--"): wl.add(d.lower())
            update_guild_cfg(payload["guild_id"], domain_allowlist=sorted(wl)); updated = True
        if not domains:
            norm = normalize_phrase(content)
            phrases = set(cfg.get("phrase_allowlist") or [])
            if norm and norm not in phrases:
                phrases.add(norm)
                update_guild_cfg(payload["guild_id"], phrase_allowlist=sorted(phrases))
                updated = True

                                                                  
            audit = get_guild_cfg(payload["guild_id"]).get("phrase_audit") or {}
            lst = list(audit.get(norm) or [])
            lst.append({"by": interaction.user.id, "ts": int(time.time())})
            audit[norm] = lst
            update_guild_cfg(payload["guild_id"], phrase_audit=audit)
        append_feedback({
            "ts": int(time.time()), "label": "false_positive",
            "guild_id": payload["guild_id"], "moderator_id": interaction.user.id,
            "message_author_id": payload["author_id"], "reasons": payload["reasons"],
            "content": content, "domains": domains,
        })
        await interaction.response.send_message(embed=embed_basic("Logged: Not a Scam ❎", "Updated allowlist & recorded feedback." if updated else "Recorded feedback." , COLOR_WARN), ephemeral=True)


                          
@client.tree.command(name="scam_enable", description="Enable Anti-Scam in this channel (log channel required)")
async def scam_enable(interaction: discord.Interaction):
    if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
    cfg = get_guild_cfg(interaction.guild_id)
    if not cfg.get("log_channel_id"): return await interaction.response.send_message("Set a **log channel** first with `/set_log_channel`.", ephemeral=True)
    chans = set(cfg.get("scam_channels") or []); chans.add(interaction.channel_id)
    update_guild_cfg(interaction.guild_id, scam_channels=sorted(chans))
    await interaction.response.send_message(embed=embed_basic("Scam Shield Enabled", f"Active in {interaction.channel.mention}", COLOR_OK), ephemeral=True)

@client.tree.command(name="scam_disable", description="Disable Anti-Scam in this channel")
async def scam_disable(interaction: discord.Interaction):
    if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
    cfg = get_guild_cfg(interaction.guild_id)
    chans = set(cfg.get("scam_channels") or []); chans.discard(interaction.channel_id)
    update_guild_cfg(interaction.guild_id, scam_channels=sorted(chans))
    await interaction.response.send_message(embed=embed_basic("Scam Shield Disabled", f"Disabled in {interaction.channel.mention}", COLOR_WARN), ephemeral=True)

@client.tree.command(name="codehelper_enable", description="Enable Inline Code Helper in this channel")
async def codehelper_enable(interaction: discord.Interaction):
    if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
    cfg = get_guild_cfg(interaction.guild_id)
    chans = set(cfg.get("codehelper_channels") or []); chans.add(interaction.channel_id)
    update_guild_cfg(interaction.guild_id, codehelper_channels=sorted(chans))
    await interaction.response.send_message(embed=embed_basic("Code Helper Enabled", f"Active in {interaction.channel.mention}", COLOR_OK), ephemeral=True)

@client.tree.command(name="codehelper_disable", description="Disable Inline Code Helper in this channel")
async def codehelper_disable(interaction: discord.Interaction):
    if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
    cfg = get_guild_cfg(interaction.guild_id)
    chans = set(cfg.get("codehelper_channels") or []); chans.discard(interaction.channel_id)
    update_guild_cfg(interaction.guild_id, codehelper_channels=sorted(chans))
    await interaction.response.send_message(embed=embed_basic("Code Helper Disabled", f"Disabled in {interaction.channel.mention}", COLOR_WARN), ephemeral=True)

@client.tree.command(name="status", description="Show current security & code-helper configuration for this server")
async def status(interaction: discord.Interaction):
    cfg = get_guild_cfg(interaction.guild_id)
    lines = [
        f"• Scam channels: {', '.join(f'<#{c}>' for c in (cfg.get('scam_channels') or [])) or 'None'}",
        f"• Code-helper channels: {', '.join(f'<#{c}>' for c in (cfg.get('codehelper_channels') or [])) or 'None'}",
        f"• Limited role: {f'<@&{cfg.get('limited_role_id')}>' if cfg.get('limited_role_id') else 'Not set'}",
        f"• Surge threshold: {cfg.get('surge_threshold_per_minute')}/minute",
        f"• Log channel: {f'<#{cfg.get('log_channel_id')}>' if cfg.get('log_channel_id') else '❌ NOT SET'}",
        f"• Domain allowlist: {', '.join(cfg.get('domain_allowlist') or []) or '—'}",
    ]
    await interaction.response.send_message(embed=embed_basic("Server Status", "\n".join(lines), COLOR_INFO), ephemeral=True)

@client.tree.command(name="set_log_channel", description="Set a channel for scam logs (mandatory for Scam Shield)")
@app_commands.describe(channel="Select a channel to receive scam logs")
async def set_log_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
    update_guild_cfg(interaction.guild_id, log_channel_id=channel.id)
    await interaction.response.send_message(embed=embed_basic("Log Channel Set", f"Logs → {channel.mention}", COLOR_OK), ephemeral=True)

                                     
@client.tree.command(name="allowlist_phrase_add", description="Allow this exact phrase (no links required)")
@app_commands.describe(phrase="Exact phrase to allow (it will be normalized)")
async def allowlist_phrase_add(interaction: discord.Interaction, phrase: str):
    if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
    cfg = get_guild_cfg(interaction.guild_id); phrases = set(cfg.get("phrase_allowlist") or [])
    phrases.add(normalize_phrase(phrase)); update_guild_cfg(interaction.guild_id, phrase_allowlist=sorted(phrases))
    await interaction.response.send_message(embed=embed_basic("Phrase allowlisted", f"“{phrase}”", COLOR_OK), ephemeral=True)

@client.tree.command(name="allowlist_phrase_remove", description="Remove a phrase from the allowlist")
@app_commands.describe(phrase="Exact phrase to remove (normalized)")
async def allowlist_phrase_remove(interaction: discord.Interaction, phrase: str):
    if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
    cfg = get_guild_cfg(interaction.guild_id); phrases = set(cfg.get("phrase_allowlist") or [])
    norm = normalize_phrase(phrase)
    if norm in phrases: phrases.remove(norm); update_guild_cfg(interaction.guild_id, phrase_allowlist=sorted(phrases))
    await interaction.response.send_message(embed=embed_basic("Phrase removed", f"“{phrase}”", COLOR_OK), ephemeral=True)

@client.tree.command(name="allowlist_phrase_list", description="List allowlisted phrases")
async def allowlist_phrase_list(interaction: discord.Interaction):
    cfg = get_guild_cfg(interaction.guild_id); phrases = cfg.get("phrase_allowlist") or []
    text = "\n".join(f"• {p}" for p in phrases) or "No phrases."
    await interaction.response.send_message(embed=embed_basic("Phrase Allowlist", text, COLOR_INFO), ephemeral=True)

                     
@client.tree.command(name="scan_test", description="Test the scam scanner against custom text")
@app_commands.describe(text="The text to scan (paste your message here)")
async def scan_test(interaction: discord.Interaction, text: str):
    cfg = get_guild_cfg(interaction.guild_id)
    domains = extract_domains(text); reasons = scan_message_for_scams(text, cfg)
    e = embed_basic("Scan Test", "", COLOR_INFO)
    e.add_field(name="Domains parsed", value=", ".join(domains) or "—", inline=False)
    e.add_field(name="Reasons", value="\n".join(f"• {r}" for r in reasons) or "—", inline=False)
    await interaction.response.send_message(embed=e, ephemeral=True)

@client.tree.command(name="lint", description="Check Python code for syntax errors (paste code here)")
@app_commands.describe(code="Your Python code (paste up to ~1800 chars)")
async def lint(interaction: discord.Interaction, code: str):
    ok, detail = try_python_syntax_check(code)
    e = embed_basic("Python Syntax Check" if ok else "Python Syntax Error", ("✅ " if ok else "❌ ") + detail, COLOR_OK if ok else COLOR_BAD)
    e.add_field(name="Excerpt", value=f"```py\n{code[:800]}\n```", inline=False)
    await interaction.response.send_message(embed=e, ephemeral=True)

@client.tree.command(name="debug_safety", description="Diagnose readiness & config")
async def debug_safety(interaction: discord.Interaction):
    cfg = get_guild_cfg(interaction.guild_id)
    has_mc = getattr(client.intents, "message_content", False)
    has_mem = getattr(client.intents, "members", False)
    lines = [
        f"• message_content intent: **{'Yes' if has_mc else 'No'}**",
        f"• members intent: **{'Yes' if has_mem else 'No'}**",
        f"• Scam channels: {', '.join(f'<#{c}>' for c in (cfg.get('scam_channels') or [])) or 'None'}",
        f"• Code-helper channels: {', '.join(f'<#{c}>' for c in (cfg.get('codehelper_channels') or [])) or 'None'}",
        f"• Log channel set: **{'Yes' if cfg.get('log_channel_id') else 'No'}**",
    ]
    await interaction.response.send_message(embed=embed_basic("Debug", "\n".join(lines), COLOR_INFO), ephemeral=True)

@client.tree.command(name="whitelisted_phrase",
                     description="List, inspect, add, or remove whitelisted phrases (logged via 'Not a Scam'). Admin only.")
@app_commands.describe(
    phrase="Optional phrase to inspect/add/remove (normalization applied)",
    action="Optional: add or remove the phrase"
)
async def whitelisted_phrase(
    interaction: discord.Interaction,
    phrase: Optional[str] = None,
    action: Optional[Literal["add","remove"]] = None
):
           
    if not admin_or_manage_guild(interaction):
        return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)

    cfg = get_guild_cfg(interaction.guild_id)
    phrases = set(cfg.get("phrase_allowlist") or [])
    audit: dict = cfg.get("phrase_audit") or {}

                                                      
    def render_all():
        if not phrases and not audit:
            return "No phrases recorded."
        lines = []
                                                            
        all_norms = set(phrases) | set(audit.keys())
        for p in sorted(all_norms):
            count = len(audit.get(p, []))
            badge = "✅" if p in phrases else "—"
            lines.append(f"• {p}  | allowlisted: {badge} | logs: {count}")
        return "\n".join(lines)[:3900] or "No phrases recorded."

                                        
    if phrase is None and action is None:
        e = embed_basic("Whitelisted Phrases (All)", render_all(), COLOR_INFO)
        return await interaction.response.send_message(embed=e, ephemeral=True)

                          
    norm = normalize_phrase(phrase or "")

                                                                 
    if phrase is not None and action is None:
        logs = audit.get(norm, [])
        allowlisted = norm in phrases
        if not logs and not allowlisted:
            e = embed_basic("Phrase Info", f"“{norm}” — no logs found and not in allowlist.", COLOR_WARN)
            return await interaction.response.send_message(embed=e, ephemeral=True)

        lines = [f"**Phrase:** {norm}",
                 f"**Allowlisted:** {'Yes ✅' if allowlisted else 'No —'}",
                 f"**Times logged via Not a Scam:** {len(logs)}"]
        if logs:
                                          
            logs_sorted = sorted(logs, key=lambda x: x.get("ts", 0), reverse=True)[:10]
            bul = []
            for rec in logs_sorted:
                by = rec.get("by")
                ts = rec.get("ts", 0)
                bul.append(f"• by <@{by}> at <t:{ts}:F> (<t:{ts}:R>)")
            if len(logs) > 10:
                bul.append(f"...and **{len(logs)-10}** more")
            lines.append("**Loggers:**\n" + "\n".join(bul))

        e = embed_basic("Phrase Info", "\n".join(lines), COLOR_INFO)
        return await interaction.response.send_message(embed=e, ephemeral=True)

                                        
    if action in ("add", "remove") and phrase is not None:
        note = ""
        if action == "add":
            if norm not in phrases:
                phrases.add(norm)
                note = f"Added “{norm}” to allowlist."
            else:
                note = f"“{norm}” is already allowlisted."
                                                         
            lst = list(audit.get(norm) or [])
            lst.append({"by": interaction.user.id, "ts": int(time.time())})
            audit[norm] = lst
            update_guild_cfg(interaction.guild_id, phrase_audit=audit)

        elif action == "remove":
            if norm in phrases:
                phrases.remove(norm)
                note = f"Removed “{norm}” from allowlist."
            else:
                note = f"“{norm}” is not in allowlist."

        update_guild_cfg(interaction.guild_id, phrase_allowlist=sorted(phrases))
        e = embed_basic("Whitelisted Phrase Updated", note, COLOR_OK if action == "add" else COLOR_WARN)
                            
        e.add_field(name="Now allowlisted", value=", ".join(sorted(phrases))[:1000] or "—", inline=False)
        return await interaction.response.send_message(embed=e, ephemeral=True)

                                                             
    e = embed_basic("Whitelisted Phrases (All)", render_all(), COLOR_INFO)
    return await interaction.response.send_message(embed=e, ephemeral=True)

@client.tree.command(name="scam_whitelist", description="Add/remove users or roles from the scam shield whitelist, or list all")
@app_commands.describe(
    user="Optional user to add/remove from the whitelist",
    role="Optional role to add/remove from the whitelist",
    action="Choose add or remove (optional)"
)
async def scam_whitelist(
    interaction: discord.Interaction,
    user: Optional[discord.User] = None,
    role: Optional[discord.Role] = None,
    action: Optional[Literal["add","remove"]] = None
):
           
    if not admin_or_manage_guild(interaction):
        return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)

    cfg = get_guild_cfg(interaction.guild_id)

                             
    def render_db(c):
        users = [f"<@{uid}>" for uid in (c.get("scam_user_whitelist") or [])]
        roles = [f"<@&{rid}>" for rid in (c.get("scam_role_whitelist") or [])]
        lines = [
            f"**Users**: {', '.join(users) if users else '—'}",
            f"**Roles**: {', '.join(roles) if roles else '—'}",
        ]
        return "\n".join(lines)

                                                 
    if user is None and role is None:
        e = embed_basic("Scam whitelist", render_db(cfg), COLOR_INFO)
        return await interaction.response.send_message(embed=e, ephemeral=True)

                                                                        
    if action is None:
        e = embed_basic("Scam whitelist (no action specified)", render_db(cfg), COLOR_INFO)
        return await interaction.response.send_message(embed=e, ephemeral=True)

                        
    users = set(cfg.get("scam_user_whitelist") or [])
    roles = set(cfg.get("scam_role_whitelist") or [])
    changed = False
    notes = []

    if user is not None:
        if action == "add":
            if user.id not in users:
                users.add(user.id); changed = True
            notes.append(f"User {'added' if changed else 'already present'}: <@{user.id}>")
        elif action == "remove":
            if user.id in users:
                users.remove(user.id); changed = True
            notes.append(f"User {'removed' if changed else 'not present'}: <@{user.id}>")

    if role is not None:
        if action == "add":
            if role.id not in roles:
                roles.add(role.id); changed = True
            notes.append(f"Role {'added' if changed else 'already present'}: <@&{role.id}>")
        elif action == "remove":
            if role.id in roles:
                roles.remove(role.id); changed = True
            notes.append(f"Role {'removed' if changed else 'not present'}: <@&{role.id}>")

    if changed:
        update_guild_cfg(interaction.guild_id,
                         scam_user_whitelist=sorted(users),
                         scam_role_whitelist=sorted(roles))

                              
    e = embed_basic(
        f"Scam whitelist: {action}",
        "\n".join(notes) + "\n\n**Current database**\n" + render_db(get_guild_cfg(interaction.guild_id)),
        COLOR_OK if action == "add" else COLOR_WARN
    )
    await interaction.response.send_message(embed=e, ephemeral=True)

                                                                     
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

class YoungestView(discord.ui.View):
    def __init__(self, duration: str, youngest_tuple, pages):
        super().__init__(timeout=180)
        self.duration = duration
        self.youngest_tuple = youngest_tuple                                 
        self.pages = pages                                      
        self.i = 0

    def _build_embed(self):
        title = f"Youngest Accounts (younger than {self.duration})"
        e = embed_basic(title, color=COLOR_INFO)

                                              
        if self.youngest_tuple:
            ym, ydt = self.youngest_tuple
            abs_t, rel_t = fmt_discord_time(ydt)
            e.add_field(
                name="Youngest account in server",
                value=f"• User: {ym.mention} (`{ym.id}`)\n• Created: {abs_t} ({rel_t})",
                inline=False
            )

                                                                    
        page = self.pages[self.i]
        val = "\n".join(page) or "None found."
        if len(val) > 1024:
            val = val[:1021] + "..."
        e.add_field(
            name=f"Accounts younger than {self.duration} — Page {self.i+1}/{len(self.pages)}",
            value=val,
            inline=False
        )
        return e

    async def _refresh(self, interaction: discord.Interaction):
                                 
        self.prev_button.disabled = (self.i == 0)
        self.next_button.disabled = (self.i >= len(self.pages)-1)
        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i > 0:
            self.i -= 1
        await self._refresh(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i < len(self.pages) - 1:
            self.i += 1
        await self._refresh(interaction)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

@client.tree.command(
    name="youngest",
    description="Show the youngest account and list all accounts younger than a duration (e.g., 1m, 1y, 1d, 30min)"
)
@app_commands.describe(duration="Single-unit duration: 1y (year), 1m (month≈30d), 1d (day), 30min (minutes)")
async def youngest(interaction: discord.Interaction, duration: str):
                       
    secs = parse_duration_to_timedelta(duration)
    if secs is None:
        return await interaction.response.send_message(
            "Invalid duration. Use exactly one unit like `1y`, `1m`, `1d`, or `30min`.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    now = discord.utils.utcnow()
    cutoff = now.timestamp() - secs

                                           
    try:
        await interaction.guild.chunk()
    except Exception:
        pass

    members = [m for m in interaction.guild.members if not m.bot]

                                                               
    under: list[tuple[discord.Member, datetime]] = []
    youngest_tuple: tuple[discord.Member, datetime] | None = None

    for m in members:
        if not m.created_at:
            continue
        created_ts = m.created_at.replace(tzinfo=timezone.utc).timestamp()
        if youngest_tuple is None or created_ts > youngest_tuple[1].replace(tzinfo=timezone.utc).timestamp():
            youngest_tuple = (m, m.created_at)
        if created_ts >= cutoff:
            under.append((m, m.created_at))

                         
    under.sort(key=lambda t: t[1], reverse=True)

                                                
    lines = []
    for m, dt in under:
        abs_t, rel_t = fmt_discord_time(dt)
        lines.append(f"• {m.mention} (`{m.id}`) — {abs_t} ({rel_t})")

                                  
    pages = _chunk_lines(lines, size=10)

    view = YoungestView(duration, youngest_tuple, pages)
    await interaction.followup.send(embed=view._build_embed(), view=view, ephemeral=True)




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

class MemberStatsView(discord.ui.View):
    def __init__(self, guild: discord.Guild, members: list[discord.Member]):
        super().__init__(timeout=300)
        self.guild = guild
        self.members = members
        self.tab = "overview"                            
        self.page = 0
        self.total_pages = 1

    async def refresh(self, interaction: discord.Interaction):
        if self.tab == "overview":
            e = build_overview_embed(self.guild, self.members)
            self.total_pages = 1
            self.page = 0
            await interaction.response.edit_message(embed=e, view=self)
        elif self.tab == "roles":
            e, total = build_top_roles_embed(self.guild, self.members, self.page)
            self.total_pages = total
            await interaction.response.edit_message(embed=e, view=self)
        elif self.tab == "graph":
            img = build_age_graph(self.members)
            file = discord.File(img, filename="age_distribution.png")
            e = embed_basic("Server Member Stats — Age Graph", "Account age distribution", COLOR_INFO)
            e.set_image(url="attachment://age_distribution.png")
            self.total_pages = 1
            self.page = 0
            await interaction.response.edit_message(embed=e, attachments=[file], view=self)

                                   
    @discord.ui.button(label="Overview", style=discord.ButtonStyle.primary)
    async def tab_overview(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab = "overview"; self.page = 0
        await self.refresh(interaction)

    @discord.ui.button(label="Top Roles", style=discord.ButtonStyle.secondary)
    async def tab_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab = "roles"; self.page = 0
        await self.refresh(interaction)

    @discord.ui.button(label="Age Graph", style=discord.ButtonStyle.secondary)
    async def tab_graph(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab = "graph"; self.page = 0
        await self.refresh(interaction)

                                                              
    @discord.ui.button(label="Prev", style=discord.ButtonStyle.success)
    async def pager_prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.tab != "roles":
            return await interaction.response.defer()
        if self.page > 0:
            self.page -= 1
        await self.refresh(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.success)
    async def pager_next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.tab != "roles":
            return await interaction.response.defer()
        if self.page < self.total_pages - 1:
            self.page += 1
        await self.refresh(interaction)




@client.tree.command(
    name="server_member_stats",
    description="Advanced member analytics: overview, top roles, and age graph."
)
async def server_member_stats(interaction: discord.Interaction):
                                 
    if not admin_or_manage_guild(interaction):
        return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)

    guild = interaction.guild
    await interaction.response.defer()                                 

                                                       
    try:
        await guild.chunk()
    except Exception:
        pass

    members = list(guild.members)

                                               
    view = MemberStatsView(guild, members)
    embed = build_overview_embed(guild, members)
    await interaction.followup.send(embed=embed, view=view)

@client.event
async def on_audit_log_entry_create(entry: discord.AuditLogEntry):
    guild = entry.guild
    config = load_audit_config()
    gid = str(guild.id)

    if not config.get(gid, {}).get("enabled", False):
        return

    user = entry.user
    target = entry.target
    reason = entry.reason or "No reason provided"
    action = entry.action.name
    timestamp = datetime.now(timezone.utc)

                           
    if isinstance(target, discord.User):
        target_display = f"{target.name}#{target.discriminator}"
    elif isinstance(target, discord.TextChannel):
        target_display = f"#{target.name}"
    elif isinstance(target, discord.Member):
        target_display = str(target)
    elif hasattr(target, 'name'):
        target_display = str(target.name)
    else:
        target_display = f"Object ID: {getattr(target, 'id', 'N/A')}"

    summary_title = f"{user.name} {action.replace('_', ' ')} {target_display}"

                  
    log_entry = f"{timestamp.isoformat()} | Action: {action} | By: {user} {user.id} | On: {target_display} | Reason: {reason}"
    append_audit_log(guild.id, log_entry)

                
    channel_id = config[gid].get("channel")
    if channel_id:
        channel = guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title="Audit Log Entry",
                color=0xffffff,
                timestamp=timestamp
            )
            embed.set_author(name=user.name, icon_url=user.display_avatar.url)
            embed.add_field(name="Action", value=action.replace("_", " ").title(), inline=False)
            embed.add_field(name="Executor", value=f"{user} ({user.id})", inline=False)
            embed.add_field(name="Target", value=f"{target_display} ({getattr(target, 'id', 'N/A')})", inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Time", value=format_dt(timestamp, style='F'), inline=False)

                                                                    
            if entry.action.name == "message_delete":
                if isinstance(target, discord.Message):
                    embed.add_field(name="Deleted In", value=f"<#{target.channel.id}>", inline=False)
                elif hasattr(entry.extra, "channel"):
                    embed.add_field(name="Deleted In", value=f"<#{entry.extra.channel.id}>", inline=False)

            await channel.send(embed=embed)




PRIVACY_FILE = "presence_privacy.json"

                                                    

def load_privacy() -> set[int]:
    if not os.path.exists(PRIVACY_FILE):
        return set()
    try:
        with open(PRIVACY_FILE, "r", encoding="utf-8") as f:
            return {int(x) for x in json.load(f)}
    except:
        return set()

def save_privacy(data: set[int]):
    with open(PRIVACY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f)

PRIVACY_SET = load_privacy()


                                                  

class PresencePaginator(discord.ui.View):
    def __init__(self, pages, author_id):
        super().__init__(timeout=60)
        self.pages = pages
        self.index = 0
        self.author_id = author_id

        if len(self.pages) <= 1:
            self.next_page.disabled = True
            self.prev_page.disabled = True

    async def update(self, interaction: discord.Interaction):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(
                "You cannot control this pagination.", ephemeral=True
            )

        await interaction.response.edit_message(
            embed=self.pages[self.index], view=self
        )

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def prev_page(self, interaction, button):
        if self.index > 0:
            self.index -= 1
        await self.update(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction, button):
        if self.index < len(self.pages) - 1:
            self.index += 1
        await self.update(interaction)


                                                             

@client.tree.command(name="presence_privacy", description="Opt in/out of presence tracking globally.")
@app_commands.describe(turn_off="Yes = opt-out | No = opt-in")
@app_commands.choices(turn_off=[
    app_commands.Choice(name="Yes (Turn off tracking)", value="yes"),
    app_commands.Choice(name="No (Allow tracking)", value="no")
])
async def presence_privacy(interaction: discord.Interaction, turn_off: app_commands.Choice[str]):

    uid = interaction.user.id

    if turn_off.value == "yes":
        PRIVACY_SET.add(uid)
        save_privacy(PRIVACY_SET)
        msg = "🔒 You have **opted OUT** of presence tracking."
    else:
        PRIVACY_SET.discard(uid)
        save_privacy(PRIVACY_SET)
        msg = "🔓 You have **opted IN** to presence tracking."

    await interaction.response.send_message(msg, ephemeral=True)


                                                                   

@client.tree.command(name="server_member_activity", description="View members by presence status or stats.")
@app_commands.choices(status=[
    app_commands.Choice(name="Online", value="online"),
    app_commands.Choice(name="Do Not Disturb", value="dnd"),
    app_commands.Choice(name="Idle", value="idle"),
    app_commands.Choice(name="Invisible/Offline", value="invisible"),
    app_commands.Choice(name="Stats", value="stats"),
])
async def server_member_activity(interaction: discord.Interaction, status: app_commands.Choice[str]):
    guild = interaction.guild
    if not guild:
        return await interaction.response.send_message("Command must be used in a server.", ephemeral=True)

                                         
    tracked = [m for m in guild.members if not m.bot and m.id not in PRIVACY_SET]

                                                              
    if status.value == "stats":

        total_members = guild.member_count
        total_bots = sum(1 for m in guild.members if m.bot)
        total_tracked = len(tracked)

        online = sum(1 for m in tracked if m.status == discord.Status.online)
        dnd = sum(1 for m in tracked if m.status == discord.Status.dnd)
        idle = sum(1 for m in tracked if m.status == discord.Status.idle)
        invisible = sum(1 for m in tracked if m.status == discord.Status.offline)

        embed = discord.Embed(title=f"{guild.name} Presence Stats", color=0xffffff)
        embed.add_field(name="Total Members", value=str(total_members))
        embed.add_field(name="Total Bots", value=str(total_bots))
        embed.add_field(name="Tracked Users", value=str(total_tracked), inline=False)
        embed.add_field(name="Online", value=str(online))
        embed.add_field(name="DND", value=str(dnd))
        embed.add_field(name="Idle", value=str(idle))
        embed.add_field(name="Invisible/Offline", value=str(invisible))

        return await interaction.response.send_message(embed=embed)

                                                             

    status_map = {
        "online": discord.Status.online,
        "dnd": discord.Status.dnd,
        "idle": discord.Status.idle,
        "invisible": discord.Status.offline,
    }

    target = status_map[status.value]

    matched = [m for m in tracked if m.status == target]

    if not matched:
        return await interaction.response.send_message(
            f"No tracked users are **{status.name}**.", ephemeral=True
        )

    pages = []
    per_page = 10

    for i in range(0, len(matched), per_page):
        chunk = matched[i:i+per_page]

        embed = discord.Embed(
            title=f"{status.name} Members",
            color=0xffffff
        )
        desc = "\n".join(
            f"`{i + idx + 1}.` {m.mention} ({m.name})"
            for idx, m in enumerate(chunk)
        )
        embed.description = desc
        pages.append(embed)

    view = PresencePaginator(pages, interaction.user.id)
    await interaction.response.send_message(embed=pages[0], view=view)

@client.tree.command(name="top_games", description="Show the top games currently being played in this server.")
async def top_games(interaction: discord.Interaction):

    guild = interaction.guild
    if not guild:
        return await interaction.response.send_message("This command must be used in a server.", ephemeral=True)

    from collections import Counter
    game_counter = Counter()

    for member in guild.members:
        if member.bot or member.id in PRIVACY_SET:
            continue

                                     
        for activity in member.activities:
            if isinstance(activity, discord.Game):
                game_counter[activity.name] += 1

    if not game_counter:
        return await interaction.response.send_message(
            "No tracked users are currently playing any games.",
            ephemeral=True
        )

    embed = discord.Embed(
        title=f"Top Games in {guild.name}",
        color=0xffffff
    )

    for game, count in game_counter.most_common(10):
        embed.add_field(name=game, value=f"{count} player(s)", inline=False)

    embed.set_footer(text="Users who opted out of presence tracking are excluded.")

    await interaction.response.send_message(embed=embed)

@client.tree.command(name="now_playing", description="See what a user is currently playing or doing.")
@app_commands.describe(user="The user to check.")
async def now_playing(interaction: discord.Interaction, user: discord.Member):

                                     
    if user.id in PRIVACY_SET:
        return await interaction.response.send_message(
            "❌ This user has opted out of presence tracking.",
            ephemeral=True
        )

    guild = interaction.guild
    if guild is None:
        return await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True
        )

                                                           
    member = guild.get_member(user.id) or user

    embed = discord.Embed(
        title=f"{member.name}'s Current Activities",
        color=0xffffff
    )

    activities = getattr(member, "activities", None)

    if not activities:
        embed.description = "This user is not doing anything detectable at the moment."
        return await interaction.response.send_message(embed=embed)

    activity_found = False

    for activity in activities:

              
        if isinstance(activity, discord.Game):
            embed.add_field(
                name="Playing",
                value=activity.name,
                inline=False
            )
            activity_found = True

                 
        elif isinstance(activity, discord.Spotify):
            embed.add_field(
                name="> Listening on Spotify",
                value=f"**{activity.title}** by **{activity.artist}**",
                inline=False
            )
            activity_found = True

                   
        elif isinstance(activity, discord.Streaming):
            embed.add_field(
                name="> Streaming",
                value=f"**{activity.name}**\n{activity.url}",
                inline=False
            )
            activity_found = True

                       
        elif isinstance(activity, discord.CustomActivity):
            if activity.name:
                embed.add_field(
                    name="> Custom Status",
                    value=activity.name,
                    inline=False
                )
                activity_found = True

                                           
        else:
            if activity.name:
                embed.add_field(
                    name="> Activity",
                    value=activity.name,
                    inline=False
                )
                activity_found = True

    if not activity_found:
        embed.description = "No detectable activities for this user."

    await interaction.response.send_message(embed=embed)



@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if "@everyone" in message.content or "@here" in message.content:
        config = load_audit_config()
        gid = str(message.guild.id)

        if not config.get(gid, {}).get("enabled", False):
            return

        timestamp = datetime.now(timezone.utc)
        log_entry = f"{timestamp.isoformat()} | Action: everyone_ping | By: {message.author} | Channel: {message.channel.name}"
        append_audit_log(message.guild.id, log_entry)

        channel_id = config[gid].get("channel")
        if channel_id:
            log_channel = message.guild.get_channel(channel_id)
            if log_channel:
                embed = discord.Embed(
                    title=f"Audit Log Entry",
                    color=0xffffff,
                    timestamp=timestamp
                )
                embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                embed.add_field(name="Action", value=f"Mentioning @everyone or @here", inline=False)
                embed.add_field(name="Executor", value=f"{message.author} ({message.author.id})", inline=False)
                embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                embed.add_field(name="Message", value=message.content[:1000], inline=False)
                embed.add_field(name="Time", value=format_dt(timestamp, style='F'), inline=False)

                await log_channel.send(embed=embed)

    await client.process_commands(message)



@client.event
async def on_message(message: discord.Message):
    await client.process_commands(message)
    if message.guild is None or message.author.bot: return
    cfg = get_guild_cfg(message.guild.id)

                                                                       
                                                                       
    if cfg.get("log_channel_id") and message.channel.id in set(cfg.get("scam_channels") or []):
                                                       
        if is_scam_whitelisted(message.author, cfg):
            return

        reasons = scan_message_for_scams(message.content or "", cfg)
        try:
            for em in message.embeds:
                if em.title: reasons += scan_message_for_scams(em.title, cfg)
                if em.description: reasons += scan_message_for_scams(em.description, cfg)
                for f in em.fields: reasons += scan_message_for_scams(f"{f.name or ''} {f.value or ''}", cfg)
        except Exception: pass
                
        s, ordered = set(), []
        for r in reasons:
            if r not in s: ordered.append(r); s.add(r)
        reasons = ordered

        if reasons:
            deleted = False
            try: await message.delete(); deleted = True
            except Exception: pass

            log_channel = message.guild.get_channel(cfg["log_channel_id"])
            if log_channel and log_channel.permissions_for(message.guild.me).send_messages:
                action_id = str(uuid.uuid4())
                domains = extract_domains(message.content or "")
                actions = load_actions()
                actions[action_id] = {
                    "guild_id": message.guild.id,
                    "author_id": message.author.id,
                    "content": message.content or "",
                    "reasons": reasons,
                    "domains": domains,
                    "ts": int(time.time()),
                }
                save_actions(actions)

                desc = f"Message from **{message.author}** {'was removed' if deleted else 'was flagged'} in {message.channel.mention}."
                e = embed_basic("Scam/Phishing Content Intercepted", desc, COLOR_BAD)
                e.add_field(name="Reasons", value=" • " + "\n • ".join(reasons), inline=False)
                snippet = (message.content or "").strip()
                e.add_field(name="Snippet", value=f"```{snippet[:900]}```" if snippet else "`(no text)`", inline=False)
                if domains: e.add_field(name="Domains", value=", ".join(domains)[:1000], inline=False)
                e.timestamp = discord.utils.utcnow()
                await log_channel.send(embed=e, view=ScamFeedbackView(action_id=action_id))

            try:
                await message.author.send(embed=embed_basic(
                    "Your message was blocked",
                    "We detected content that resembles known scams/phishing. A moderator can mark it **Not a Scam** in the log.",
                    COLOR_WARN
                ))
            except Exception: pass

            return                                            

                                                              
    if message.channel.id in set(cfg.get("codehelper_channels") or []):
        handled = 0
        for m in CODEBLOCK_CLOSED_RE.finditer(message.content or ""):
            if handled >= 2: break
            lang = (m.group("lang") or "").strip(); code = m.group("code") or ""
            if lang.lower() in ("py", "python") and code.strip():
                ok, detail = try_python_syntax_check(code)
                e = embed_basic("Python Syntax Check" if ok else "Python Syntax Error",
                                ("✅ " if ok else "❌ ") + detail, COLOR_OK if ok else COLOR_BAD)
                e.add_field(name="Excerpt", value=f"```py\n{code[:800]}\n```", inline=False)
                await message.reply(embed=e, mention_author=False)
                handled += 1
        if handled == 0:
            m = CODEBLOCK_UNTERMINATED_RE.search(message.content or "")
            if m:
                lang = (m.group("lang") or "").strip(); code = m.group("code") or ""
                if lang.lower() in ("py", "python") and code.strip():
                    ok, detail = try_python_syntax_check(code)
                    e = embed_basic("Python Syntax Check" if ok else "Python Syntax Error",
                                    ("✅ " if ok else "❌ ") + detail, COLOR_OK if ok else COLOR_BAD)
                    e.add_field(name="Excerpt", value=f"```py\n{code[:800]}\n```", inline=False)
                    await message.reply(embed=e, mention_author=False)
    

                                                                                                 

client.run(os.getenv("DISCORD_TOKEN"))
  