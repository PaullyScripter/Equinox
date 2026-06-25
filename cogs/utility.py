import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional, Literal
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os
import qrcode
from PyDictionary import PyDictionary
from googletrans import Translator
import wikipedia
import aiohttp
import httpx
from io import BytesIO
from discord.utils import format_dt
from collections import deque, defaultdict
import uuid
import string
from discord.ext import tasks

@app_commands.context_menu(name="Translate")
async def app_translate(interaction: discord.Interaction, message: discord.Message):
    
    t = Translator()
    a = t.translate(message.content, dest='en')
    embe = discord.Embed(color = 0xffffff)
    sourcelang = googletrans.LANGUAGES[(a.src).lower()]
    embe.set_author(name="Equinox Translator", icon_url=interaction.client.user.avatar)
    embe.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/google-translate-xxl.png")
    embe.add_field(name=f"Original Text - {sourcelang.capitalize()}", value=message.content, inline=False)
    embe.add_field(name=f"Translated Text - None", value="Please choose your destination language below.", inline=False)
    embe.set_footer(text=f"Translated by {interaction.user}", icon_url=interaction.user.avatar)
    view = translateSelect(message.content, interaction.user.id, "None")
    await interaction.response.defer()
    msg = await interaction.followup.send(embed=embe, view=view)
    view.message = msg


# ---------------------------------------------------------------------------
# Embed Builder — modals, view, and command
# ---------------------------------------------------------------------------

class _AuthorModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Embed Author")
        self.view = view
        cur = view.embed.author
        self.name_inp = discord.ui.TextInput(
            label="Author Name",
            placeholder="e.g. Equinox Bot",
            required=False,
            max_length=256,
            default=cur.name or "",
        )
        self.icon_inp = discord.ui.TextInput(
            label="Author Icon URL",
            placeholder="https://example.com/icon.png",
            required=False,
            default=cur.icon_url or "",
        )
        self.add_item(self.name_inp)
        self.add_item(self.icon_inp)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name_inp.value.strip()
        icon = self.icon_inp.value.strip()
        if name:
            self.view.embed.set_author(name=name, icon_url=icon or None)
        else:
            self.view.embed.remove_author()
        await self.view.refresh(interaction)


class _TitleModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Embed Title")
        self.view = view
        self.inp = discord.ui.TextInput(
            label="Title",
            placeholder="Embed title",
            max_length=256,
            default=view.embed.title or "",
        )
        self.add_item(self.inp)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.inp.value.strip()
        self.view.embed.title = val or None
        await self.view.refresh(interaction)


class _DescriptionModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Embed Description")
        self.view = view
        self.inp = discord.ui.TextInput(
            label="Description",
            placeholder="Embed description",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=4000,
            default=view.embed.description or "",
        )
        self.add_item(self.inp)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.inp.value.strip()
        self.view.embed.description = val or None
        await self.view.refresh(interaction)


class _ColorModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Embed Color")
        self.view = view
        cur = view.embed.color
        default_hex = hex(cur.value)[2:].zfill(6) if cur and cur.value else "89b4fa"
        self.inp = discord.ui.TextInput(
            label="Color (hex, no #)",
            placeholder="89b4fa",
            max_length=6,
            min_length=6,
            default=default_hex,
        )
        self.add_item(self.inp)

    async def on_submit(self, interaction: discord.Interaction):
        raw = self.inp.value.strip()
        try:
            self.view.embed.color = discord.Color(int(raw, 16))
        except ValueError:
            await interaction.response.send_message(
                "Invalid hex color. Use 6 hex digits (e.g. `89b4fa`).",
                ephemeral=True,
            )
            return
        await self.view.refresh(interaction)


class _ImageModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Embed Image")
        self.view = view
        cur = view.embed.image
        self.inp = discord.ui.TextInput(
            label="Image URL",
            placeholder="https://example.com/image.png",
            required=False,
            default=cur.url if cur and cur.url else "",
        )
        self.add_item(self.inp)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.inp.value.strip()
        if val:
            self.view.embed.set_image(url=val)
        else:
            self.view.embed.set_image(url=None)
        await self.view.refresh(interaction)


