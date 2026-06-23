import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional, Literal
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os
from discord.utils import format_dt
import aiohttp

class PresenceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server_member_activity", description="View members by presence status or stats.")
    @app_commands.choices(status=[
        app_commands.Choice(name="Online", value="online"),
        app_commands.Choice(name="Do Not Disturb", value="dnd"),
        app_commands.Choice(name="Idle", value="idle"),
        app_commands.Choice(name="Invisible/Offline", value="invisible"),
        app_commands.Choice(name="Stats", value="stats"),
    ])
    async def server_member_activity(self, interaction: discord.Interaction, status: app_commands.Choice[str]):
        guild = interaction.guild
        from state import PRIVACY_SET, PresencePaginator
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


    @app_commands.command(name="top_games", description="Show the top games currently being played in this server.")
    async def top_games(self, interaction: discord.Interaction):
        from state import PRIVACY_SET
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


    @app_commands.command(name="now_playing", description="See what a user is currently playing or doing.")
    # @app_commands.describe(user="The user to check.")
    async def now_playing(self, interaction: discord.Interaction, user: discord.Member):
        from state import PRIVACY_SET, STATUS_PRIVACY_SET
        if user.id in PRIVACY_SET or user.id in STATUS_PRIVACY_SET:
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


    @app_commands.command(
        name="role_presence_stats",
        description="View presence stats for a specific role."
    )
    async def role_presence_stats(self, 
        interaction: discord.Interaction,
        role: discord.Role,
    ):
        from state import PRIVACY_SET
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message(
                "This command must be used in a server.", ephemeral=True
            )

        # Respect your existing privacy set
        tracked = [m for m in guild.members if not m.bot and m.id not in PRIVACY_SET]

        members = [m for m in tracked if role in m.roles]
        if not members:
            return await interaction.response.send_message(
                f"No tracked members have the role {role.mention}.",
                ephemeral=True
            )

        online = sum(1 for m in members if m.status == discord.Status.online)
        idle = sum(1 for m in members if m.status == discord.Status.idle)
        dnd = sum(1 for m in members if m.status == discord.Status.dnd)
        off = sum(1 for m in members if m.status == discord.Status.offline)

        embed = discord.Embed(
            title=f"Presence Stats per Role – {role.name}",
            color=0xffffff
        )
        embed.add_field(name="Online", value=str(online))
        embed.add_field(name="Idle", value=str(idle))
        embed.add_field(name="DND", value=str(dnd))
        embed.add_field(name="Offline", value=str(off))
        embed.set_footer(text="Users who opted out of presence tracking are excluded.")

        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="privacy", description="Manage your privacy and tracking settings")
    async def privacy(self, interaction: discord.Interaction):
        uid = interaction.user.id
        gid = interaction.guild.id if interaction.guild else None
        embed = PrivacyView.build_embed(uid, gid, None)
        view = PrivacyView(uid, gid)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(
        name="server_member_stats",
        description="Advanced member analytics: overview, top roles, and age graph."
    )
    async def server_member_stats(self, interaction: discord.Interaction):
        from state import admin_or_manage_guild, MemberStatsView, build_overview_embed
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


class PrivacySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Presence Tracking", value="presence", description="Visibility in server presence commands", emoji="👤"),
            discord.SelectOption(label="Status & Activity", value="status", description="Visibility of your status in /userinfo", emoji="🔄"),
            discord.SelectOption(label="Message Tracking", value="messages", description="Whether your messages are counted", emoji="💬"),
        ]
        super().__init__(placeholder="Select a tracking category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_category = self.values[0]
        self.view.update_buttons()
        embed = self.view._current_embed()
        await interaction.response.edit_message(embed=embed, view=self.view)


class PrivacyView(discord.ui.View):
    def __init__(self, user_id, guild_id):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.guild_id = guild_id
        self.selected_category = None
        self.add_item(PrivacySelect())
        self.enable_button.disabled = True
        self.disable_button.disabled = True

    @staticmethod
    def build_embed(user_id, guild_id, selected_category):
        from state import load_privacy_settings, load_server_data
        data = load_privacy_settings()
        uid = str(user_id)
        cats = data.get(uid, [])

        embed = discord.Embed(title="🔒 Privacy Controls", color=0xffffff)

        items = [
            ("presence", "Presence Tracking", "Visibility in server presence commands"),
            ("status", "Status & Activity", "Visibility of your status in /userinfo"),
        ]

        if guild_id:
            server_data = load_server_data(str(guild_id))
            opted_out_msgs = server_data.get("opted_out_users", []) if server_data else []
            msg_disabled = str(user_id) in opted_out_msgs
            items.append(("messages", "Message Tracking", "Whether your messages are counted on this server"))

        for cat_id, label, desc in items:
            if cat_id == "messages":
                disabled = msg_disabled
            else:
                disabled = cat_id in cats
            status_icon = "🔴" if disabled else "🟢"
            status_text = "Disabled" if disabled else "Enabled"
            sel = "➡️ " if cat_id == selected_category else ""
            embed.add_field(
                name=f"{sel}{status_icon} {label}",
                value=f"{status_text}\n> {desc}",
                inline=False
            )

        return embed

    def _current_embed(self):
        return PrivacyView.build_embed(self.user_id, self.guild_id, self.selected_category)

    def update_buttons(self):
        if not self.selected_category:
            self.enable_button.disabled = True
            self.disable_button.disabled = True
            return
        from state import load_server_data, load_privacy_settings
        uid = self.user_id

        if self.selected_category == "messages":
            if not self.guild_id:
                self.enable_button.disabled = True
                self.disable_button.disabled = True
                return
            server_data = load_server_data(str(self.guild_id))
            opted_out = server_data.get("opted_out_users", []) if server_data else []
            is_opted_out = str(uid) in opted_out
        else:
            data = load_privacy_settings()
            ustr = str(uid)
            opted_out_cats = data.get(ustr, [])
            is_opted_out = self.selected_category in opted_out_cats

        self.enable_button.disabled = not is_opted_out
        self.disable_button.disabled = is_opted_out

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.success, row=1)
    async def enable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        from state import load_server_data, save_server_data, load_privacy_settings, save_privacy_settings, reload_privacy_sets

        if self.selected_category == "messages":
            if not self.guild_id:
                return await interaction.response.send_message("❌ This setting is only available in a server.", ephemeral=True)
            server_data = load_server_data(str(self.guild_id))
            if not server_data:
                return await interaction.response.send_message("❌ Message counter has not been set up for this server.", ephemeral=True)
            opted_out = server_data.setdefault("opted_out_users", [])
            if str(self.user_id) in opted_out:
                opted_out.remove(str(self.user_id))
            save_server_data(str(self.guild_id), server_data)
        else:
            data = load_privacy_settings()
            ustr = str(self.user_id)
            if ustr not in data:
                data[ustr] = []
            if self.selected_category in data[ustr]:
                data[ustr].remove(self.selected_category)
            save_privacy_settings(data)
            reload_privacy_sets()

        embed = PrivacyView.build_embed(self.user_id, self.guild_id, None)
        await interaction.response.edit_message(embed=embed, view=PrivacyView(self.user_id, self.guild_id))
        await interaction.followup.send(f"✅ **{self.selected_category.replace('_', ' ').title()}** tracking has been enabled.", ephemeral=True)

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.danger, row=1)
    async def disable_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        from state import load_server_data, save_server_data, load_privacy_settings, save_privacy_settings, reload_privacy_sets

        if self.selected_category == "messages":
            if not self.guild_id:
                return await interaction.response.send_message("❌ This setting is only available in a server.", ephemeral=True)
            server_data = load_server_data(str(self.guild_id))
            if not server_data:
                return await interaction.response.send_message("❌ Message counter has not been set up for this server.", ephemeral=True)
            opted_out = server_data.setdefault("opted_out_users", [])
            if str(self.user_id) not in opted_out:
                opted_out.append(str(self.user_id))
            save_server_data(str(self.guild_id), server_data)
        else:
            data = load_privacy_settings()
            ustr = str(self.user_id)
            if ustr not in data:
                data[ustr] = []
            if self.selected_category not in data[ustr]:
                data[ustr].append(self.selected_category)
            save_privacy_settings(data)
            reload_privacy_sets()

        embed = PrivacyView.build_embed(self.user_id, self.guild_id, None)
        await interaction.response.edit_message(embed=embed, view=PrivacyView(self.user_id, self.guild_id))
        await interaction.followup.send(f"✅ **{self.selected_category.replace('_', ' ').title()}** tracking has been disabled.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(PresenceCog(bot))
