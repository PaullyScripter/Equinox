import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from collections import OrderedDict
import random, asyncio, math, sqlite3, json, os, hashlib, logging
from asyncio import sleep

log = logging.getLogger("gacha")


# ── Constants ──

ROLL_NAMES = [
    "Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine",
    "Myth in the Making", "Samantha", "Paully", "Tommy",
]

ROLL_GIFS = [
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXN2ZmhsdDE5ajFpamY4YmJ4cnBrM2F1OGczM3ZmODl2N3VmcGhtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dfAXMYZfSmUjYttjqM/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXE2ZHcxd3EwdDFwOGV6M3JxYmJwbzRyMGVhMjl6Ynl2d2hkcmplMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5EG56vzNYvfgJWldgS/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDNndGxyMXFsY3EzZ3djNWJrMHgwZ204aWE2NTA3eGdiNXBsd2l2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9f3OzkeQ6h0tbyKlTr/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXFkbm9wNmRkOXp4c2E1eTFiZ2FqZnZ1aHIxMjNhZnFqd2swNDA2OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/smZYhZ2Bwz8mPCwDPl/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXlza3gxYno2Z2I2NGNrdnNyMDlneGQwdmZicWxudGVzZmk3cTQ4NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mGl6JhTtCc0ukOugQ5/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3UxdWZrbDVvc281N2swc202cGR6Zmp4MGUyNmhuYjk0NWhvdXYyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cbhVQuTa5BFS5RlHFG/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDAxcm10MThzajBwbGYwOGhxMWdzZDYyazJ6OHg0dm05bWNpYW83NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FPjwcGYUkDO3kok4PP/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTRmYXA4YWl3NHdwY3k1ZGNrYjh2bzZxY2ZhZzY3eXp4a2p3eHoybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gsp2q6vt6KPZeyJgQd/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGNoa3FmYnNxc3M4Nm90ZTF0cDg4NTFpMjU0aWdndjN4ZXN2cHJzZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Xpb7aXuOuormG3MfnL/giphy.gif",
    "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ptYXg5Ymc2NHRuZmkzdDQ3YTJoN3JrZ3RiZXczMXdyd2tiZjRjbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jbsoD38dcXoEmjfNQQ/giphy.gif",
]

ITEMS = [
    "Fortune Drink", "Witch's Potion", "Divine Fluid",
    "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm",
]

RARITY_PROBABILITY = [1/2, 1/3, 1/4, 1/10, 1/100, 1/500, 1/1000, 1/10000, 1/10000, 1/10000]

PROB_LABELS = ["1/2", "1/3", "1/4", "1/10", "1/100", "1/500", "1/1,000", "1/10,000", "1/10,000", "1/10,000"]

ROLL_LABELS = [f"{ROLL_NAMES[i]}|({PROB_LABELS[i]})" for i in range(10)]

