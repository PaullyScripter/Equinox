import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from cogs.ticket_views import BuyPremium2, DeleteTicketSystemButton, TicketButton
from cogs.ticket_views import load_json, save_json, get_ticket_config, append_ticket_history, add_ticket_participant

TICKET_DIR = "ticket-json"

def guild_ticket_path(guild_id: int) -> str:
    return f"{TICKET_DIR}/{guild_id}-ticket.json"

def load_guild_tickets(guild_id: int):
    path = guild_ticket_path(guild_id)
    data = load_json(path)
    return data if data is not None else {"message": []}


class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="make_ticket", description="Make a ticket system. (Administrator required)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.checks.bot_has_permissions(manage_channels=True, manage_roles=True)
    async def make_ticket(
        self,
        interaction: discord.Interaction,
        title: Optional[str],
        description: Optional[str],
        image: Optional[str],
        category: discord.CategoryChannel,
        role: Optional[str],
        ticket_message: Optional[str]
    ):
        import sys as _sys
        is_premium = _sys.modules["__main__"].is_premium
        refresh = _sys.modules["__main__"].refresh
        refresh()

        guild_id = interaction.guild.id
        active, tier, expires = await is_premium(interaction.user.id)
        await interaction.response.defer()

        ticket_roles = [int(r.strip().strip('<@&>')) for r in role.split(",")] if role else None

        ticket_data = load_guild_tickets(guild_id)

        if not active:
            if image:
                await interaction.channel.send(
                    embed=discord.Embed(
                        title="You're being restricted",
                        description=(
                            "The owner of this server does not have premium.\n"
                            "Non-premium users do not have access to ticket's image.\n"
                            "Consider not including an image or buy our useful premium with lots of perks.\n"
                            "Use: </help:1242738769099231302> to check out our premium perks."
                        ),
                        color=0xffffff
                    ),
                    view=BuyPremium2()
                )
                return

            if len(ticket_data["message"]) >= 3:
                embed = discord.Embed(
                    title="Your Ticket Systems",
                    description=(
                        "The owner of this server does not have premium.\n"
                        "Non-premium users are only allowed to deploy 3 ticket systems into their server.\n"
                        "Consider deleting an existing ticket system below or buy our useful premium with lots of perks.\n"
                        "Use: </help:1242738769099231302> to check out our premium perks."
                    ),
                    color=0xffffff
                )
                for i, msg_data in enumerate(ticket_data['message'][:25]):
                    embed.add_field(
                        name=f"No: 0{i+1} Ticket System:",
                        value=f"Url: {msg_data['url']}\nId: {msg_data['messageid']}",
                        inline=True
                    )
                await interaction.channel.send(embed=embed, view=DeleteTicketSystemButton())
                return

        embed = discord.Embed(
            title=title or "Equinox Ticket",
            description=description or "```Click the gray button below to make a ticket```",
            color=0xffffff
        )
        embed.set_footer(text="Ticket status: Enabled | Max Ticket Per User: ∞")
        if image and active:
            embed.set_image(url=image)

        view = TicketButton()
        ticket_msg = await interaction.followup.send(embed=embed, view=view)
        view.message = ticket_msg

        path = guild_ticket_path(guild_id)
        update_data = {
            "messageid": ticket_msg.id,
            "channel_id": interaction.channel.id,
            "category": category.id,
            "ticket_message": ticket_message,
            "ticket_role": ticket_roles,
            "url": ticket_msg.jump_url,
            "disabled": False,
            "max_ticket": None
        }
        try:
            file_data = load_json(path)
            if file_data is None:
                file_data = {"message": []}
            file_data.setdefault("message", []).append(update_data)
        except Exception:
            file_data = {"message": [update_data]}
        save_json(path, file_data)


    def _is_ticket_authorized(self, interaction: discord.Interaction) -> bool:
        user = interaction.user
        if user == interaction.guild.owner:
            return True
        if user.guild_permissions.administrator:
            return True

        config = get_ticket_config(interaction.guild.id)
        ticket_role_ids = set()
        for msg in config.get("message", []):
            roles = msg.get("ticket_role")
            if roles:
                ticket_role_ids.update(roles)

        if not ticket_role_ids:
            return False

        user_role_ids = {r.id for r in user.roles}
        return bool(ticket_role_ids & user_role_ids)

    @app_commands.command(name="addmember", description="Add a member to the ticket.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def addmember(self, interaction: discord.Interaction, member: discord.Member):
        if not self._is_ticket_authorized(interaction):
            await interaction.response.send_message(
                "You are not authorized to add members. Only ticket role holders, administrators, or the server owner can use this.",
                ephemeral=True
            )
            return

        cid = interaction.channel.id
        await interaction.channel.set_permissions(member, read_messages=True, send_messages=True, attach_files=True)
        append_ticket_history(cid, "member_added", interaction.user.id, f"Added {member.id}")
        add_ticket_participant(cid, interaction.user.id)
        await interaction.response.send_message(
            embed=discord.Embed(title=f"Successfully added {member.mention} to {interaction.channel.mention}", color=0xffffff)
        )

    @app_commands.command(name="revmember", description="Remove a member from a ticket.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    async def revmember(self, interaction: discord.Interaction, member: discord.Member):
        if not self._is_ticket_authorized(interaction):
            await interaction.response.send_message(
                "You are not authorized to remove members. Only ticket role holders, administrators, or the server owner can use this.",
                ephemeral=True
            )
            return

        cid = interaction.channel.id
        await interaction.channel.set_permissions(member, send_messages=False, read_messages=False)
        append_ticket_history(cid, "member_removed", interaction.user.id, f"Removed {member.id}")
        add_ticket_participant(cid, interaction.user.id)
        await interaction.response.send_message(
            embed=discord.Embed(title=f"Successfully removed {member} from {interaction.channel.mention}", color=0xffffff)
        )


async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
