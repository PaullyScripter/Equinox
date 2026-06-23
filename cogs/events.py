import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os

class EventsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        from state import ReactionRoleView, ScamFeedbackView, client, char1, read_json, write_json, load_data, init_db_pool
        await init_db_pool(min_size=1, max_size=5)
        await self.bot.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(type=discord.ActivityType.listening, name="/help me!")
        )
        if ScamFeedbackView:
            self.bot.add_view(ScamFeedbackView(action_id="dummy"))

               
        try:
            synced = await self.bot.tree.sync()
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

        self.bot.monthly_codes  = monthly_data.get("monthlycodes", [])
        self.bot.yearly_codes   = yearly_data.get("yearlycodes", [])
        self.bot.lifetime_codes = lifetime_data.get("lifetimecodes", [])

                                                          
        monthly_user_data = await asyncio.to_thread(read_json, "monthly_user")
        yearly_user_data  = await asyncio.to_thread(read_json, "yearly_user")
        self.bot.monthly_user = monthly_user_data.get("monthly_users", [])
        self.bot.yearly_user  = yearly_user_data.get("yearly_users", [])

                                                                               
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
            generate_codes("monthcode", "monthlycodes", self.bot.monthly_codes),
            generate_codes("yearlycode", "yearlycodes", self.bot.yearly_codes),
            generate_codes("lifetimecode", "lifetimecodes", self.bot.lifetime_codes),                                               
        )

                                                     

        print("Equinox is here!")

                                           
        data = load_data()
        if ReactionRoleView:
            for template_name, templates in data.items():
                for name, template in templates.items():
                    if template.get("roles"):
                        custom_id = f"reaction_role_dropdown:{name}"
                        view = ReactionRoleView(template['roles'], custom_id)
                        self.bot.add_view(view)




    @commands.Cog.listener()
    async def on_member_join(self, member):
      from state import load_autoping_channels, load_autorole
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
     

    @commands.Cog.listener()
    async def on_member_remove(self, member):
      if member.guild.id == 1243501449879752775:
        if not member.bot:
          guild = member.guild
          channel = guild.get_channel(1245008595066814474)
          await channel.send(embed=discord.Embed(title=f"Bye {member} 💀", description=f"> You have been here since: {member.joined_at.strftime('%A, %B %d %Y')}\n> {guild} now has {str(guild.member_count)} member(s)", color=0xffffff))


    @commands.Cog.listener()
    async def on_app_command_completion(
        self,
        interaction: discord.Interaction,
        command: discord.app_commands.Command
    ):
        from state import _log_command
        if interaction.user and not interaction.user.bot:
            _log_command(interaction.user.id, command.qualified_name)



    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        from state import load_server_data, save_server_data, PREFIX, _log_command, load_audit_config, append_audit_log, get_guild_cfg, is_scam_whitelisted, scan_message_for_scams, load_actions, save_actions, extract_domains, embed_basic, COLOR_BAD, COLOR_WARN, COLOR_OK, CODEBLOCK_CLOSED_RE, CODEBLOCK_UNTERMINATED_RE, try_python_syntax_check, ScamFeedbackView

        if message.author.bot:
            return

        if self.bot.user.mention in message.content.split():
            embed = discord.Embed(title=f"Equinox 🤍", description=f"I operate with slash commands, type **/** to see all available commands.", color=0xffffff)
            await message.reply(embed=embed)

        if message.guild is None:
            return

        guild_id = str(message.guild.id)

        if "@everyone" in message.content or "@here" in message.content:
            config = load_audit_config()
            gid = str(message.guild.id)
            if config.get(gid, {}).get("enabled", False):
                timestamp = datetime.now(timezone.utc)
                log_entry = f"{timestamp.isoformat()} | Action: everyone_ping | By: {message.author} | Channel: {message.channel.name}"
                append_audit_log(message.guild.id, log_entry)
                channel_id = config[gid].get("channel")
                if channel_id:
                    log_channel = message.guild.get_channel(channel_id)
                    if log_channel:
                        embed = discord.Embed(title="Audit Log Entry", color=0xffffff, timestamp=timestamp)
                        embed.set_author(name=message.author.name, icon_url=message.author.display_avatar.url)
                        embed.add_field(name="Action", value="Mentioning @everyone or @here", inline=False)
                        embed.add_field(name="Executor", value=f"{message.author} ({message.author.id})", inline=False)
                        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
                        embed.add_field(name="Message", value=message.content[:1000], inline=False)
                        embed.add_field(name="Time", value=format_dt(timestamp, style='F'), inline=False)
                        await log_channel.send(embed=embed)

        cfg = get_guild_cfg(message.guild.id)

        if cfg.get("log_channel_id") and message.channel.id in set(cfg.get("scam_channels") or []):
            if is_scam_whitelisted(message.author, cfg):
                pass
            else:
                reasons = scan_message_for_scams(message.content or "", cfg)
                try:
                    for em in message.embeds:
                        if em.title: reasons += scan_message_for_scams(em.title, cfg)
                        if em.description: reasons += scan_message_for_scams(em.description, cfg)
                        for f in em.fields: reasons += scan_message_for_scams(f"{f.name or ''} {f.value or ''}", cfg)
                except Exception:
                    pass
                s, ordered = set(), []
                for r in reasons:
                    if r not in s: ordered.append(r); s.add(r)
                reasons = ordered
                if reasons:
                    deleted = False
                    try:
                        await message.delete(); deleted = True
                    except Exception:
                        pass
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
                    except Exception:
                        pass
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

        data = load_server_data(guild_id)
        if data and data.get("status") == "enabled":
            if str(message.channel.id) not in data.get("blacklisted_channels", []):
                user_id = str(message.author.id)
                if user_id not in data.get("opted_out_users", []):
                    data["users"][user_id] = data["users"].get(user_id, 0) + 1
                    save_server_data(guild_id, data)

        if message.content.startswith(PREFIX):
            cmd_name = message.content[len(PREFIX):].split()[0].lower()
            _log_command(message.author.id, cmd_name)

        await self.bot.process_commands(message)


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
      channel = self.bot.get_channel(1242633669890277456)
      embed=discord.Embed(title=f"{self.bot.user} was invited to a new guild!", description=f"```js\nGuild Name: {guild}\nGuild Membercount: {guild.member_count}\nClient Guilds: {len(self.bot.guilds)}\nClient Users: {len(set(self.bot.get_all_members()))}\n```", color =0xffffff)
      embed.set_thumbnail(url=guild.icon)
      msg = await channel.send(embed=embed)


    @commands.Cog.listener()
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        from state import load_audit_config, append_audit_log
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


async def setup(bot):
    await bot.add_cog(EventsCog(bot))