CRAFTING_RECIPES = {
    "Fortune Drink":       (["Common", "Uncommon"],                          [5, 3]),
    "Witch's Potion":      (["Common", "Uncommon", "Rare"],                  [15, 10, 5]),
    "Divine Fluid":        (["Common", "Uncommon", "Rare", "Epic"],          [30, 20, 10, 5]),
    "Angel Dust":          (["Common", "Uncommon", "Rare", "Epic", "Legendary"], [100, 70, 40, 20, 5]),
    "Me When Im Lucky":    (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine"], [250, 100, 70, 50, 25, 1]),
    "Touch of Divinity":   (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine"], [1000, 500, 400, 100, 70, 10]),
    "Trio Charm":          (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Mythic in the Making"], [5000, 2500, 1000, 500, 300, 100, 10]),
}

ITEM_EFFECTS = {
    "Fortune Drink":       ([1],       2,   [0, 1]),
    "Witch's Potion":      ([2],       3,   [1, 2]),
    "Divine Fluid":        ([3],       5,   [2, 3]),
    "Angel Dust":          ([4],      10,   [3, 4]),
    "Me When Im Lucky":    ([5],      50,   [4, 5]),
    "Touch of Divinity":   ([6],     100,   [4, 5, 6]),
    "Trio Charm":          ([7, 8, 9], 500, [7, 8, 9]),
}

DB_PATH = "data/gacha.db"
FLUSH_INTERVAL = 10
MAX_CACHE_SIZE = 1000


# ── SQLite ──

_db_lock = asyncio.Lock()
_db_conn: sqlite3.Connection = None
_db_ready = asyncio.Event()


def _init_db_sync():
    global _db_conn
    os.makedirs("data", exist_ok=True)
    _db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    _db_conn.row_factory = sqlite3.Row
    _db_conn.execute("PRAGMA journal_mode=WAL")
    _db_conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY,
            roll_count INTEGER NOT NULL DEFAULT 0,
            email TEXT,
            eligible INTEGER NOT NULL DEFAULT 0,
            reset_requested_at INTEGER
        )
    """)
    _db_conn.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            userid INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (userid, item_name)
        )
    """)
    # migrate: add reset_requested_at if missing (legacy DBs)
    try:
        _db_conn.execute("ALTER TABLE users ADD COLUMN reset_requested_at INTEGER")
    except sqlite3.OperationalError:
        pass
    _db_conn.commit()


def _migrate_json_sync():
    json_path = "data/userinventory.json"
    if not os.path.exists(json_path):
        return
    with open(json_path) as f:
        data = json.load(f)
    users = data.get("user", [])
    if not users:
        return
    for user in users:
        uid = user["userid"]
        email = user.get("email")
        eligible = 1 if user.get("eligible") else 0
        reset_at = user.get("reset_requested_at")
        _db_conn.execute(
            "INSERT OR IGNORE INTO users (userid, roll_count, email, eligible, reset_requested_at) VALUES (?, ?, ?, ?, ?)",
            (uid, user.get("roll", 0), email, eligible, reset_at),
        )
        for item_name, qty in user.get("inventory", [{}])[0].items():
            if qty > 0:
                _db_conn.execute(
                    "INSERT OR IGNORE INTO inventory (userid, item_name, quantity) VALUES (?, ?, ?)",
                    (uid, item_name, qty),
                )
    _db_conn.commit()
    os.rename(json_path, json_path + ".backup")


def _user_from_db_sync(userid):
    c = _db_conn.cursor()
    c.execute("SELECT roll_count, email, eligible, reset_requested_at FROM users WHERE userid = ?", (userid,))
    row = c.fetchone()
    if row is None:
        return None
    c.execute("SELECT item_name, quantity FROM inventory WHERE userid = ?", (userid,))
    inv = {r["item_name"]: r["quantity"] for r in c.fetchall()}
    return {
        "roll_count": row["roll_count"],
        "inventory": inv,
        "email": row["email"],
        "eligible": row["eligible"],
        "reset_requested_at": row["reset_requested_at"],
    }


def _create_user_sync(userid):
    _db_conn.execute("INSERT OR IGNORE INTO users (userid, roll_count, email, eligible, reset_requested_at) VALUES (?, 0, NULL, 0, NULL)", (userid,))
    _db_conn.commit()


def _flush_users_sync(user_data_map):
    for uid, data in user_data_map.items():
        _db_conn.execute(
            "INSERT INTO users (userid, roll_count, email, eligible, reset_requested_at) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(userid) DO UPDATE SET roll_count = ?, email = ?, eligible = ?, reset_requested_at = ?",
            (uid, data["roll_count"], data.get("email"), data.get("eligible"), data.get("reset_requested_at"),
             data["roll_count"], data.get("email"), data.get("eligible"), data.get("reset_requested_at")),
        )
        _db_conn.execute("DELETE FROM inventory WHERE userid = ?", (uid,))
        for item_name, qty in data["inventory"].items():
            if qty > 0:
                _db_conn.execute(
                    "INSERT INTO inventory (userid, item_name, quantity) VALUES (?, ?, ?)",
                    (uid, item_name, qty),
                )
    _db_conn.commit()


async def _init_database():
    async with _db_lock:
        await asyncio.get_event_loop().run_in_executor(None, _init_db_sync)
        await asyncio.get_event_loop().run_in_executor(None, _migrate_json_sync)
    _db_ready.set()


# ── In-memory cache (read-through, write-through with async flush) ──

_cache: OrderedDict = OrderedDict()
_dirty: set = set()


def _cache_get(userid):
    if userid in _cache:
        _cache.move_to_end(userid)
        return _cache[userid]
    return None


def _cache_set(userid, data):
    _cache[userid] = data
    _cache.move_to_end(userid)
    while len(_cache) > MAX_CACHE_SIZE:
        _cache.popitem(last=False)


async def _get_user(userid):
    cached = _cache_get(userid)
    if cached is not None:
        return cached
    await _db_ready.wait()
    async with _db_lock:
        data = await asyncio.get_event_loop().run_in_executor(None, _user_from_db_sync, userid)
    if data is None:
        return None
    _cache_set(userid, data)
    return data


async def _ensure_user(userid):
    data = await _get_user(userid)
    if data is not None:
        return data
    await _db_ready.wait()
    async with _db_lock:
        await asyncio.get_event_loop().run_in_executor(None, _create_user_sync, userid)
    data = {"roll_count": 0, "inventory": {}, "email": None, "eligible": 0, "reset_requested_at": None}
    _cache_set(userid, data)
    return data


def _mark_dirty(userid):
    _dirty.add(userid)


async def _flush_dirty():
    if not _dirty:
        return
    to_flush = {}
    for uid in list(_dirty):
        if uid in _cache:
            to_flush[uid] = _cache[uid]
    _dirty.clear()
    if not to_flush:
        return
    async with _db_lock:
        await asyncio.get_event_loop().run_in_executor(None, _flush_users_sync, to_flush)


async def _flush_loop():
    await _db_ready.wait()
    while True:
        await asyncio.sleep(FLUSH_INTERVAL)
        await _flush_dirty()


async def _flush_all():
    await _flush_dirty()
    if _db_conn:
        async with _db_lock:
            await asyncio.get_event_loop().run_in_executor(None, _db_conn.close)


# ── Email / Eligible helpers (used by LoginModal, ResetButton) ──

async def _set_field(userid, field, value):
    if field not in ("email", "eligible", "reset_requested_at"):
        raise ValueError(f"Invalid field: {field}")
    data = _cache_get(userid)
    if data is not None:
        data[field] = value
        _mark_dirty(userid)
        return
    await _db_ready.wait()
    async with _db_lock:
        def _exec():
            _db_conn.execute(f"UPDATE users SET {field} = ? WHERE userid = ?", (value, userid))
            _db_conn.commit()
        await asyncio.get_event_loop().run_in_executor(None, _exec)

async def _get_user_full(userid):
    """Return full user dict including email/eligible, or None."""
    return await _get_user(userid)

async def _delete_user(userid):
    """Remove a user entirely from cache and DB."""
    _cache.pop(userid, None)
    _dirty.discard(userid)
    await _db_ready.wait()
    async with _db_lock:
        _cache.pop(userid, None)
        _dirty.discard(userid)
        def _exec():
            _db_conn.execute("DELETE FROM inventory WHERE userid = ?", (userid,))
            _db_conn.execute("DELETE FROM users WHERE userid = ?", (userid,))
            _db_conn.commit()
        await asyncio.get_event_loop().run_in_executor(None, _exec)


def _hash_email(email: str) -> str:
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()


async def _set_email(userid: int, email: str):
    """Hash and store an email for a user, then mark them eligible."""
    h = _hash_email(email)
    await _set_field(userid, "email", h)
    await _set_field(userid, "eligible", 1)


async def _check_email(userid: int, email: str) -> bool:
    """Check if the given email matches the stored hash."""
    data = await _get_user(userid)
    if data is None:
        return False
    stored = data.get("email")
    if stored is None:
        return False
    return stored == _hash_email(email)


# ── Playtime helper ──

def _playtime_str(roll_count: int) -> str:
    secs = roll_count * 4
    yrs, secs = divmod(secs, 60 * 60 * 24 * 30.5 * 12)
    mth, secs = divmod(secs, 60 * 60 * 24 * 30)
    days, secs = divmod(secs, 60 * 60 * 24)
    hrs, secs = divmod(secs, 60 * 60)
    mins, secs = divmod(secs, 60)
    secs = round(secs, 2)

    parts = []
    if yrs > 0:
        parts.append(f"{int(yrs)} year(s)")
    if mth > 0:
        parts.append(f"{int(mth)} month(s)")
    if days > 0:
        parts.append(f"{int(days)} day(s)")
    if hrs > 0:
        parts.append(f"{int(hrs)} hour(s)")
    if mins > 0:
        parts.append(f"{int(mins)} minute(s)")
    parts.append(f"{secs} second(s)")
    return ", ".join(parts)


# ── Shared flex/stat logic ──

async def _flex_response(interaction: discord.Interaction, member: discord.Member, ephemeral: bool = False):
    from state import FlexButton

    data = await _get_user(member.id)

    if data is None:
        embed = discord.Embed(
            title=f"{member.name} has no items to flex.",
            description="This user has no items\nIf this is you, you can start collecting items by running /roll",
            color=0xffffff,
        )
        if ephemeral:
            await interaction.followup.send(embed=embed)
        else:
            await interaction.channel.send(embed=embed)
        return

    roll_amount = data.get("roll_count", 0)
    inventory = data.get("inventory", {})

    user_roll_names = [k for k in inventory if k in ROLL_NAMES]
    user_item_names = [k for k in inventory if k in ITEMS]

    user_rolls_ordered = [r for r in ROLL_NAMES if r in user_roll_names]
    user_items_ordered = [r for r in ITEMS if r in user_item_names]

    best_roll = user_rolls_ordered[-1] if user_rolls_ordered else None
    best_item = user_items_ordered[-1] if user_items_ordered else None

    gif_url = ""
    rarity_label = ""
    if best_roll is not None:
        idx = ROLL_NAMES.index(best_roll)
        gif_url = ROLL_GIFS[idx]
        rarity_label = PROB_LABELS[idx]

    playtime = _playtime_str(roll_amount)
    all_rolls = ", ".join(user_rolls_ordered)
    all_items = ", ".join(user_items_ordered)

    embed = discord.Embed(
        title=f"🤍 {member.name}'s Gacha Stats",
        description="Items shown are virtual items,\nand could not possibly resell or trade with real items.",
        color=0xffffff,
    )
    embed.add_field(name="> Rolling Stats:", value=f"```{member.name} has rolled {roll_amount} time(s)```", inline=False)
    embed.add_field(name="> Playtime:", value=f"```{playtime}```", inline=False)
    embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
    embed.set_thumbnail(url=member.avatar)

    view = FlexButton(interaction.user.id, best_roll, best_item, all_rolls, all_items, member, gif_url, rarity_label)

    if ephemeral:
        msg = await interaction.followup.send(embed=embed, view=view)
    else:
        msg = await interaction.channel.send(embed=embed, view=view)
    view.message = msg


# ── Context Menu ──

@app_commands.context_menu(name="Gacha Stats")
async def gacha_stats(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    await _flex_response(interaction, member, ephemeral=True)


# ── Cog ──

class GachaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.flush_task = None

    async def cog_unload(self):
        await _flush_dirty()
        if self.flush_task and not self.flush_task.done():
            self.flush_task.cancel()

    gacha = app_commands.Group(name="gacha", description="Gacha game commands")

    @gacha.command(name="roll", description="Gacha game")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.choices(item=[
        discord.app_commands.Choice(name='Fortune Drink', value=1),
        discord.app_commands.Choice(name="Witch's Potion", value=2),
        discord.app_commands.Choice(name='Divine Fluid', value=3),
        discord.app_commands.Choice(name='Angel Dust', value=4),
        discord.app_commands.Choice(name='Me When Im Lucky', value=5),
        discord.app_commands.Choice(name='Touch of Divinity', value=6),
        discord.app_commands.Choice(name='Trio Charm', value=7),
    ])
    async def roll(self, interaction: discord.Interaction, item: Optional[discord.app_commands.Choice[int]]):
        from state import is_premium, refresh

        refresh()
        await interaction.response.defer()
        data = await _ensure_user(interaction.user.id)

        luck = 1
        active = False
        try:
            active, tier, expires = await is_premium(interaction.user.id)
            if active:
                luck = 2
        except Exception as exc:
            log.warning("is_premium check failed in roll: %s", exc)

        rarity_priority: list[int] = []
        probability = 1
        luck_boost_index: list[int] = []
        able_to_roll = True
        item_name_used = "None"
        item_consumed = False

        if item is not None:
            inv = data["inventory"]
            qty = inv.get(item.name, 0)

            if qty <= 0:
                able_to_roll = False
            else:
                inv[item.name] = qty - 1
                if inv[item.name] <= 0:
                    del inv[item.name]
                item_consumed = True
                item_name_used = item.name
                _mark_dirty(interaction.user.id)

                effects = ITEM_EFFECTS.get(item.name)
                if effects:
                    rarity_priority, probability, luck_boost_index = effects

        if not able_to_roll:
            embed = discord.Embed(title="Error in the rolling...", color=0xffffff)
            embed.add_field(name=f"{item.name}", value=f"> Missing: {item.name}", inline=False)
            await interaction.followup.send(embed=embed)
            return

        weights = []
        for i in range(10):
            if i in luck_boost_index:
                if i in rarity_priority:
                    w = math.ceil(int(10000 * probability * luck / 2))
                else:
                    w = math.ceil(int(10000 * probability * luck / 1.5))
            else:
                w = math.ceil(int(10000 * RARITY_PROBABILITY[i] * probability * luck))
            weights.append(w)

        rolled_label = random.choices(ROLL_LABELS, weights=weights, k=1)[0]
        name_part, prob_part = rolled_label.split("|")
        prob_part = prob_part.strip("()")
        roll_index = ROLL_NAMES.index(name_part)

        data["roll_count"] = data.get("roll_count", 0) + 1
        data["inventory"][name_part] = data["inventory"].get(name_part, 0) + 1
        _mark_dirty(interaction.user.id)

        roll_time = random.randint(1, 2) if active else 5

        loading_embed = discord.Embed(title="Rolling...", color=0xffffff)
        loading_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWJjMml0Y3B5dmsydmVkZGtmNHl6cTZ3OG1vczQ5OHB1aGZsdXNpZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eFgDbfks97Mq906D3A/giphy.gif")
        await interaction.followup.send(embed=loading_embed)

        if roll_index > 3:
            await sleep(3)
            secret_embed = discord.Embed(title="Rolling...???", color=0xffffff)
            secret_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW5yYjEwaGl2bzZ3cnNidDJtMnFscmkyNXY5MjVpZDZ4dXZpMTNkeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FJM4c4RYkb72qvAcBt/giphy.gif")
            await interaction.edit_original_response(embed=secret_embed)

        await sleep(roll_time)

        result = discord.Embed(
            title="You Rolled:",
            description=f"**{name_part}** with the probability of **{prob_part}**\nItem used: **{item_name_used}**",
            color=0xffffff,
        )
        if active:
            result.add_field(name="Premium Perk:", value="**x2 Luck**")
        result.set_image(url=ROLL_GIFS[roll_index])
        result.set_footer(text=f"Rolled by {interaction.user}", icon_url=interaction.user.avatar)

        await interaction.edit_original_response(embed=result)

    # ──────────────────────────────────────────────────────
    #  /flex
    # ──────────────────────────────────────────────────────

    @gacha.command(name="flex", description="Show a member's gacha stats")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.user.id))
    async def flex(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        if member is None:
            member = interaction.user
        await interaction.response.defer()
        await _flex_response(interaction, member, ephemeral=True)

    # ──────────────────────────────────────────────────────
    #  /inventory
    # ──────────────────────────────────────────────────────

    @gacha.command(name="inventory", description="Show a member's inventory")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.user.id))
    @app_commands.choices(type=[
        discord.app_commands.Choice(name='Rolls', value=1),
        discord.app_commands.Choice(name="Items", value=2),
    ])
    async def inventory(self, interaction: discord.Interaction, member: Optional[discord.Member], type: discord.app_commands.Choice[int]):
        if member is None:
            member = interaction.user

        embed = discord.Embed(
            title=f"{member}'s {type.name} Inventory",
            description="Items shown are virtual items,\nand could not possibly resell or trade with real items.",
            color=0xffffff,
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        data = await _get_user(member.id)

        if data is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Inventory Not Found",
                    description="This user does not have an inventory yet.",
                    color=0xffffff,
                ),
                ephemeral=True,
            )
            return

        inventory = data.get("inventory", {})

        if not inventory:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Inventory Not Found",
                    description="This user has no inventory data.",
                    color=0xffffff,
                ),
                ephemeral=True,
            )
            return

        if type.name == "Rolls":
            found_any = False
            for rarity_name in ROLL_NAMES:
                amount = inventory.get(rarity_name, 0)
                if amount > 0:
                    found_any = True
                    embed.add_field(
                        name=f"🤍 {rarity_name}",
                        value=f"> Amount: **{amount}**",
                        inline=True,
                    )
            if not found_any:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=f"{member} has no rolls to show.",
                        description="This user has no roll inventory.",
                        color=0xffffff,
                    ),
                )
                return

        elif type.name == "Items":
            join_item = ""
            for item_name in ITEMS:
                amount = inventory.get(item_name, 0)
                if amount > 0:
                    join_item += f"> {item_name} **(x{amount})**\n"
            if join_item:
                embed.add_field(
                    name="🤍 Craftable Items",
                    value=join_item,
                    inline=False,
                )
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=f"{member} has no items to show.",
                        description="This user has no items.\nIf this is you, you can start collecting items by running /roll",
                        color=0xffffff,
                    ),
                )
                return

        embed.set_footer(
            text="Equinox Inventory",
            icon_url=interaction.user.display_avatar.url,
        )
        await interaction.response.send_message(embed=embed)

    # ──────────────────────────────────────────────────────
    #  /shop
    # ──────────────────────────────────────────────────────

    @gacha.command(name="shop", description="Show the gacha shop")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def shop(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Equinox's Gacha Shop",
            description="Items shown are virtual items,\nand could not possibly resell or trade with real items.",
            color=0xffffff,
        )

        for item_name in ITEMS:
            requirements, amounts = CRAFTING_RECIPES[item_name]
            ingredients = ", ".join(f"**{a} {r}**" for r, a in zip(requirements, amounts))
            effects = ITEM_EFFECTS[item_name]
            _, mult, _ = effects
            embed.add_field(
                name=f"🤍 {item_name}",
                value=f"> Ingredients: {ingredients}\n> Stats: x{mult} Lucky",
                inline=True,
            )

        await interaction.response.send_message(embed=embed)

    # ──────────────────────────────────────────────────────
    #  /daily
    # ──────────────────────────────────────────────────────

    @gacha.command(name="daily", description="Daily chest of potions")
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.user.id))
    async def daily(self, interaction: discord.Interaction):
        from state import BuyPremium, is_premium, refresh

        refresh()
        active = False
        try:
            active, tier, expires = await is_premium(interaction.user.id)
        except Exception as exc:
            log.warning("is_premium check failed in daily: %s", exc)

        if not active:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="You are being restricted",
                    description="Daily command is only available to our elite users.\nConsider buying our useful premium with lots of perks?\nUse </help:1242738769099231302> to check out our premium perks.",
                    color=0xffffff,
                ),
                view=BuyPremium(),
            )
            return

        data = await _ensure_user(interaction.user.id)

        item_list = ["Fortune Drink"] * 9 + ["Witch's Potion"] * 6 + ["Divine Fluid"] * 4 + ["Angel Dust"] * 3 + ["Me When Im Lucky"] * 2
        daily_items = [random.choice(item_list) for _ in range(3)]

        inv = data["inventory"]
        for di in daily_items:
            inv[di] = inv.get(di, 0) + 1

        _mark_dirty(interaction.user.id)

        lines = "\n".join(f"x1 **{daily_items[j]}**" for j in range(3))
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Daily Chest",
                description=f"You received:\n{lines}",
                color=0xffffff,
            ),
        )

    # ──────────────────────────────────────────────────────
    #  /craft
    # ──────────────────────────────────────────────────────

    @gacha.command(name="craft", description="Craft an item")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.choices(item=[
        discord.app_commands.Choice(name='Fortune Drink', value=1),
        discord.app_commands.Choice(name="Witch's Potion", value=2),
        discord.app_commands.Choice(name='Divine Fluid', value=3),
        discord.app_commands.Choice(name='Angel Dust', value=4),
        discord.app_commands.Choice(name='Me When Im Lucky', value=5),
        discord.app_commands.Choice(name='Touch of Divinity', value=6),
        discord.app_commands.Choice(name='Trio Charm', value=7),
    ])
    async def craft(self, interaction: discord.Interaction, item: discord.app_commands.Choice[int], amount: Optional[int] = 1):
        if amount <= 0:
            amount = 1

        requirements, required_amounts = CRAFTING_RECIPES.get(item.name, ([], []))

        data = await _ensure_user(interaction.user.id)
        inv = data["inventory"]

        missing_requirements = []
        for req, req_amt in zip(requirements, required_amounts):
            needed = req_amt * amount
            have = inv.get(req, 0)
            if have < needed:
                missing_requirements.append((req, needed - have))

        if missing_requirements:
            embed = discord.Embed(title="Error in Crafting", color=0xffffff)
            for req, missing in missing_requirements:
                embed.add_field(name=req, value=f"Missing: {missing}", inline=False)
            await interaction.response.send_message(embed=embed)
            return

        for req, req_amt in zip(requirements, required_amounts):
            needed = req_amt * amount
            inv[req] = inv.get(req, 0) - needed
            if inv[req] <= 0:
                del inv[req]

        inv[item.name] = inv.get(item.name, 0) + amount
        _mark_dirty(interaction.user.id)

        embed = discord.Embed(
            title="🤍 Successfully Crafted",
            description=f"Item crafted: {item.name} (x{amount})",
            color=0xffffff,
        )
        await interaction.response.send_message(embed=embed)


# ── Setup ──

async def setup(bot):
    await _init_database()
    _flush_task = bot.loop.create_task(_flush_loop())
    bot.tree.add_command(gacha_stats)
    cog = GachaCog(bot)
    cog.flush_task = _flush_task
    await bot.add_cog(cog)
