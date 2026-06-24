import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional, Literal
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os
import cogs.database as db


def load_data():
    return db.load_reaction_roles_cog()


def save_data(data):
    db.save_reaction_roles_cog(data)

async def template_name_autocomplete(interaction: discord.Interaction, current: str):
    data = load_data()
    gid = str(interaction.guild_id)
    templates = data.get(gid, {})
    return [discord.app_commands.Choice(name=t, value=t) for t in templates if current.lower() in t.lower()][:25]

class ReactionRolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="rrgame", description="Make a selection role (Dev only)")
    async def rr(self, interaction: discord.Interaction):
      if interaction.user.id in devs:
        from state import devs, rrSelectGames, rrSelectGender, rrSelectPing, rrSelectServer
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



    @app_commands.command(name="reactionrolesetup", description="Add or remove a reaction role template.")
    @app_commands.autocomplete(name=template_name_autocomplete)
    @app_commands.checks.has_permissions(manage_roles=True)
    # @app_commands.describe(name="Name of the template", action="Choose whether to add or remove the template")
    async def reactionrolesetup(
        self,
        interaction: discord.Interaction,
        name: str,
        action: Literal["Add", "Remove"]                                     
    ):

        from state import BuyPremium, is_premium
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
                active, tier, expires = await is_premium(interaction.guild.owner_id)
                if not active:
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


    @app_commands.command(name="reactionroleedit", description="Add or remove roles from a template.")
    @app_commands.autocomplete(name=template_name_autocomplete)
    @app_commands.checks.has_permissions(manage_roles=True)
    # @app_commands.describe(name="Template name", role="Role to add or remove", action="Add or Remove", emoji="Optional default emoji")
    async def reactionroleedit(
        self,
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



    @app_commands.command(name="reactionroleembed", description="View or edit embed of a reaction role template.")
    @app_commands.autocomplete(name=template_name_autocomplete)
    @app_commands.checks.has_permissions(manage_roles=True)
    # @app_commands.describe(name="Template name", title="New embed title", color="New embed color in HEX")
    async def reactionroleembed(
        self,
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



    @app_commands.command(name="reactionroledeploy", description="Deploy a reaction role template to a channel.")
    @app_commands.autocomplete(name=template_name_autocomplete)
    @app_commands.checks.has_permissions(manage_roles=True)
    # @app_commands.describe(name="Template name", channel="Optional channel to send to")
    async def reactionroledeploy(
        self,
        interaction: discord.Interaction,
        name: str,
        channel: discord.TextChannel = None
    ):
        from state import ReactionRoleView
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


async def setup(bot):
    await bot.add_cog(ReactionRolesCog(bot))
