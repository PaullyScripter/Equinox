import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    channel = app_commands.Group(name="channel", description="Channel management commands")
    user = app_commands.Group(name="user", description="User management commands")

    @channel.command(name="slowmode", description="Set slowmode for current channel. (Manage channels required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    # @app_commands.describe(slowmode="Set slowmode in second")
    async def slowmode(self, interaction: discord.Interaction, slowmode: int):
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


    @channel.command(name="lockdown", description="Lockdown a channel, not allowing members to chat. (Manage channels required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def lockdown(self, interaction: discord.Interaction):
      await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False, add_reactions=False)
      await interaction.response.send_message(embed=discord.Embed(title=f"Successfully lockdown {interaction.channel.mention}", color=0xffffff))


    @channel.command(name="unlockdown", description="Unlockdown a channel, allows members to chat. (Manage channels required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def unlockdown(self, interaction: discord.Interaction):
      await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True, add_reactions=True)
      await interaction.response.send_message(embed=discord.Embed(title=f"Successfully unlock {interaction.channel.mention}", color=0xffffff))


    @channel.command(name="private", description="Private a channel, not allowing members to see. (Manage channels required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def private(self, interaction: discord.Interaction):
      await interaction.channel.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)
      await interaction.response.send_message(embed=discord.Embed(title=f"Successfully private {interaction.channel.mention}", color=0xffffff))


    @channel.command(name="unprivate", description="Unprivate a channel, allows members to see. (Manage channels required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def unprivate(self, interaction: discord.Interaction):
      await interaction.channel.set_permissions(interaction.guild.default_role, read_messages=True, send_messages=True)
      await interaction.response.send_message(embed=discord.Embed(title=f"Successfully unprivate {interaction.channel.mention}", color=0xffffff))


    @user.command(name="kick", description="Kick a member. (Kick members required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.checks.bot_has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str]):
      bot_user = interaction.guild.get_member(self.bot.user.id)
      clienttop_role = bot_user.top_role
      if interaction.user.id == interaction.guild.owner_id:
        await interaction.guild.kick(user=member, reason=reason)
        await interaction.response.send_message(embed=discord.Embed(title=f"Successfully kicked {member.name}", description=f"**Reason:** {reason}", color=0xffffff))
      else:
        if interaction.user.top_role <= member.top_role or clienttop_role <= member.top_role or interaction.user.id == member.id or member == interaction.guild.owner:
          await interaction.response.send_message(embed=discord.Embed(title="Failed to kick, please check if the member's hierchy is:", description="> Higher than yours\n> Equals to yours\n> Higher than mine\n> Equals to mine\n> Is you\n> Is server's owner", color=0xffffff))
        else:
          await interaction.guild.kick(user=member, reason=reason)
          await interaction.response.send_message(embed=discord.Embed(title=f"Successfully kicked {member.name}", description=f"**Reason:** {reason}", color=0xffffff))


    @user.command(name="unban", description="Unban a user. (Ban members required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, memberid: str):
        try:
            uid = int(memberid)
        except ValueError:
            return await interaction.response.send_message(embed=discord.Embed(title="Invalid ID", description="User ID must be a numeric Discord ID.", color=0xffffff))
        user = self.bot.get_user(uid)
        if user is None:
            try:
                user = await self.bot.fetch_user(uid)
            except discord.NotFound:
                return await interaction.response.send_message(embed=discord.Embed(title="User not found", description=f"No user with ID `{memberid}` exists.", color=0xffffff))
        await interaction.guild.unban(user)
        await interaction.response.send_message(embed=discord.Embed(title=f"Successfully unban {user}!", color=0xffffff))


    @user.command(name="ban", description="Ban a member. (Ban members required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: Optional[str]):
      bot_user = interaction.guild.get_member(self.bot.user.id)
      from state import UnbanButton
      clienttop_role = bot_user.top_role
      if interaction.user.id == interaction.guild.owner_id:
        await interaction.guild.ban(user=member, reason=reason)
        view=UnbanButton(member.id)
        await interaction.response.defer()
        msg = await interaction.followup.send(embed=discord.Embed(title=f"Successfully banned {member.name}", description=f"**Reason:** {reason}", color=0xffffff), view=view)
        view.message = msg
      else:
        if interaction.user.top_role <= member.top_role or clienttop_role <= member.top_role or interaction.user.id == member.id or member == interaction.guild.owner:
          await interaction.response.send_message(embed=discord.Embed(title="Failed to ban, please check if the member's hierchy is:", description="> Higher than yours\n> Equals to yours\n> Higher than mine\n> Equals to mine\n> Is you\n> Is server's owner", color=0xffffff))
        else:
          await interaction.guild.ban(user=member, reason=reason)
          view=UnbanButton(member.id)
          await interaction.response.defer()
          msg = await interaction.followup.send(embed=discord.Embed(title=f"Successfully banned {member.name}", description=f"**Reason:** {reason}", color=0xffffff), view=view)
          view.message = msg



    @channel.command(name="clone", description="Clone current channel. (Manage channels required)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def clone(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel]):
      from state import CloneButton
      await interaction.response.defer()
      if channel == None:
        channel = interaction.channel
      view = CloneButton(interaction.user.id, channel)
      embed = discord.Embed(title="Cloning Caution ⚠️", description="```diff\nThe clone command allows you to either:\n+ Clone and delete channel\nor\n- Clone channel only\n```", color=0xffffff)
      embed.set_footer(text=f"Issued by {interaction.user} | Ignore to cancel", icon_url=interaction.user.avatar)
      msg = await interaction.followup.send(interaction.user.mention, embed=embed, view=view)
      view.message = msg


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
