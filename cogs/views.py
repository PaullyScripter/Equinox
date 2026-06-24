import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
from discord.ui import View, Modal, Button, Select, TextInput
from typing import Optional, Any, Dict, List, Tuple, Literal
from collections import deque, defaultdict
import asyncio
from datetime import datetime, date, timezone, timedelta
import json, random, os, re, math, io, hashlib, ssl, smtplib, string, uuid, secrets, time
from asyncio import sleep, gather, wait_for, create_task
from email.message import EmailMessage
import aiohttp
import googletrans
from googletrans import Translator


def _email_ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx
import wikipedia
import numpy
import matplotlib.pyplot as plt
from captcha.image import ImageCaptcha
from io import BytesIO
import sys
import PyDictionary
from PyDictionary import PyDictionary
import httpx
import qrcode
from PIL import Image
import requests

import state
import cogs.database as db

DEV_USER_ID = [857932717681147954]

email_sender = os.getenv("email_sender")
email_password = os.getenv("email_password")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def load_verifying_users() -> set[tuple[int, int]]:
    return db.load_verifying_users()


def save_verifying_users(data: set[tuple[int, int]]):
    db.save_verifying_users(data)


VERIFYING_USERS: set[tuple[int, int]] = db.load_verifying_users()

_pending_auths: dict[int, dict] = {}
AUTH_CODE_EXPIRY = 300
AUTH_MAX_ATTEMPTS = 3
RESET_COOLDOWN = 86400

update = "EV-5.1"
update_note_content = "```diff\n+Added giveaway command\n  > Start a giveaway.\n\n+Added graph command. (Premium only)\n  > Create a graph with a function.```"

language_dict = {}
for key, value in googletrans.LANGUAGES.items():
    if key in ['af', 'ar', 'hy', 'bs', 'bg', 'zh-cn', 'zh-tw', 'hr', 'nl', 'en', 'tl', 'fr', 'el', 'hi', 'id', 'ga', 'it', 'ja', 'ko', 'lo', 'ms', 'pt', 'es', 'th', 'vi']:
        language_dict[key] = value

SAFE_CHARS_RE = re.compile(r'^[\w\s+\-*/()\[\],.:=%!<>&|~^@]+$')

def _update_code_display(view, embed, num):
    val = f"```{num}```" if num else "```Code:```"
    embed.set_field_at(0, name="Your Code:", value=val, inline=False)

def generate_captcha():
    captcha_code = f"{random.randint(0, 99999999):08d}"
    image_captcha = ImageCaptcha(width=300, height=120)
    image_data = image_captcha.generate(captcha_code)
    image_buffer = io.BytesIO(image_data.getvalue())
    return captcha_code, image_buffer