class _ThumbnailModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Embed Thumbnail")
        self.view = view
        cur = view.embed.thumbnail
        self.inp = discord.ui.TextInput(
            label="Thumbnail URL",
            placeholder="https://example.com/thumb.png",
            required=False,
            default=cur.url if cur and cur.url else "",
        )
        self.add_item(self.inp)

    async def on_submit(self, interaction: discord.Interaction):
        val = self.inp.value.strip()
        if val:
            self.view.embed.set_thumbnail(url=val)
        else:
            self.view.embed.set_thumbnail(url=None)
        await self.view.refresh(interaction)


class _FooterModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Embed Footer")
        self.view = view
        cur = view.embed.footer
        self.text_inp = discord.ui.TextInput(
            label="Footer Text",
            placeholder="Footer text",
            required=False,
            max_length=2048,
            default=cur.text or "",
        )
        self.icon_inp = discord.ui.TextInput(
            label="Footer Icon URL",
            placeholder="https://example.com/icon.png",
            required=False,
            default=cur.icon_url or "",
        )
        self.add_item(self.text_inp)
        self.add_item(self.icon_inp)

    async def on_submit(self, interaction: discord.Interaction):
        text = self.text_inp.value.strip()
        icon = self.icon_inp.value.strip()
        if text:
            self.view.embed.set_footer(text=text, icon_url=icon or None)
        else:
            self.view.embed.remove_footer()
        await self.view.refresh(interaction)


class _FieldAddModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        n = len(view.embed.fields) + 1
        super().__init__(title=f"Add Field {n}")
        self.view = view
        self.name_inp = discord.ui.TextInput(
            label=f"Field {n} Name",
            placeholder="Field name",
            max_length=256,
        )
        self.val_inp = discord.ui.TextInput(
            label=f"Field {n} Value",
            placeholder="Field value",
            style=discord.TextStyle.paragraph,
            max_length=1024,
        )
        self.inline_inp = discord.ui.TextInput(
            label=f"Field {n} Inline",
            placeholder="y / n (default y)",
            max_length=3,
            required=False,
            default="y",
        )
        self.add_item(self.name_inp)
        self.add_item(self.val_inp)
        self.add_item(self.inline_inp)

    async def on_submit(self, interaction: discord.Interaction):
        name = self.name_inp.value.strip()[:256] or "—"
        val = self.val_inp.value.strip()[:1024] or "—"
        inline = self.inline_inp.value.strip().lower() in ("y", "yes")
        self.view.embed.add_field(name=name, value=val, inline=inline)
        await self.view.refresh(interaction)


class _FieldEditModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Edit Field")
        self.view = view
        self.num_inp = discord.ui.TextInput(
            label="Field Number",
            placeholder="1, 2, 3, ...",
            max_length=2,
        )
        self.name_inp = discord.ui.TextInput(
            label="New Name",
            placeholder="Field name",
            max_length=256,
            required=False,
        )
        self.val_inp = discord.ui.TextInput(
            label="New Value",
            placeholder="Field value",
            style=discord.TextStyle.paragraph,
            max_length=1024,
            required=False,
        )
        self.inline_inp = discord.ui.TextInput(
            label="Inline",
            placeholder="y / n (leave blank to keep)",
            max_length=3,
            required=False,
        )
        self.add_item(self.num_inp)
        self.add_item(self.name_inp)
        self.add_item(self.val_inp)
        self.add_item(self.inline_inp)

    async def on_submit(self, interaction: discord.Interaction):
        fields = self.view.embed.fields
        try:
            idx = int(self.num_inp.value.strip()) - 1
            if idx < 0 or idx >= len(fields):
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                f"Invalid field number. There are {len(fields)} fields.",
                ephemeral=True,
            )
            return

        name = self.name_inp.value.strip()
        val = self.val_inp.value.strip()
        inline = self.inline_inp.value.strip().lower()

        old = fields[idx]
        new_name = name[:256] if name else old.name
        new_val = val[:1024] if val else old.value
        new_inline = inline in ("y", "yes") if inline else old.inline

        self.view.embed.set_field_at(idx, name=new_name, value=new_val, inline=new_inline)
        await self.view.refresh(interaction)


