import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os
from discord.utils import format_dt

from cogs.giveaway_views import (
    GiveawayView, ensure_guild_json_file, load_guild_giveaways, save_guild_giveaways
)

class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="giveaway_manage", description="Reroll or finalize a giveaway by message ID.")
    @app_commands.choices(action=[
        app_commands.Choice(name="Reroll", value="reroll"),
        app_commands.Choice(name="Finalize", value="finalize"),
    ])
    # @app_commands.describe(message_id="The message ID of the giveaway")
    async def giveaway_manage(
        self,
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

        view = GiveawayView(self.bot, giveaway_data)
        if action.value == "reroll":
            await view.reroll(interaction)
        elif action.value == "finalize":
            await view.finalize_winner(interaction)






    @app_commands.command(name="giveaway_console", description="View all giveaways in this server.")
    async def giveaway_console(self, interaction: discord.Interaction):
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
                now = datetime.now(timezone.utc)
                time_left = f"<t:{int(end_time.timestamp())}:R>"
                ends_on = f"<t:{int(end_time.timestamp())}:F>"

                                                             
                stored_status = g.get("status", "On Going / Winner not revealed")

                if now >= end_time:
                    status = "Ended"
                elif stored_status == "On Going / Winner revealed":
                    status = "Ongoing | Winner revealed"
                else:
                    status = "Ongoing | Winner not revealed"

                channel_id = g.get("channel_id", interaction.channel.id)
                msg_url = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"

                                 
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


    @app_commands.command(name='giveaway', description='Create a giveaway')
    # @app_commands.describe(duration="Giveaway's duration (e.g., 1s, 2m, 3h, 4d)", prize="Giveaway's prize", hosts="Comma-separated list of host IDs (userID, roleID)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def giveaway(self, interaction: discord.Interaction, duration: str, prize: str, hosts: str = None):
        import sys as _sys
        is_premium = _sys.modules["__main__"].is_premium
        BuyPremium = _sys.modules["__main__"].BuyPremium
        await interaction.response.defer()

        guild_id = interaction.guild.id
        ensure_guild_json_file(guild_id)
        giveaways = load_guild_giveaways(guild_id)

        active, tier, expires = await is_premium(interaction.user.id)
        active_giveaways = [g for g in giveaways.values() if g.get("message_id")]

        if not active and len(active_giveaways) >= 3:
            embed = discord.Embed(
                title="You are being restricted",
                description="Normal servers can only host **3 active giveaways**.\n"
                            "The server owner is **not a premium user**.\n\n"
                            "Consider finalizing an existing giveaway using </giveaway_manage:1370458427100368898>\n"
                            "or upgrade to premium.",
                color=0xffffff
            )

            view = BuyPremium()
            for index, g in enumerate(active_giveaways, start=1):
                embed.add_field(
                    name=f"Giveaway {index}: {g['message_id']}",
                    value="",
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
            "guild_id": guild_id,
            "channel_id": interaction.channel.id
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

        view = GiveawayView(self.bot, giveaway_data)
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


async def setup(bot):
    await bot.add_cog(GiveawayCog(bot))