def fetch_word_example(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en_US/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'meanings' in data[0] and 'definitions' in data[0]['meanings'][0] and 'example' in data[0]['meanings'][0]['definitions'][0]:
            example = data[0]['meanings'][0]['definitions'][0]['example']
            return example
    return None

def snowflake_time(id):
    return datetime.utcfromtimestamp(((id >> 22) + 1420070400000) / 1000)

def random_color():
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def process_function(func):
    func = func.strip()
    if not SAFE_CHARS_RE.match(func):
        return None
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
        y = eval(safe_func, {"__builtins__": {}, "numpy": numpy, "x": test_x})
        return y.shape == x.shape
    except Exception:
        return False

def generate_graph(user_id, zoom_factor=1.0):
    try:
        if user_id not in state.user_graph_data:
            raise ValueError("No functions or points to plot.")
        if 'zoom' not in state.user_graph_data[user_id]:
            state.user_graph_data[user_id]['zoom'] = 1.0
        state.user_graph_data[user_id]['zoom'] *= zoom_factor
        zoom = state.user_graph_data[user_id]['zoom']
        x_min, x_max = -10 * zoom, 10 * zoom
        y_min, y_max = -10 * zoom, 10 * zoom
        x = numpy.linspace(x_min, x_max, 400)
        plt.figure(figsize=(6, 6))
        for func, color in state.user_graph_data[user_id].get('functions', []):
            try:
                valid_func = process_function(func)
                safe_x = numpy.copy(x)
                if "numpy.sqrt" in valid_func:
                    safe_x = numpy.where(safe_x >= 0, safe_x, numpy.nan)
                y = eval(valid_func, {"__builtins__": {}, "numpy": numpy, "x": safe_x})
                plt.plot(x, y, label=func, color=color)
            except Exception as e:
                raise ValueError(f"Invalid function '{func}'. Error: {e}")
        for point in state.user_graph_data[user_id].get('points', []):
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
        state.user_graph_data[user_id]['graph_image'] = buf
        plt.clf()
    except Exception as e:
        state.user_graph_data[user_id]['graph_image'] = None
        raise

async def send_graph_embed(interaction: discord.Interaction, user_id):
    graph_image = state.user_graph_data[user_id]["graph_image"]
    if graph_image is None:
        return await interaction.response.send_message("Failed to generate the graph.", ephemeral=True)
    embed = discord.Embed(title=None, description=None, color=0xffffff)
    embed.set_author(name=f"{interaction.user.name}'s Graph", icon_url=interaction.user.avatar)
    embed.set_image(url="attachment://graph.png")
    if "message" in state.user_graph_data[user_id] and state.user_graph_data[user_id]["message"]:
        try:
            old_message = state.user_graph_data[user_id]["message"]
            old_view = GraphView(user=interaction.user, message=old_message)
            for item in old_view.children:
                item.disabled = True
            await old_message.edit(view=old_view)
        except (discord.NotFound, discord.HTTPException):
            pass
    view = GraphView(interaction.user)
    message = await interaction.channel.send(embed=embed, file=discord.File(graph_image, filename="graph.png"), view=view)
    state.user_graph_data[user_id]["message"] = message

def remove_code_from_pool(tier: str, code: str):
    if tier == "monthly":
        data = state.read_json("monthcode")
        if code in data.get("monthlycodes", []):
            data["monthlycodes"].remove(code)
            state.write_json(data, "monthcode")
        state.client.monthly_codes = state.read_json("monthcode").get("monthlycodes", [])
    elif tier == "yearly":
        data = state.read_json("yearlycode")
        if code in data.get("yearlycodes", []):
            data["yearlycodes"].remove(code)
            state.write_json(data, "yearlycode")
        state.client.yearly_codes = state.read_json("yearlycode").get("yearlycodes", [])
    elif tier == "lifetime":
        data = state.read_json("lifetimecode")
        if code in data.get("lifetimecodes", []):
            data["lifetimecodes"].remove(code)
            state.write_json(data, "lifetimecode")
        state.client.lifetime_codes = state.read_json("lifetimecode").get("lifetimecodes", [])

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

class ReactionRoleView(discord.ui.View):
    def __init__(self, roles, custom_id):
        super().__init__(timeout=None)
        self.add_item(ReactionRoleDropdown(roles, custom_id))

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
            if self.all_item:
                await interaction.response.defer(ephemeral=True)
                embed=discord.Embed(title=f"All {self.member.name}'s Acquired Item(s):", description=f"```{self.all_item}```", color=0xffffff)
                msg = await interaction.followup.send(embed=embed)
                await sleep(15)
                await msg.delete()
            else:
                await interaction.response.defer()
        else:
            await interaction.response.defer()

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.NotFound:
            pass

class BuyPremium(View):
    def __init__(self):
        super().__init__(timeout=60)
        button = discord.ui.Button(label='Buy Premium', style=discord.ButtonStyle.url, url='https://discord.gg/Cu8JR7Vsvx')
        self.add_item(button)

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

class myInvite(View):
    def __init__(self):
        super().__init__(timeout=60)
        button = discord.ui.Button(label='Admin Perms', style=discord.ButtonStyle.url, url='https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=8&scope=bot')
        button2 = discord.ui.Button(label='Limited Perms', style=discord.ButtonStyle.url, url='https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=268494870&scope=bot')
        self.add_item(button)
        self.add_item(button2)

class Mymodal(ui.Modal, title="Be an elite user"):
    code = ui.TextInput(
        label="Enter code",
        placeholder="Include capitals and dashes.",
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = state.client.get_channel(1242633669890277456)
        msg = await channel.send(self.code)
        user_input = msg.content.strip()
        state.refresh()

        active, current_tier, _expires = await state.is_premium(interaction.user.id)
        if active:
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
        if user_input in getattr(state.client, "monthly_codes", []):
            tier = "monthly"
        elif user_input in getattr(state.client, "yearly_codes", []):
            tier = "yearly"
        elif hasattr(state.client, "lifetime_codes") and user_input in getattr(state.client, "lifetime_codes", []):
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
        state.add_subscription(interaction.user.id, tier, user_input)

        try:
            state.replenish_codes(tier, 5)
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

class AuthButton(discord.ui.View):
    def __init__(self, email, authorID):
        self.email = email
        self.authorID = authorID
        super().__init__(timeout=60)
    @discord.ui.button(label="Send")
    async def Send(self, interaction: discord.Interaction, Button: discord.Button):
        if interaction.user.id != self.authorID:
            await interaction.response.defer()
            return

        auth_code = str(secrets.randbelow(1_000_000)).zfill(6)
        try:
            subject = f"Authorization Code Equinox - {auth_code}"
            body = f"Greetings!\nThis is an automated email from Equinox Messenger.\n\nYour authorization code is: {auth_code}\n\nDo not send this to anyone\n\nEquinox Team."

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = self.email
            em['Subject'] = subject
            em.set_content(body)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=_email_ssl_context()) as smtp:
                smtp.login(email_sender, email_password)
                smtp.sendmail(email_sender, self.email, em.as_string())
        except Exception as e:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="Email Failed",
                    description=f"Could not send the email.\n`{e}`",
                    color=0xED4245,
                ),
                view=self,
            )
            return

        _pending_auths[interaction.user.id] = {
            "code": auth_code,
            "email": self.email,
            "expires": time.time() + AUTH_CODE_EXPIRY,
            "attempts": 0,
            "unlink_mode": getattr(self, "unlink_mode", False),
        }
        await interaction.response.send_modal(AuthModal())

    async def on_timeout(self) -> None:
        self._cleanup()
        await self.message.delete()

    def _cleanup(self):
        _pending_auths.pop(self.authorID, None)