class _FieldDeleteModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Delete Field")
        self.view = view
        self.num_inp = discord.ui.TextInput(
            label="Field Number to Delete",
            placeholder="1, 2, 3, ...",
            max_length=2,
        )
        self.add_item(self.num_inp)

    async def on_submit(self, interaction: discord.Interaction):
        fields = self.view.embed.fields
        try:
            idx = int(self.num_inp.value.strip()) - 1
            if idx < 0 or idx >= len(fields):
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                f"Invalid field number. There are {len(fields)} fields.",
                ephemeral=True,
            )
            return
        self.view.embed.remove_field(idx)
        await self.view.refresh(interaction)


class _SendToModal(discord.ui.Modal):
    def __init__(self, view: "EmbedBuilderView"):
        super().__init__(title="Send to Channel")
        self.view = view
        self.channel_inp = discord.ui.TextInput(
            label="Channel ID",
            placeholder="Paste the channel ID",
            max_length=20,
        )
        self.add_item(self.channel_inp)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            cid = int(self.channel_inp.value.strip())
        except ValueError:
            await interaction.response.send_message("Invalid channel ID.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(cid)
        if channel is None:
            await interaction.response.send_message("Channel not found.", ephemeral=True)
            return
        await channel.send(embed=self.view.embed)
        await interaction.response.send_message(
            f"Embed sent to {channel.mention}.", ephemeral=True
        )


class EmbedBuilderView(discord.ui.View):
    def __init__(self, embed: discord.Embed, user_id: int):
        super().__init__(timeout=600)
        self.embed = embed
        self.user_id = user_id

    async def refresh(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embed, view=self)

    # --- Select: choose an embed part to edit ---

    @discord.ui.select(
        placeholder="Choose an embed part…",
        options=[
            discord.SelectOption(label="Author", value="author", description="Author name + icon"),
            discord.SelectOption(label="Title", value="title", description="Set the embed title"),
            discord.SelectOption(label="Description", value="description", description="Set the description"),
            discord.SelectOption(label="Color", value="color", description="Change embed color (hex)"),
            discord.SelectOption(label="Image", value="image", description="Large embed image"),
            discord.SelectOption(label="Thumbnail", value="thumbnail", description="Top-right thumbnail"),
            discord.SelectOption(label="Footer", value="footer", description="Footer text + icon"),
            discord.SelectOption(label="Add Field", value="add_field", description="Add a new field"),
        ],
    )
    async def part_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            return
        val = select.values[0]
        modals = {
            "author": _AuthorModal,
            "title": _TitleModal,
            "description": _DescriptionModal,
            "color": _ColorModal,
            "image": _ImageModal,
            "thumbnail": _ThumbnailModal,
            "footer": _FooterModal,
            "add_field": _FieldAddModal,
        }
        modal_cls = modals.get(val)
        if modal_cls:
            await interaction.response.send_modal(modal_cls(self))

    # --- Buttons ---

    @discord.ui.button(label="Edit Field", style=discord.ButtonStyle.secondary)
    async def edit_field(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.send_modal(_FieldEditModal(self))

    @discord.ui.button(label="Delete Field", style=discord.ButtonStyle.danger)
    async def delete_field(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.send_modal(_FieldDeleteModal(self))

    @discord.ui.button(label="Send Here", style=discord.ButtonStyle.success, row=2)
    async def send_here(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        await interaction.channel.send(embed=self.embed)
        await interaction.response.send_message("Embed sent!", ephemeral=True)

    @discord.ui.button(label="Send To…", style=discord.ButtonStyle.secondary, row=2)
    async def send_to(self, interaction: discord.Interaction, btn: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.send_modal(_SendToModal(self))


class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    messages = app_commands.Group(name="messages", description="Message counter commands")

    @app_commands.command(name="embed", description="Build an embed with a visual editor. (Manage messages required)")
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x89B4FA)
        embed.set_footer(text="Embed Builder")
        view = EmbedBuilderView(embed, interaction.user.id)
        await interaction.response.send_message(
            "Use the dropdown and buttons below to build your embed. Changes update live.",
            embed=embed,
            view=view,
            ephemeral=True,
        )
    

    @app_commands.command(name="purge", description="Clear messages. (Manage messages required)")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    # @app_commands.describe(amount="Number of messages to clear (less than 1000)")
    async def purge(self, interaction: discord.Interaction, amount: int, bot_messages: bool = True, embed_messages: bool = True, user_messages: bool = True):
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



                                                                       

    @app_commands.command(name="serverinfo", description="Shows information of the current server")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def serverinfo(self, interaction: discord.Interaction):
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



    @app_commands.command(name="userinfo", description="Shows information of a user")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def userinfo(self, interaction: discord.Interaction, member: Optional[discord.Member]):
        from state import STATUS_PRIVACY_SET
        if member is None:
            member = interaction.user

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

                              
        if member.id in STATUS_PRIVACY_SET:
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



    @app_commands.command(name="roleinfo", description="Shows informations of a role")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role = None):  
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



    @app_commands.command(name="avatar", description="Displays the image of a user's avatar")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def avatar(self, interaction: discord.Interaction, member: Optional[discord.Member]):
      if member == None:
        member = interaction.user
      embed = discord.Embed(title=f"{member}'s Avatar", url=f"{member.avatar}", color = 0xffffff)
      embed.set_image(url = member.avatar)
      embed.set_footer(icon_url = interaction.user.avatar, text = f"Issued by {interaction.user}")
      await interaction.response.send_message(embed=embed)
  

    @app_commands.command(name="poll", description="Make a poll. (Manage messages required)")
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.has_permissions(manage_messages=True)
    # @app_commands.describe(first_emoji = "First emoji", first_option = "First option", second_emoji = "Second emoji", second_option = "Second option", third_emoji = "Third emoji", third_option = "Third option")
    async def poll(self, interaction: discord.Interaction, first_emoji: str, first_option: str, second_emoji: str, second_option: str, third_emoji: Optional[str], third_option: Optional[str]):
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


    @app_commands.command(name="qrcode", description="Generate qr-code from text, link, ...")
    @app_commands.checks.cooldown(1, 69, key=lambda i: (i.user.id))
    # @app_commands.describe(parm = "Value of Qr-code")
    async def qr(self, interaction: discord.Interaction, parm:str):
      qrim = qrcode.make(parm)
      qrim.save('data_assets/qrcode.png')
      with open('data_assets/qrcode.png', 'rb') as f:
          picture = discord.File(f)
      embed = discord.Embed(title='',color=0xffffff)
      embed.add_field(name=f'QR Code Maker',value=f'**Context**: `{parm}`')
      embed.set_image(url="attachment://qrcode.png")
      await interaction.response.send_message(file=discord.File('data_assets/qrcode.png'),embed=embed)


    @app_commands.command(name="daysbetween", description="Find the days between a pair of day, month, and year")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    # @app_commands.describe(firstdate = "The first date dd/mm/yy", seconddate = "The second date dd/mm/yy")
    async def daysbetween(self, interaction: discord.Interaction, firstdate: str, seconddate: str):
      from state import DaysBetweenButton
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

   


    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
      embed=discord.Embed(color = 0xffffff)
      embed.add_field(name="> 🤍 Client Ping", value=f"```{round(self.bot.latency * 1000)}ms```")
      await interaction.response.send_message(embed=embed)


   


    @app_commands.command(name="invite", description="Invite Equinox")
    async def invite(self, interaction: discord.Interaction):
      from state import myInvite
      emb = discord.Embed(title="You're choosing the best bot for your server! :D",color = 0xffffff)
      await interaction.response.send_message(embed=emb, view=myInvite())

                                                                         


    @app_commands.command(name="def", description="Find a definition of a word")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def define(self, interaction: discord.Interaction, word: str):
      from state import dictionary, fetch_word_example, DefineButton
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


    @app_commands.command(name="translate", description="Translate a text to a destinated language")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def trans(self, interaction: discord.Interaction, args: str, lang: str):
        from state import RawCopyButton
        t = Translator()
        a = t.translate(args, dest=lang)
        embe = discord.Embed(color = 0xffffff)
        sourcelang = googletrans.LANGUAGES[(a.src).lower()]
        translated_sourcelang = googletrans.LANGUAGES[(a.dest).lower()]
        embe.set_author(name="Equinox Translator", icon_url=self.bot.user.avatar)
        embe.set_thumbnail(url="https://www.iconsdb.com/icons/preview/white/google-translate-xxl.png")
        embe.add_field(name=f"Original Text - {sourcelang.capitalize()}", value=args, inline=False)
        embe.add_field(name=f"Translated Text - {translated_sourcelang.capitalize()}", value=a.text, inline=False)
        embe.set_footer(text=f"Translated by {interaction.user}", icon_url=interaction.user.avatar)
        view = RawCopyButton(a.text, interaction.user.id)
        await interaction.response.defer()
        msg = await interaction.followup.send(embed=embe, view=view)
        view.message = msg




    @app_commands.command(name="timedif", description="Find time differences between 2 message id.")
    async def timedif(self, interaction: discord.Interaction, id1: str, id2: str):
        from state import Paginator
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


    @app_commands.command(name="steal", description="Steal multiple emojis from another server")
    # @app_commands.describe(emojis="The emojis to steal", names="Optional new names for the emojis, separated by spaces")
    @app_commands.checks.has_permissions(manage_emojis_and_stickers=True)
    async def steal(self, interaction: discord.Interaction, emojis: str, names: str = None):
        from state import client
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



    @app_commands.command(name="help", description="Shows a selectable drow down menu of available commands")
    @app_commands.checks.cooldown(1, 20, key=lambda i: (i.user.id))
    async def help(self, interaction: discord.Interaction):
      from state import update, update_note, mySelect
      embed=discord.Embed(title="Equinox Navigator | /equinox", description="```Currently only operable with slash prefix.```", color=0xffffff)
      embed.set_author(name="Equinox' Commands List", icon_url=self.bot.user.avatar)
      embed.add_field(name="My Categories", value="```Search through drop down menu down below.```", inline=False)
      embed.add_field(name=f"Updates {update}", value=update_note, inline=False)
      embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
      view = mySelect(interaction.user.id)
      await interaction.response.defer()
      msg = await interaction.followup.send(embed=embed, view=view)
      view.message = msg
      view.embed = embed


    @app_commands.command(name="exchange", description="Convert fiat <-> crypto <-> fiat using real-time rates")
    # @app_commands.describe(from_currency="Currency or crypto you're converting from (e.g. usd, btc, ltc)", amount="Amount to convert", to_currency="Currency or crypto you're converting to (e.g. vnd, xmr, eur)")
    async def exchange(
        self,
        interaction: discord.Interaction,
        from_currency: str,
        amount: float,
        to_currency: str
    ):
        await interaction.response.defer()
        from state import SYMBOL_TO_ID, SUPPORTED_FIAT, CurrencyView
        from_currency = from_currency.lower()
        to_currency = to_currency.lower()

        is_from_crypto = from_currency in SYMBOL_TO_ID
        is_to_crypto = to_currency in SYMBOL_TO_ID

        timestamp = int(datetime.now(timezone.utc).timestamp())

        cache_key = f"{from_currency}:{to_currency}"
        cached = getattr(self.exchange, "_rate_cache", {}).get(cache_key)
        if cached and (timestamp - cached["ts"] < 60):
            rate = cached["rate"]
            converted = amount * rate if is_from_crypto or (not is_from_crypto and not is_to_crypto) else amount / rate
        else:
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

                    if not hasattr(self.exchange, "_rate_cache"):
                        self.exchange._rate_cache = {}
                    self.exchange._rate_cache[cache_key] = {"rate": rate, "ts": timestamp}
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

                                        


    @app_commands.command(name="check_tx", description="Check transaction details across chains")
    # @app_commands.describe(txid="Transaction ID/hash",chain="Blockchain to check (btc, ltc, doge, eth)",min_confirmations="Notify when this confirmation count is reached (max 11)",))
    async def check_tx(self, interaction: discord.Interaction, txid: str, chain: str, min_confirmations: int = None):
        from state import fetch_tx_data, parse_tx_data, pending_alerts, SUPPORTED_CHAINS
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

                                                        

    @messages.command(name="toggle")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(option=[
        app_commands.Choice(name="Enable", value="enable"),
        app_commands.Choice(name="Disable", value="disable")
    ])
    async def messages_toggle(self, interaction: discord.Interaction, option: app_commands.Choice[str]):
        from state import load_server_data, save_server_data

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


    @messages.command(name="count")
    async def messages_count(self, interaction: discord.Interaction, user: discord.User = None):
        from state import load_server_data, save_server_data
        user = user or interaction.user
        guild_id = str(interaction.guild.id)
        data = load_server_data(guild_id)
        if not data:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Message Counter",
                    description="```\nMessage counter has not been set up for this server, use /messages toggle.\n```",
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

    
    

    @messages.command(name="blacklist_view")
    async def messages_blacklist_view(self, interaction: discord.Interaction):
        from state import load_server_data, save_server_data

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


    @messages.command(name="deduct")
    @app_commands.checks.has_permissions(administrator=True)
    async def messages_deduct(self, interaction: discord.Interaction, user: discord.User, amount: int):
        from state import load_server_data, save_server_data, PaginationView

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



    @messages.command(name="leaderboard")
    async def messages_leaderboard(self, interaction: discord.Interaction):
        from state import load_server_data, save_server_data, PaginationView
        guild_id = str(interaction.guild.id)
        data = load_server_data(guild_id)
        if not data:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Message Counter",
                    description="```\nMessage counter has not been set up for this server, use /messages toggle.\n```",
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
            embed.set_footer(text="Use /privacy to control message tracking.")
            embeds.append(embed)

        current_page = 0
        await interaction.response.send_message(embed=embeds[current_page], ephemeral=False)
        message = await interaction.original_response()

        if len(embeds) > 1:
            await message.edit(view=PaginationView(embeds))


    @messages.command(name="give", description="Transfer your message count to another user.")
    async def messages_give(self, interaction: discord.Interaction, to_user: discord.User, amount: int):
        from state import load_server_data, save_server_data
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
                    description="```\nMessage counter has not been set up for this server, use /messages toggle.\n```",
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



    @messages.command(name="blacklist")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove")
    ])
    async def messages_blacklist(self, interaction: discord.Interaction, action: app_commands.Choice[str], channel: discord.TextChannel):
        from state import load_server_data, save_server_data

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


    @app_commands.command(name="ask_gemini", description="Ask Gemini AI any question")
    @app_commands.checks.has_permissions(administrator=True)
    async def ask_gemini_command(self, interaction: discord.Interaction):
        from state import BuyPremium, load_gemini_servers, RemoveGeminiView, save_gemini_servers, PromptButtonView, is_premium
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            await interaction.followup.send("❌ This command must be used in a server.", ephemeral=True)
            return

        owner_id = guild.owner_id

        active, tier, expires = await is_premium(owner_id)

        if not active:
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


    @app_commands.command(name="drop", description="Start a drop game.")
    # @app_commands.describe(prize="The prize for the drop", reaction="Add participation reaction (🤚)?")
    async def drop(self, interaction: discord.Interaction, prize: str, reaction: bool = False):
        from state import DropView, DeployView
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





    @app_commands.command(name="graph", description="Create a graph with a function")
    async def graph_command(self, interaction: discord.Interaction, function: str):
      from state import user_graph_data, random_color, generate_graph, GraphView, is_premium
      active, tier, expires = await is_premium(interaction.user.id)
      if active:
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


    @app_commands.command(name="update", description="Setup a Equinox' updates (Devs only, users use /help)")
    async def update_setup(self, interaction: discord.Interaction):
      from state import devs, UpdateButton
      if interaction.user.id in devs:
        embed = discord.Embed(title=f"Equinox's Updates Checker", description="```Please click the button if you wish to check Equinox' update(s)```", color=0xffffff)
        await interaction.response.send_message(embed=embed, view=UpdateButton())
      else:
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Devs only")

                                                                              




    @app_commands.command(name="wiki", description="Search anything from wikipedia")
    async def wikipedia_query(self, interaction: discord.Interaction, search: str):
      from state import WikipediaButton
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
            except Exception:
              embed.add_field(name=f"{i+1} - {output[i]}", value="...", inline=False)
          view = WikipediaButton(interaction.user.id, output)
          await msg.delete()
          msg2 = await interaction.channel.send(content=f"{interaction.user.mention}", embed=embed, view=view)
          view.message = msg2
      else:
        embed = discord.Embed(title=f"Wikipedia Search Results - {search.capitalize()}", description=f"No result(s) found for {search.capitalize()} :(", color=0xffffff)
        await interaction.channel.send(content=interaction.user.mention, embed=embed)


async def setup(bot):
    bot.tree.add_command(app_translate)
    await bot.add_cog(UtilityCog(bot))
