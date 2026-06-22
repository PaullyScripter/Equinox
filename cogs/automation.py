import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os

class AutomationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="autoping_whitelist", description="Manage auto-ping channels for new members.")
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="View", value="view")
    ])
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_messages=True)
    # @app_commands.describe(action="Add, remove, or view whitelist", channel="The channel to modify")
    async def autoping_whitelist(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        channel: discord.TextChannel = None
    ):
        import sys as _sys
        load_autoping_channels = _sys.modules["__main__"].load_autoping_channels
        save_autoping_channels = _sys.modules["__main__"].save_autoping_channels
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


    @app_commands.command(name="autorole", description="Manage the auto-role for new members.")
    # @app_commands.describe(action="Choose add, remove, or view", role="The role to assign")
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
        app_commands.Choice(name="Console", value="console")
    ])
    @app_commands.checks.has_permissions(manage_roles=True)
    async def autorole(self, interaction: discord.Interaction, action: app_commands.Choice[str], role: discord.Role = None):
        guild = interaction.guild
        import sys as _sys
        load_autorole = _sys.modules["__main__"].load_autorole
        remove_autorole = _sys.modules["__main__"].remove_autorole
        save_autorole = _sys.modules["__main__"].save_autorole
        autorole_id = load_autorole(guild.id)

        if action.value == "add":
            if not role:
                return await interaction.response.send_message("You must specify a role to add.", ephemeral=True)

            if autorole_id:
                return await interaction.response.send_message("Auto-role already set. Remove it first to change.", ephemeral=True)

                                      
            if interaction.user.id != guild.owner_id:
                if role >= interaction.user.top_role:
                    return await interaction.response.send_message("⚠️ You can't assign a role higher than or equal to your top role.", ephemeral=True)

            bot_member = guild.get_member(self.bot.user.id)
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


async def setup(bot):
    await bot.add_cog(AutomationCog(bot))