class AuthModal(ui.Modal, title="Email Authentication"):
    code_input = ui.TextInput(
        label="Enter the 6-digit code sent to your email",
        placeholder="000000",
        min_length=6,
        max_length=6,
    )

    async def on_submit(self, interaction: discord.Interaction):
        from cogs.gacha import _set_email
        pending = _pending_auths.get(interaction.user.id)
        if pending is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="No Pending Request",
                    description="No authentication was requested. Please run /login again.",
                    color=0xED4245,
                ),
                ephemeral=True,
            )
            return

        if time.time() > pending["expires"]:
            _pending_auths.pop(interaction.user.id, None)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Code Expired",
                    description="The code has expired. Please run /login again.",
                    color=0xED4245,
                ),
                ephemeral=True,
            )
            return

        if pending["attempts"] >= AUTH_MAX_ATTEMPTS:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Too Many Attempts",
                    description="You have exceeded the maximum number of attempts. Please run /login again.",
                    color=0xED4245,
                ),
                ephemeral=True,
            )
            return

        if self.code_input.value.strip() == pending["code"]:
            _pending_auths.pop(interaction.user.id, None)
            if pending.get("unlink_mode"):
                from cogs.gacha import _set_field
                await _set_field(interaction.user.id, "email", None)
                await _set_field(interaction.user.id, "eligible", 0)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Email Unlinked",
                        description="Your email has been removed from your account. You can link a new one with /login.",
                        color=0x57F287,
                    ),
                    ephemeral=True,
                )
            else:
                await _set_email(interaction.user.id, pending["email"])
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Email Verified",
                        description="Your email has been successfully linked and you are now eligible for account management.",
                        color=0x57F287,
                    ),
                    ephemeral=True,
                )
        else:
            pending["attempts"] += 1
            remaining = AUTH_MAX_ATTEMPTS - pending["attempts"]
            msg = "The code you entered does not match. Please try again."
            if remaining > 0:
                msg += f" {remaining} attempt(s) remaining."
            else:
                msg = "No more attempts. Please run /login again."
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invalid Code",
                    description=msg,
                    color=0xED4245,
                ),
                ephemeral=True,
            )

