import discord
from discord.ui import View, Button
from datetime import datetime, timezone
import json
import os
import random
import asyncio
import time
from typing import Optional
import cogs.database as db

_entry_cooldowns: dict[int, float] = {}


def load_guild_giveaways(guild_id: int):
    return db.load_guild_giveaways(guild_id)


def save_guild_giveaways(guild_id: int, data: dict):
    db.save_guild_giveaways(guild_id, data)


def ensure_guild_json_file(guild_id: int):
    pass


def remove_guild_giveaway(guild_id: int, message_id: int):
    giveaways = db.load_guild_giveaways(guild_id)
    if str(message_id) in giveaways:
        del giveaways[str(message_id)]
        db.save_guild_giveaways(guild_id, giveaways)


class GiveawayView(View):
    def __init__(self, client, giveaway_data):
        super().__init__(timeout=None)
        self.client = client
        self.giveaway_data = giveaway_data
        self.entries = set(giveaway_data["entries"])
        self.end_time = datetime.strptime(giveaway_data["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        self.message = None
        self.host_ids = giveaway_data["hosts"]
        self.role_ids = giveaway_data["roles"]
        self.guild_id = giveaway_data.get("guild_id")
        guild = client.get_guild(self.guild_id) if self.guild_id else None
        self.guild_name = guild.name if guild else "Unknown Server"
        self.original_winner = None
        self.previous_winners = set()
        self.winner_message_id = None
        self.giveaway_ended = False
        self.timer_task = None

    def _get_guild(self):
        return self.client.get_guild(self.guild_id) if self.guild_id else None

    async def _resolve_winner(self, user_id: int):
        guild = self._get_guild()
        if guild:
            member = guild.get_member(user_id)
            if member:
                return member
        user = self.client.get_user(user_id)
        if user:
            return user
        try:
            return await self.client.fetch_user(user_id)
        except (discord.NotFound, discord.HTTPException):
            return None

    async def check_host_permission(self, interaction):
        if interaction.user.id in self.host_ids:
            return True

        member = interaction.guild.get_member(interaction.user.id)
        if member:
            for role_id in self.role_ids:
                if discord.utils.get(member.roles, id=role_id):
                    return True

        return False

    async def start_timer(self):
        try:
            remaining = (self.end_time - datetime.now(timezone.utc)).total_seconds()
            if remaining > 0:
                await asyncio.sleep(remaining)
            await self.end_giveaway()
        except asyncio.CancelledError:
            pass

    async def end_giveaway(self, interaction: Optional[discord.Interaction] = None):
        if interaction:
            await interaction.response.defer()
            if not await self.check_host_permission(interaction):
                await interaction.followup.send("You do not have permission to stop this giveaway.", ephemeral=True)
                return

        if self.giveaway_ended:
            if interaction:
                await interaction.followup.send("This giveaway has already been ended or canceled.", ephemeral=True)
            return

        self.giveaway_ended = True
        await self.disable_buttons()

        if len(self.entries) > 0:
            self.original_winner = random.choice(list(self.entries))
            self.previous_winners.add(self.original_winner)

            winner = await self._resolve_winner(self.original_winner)
            if winner:
                embed = discord.Embed(title="Winner Announcement", color=0xffffff)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** {winner.mention}", inline=False)
                embed.add_field(name="<a:snow:1311099641932152903> </giveaway_manage:1370458427100368898>", value=f"", inline=False)

                try:
                    await winner.send(f"Congratulations! You won the **{self.giveaway_data['prize']}** giveaway in **{self.guild_name}**!")
                except (discord.Forbidden, discord.HTTPException):
                    pass

                winner_view = WinnerButtonView(self)
                winner_message = await self.message.channel.send(
                    f"Congratulations {winner.mention}! You won the giveaway!",
                    embed=embed,
                    view=winner_view
                )
                winner_view.message = winner_message
                self.winner_message_id = winner_message.id
            else:
                await self.message.channel.send("The winner could not be found.")
                embed = discord.Embed(title="Winner Announcement", color=0xffffff)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)
                embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** N/A", inline=False)
                embed.add_field(name="<a:snow:1311099641932152903> </giveaway_manage:1370458427100368898>", value=f"", inline=False)
        else:
            await self.message.channel.send("No entries were found for the giveaway.")
            embed = discord.Embed(title="Winner Announcement", color=0xffffff)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** N/A", inline=False)
            embed.add_field(name="<a:snow:1311099641932152903> </giveaway_manage:1370458427100368898>", value=f"", inline=False)

        guild_id = self.giveaway_data["guild_id"]
        giveaways = load_guild_giveaways(guild_id)
        giveaways[str(self.giveaway_data["message_id"])]["status"] = "On Going / Winner revealed"
        save_guild_giveaways(guild_id, giveaways)

        try:
            embed = self.message.embeds[0]
            embed.set_footer(text="Status: Ended")
            await self.message.edit(embed=embed)
        except (IndexError, AttributeError):
            pass

    async def reroll(self, interaction: discord.Interaction):
        await interaction.response.defer()
        if not await self.check_host_permission(interaction):
            await interaction.followup.send("You do not have permission to reroll the winner.", ephemeral=True)
            return

        current_time = datetime.now(timezone.utc)
        giveaway_end_time = datetime.strptime(self.giveaway_data["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        if current_time < giveaway_end_time:
            await interaction.followup.send(
                "This giveaway has not ended yet. You can only reroll after it ends.",
                ephemeral=True
            )
            return

        eligible_entries = [entry for entry in self.entries if entry not in self.previous_winners]

        if len(eligible_entries) == 0:
            await interaction.followup.send("No eligible entries left for rerolling.", ephemeral=True)
            return

        try:
            if self.winner_message_id:
                prev_message = await interaction.channel.fetch_message(self.winner_message_id)
                if prev_message:
                    await prev_message.edit(view=None)
        except Exception as e:
            print(f"Error disabling buttons on previous winner embed: {e}")

        new_winner_id = random.choice(eligible_entries)
        new_winner = await self._resolve_winner(new_winner_id)

        if new_winner:
            self.previous_winners.add(new_winner_id)

            embed = discord.Embed(title="New Winner", color=0xffffff)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Prize:** {self.giveaway_data['prize']}", inline=False)

            winner_view = WinnerButtonView(self)
            embed.add_field(name="", value=f"<a:snow:1311099641932152903> **Winner:** {new_winner.mention}", inline=False)

            winner_message = await self.message.channel.send(
                f"Congratulations {new_winner.mention}! You are the new winner of the giveaway!",
                embed=embed,
                view=winner_view
            )
            winner_view.message = winner_message
            self.winner_message_id = winner_message.id
        else:
            await interaction.followup.send("The new winner could not be found.", ephemeral=True)

    async def finalize_winner(self, interaction: discord.Interaction):
        messageExist = True

        await interaction.response.defer()

        if not await self.check_host_permission(interaction):
            await interaction.followup.send("You do not have permission to finalize the winner.", ephemeral=True)
            return

        current_time = datetime.now(timezone.utc)
        giveaway_end_time = datetime.strptime(self.giveaway_data["end_time"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        if current_time < giveaway_end_time:
            await interaction.followup.send(
                "This giveaway has not ended yet. You can only finalize after it ends.",
                ephemeral=True
            )
            return

        if not self.message:
            try:
                self.message = await interaction.channel.fetch_message(self.giveaway_data["message_id"])
            except Exception:
                messageExist = False
                pass

        if self.winner_message_id:
            try:
                winner_message = await interaction.channel.fetch_message(self.winner_message_id)
                await winner_message.edit(view=None)
            except Exception:
                pass

        guild_id = interaction.guild_id if interaction.guild else self.giveaway_data.get("guild_id")
        remove_guild_giveaway(guild_id, self.giveaway_data["message_id"])

        await interaction.followup.send("Winner has been finalized.", ephemeral=True)

        if messageExist:
            try:
                embed = self.message.embeds[0]
                embed.set_footer(text="Status: Finalized")
                await self.message.edit(embed=embed)
            except (IndexError, AttributeError):
                pass

    async def enter(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        now = time.time()

        if user_id in _entry_cooldowns and now - _entry_cooldowns[user_id] < 3:
            await interaction.response.send_message("You're doing that too fast. Please wait a few seconds.", ephemeral=True)
            return

        await interaction.response.defer()

        if interaction.user.bot:
            return

        guild_id = interaction.guild.id
        message_id = str(self.message.id)

        giveaways = load_guild_giveaways(guild_id)

        if user_id in self.entries:
            self.entries.remove(user_id)
            self.giveaway_data["entries"] = list(self.entries)

            giveaways[message_id]["entries"] = list(self.entries)
            save_guild_giveaways(guild_id, giveaways)

            await interaction.followup.send("You've been successfully removed from this giveaway!", ephemeral=True)
            _entry_cooldowns[user_id] = now
            return

        self.entries.add(user_id)
        self.giveaway_data["entries"] = list(self.entries)

        giveaways[message_id]["entries"] = list(self.entries)
        save_guild_giveaways(guild_id, giveaways)

        await interaction.followup.send("You've successfully entered the giveaway!", ephemeral=True)
        _entry_cooldowns[user_id] = now

    async def show_entries(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(title="Number of entries:", color=0xffffff)
        embed.add_field(name="", value=f"<a:snow:1311099641932152903> {str(len(self.entries))} user(s)", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def cancel_giveaway(self, interaction: discord.Interaction):
        if not await self.check_host_permission(interaction):
            await interaction.response.send_message("You do not have permission to cancel this giveaway.", ephemeral=True)
            return

        if self.giveaway_ended:
            await interaction.response.send_message("This giveaway has already been ended or canceled.", ephemeral=True)
            return

        self.giveaway_ended = True

        if self.timer_task is not None and not self.timer_task.done():
            self.timer_task.cancel()
            self.timer_task = None

        await self.disable_buttons()

        await interaction.response.send_message("The giveaway has been successfully canceled.")

        try:
            embed = self.message.embeds[0]
            embed.set_footer(text="Status: Canceled")
            await self.message.edit(embed=embed)
        except (IndexError, AttributeError):
            pass

        remove_guild_giveaway(interaction.guild_id, self.message.id)

    async def disable_buttons(self):
        for item in self.children:
            item.disabled = True

        await self.message.edit(view=self)

    async def stop_button_callback(self, interaction: discord.Interaction):
        if not await self.check_host_permission(interaction):
            await interaction.response.send_message("You do not have permission to stop this giveaway.", ephemeral=True)
            return

        await self.end_giveaway(interaction)

    async def cancel_button_callback(self, interaction: discord.Interaction):
        await self.cancel_giveaway(interaction)


class WinnerButtonView(View):
    def __init__(self, giveaway_view: GiveawayView, timeout: float = 86400):
        super().__init__(timeout=timeout)
        self.giveaway_view = giveaway_view
        self.message = None

        reroll_button = Button(label="Reroll", style=discord.ButtonStyle.primary)
        async def reroll_button_callback(interaction: discord.Interaction):
            await self.giveaway_view.reroll(interaction)
        reroll_button.callback = reroll_button_callback
        self.add_item(reroll_button)

        finalize_button = Button(label="Finalize Winner", style=discord.ButtonStyle.secondary)
        async def finalize_button_callback(interaction: discord.Interaction):
            await self.giveaway_view.finalize_winner(interaction)
        finalize_button.callback = finalize_button_callback
        self.add_item(finalize_button)

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            await self.message.edit(view=self)
