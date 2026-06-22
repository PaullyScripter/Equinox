import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional, Literal
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os
import aiohttp
from discord.utils import format_dt

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="auditlogsetup", description="Enable or disable audit logging.")
    @app_commands.checks.has_permissions(administrator=True)
    # @app_commands.describe(state="Turn audit logging on or off")
    async def auditlogsetup(self, interaction: discord.Interaction, state: Literal["on", "off"]):
        if not interaction.user.guild_permissions.administrator:
            import sys as _sys
            load_audit_config = _sys.modules["__main__"].load_audit_config
            save_audit_config = _sys.modules["__main__"].save_audit_config
            await interaction.response.send_message("You need admin permissions.", ephemeral=True)
            return

        config = load_audit_config()
        gid = str(interaction.guild_id)

        if gid not in config:
            config[gid] = {}

        config[gid]["enabled"] = state == "on"
        save_audit_config(config)

        await interaction.response.send_message(f"Audit logging has been turned **{state}**.", ephemeral=True)


    @app_commands.command(name="auditlogchannel", description="Set a channel to receive audit log entries.")
    @app_commands.checks.has_permissions(administrator=True)
    # @app_commands.describe(channel="Channel to send audit logs to")
    async def auditlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not interaction.user.guild_permissions.administrator:
            import sys as _sys
            load_audit_config = _sys.modules["__main__"].load_audit_config
            save_audit_config = _sys.modules["__main__"].save_audit_config
            await interaction.response.send_message("You need admin permissions.", ephemeral=True)
            return

        config = load_audit_config()
        gid = str(interaction.guild_id)

        if gid not in config:
            config[gid] = {}

        config[gid]["channel"] = channel.id
        save_audit_config(config)

        await interaction.response.send_message(f"Audit log channel set to {channel.mention}.", ephemeral=True)


    @app_commands.command(name="auditlogdownload", description="Download server audit logs for the past X days.")
    @app_commands.checks.has_permissions(administrator=True)
    # @app_commands.describe(duration="Number of days (1-7)")
    async def auditlogdownload(self, interaction: discord.Interaction, duration: app_commands.Range[int, 1, 7]):
        config = load_audit_config()
        import sys as _sys
        load_audit_config = _sys.modules["__main__"].load_audit_config
        read_audit_log = _sys.modules["__main__"].read_audit_log
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



    @app_commands.command(name="scam_enable", description="Enable Anti-Scam in this channel (log channel required)")
    async def scam_enable(self, interaction: discord.Interaction):
        if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
        import sys as _sys
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
        cfg = get_guild_cfg(interaction.guild_id)
        if not cfg.get("log_channel_id"): return await interaction.response.send_message("Set a **log channel** first with `/set_log_channel`.", ephemeral=True)
        chans = set(cfg.get("scam_channels") or []); chans.add(interaction.channel_id)
        update_guild_cfg(interaction.guild_id, scam_channels=sorted(chans))
        await interaction.response.send_message(embed=embed_basic("Scam Shield Enabled", f"Active in {interaction.channel.mention}", COLOR_OK), ephemeral=True)


    @app_commands.command(name="scam_disable", description="Disable Anti-Scam in this channel")
    async def scam_disable(self, interaction: discord.Interaction):
        if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
        import sys as _sys
        COLOR_WARN = _sys.modules["__main__"].COLOR_WARN
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
        cfg = get_guild_cfg(interaction.guild_id)
        chans = set(cfg.get("scam_channels") or []); chans.discard(interaction.channel_id)
        update_guild_cfg(interaction.guild_id, scam_channels=sorted(chans))
        await interaction.response.send_message(embed=embed_basic("Scam Shield Disabled", f"Disabled in {interaction.channel.mention}", COLOR_WARN), ephemeral=True)


    @app_commands.command(name="codehelper_enable", description="Enable Inline Code Helper in this channel")
    async def codehelper_enable(self, interaction: discord.Interaction):
        if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
        import sys as _sys
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
        cfg = get_guild_cfg(interaction.guild_id)
        chans = set(cfg.get("codehelper_channels") or []); chans.add(interaction.channel_id)
        update_guild_cfg(interaction.guild_id, codehelper_channels=sorted(chans))
        await interaction.response.send_message(embed=embed_basic("Code Helper Enabled", f"Active in {interaction.channel.mention}", COLOR_OK), ephemeral=True)


    @app_commands.command(name="codehelper_disable", description="Disable Inline Code Helper in this channel")
    async def codehelper_disable(self, interaction: discord.Interaction):
        if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
        import sys as _sys
        COLOR_WARN = _sys.modules["__main__"].COLOR_WARN
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
        cfg = get_guild_cfg(interaction.guild_id)
        chans = set(cfg.get("codehelper_channels") or []); chans.discard(interaction.channel_id)
        update_guild_cfg(interaction.guild_id, codehelper_channels=sorted(chans))
        await interaction.response.send_message(embed=embed_basic("Code Helper Disabled", f"Disabled in {interaction.channel.mention}", COLOR_WARN), ephemeral=True)


    @app_commands.command(name="set_log_channel", description="Set a channel for scam logs (mandatory for Scam Shield)")
    # @app_commands.describe(channel="Select a channel to receive scam logs")
    async def set_log_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
        import sys as _sys
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
        update_guild_cfg(interaction.guild_id, log_channel_id=channel.id)
        await interaction.response.send_message(embed=embed_basic("Log Channel Set", f"Logs → {channel.mention}", COLOR_OK), ephemeral=True)

                                     

    @app_commands.command(name="allowlist_phrase_add", description="Allow this exact phrase (no links required)")
    # @app_commands.describe(phrase="Exact phrase to allow (it will be normalized)")
    async def allowlist_phrase_add(self, interaction: discord.Interaction, phrase: str):
        if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
        import sys as _sys
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        normalize_phrase = _sys.modules["__main__"].normalize_phrase
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
        cfg = get_guild_cfg(interaction.guild_id); phrases = set(cfg.get("phrase_allowlist") or [])
        phrases.add(normalize_phrase(phrase)); update_guild_cfg(interaction.guild_id, phrase_allowlist=sorted(phrases))
        await interaction.response.send_message(embed=embed_basic("Phrase allowlisted", f"“{phrase}”", COLOR_OK), ephemeral=True)


    @app_commands.command(name="allowlist_phrase_remove", description="Remove a phrase from the allowlist")
    # @app_commands.describe(phrase="Exact phrase to remove (normalized)")
    async def allowlist_phrase_remove(self, interaction: discord.Interaction, phrase: str):
        if not admin_or_manage_guild(interaction): return await interaction.response.send_message("Need **Manage Server** or **Admin**.", ephemeral=True)
        import sys as _sys
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        normalize_phrase = _sys.modules["__main__"].normalize_phrase
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
        cfg = get_guild_cfg(interaction.guild_id); phrases = set(cfg.get("phrase_allowlist") or [])
        norm = normalize_phrase(phrase)
        if norm in phrases: phrases.remove(norm); update_guild_cfg(interaction.guild_id, phrase_allowlist=sorted(phrases))
        await interaction.response.send_message(embed=embed_basic("Phrase removed", f"“{phrase}”", COLOR_OK), ephemeral=True)


    @app_commands.command(name="allowlist_phrase_list", description="List allowlisted phrases")
    async def allowlist_phrase_list(self, interaction: discord.Interaction):
        cfg = get_guild_cfg(interaction.guild_id); phrases = cfg.get("phrase_allowlist") or []
        import sys as _sys
        COLOR_INFO = _sys.modules["__main__"].COLOR_INFO
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        text = "\n".join(f"• {p}" for p in phrases) or "No phrases."
        await interaction.response.send_message(embed=embed_basic("Phrase Allowlist", text, COLOR_INFO), ephemeral=True)

                     

    @app_commands.command(name="scan_test", description="Test the scam scanner against custom text")
    # @app_commands.describe(text="The text to scan (paste your message here)")
    async def scan_test(self, interaction: discord.Interaction, text: str):
        cfg = get_guild_cfg(interaction.guild_id)
        import sys as _sys
        COLOR_INFO = _sys.modules["__main__"].COLOR_INFO
        embed_basic = _sys.modules["__main__"].embed_basic
        extract_domains = _sys.modules["__main__"].extract_domains
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        scan_message_for_scams = _sys.modules["__main__"].scan_message_for_scams
        domains = extract_domains(text); reasons = scan_message_for_scams(text, cfg)
        e = embed_basic("Scan Test", "", COLOR_INFO)
        e.add_field(name="Domains parsed", value=", ".join(domains) or "—", inline=False)
        e.add_field(name="Reasons", value="\n".join(f"• {r}" for r in reasons) or "—", inline=False)
        await interaction.response.send_message(embed=e, ephemeral=True)


    @app_commands.command(name="lint", description="Check Python code for syntax errors (paste code here)")
    # @app_commands.describe(code="Your Python code (paste up to ~1800 chars)")
    async def lint(self, interaction: discord.Interaction, code: str):
        ok, detail = try_python_syntax_check(code)
        import sys as _sys
        COLOR_BAD = _sys.modules["__main__"].COLOR_BAD
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        embed_basic = _sys.modules["__main__"].embed_basic
        try_python_syntax_check = _sys.modules["__main__"].try_python_syntax_check
        e = embed_basic("Python Syntax Check" if ok else "Python Syntax Error", ("✅ " if ok else "❌ ") + detail, COLOR_OK if ok else COLOR_BAD)
        e.add_field(name="Excerpt", value=f"```py\n{code[:800]}\n```", inline=False)
        await interaction.response.send_message(embed=e, ephemeral=True)


    @app_commands.command(name="debug_safety", description="Diagnose readiness & config")
    async def debug_safety(self, interaction: discord.Interaction):
        cfg = get_guild_cfg(interaction.guild_id)
        import sys as _sys
        COLOR_INFO = _sys.modules["__main__"].COLOR_INFO
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        has_mc = getattr(self.bot.intents, "message_content", False)
        has_mem = getattr(self.bot.intents, "members", False)
        lines = [
            f"• message_content intent: **{'Yes' if has_mc else 'No'}**",
            f"• members intent: **{'Yes' if has_mem else 'No'}**",
            f"• Scam channels: {', '.join(f'<#{c}>' for c in (cfg.get('scam_channels') or [])) or 'None'}",
            f"• Code-helper channels: {', '.join(f'<#{c}>' for c in (cfg.get('codehelper_channels') or [])) or 'None'}",
            f"• Log channel set: **{'Yes' if cfg.get('log_channel_id') else 'No'}**",
        ]
        await interaction.response.send_message(embed=embed_basic("Debug", "\n".join(lines), COLOR_INFO), ephemeral=True)


    @app_commands.command(name="whitelisted_phrase",
                         description="List, inspect, add, or remove whitelisted phrases (logged via 'Not a Scam'). Admin only.")
    # @app_commands.describe(phrase="Optional phrase to inspect/add/remove (normalization applied)", action="Optional: add or remove the phrase")
    async def whitelisted_phrase(
        self,
        interaction: discord.Interaction,
        phrase: Optional[str] = None,
        action: Optional[Literal["add","remove"]] = None
    ):
           
        import sys as _sys
        COLOR_INFO = _sys.modules["__main__"].COLOR_INFO
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        COLOR_WARN = _sys.modules["__main__"].COLOR_WARN
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        normalize_phrase = _sys.modules["__main__"].normalize_phrase
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
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


    @app_commands.command(name="scam_whitelist", description="Add/remove users or roles from the scam shield whitelist, or list all")
    # @app_commands.describe(user="Optional user to add/remove from the whitelist", role="Optional role to add/remove from the whitelist", action="Choose add or remove (optional)")
    async def scam_whitelist(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.User] = None,
        role: Optional[discord.Role] = None,
        action: Optional[Literal["add","remove"]] = None
    ):
           
        import sys as _sys
        COLOR_INFO = _sys.modules["__main__"].COLOR_INFO
        COLOR_OK = _sys.modules["__main__"].COLOR_OK
        COLOR_WARN = _sys.modules["__main__"].COLOR_WARN
        admin_or_manage_guild = _sys.modules["__main__"].admin_or_manage_guild
        embed_basic = _sys.modules["__main__"].embed_basic
        get_guild_cfg = _sys.modules["__main__"].get_guild_cfg
        update_guild_cfg = _sys.modules["__main__"].update_guild_cfg
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

                                                                     

    @app_commands.command(name="status", description="Show current security & code-helper configuration for this server")
    async def status(self, interaction: discord.Interaction):
        import sys as _sys
        _m = _sys.modules["__main__"]
        get_guild_cfg = _m.get_guild_cfg
        embed_basic = _m.embed_basic
        COLOR_INFO = _m.COLOR_INFO
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

    @app_commands.command(
        name="youngest",
        description="Show the youngest account and list all accounts younger than a duration (e.g., 1m, 1y, 1d, 30min)"
    )
    async def youngest(self, interaction: discord.Interaction, duration: str):
        import sys as _sys
        _m = _sys.modules["__main__"]
        parse_duration_to_timedelta = _m.parse_duration_to_timedelta
        fmt_discord_time = _m.fmt_discord_time
        _chunk_lines = _m._chunk_lines
        YoungestView = _m.YoungestView
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

        under = []
        youngest_tuple = None

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


async def setup(bot):
    await bot.add_cog(SecurityCog(bot))