class LoginModal(ui.Modal, title="Email"):
    email = ui.TextInput(label="Enter email", style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
        from cogs.gacha import _get_user_full, _check_email, _set_field
        user_data = await _get_user_full(interaction.user.id)

        if user_data is None or user_data.get("email") is None:
            view = AuthButton(self.email.value.strip(), interaction.user.id)
            await interaction.response.defer()
            msg2 = await interaction.followup.send(
                content="You do not have any credentials paired with your databases, can I send a code to your input email?",
                view=view,
            )
            view.message = msg2
        else:
            if await _check_email(interaction.user.id, self.email.value.strip()):
                await _set_field(interaction.user.id, "eligible", 1)
                title = "You have successfully logged in."
                description = "You can now use login required commands."
            else:
                title = "You have failed to log in"
                description = "Please check if your input is correct"
            await interaction.response.send_message(
                embed=discord.Embed(title=title, description=description, color=0xffffff),
            )

class ResetButton(discord.ui.View):
    def __init__(self, authorID, mode: str):
        self.authorID = authorID
        self.mode = mode
        super().__init__(timeout=60)
    @discord.ui.button(label="Reset", style=discord.ButtonStyle.red)
    async def Reset(self, interaction: discord.Interaction, Button: discord.Button):
        if interaction.user.id == self.authorID:
            from cogs.gacha import _get_user_full, _set_field, _delete_user
            Button.disabled = True

            if self.mode == "request":
                await _set_field(self.authorID, "reset_requested_at", int(time.time()) + RESET_COOLDOWN)
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="Reset Requested",
                        description="Your data will be eligible for reset in 24 hours. You'll be DMed when ready.",
                        color=0xffffff,
                    ),
                    view=self,
                )
                async def _notify():
                    await asyncio.sleep(RESET_COOLDOWN)
                    try:
                        user = state.client.get_user(self.authorID) or await state.client.fetch_user(self.authorID)
                        await user.send(
                            "Your 24-hour reset cooldown has ended. Run `/reset` to confirm and permanently delete your data."
                        )
                    except Exception:
                        pass
                asyncio.create_task(_notify())
            elif self.mode == "confirm":
                user_data = await _get_user_full(self.authorID)
                if user_data and user_data.get("eligible"):
                    await _delete_user(self.authorID)
                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="All your data have been reseted",
                            description="> To collect items again, use **/roll**\n> To craft, use **/craft**\n> To show inventory, use **/inventory**",
                            color=0xffffff,
                        ),
                        view=self,
                    )
                else:
                    await interaction.response.edit_message(
                        embed=discord.Embed(
                            title="You are not authorized to reset",
                            description="Please use /login to reset your databases.",
                            color=0xffffff,
                        ),
                        view=self,
                    )
        else:
            await interaction.response.defer()

    async def on_timeout(self) -> None:
        await self.message.delete()

class NumbersButton(discord.ui.View):
    def __init__(self, guild_id, authorid, revroleid, addroleid, code):
        super().__init__(timeout=120)
        self.num = ""
        self.guild_id = guild_id
        self.authorid = authorid
        self.revroleid = revroleid
        self.addroleid = addroleid
        self.code = code
    async def on_timeout(self) -> None:
        if (self.guild_id, self.authorid) not in VERIFYING_USERS:
            return
        if not self.message:
            return
        try:
            await self.message.channel.send(f"<@{self.authorid}> ⏰ Verification timed out. Click the button to try again.", delete_after=10)
        except:
            pass
        try:
            await self.message.delete()
        except discord.NotFound:
            pass
        VERIFYING_USERS.discard((self.guild_id, self.authorid))
        save_verifying_users(VERIFYING_USERS)

    async def edit_embed(self, interaction, number):
        if interaction.user.id != self.authorid:
            return await interaction.response.defer()
        if len(self.num) >= 8:
            return await interaction.response.defer()
        self.num += f"{number}"
        embed = self.message.embeds[0]
        _update_code_display(self, embed, self.num)
        await interaction.response.edit_message(embed=embed, view=self)

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
        if interaction.user.id != self.authorid:
            return await interaction.response.defer()
        if not self.num:
            return await interaction.response.defer()
        self.num = self.num[:-1]
        embed = self.message.embeds[0]
        _update_code_display(self, embed, self.num)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Regenerate", style=discord.ButtonStyle.blurple, custom_id="regenerate", row=2)
    async def regenerate(self, interaction: discord.Interaction, Button: discord.Button):
        if interaction.user.id != self.authorid:
            return await interaction.response.defer()
        captcha_code, captcha_image = generate_captcha()
        self.code = captcha_code
        self.num = ""
        embed = self.message.embeds[0]
        _update_code_display(self, embed, "")
        file = discord.File(captcha_image, filename="captcha.png")
        await interaction.response.edit_message(embed=embed, view=self, attachments=[file])

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.grey, custom_id="submit")
    async def submit(self, interaction: discord.Interaction, Button: discord.Button):
        if interaction.user.id != self.authorid:
            return await interaction.response.defer(ephemeral=True)
        if len(self.num) != 8:
            return await interaction.response.send_message("Code must be exactly 8 digits.", ephemeral=True)

        if self.num != self.code:
            VERIFYING_USERS.discard((self.guild_id, self.authorid))
            save_verifying_users(VERIFYING_USERS)
            await interaction.response.send_message("❌ Wrong code. You can click the button again to retry.", ephemeral=True)
            await self.message.delete()
            return

        if self.revroleid is not None:
            try:
                rev_role = interaction.guild.get_role(self.revroleid)
                if rev_role:
                    await interaction.user.remove_roles(rev_role)
            except discord.Forbidden:
                pass
        if self.addroleid is not None:
            try:
                add_role = interaction.guild.get_role(self.addroleid)
                if add_role:
                    await interaction.user.add_roles(add_role)
            except discord.Forbidden:
                pass

        VERIFYING_USERS.discard((self.guild_id, self.authorid))
        save_verifying_users(VERIFYING_USERS)
        await interaction.response.send_message("✅ You have been verified!", ephemeral=True)
        await self.message.delete()

class VerifyButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Start the verify progress", style=discord.ButtonStyle.green, custom_id="verifybutton")
    async def verifybutton(self, interaction: discord.Interaction, Button: discord.Button):
        config = db.get_verify_config(interaction.guild.id)

        if config is None:
            await interaction.response.defer()
            await interaction.followup.send("This verify system is outdated and or removed, please contact server owner/admins.", ephemeral=True)
            return

        gid = interaction.guild.id
        uid = interaction.user.id

        if (gid, uid) in VERIFYING_USERS:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("You already have an ongoing verification in this server. Finish it first.", ephemeral=True)
            return

        captcha_code, captcha_image = generate_captcha()
        file = discord.File(captcha_image, filename="captcha.png")

        embed=discord.Embed(title="Enter the 8 digits show above to verify.", color=0xffffff)
        embed.add_field(name="Your Code:", value="```Code:```", inline=False)
        embed.set_footer(text=f"Verifying {interaction.user.name}...", icon_url=interaction.user.avatar.url)
        view = NumbersButton(gid, uid, config['remove_role'], config['add_role'], captcha_code)
        await interaction.response.defer()
        msg = await interaction.followup.send(interaction.user.mention, embed=embed, view=view, file=file)
        view.message = msg
        VERIFYING_USERS.add((gid, uid))
        save_verifying_users(VERIFYING_USERS)

class DeleteVerifySystem(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
    @discord.ui.button(label="Delete Verify System (owner only)", style=discord.ButtonStyle.red)
    async def deleteverifysystem(self, interaction: discord.Interaction, Button: discord.Button):
        if interaction.user.id == interaction.guild.owner_id:
            db.delete_verify_config(interaction.guild.id)
            await interaction.response.send_message(embed=discord.Embed(title="Successfully deleted verify system.", color=0xffffff))
        else:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("You need to be the server's owner to do this.", ephemeral=True)

    async def on_timeout(self) -> None:
        if not self.message:
            return
        deleteverifyssytembutton = discord.utils.get(self.children, label="Delete Verify System (owner only)")
        if deleteverifyssytembutton:
            deleteverifyssytembutton.disabled = True
        try:
            await self.message.edit(view=self)
        except discord.NotFound:
            pass

class EmailCheck(discord.ui.View):
    def __init__(self, email, code, codetype):
        super().__init__(timeout=60)
        self.email = email
        self.code = code
        self.codetype = codetype
    @discord.ui.button(label="Yes, send.", style=discord.ButtonStyle.red)
    async def EmailCheckButton(self, interaction: discord.Interaction, Button: discord.Button):
        if interaction.user.id in state.devs:
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

                try:
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=_email_ssl_context()) as smtp:
                        smtp.login(email_sender, email_password)
                        smtp.sendmail(email_sender, email_receiver, em.as_string())
                except Exception as exc:
                    await interaction.edit_original_response(
                        embed=discord.Embed(title="Email Send Failed", description=f"Email error: {exc}", color=0xED4245),
                        view=None,
                    )
                    return
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
        if interaction.user.id in state.devs:
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

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=_email_ssl_context()) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email_receiver, em.as_string())
            except Exception as exc:
                await interaction.edit_original_response(
                    embed=discord.Embed(title="Email Send Failed", description=f"Email error: {exc}", color=0xED4245),
                )
                return
            embed=discord.Embed(title=subject, description=body, color=0xffffff)
            await interaction.edit_original_response(embed=embed)
        else:
            await interaction.response.defer()

    async def on_timeout(self) -> None:
        emailcheckbutton = discord.utils.get(self.children, label="Yes, send.")
        emailcheckbutton.disabled = True
        await self.message.edit(view=self)

