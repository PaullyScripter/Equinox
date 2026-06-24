import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os
from captcha.image import ImageCaptcha
from PIL import Image
import cogs.database as db

class VerificationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="make_verify", description="Make verify system (Server owner only)")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    async def make_verify(
        self,
        interaction: discord.Interaction,
        rev_role: Optional[discord.Role],
        add_role: Optional[discord.Role],
        message: Optional[str],
        image: Optional[str]
    ):
        from state import BuyPremium2, DeleteVerifySystem, VerifyButton, is_premium, refresh
        await interaction.response.defer()
        description = "```Each user will have 120 seconds (2mins) to complete captcha.```"
        can_image = False
        refresh()

        active, tier, expires = await is_premium(interaction.guild.owner_id)
    
        if message and not active:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="You're being restricted",
                    description=(
                        "The owner of this server does not have premium.\n"
                        "Non-premium users do not have access to customize the verify system's message.\n"
                        "Consider not including a message or buy our premium for more perks.\n"
                        "Use: </help:1242738769099231302> to check out our premium perks."
                    ),
                    color=0xffffff
                ),
                view=BuyPremium2()
            )
            return
    
        if image and not active:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="You're being restricted",
                    description=(
                        "The owner of this server does not have premium.\n"
                        "Non-premium users do not have access to customize the verify system's image.\n"
                        "Consider not including an image or buy our premium for more perks.\n"
                        "Use: </help:1242738769099231302> to check out our premium perks."
                    ),
                    color=0xffffff
                ),
                view=BuyPremium2()
            )
            return
    
        if active:
            description = message if message else description
            can_image = bool(image)
    
        user = interaction.guild.get_member(self.bot.user.id)
        client_top_role = user.top_role
        roles = [role for role in (rev_role, add_role) if role]
    
        eligible = all(
            not role.is_bot_managed() and
            (interaction.user.id == interaction.guild.owner_id or interaction.user.top_role > role) and
            client_top_role > role
            for role in roles
        )
    
        if len(set(roles)) < len(roles):                                  
            eligible = False
    
        if not eligible:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="Error...",
                    description="```The role(s) you specified are either too high or managed by a bot.```",
                    color=0xffffff
                )
            )
            return
    
        rev_role_id = rev_role.id if rev_role else None
        add_role_id = add_role.id if add_role else None
    
        configs = db.get_verify_configs()
        existing_ids = {g['guildid'] for g in configs}
        if interaction.guild.id in existing_ids:
            guild = next(g for g in configs if g['guildid'] == interaction.guild.id)
            embed = discord.Embed(
                title="Error...",
                description="```Only one verify system can be deployed per server.```",
                color=0xffffff
            )
            embed.add_field(name="Verify Message URL", value=f"> {guild['url']}")
            await interaction.followup.send(embed=embed, view=DeleteVerifySystem())
            return
    
        embed = discord.Embed(title="Complete captcha to verify as a user!", description=description, color=0xffffff)
        if can_image:
            embed.set_image(url=image)
    
        msg = await interaction.followup.send(embed=embed, view=VerifyButton())
        db.set_verify_config(
            interaction.guild.id,
            remove_role=rev_role_id,
            add_role=add_role_id,
            url=msg.jump_url,
            message_id=msg.id
        )


async def setup(bot):
    await bot.add_cog(VerificationCog(bot))