class UnbanButton(discord.ui.View):
    def __init__(self, userID):
        super().__init__(timeout=60)
        self.userID = userID
    @discord.ui.button(label="Unban Member", style=discord.ButtonStyle.grey, custom_id="unban")
    async def unban(self, interaction: discord.Interaction, Button: discord.Button):
        if interaction.user.guild_permissions.ban_members:
            user = await state.client.fetch_user(self.userID)
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

class translateSelect(View):
    def __init__(self, original_message, authorID, translated_message):
        super().__init__(timeout=60)
        self.original_message = original_message
        self.authorID = authorID
        self.translated_message = translated_message

    @discord.ui.select(placeholder="Choose a destination language",
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
            embe.set_author(name="Equinox Translator", icon_url=state.client.user.avatar)
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
            except Exception:
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
            except Exception:
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
            except Exception:
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
            except Exception:
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
            except Exception:
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
            except Exception:
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
            except Exception:
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
            except Exception:
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
            except Exception:
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
            except Exception:
                await msg.delete()
                await interaction.channel.send(embed=discord.Embed(title=f"{self.output[0]} - Wikipedia Result", description=f"```No page available for this query sorry :(```",color=0xffffff))
        else:
            await interaction.response.defer()

    async def on_timeout(self) -> None:
        for children in self.children:
            children.disabled = True
        await self.message.edit(view=self)

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

class rrSelectGames(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Click here to choose a game!",
                       options=[
                          discord.SelectOption(label="Genshin Impact", value="1", description="Genshin Impact", emoji="<:GI1Primogem:1265298846880370691>"),
                          discord.SelectOption(label="Honkai: Star Rail", value="2", description="Honkai: Star Rail", emoji="<:HSR1Stellarjade:1265292394459299975>"),
                          discord.SelectOption(label="Zenless Zone Zero", value="3", description="Zenless Zone Zero", emoji="<:ZZZ1Polychrome:1265304068662759517>"),
                          discord.SelectOption(label="Wuthering Waves", value="4", description="Wuthering Waves", emoji="<:Astrite:1265305744480276603>")
                          ],
                       custom_id="rrSelectGamesSelection"
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

    @discord.ui.select(placeholder="Click here to choose a pronoun!",
                       options=[
                          discord.SelectOption(label="She/Her", value="1", description="She/Her", emoji="🩷"),
                          discord.SelectOption(label="He/Him", value="2", description="He/Him", emoji="💙"),
                          discord.SelectOption(label="They/Them", value="3", description="They/Them", emoji="🖤"),
                          discord.SelectOption(label="Other Pronouns", value="4", description="Other Pronouns", emoji="🤍")
                          ],
                       custom_id="rrSelectGenderSelection"
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

    @discord.ui.select(placeholder="Click here to choose a ping role!",
                       options=[
                          discord.SelectOption(label="Announcement Ping", value="1", description="Announcement Ping", emoji="✉️"),
                          discord.SelectOption(label="Giveaway Ping", value="2", description="Giveaway Ping", emoji="🎉"),
                          discord.SelectOption(label="Events Ping", value="3", description="Events Ping", emoji="🔊"),
                          discord.SelectOption(label="Dead Chat Ping", value="4", description="Dead Chat Ping", emoji="💬")
                          ],
                       custom_id="rrSelectPingSelection"
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

    @discord.ui.select(placeholder="Click here to choose a server role!",
                       options=[
                          discord.SelectOption(label="NA Server", value="1", description="NA Server", emoji="🌎"),
                          discord.SelectOption(label="EU Server", value="2", description="EU Server", emoji="🌍"),
                          discord.SelectOption(label="Asia Server", value="3", description="Asia Server", emoji="🌏")
                          ],
                       custom_id="rrSelectServerSelection"
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

class mySelect(View):
    def __init__(self, authorID):
        super().__init__(timeout=60)
        self.authorID = authorID
        self.embed = None
        button = discord.ui.Button(label='Invite Me', style=discord.ButtonStyle.url, url='https://discord.com/oauth2/authorize?client_id=1237992032715280385&permissions=8&scope=bot')
        button2 = discord.ui.Button(label='Privacy Policy', style=discord.ButtonStyle.url, url='https://gist.github.com/PaullyScripter/c6ed57ac20fcc54dcf01adac78e6f712')
        button3 = discord.ui.Button(label='Support Server', style=discord.ButtonStyle.url, url='https://discord.gg/wAqVkf3MmG')
        button4 = discord.ui.Button(label='Website', style=discord.ButtonStyle.url, url='https://equinoxbot.netlify.app')
        self.add_item(button)
        self.add_item(button2)
        self.add_item(button3)
        self.add_item(button4)

    @discord.ui.select(placeholder="Choose a catergory",
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
                em.set_author(name="Utilities Commands List", icon_url=state.client.user.avatar)
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
                state.refresh()
                member = interaction.user
                active, tier, expires_at = await state.is_premium(member.id)
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
                embed.set_author(name="Black or White, Equinox.", icon_url=state.client.user.avatar)
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

class CurrencyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Supported Currencies", style=discord.ButtonStyle.grey, custom_id="supported_currencies")
    async def supported_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        fiat_list = ", ".join(sorted(state.SUPPORTED_FIAT))
        crypto_list = ", ".join(sorted(state.SYMBOL_TO_ID.keys()))
        embed = discord.Embed(title="Supported Currencies", color=0xffffff)
        embed.add_field(name="Fiat", value=fiat_list, inline=False)
        embed.add_field(name="Crypto", value=crypto_list, inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        gemini_data = state.load_gemini_servers()
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

class RemoveGeminiView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = str(guild_id)

    @discord.ui.button(label="Remove Gemini", style=discord.ButtonStyle.danger, custom_id="remove_gemini_button")
    async def remove_gemini(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Only administrators can remove Gemini implementation.", ephemeral=True)
            return

        gemini_data = state.load_gemini_servers()
        if self.guild_id in gemini_data["servers"]:
            gemini_data["servers"].remove(self.guild_id)
            state.save_gemini_servers(gemini_data)
            await interaction.response.send_message("✅ Gemini implementation removed for this server.", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ This server isn't registered with Gemini.", ephemeral=True)

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
        functions = state.user_graph_data.get(user_id, {}).get('functions', [])
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
        state.user_graph_data.setdefault(user_id, {"functions": [], "graph_image": None})
        state.user_graph_data[user_id]["functions"].append((self.function_input.value.strip(), random_color()))
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
            if len(state.user_graph_data[user_id]["functions"]) == 1:
                return await interaction.response.send_message("You cannot delete the last function.", ephemeral=True)

            index = int(self.function_index.value) - 1
            if 0 <= index < len(state.user_graph_data[user_id]["functions"]):
                await interaction.response.defer()
                removed_function = state.user_graph_data[user_id]["functions"].pop(index)
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

class UpdateButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Check update", style=discord.ButtonStyle.green, custom_id="update_check")
    async def update_check(self, interaction: discord.Interaction, Button: discord.Button):
        await interaction.response.defer()
        embed = discord.Embed(title=f"Equinox's Update - {update}", description=update_note_content, color=0xffffff)
        await interaction.followup.send(embed=embed, ephemeral=True)

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
        self.roles_data = roles
        self.role_ids = [role['id'] for role in roles]
        self.role_map = {role['name']: role['id'] for role in roles}

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild

        if not self.values:
            data = state.load_data()
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
            if not role:
                continue
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

        for opt in self.options:
            role_id = int(self.role_map[opt.label])
            role = guild.get_role(role_id)
            opt.default = role in user.roles if role else False

        await interaction.response.edit_message(view=self.view)
        await interaction.followup.send(log_message, ephemeral=True)

class ScamFeedbackView(discord.ui.View):
    def __init__(self, action_id: str = None):
        super().__init__(timeout=None)
        self.action_id = action_id

    async def _disable(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Mark as Scam", style=discord.ButtonStyle.success, custom_id="scamfb:tp")
    async def mark_scam(self, interaction: discord.Interaction, button: discord.ui.Button):
        actions = state.load_actions()
        payload = actions.get(self.action_id)
        if not payload:
            return await interaction.response.send_message("Action not found or expired.", ephemeral=True)
        reasons = payload.get("reasons") or []
        weights = state.load_pattern_weights()
        boost_note = ""
        changed = False
        for r in reasons:
            old = weights.get(r, 1.0)
            new = min(1.0, old + 0.1)
            if new != old:
                weights[r] = new
                changed = True
                boost_note += f"\n• **{r}**: boosted from {old:.0%} → {new:.0%}"
        if changed:
            state.save_pattern_weights(weights)
        state.append_feedback({
            "ts": int(time.time()), "label": "true_positive",
            "guild_id": payload["guild_id"], "moderator_id": interaction.user.id,
            "message_author_id": payload["author_id"], "reasons": reasons,
            "content": payload["content"], "domains": payload.get("domains", []),
        })
        await self._disable(interaction)
        await interaction.response.send_message(embed=state.embed_basic("Logged: Marked as Scam ✅", f"Thanks!{boost_note}"), ephemeral=True)

    @discord.ui.button(label="Not a Scam", style=discord.ButtonStyle.danger, custom_id="scamfb:fp")
    async def mark_not_scam(self, interaction: discord.Interaction, button: discord.ui.Button):
        actions = state.load_actions()
        payload = actions.get(self.action_id)
        if not payload:
            return await interaction.response.send_message("Action not found or expired.", ephemeral=True)
        cfg = state.get_guild_cfg(payload["guild_id"])
        updated = False
        domains = payload.get("domains", []) or []
        content = payload.get("content", "") or ""
        reasons = payload.get("reasons") or []
        brand_reasons = {"Brand Impersonation", "Impersonation Domain"}
        has_brand = brand_reasons & set(reasons)
        if cfg.get("auto_whitelist_on_false_positive", True) and domains and not has_brand:
            wl = set(cfg.get("domain_allowlist") or [])
            for d in domains:
                if not d.startswith("xn--"):
                    wl.add(d.lower())
            state.update_guild_cfg(payload["guild_id"], domain_allowlist=sorted(wl))
            updated = True
        if not domains and not has_brand:
            norm = state.normalize_phrase(content)
            phrases = set(cfg.get("phrase_allowlist") or [])
            if norm and norm not in phrases:
                phrases.add(norm)
                state.update_guild_cfg(payload["guild_id"], phrase_allowlist=sorted(phrases))
                updated = True

            audit = state.get_guild_cfg(payload["guild_id"]).get("phrase_audit") or {}
            lst = list(audit.get(norm) or [])
            lst.append({"by": interaction.user.id, "ts": int(time.time())})
            audit[norm] = lst
            state.update_guild_cfg(payload["guild_id"], phrase_audit=audit)
        reasons = payload.get("reasons") or []
        degraded = state.degrade_pattern_weights(reasons)
        feedback_entry = {
            "ts": int(time.time()), "label": "false_positive",
            "guild_id": payload["guild_id"], "moderator_id": interaction.user.id,
            "message_author_id": payload["author_id"], "reasons": reasons,
            "content": content, "domains": domains,
        }
        state.append_feedback(feedback_entry)
        weights_note = ""
        if degraded:
            for r in reasons:
                w = degraded.get(r, 1.0)
                weights_note += f"\n• **{r}**: weight dropped to {w:.0%}"
        await self._disable(interaction)
        await interaction.response.send_message(
            embed=state.embed_basic("Logged: Not a Scam ❎", f"Updated allowlist & recorded feedback.{weights_note}" if updated else f"Recorded feedback.{weights_note}", state.COLOR_WARN),
            ephemeral=True
        )

class YoungestView(discord.ui.View):
    def __init__(self, duration: str, youngest_tuple, pages):
        super().__init__(timeout=180)
        self.duration = duration
        self.youngest_tuple = youngest_tuple
        self.pages = pages
        self.i = 0

    def _build_embed(self):
        title = f"Youngest Accounts (younger than {self.duration})"
        e = state.embed_basic(title, color=state.COLOR_INFO)

        if self.youngest_tuple:
            ym, ydt = self.youngest_tuple
            abs_t, rel_t = state.fmt_discord_time(ydt)
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
            e = state.build_overview_embed(self.guild, self.members)
            self.total_pages = 1
            self.page = 0
            await interaction.response.edit_message(embed=e, view=self)
        elif self.tab == "roles":
            e, total = state.build_top_roles_embed(self.guild, self.members, self.page)
            self.total_pages = total
            await interaction.response.edit_message(embed=e, view=self)
        elif self.tab == "graph":
            img = state.build_age_graph(self.members)
            file = discord.File(img, filename="age_distribution.png")
            e = state.embed_basic("Server Member Stats — Age Graph", "Account age distribution", state.COLOR_INFO)
            e.set_image(url="attachment://age_distribution.png")
            self.total_pages = 1
            self.page = 0
            await interaction.response.edit_message(embed=e, attachments=[file], view=self)

    @discord.ui.button(label="Overview", style=discord.ButtonStyle.primary)
    async def tab_overview(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab = "overview"
        self.page = 0
        await self.refresh(interaction)

    @discord.ui.button(label="Top Roles", style=discord.ButtonStyle.secondary)
    async def tab_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab = "roles"
        self.page = 0
        await self.refresh(interaction)

    @discord.ui.button(label="Age Graph", style=discord.ButtonStyle.secondary)
    async def tab_graph(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.tab = "graph"
        self.page = 0
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
