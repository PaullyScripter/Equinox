import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os, time
import aiohttp
import string
import uuid
from discord.utils import format_dt

class PremiumCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="redeem", description="Redeem a premium code")
    async def redeem(self, interaction: discord.Interaction):
        from state import Mymodal
        await interaction.response.send_modal(Mymodal())



    @app_commands.command(name="login", description="Login to your database using email")
    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.user.id))
    async def login(self, interaction: discord.Interaction):
      from state import LoginModal
      from cogs.gacha import _ensure_user
      await _ensure_user(interaction.user.id)
      await interaction.response.send_modal(LoginModal())


    @app_commands.command(name="reset", description="Resets your databases (24h cooldown)")
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.user.id))
    async def reset(self, interaction: discord.Interaction):
        from state import ResetButton
        from cogs.gacha import _get_user_full, _set_field

        data = await _get_user_full(interaction.user.id)
        reset_at = data.get("reset_requested_at") if data else None
        now = time.time()

        if reset_at is None or reset_at == 0:
            embed = discord.Embed(
                title="Are you sure with resetting all your data?",
                description="This includes your rolls, items, credentials, and stats.\nClick Reset to start a 24-hour cooldown. After that, run `/reset` again to confirm.",
                color=0xffffff,
            )
            view = ResetButton(interaction.user.id, "request")
            await interaction.response.defer()
            msg = await interaction.followup.send(embed=embed, view=view)
            view.message = msg
        elif reset_at > now:
            remaining = int(reset_at - now)
            hrs = remaining // 3600
            mins = (remaining % 3600) // 60
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Reset in Progress",
                    description=f"Reset will be available in **{hrs}h {mins}m**. Come back later.",
                    color=0xffffff,
                ),
            )
        else:
            embed = discord.Embed(
                title="Reset Ready",
                description="The 24-hour cooldown has passed. Click Reset to permanently delete your data.",
                color=0xED4245,
            )
            view = ResetButton(interaction.user.id, "confirm")
            await interaction.response.defer()
            msg = await interaction.followup.send(embed=embed, view=view)
            view.message = msg



    @app_commands.command(name="account", description="View your account status")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def account(self, interaction: discord.Interaction):
        from cogs.gacha import _get_user_full
        data = await _get_user_full(interaction.user.id)
        if data is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="No Account Found",
                    description="You don't have any data yet. Use /roll to get started.",
                    color=0xffffff,
                ),
            )
            return

        email_hash = data.get("email")
        eligible = data.get("eligible")
        reset_at = data.get("reset_requested_at")

        embed = discord.Embed(
            title=f"{interaction.user.name}'s Account",
            color=0xffffff,
        )

        if email_hash:
            embed.add_field(name="Email", value=f"Linked (SHA-256: `{email_hash[:12]}...`)", inline=False)
        else:
            embed.add_field(name="Email", value="Not linked", inline=False)

        embed.add_field(name="Eligible for Reset", value="Yes" if eligible else "No", inline=True)
        embed.add_field(name="Rolls", value=str(data.get("roll_count", 0)), inline=True)

        if reset_at and reset_at > time.time():
            remaining = int(reset_at - time.time())
            hrs = remaining // 3600
            mins = (remaining % 3600) // 60
            embed.add_field(name="Reset Available In", value=f"{hrs}h {mins}m", inline=True)

        embed.set_footer(text="Emails are stored as SHA-256 hashes for privacy.")
        await interaction.response.send_message(embed=embed)


    @app_commands.command(name="unlink", description="Unlink your email from the bot")
    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.user.id))
    async def unlink(self, interaction: discord.Interaction):
        from cogs.gacha import _get_user_full, _hash_email

        data = await _get_user_full(interaction.user.id)
        if data is None or data.get("email") is None:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="No Email Linked",
                    description="You don't have an email linked to your account.",
                    color=0xffffff,
                ),
            )
            return

        stored_hash = data["email"]
        await interaction.response.send_modal(self.UnlinkModal(stored_hash, interaction.user.id))



    class UnlinkModal(Modal, title="Unlink Email"):
        def __init__(self, stored_hash: str, userid: int):
            super().__init__()
            self.stored_hash = stored_hash
            self.userid = userid
            self.email_input = TextInput(
                label="Enter the email linked to your account",
                placeholder="you@example.com",
            )
            self.add_item(self.email_input)

        async def on_submit(self, interaction: discord.Interaction):
            from cogs.gacha import _hash_email
            from state import AuthButton

            if _hash_email(self.email_input.value) != self.stored_hash:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Email Mismatch",
                        description="The email you entered doesn't match the one on your account.",
                        color=0xED4245,
                    ),
                )
                return

            email = self.email_input.value.strip()
            view = AuthButton(email, interaction.user.id)
            view.unlink_mode = True
            msg = await interaction.response.send_message(
                content="A verification code will be sent to your email. Confirm to proceed with unlinking.",
                view=view,
            )
            view.message = msg


    @app_commands.command(name="premium", description="Check your premium status")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def premium(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        from state import is_premium, format_expires
        if member is None:
            member = interaction.user

        active, tier, expires_at = await is_premium(member.id)

        emb = discord.Embed(color=0xFFFFFF)

        if active and tier:
            emb.set_author(name=f"{member}'s premium status: 🤍")
            emb.add_field(name="Premium Plan", value=f"**> {tier.title()}**", inline=False)

            emb.add_field(name="Expires", value=format_expires(expires_at), inline=False)
        else:
            emb.set_author(name=f"{member}'s premium status: 👻")
            emb.add_field(name="Premium Plan", value="**> None**", inline=False)

        if member.avatar:
            emb.set_thumbnail(url=member.avatar.url)

        emb.set_footer(text="Navigate to premium section of /help to check your perks!")
        await interaction.response.send_message(embed=emb, ephemeral=True)



    @app_commands.command(name="is_premium", description="Check your premium status")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def i_spremium(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        from state import is_premium
        target = interaction.user
        active, tier, expires = await is_premium(target.id)

        if active:
            msg = f"✅ {target} is premium ({tier})"
            if expires:
                msg += f"\nExpires at: `{expires}`"
            else:
                msg += "\nExpires: `never`"
            await interaction.response.send_message(msg)
        else:
            await interaction.response.send_message(f"❌ {target} is not premium.")


    @app_commands.command(name="prem_nsfw", description="Displays various catergories of nsfw contents (for premium users)")
    async def prem_nsfw(self, interaction: discord.Interaction, catergory: Optional[str]):
      from state import refresh, BuyPremium, is_premium
      refresh()
      active, tier, expires = await is_premium(interaction.user.id)
      if active:
        if interaction.channel.is_nsfw():
          if catergory != None:
              if catergory.lower() in ["anal", "asian", "ass", "bdsm", "blowjob", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys", "waifu", "neko", "trap"]:
                if catergory.lower() in ["anal", "asian", "ass", "bdsm", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
                  link = "https://api-popcord.vercel.app/img/nsfw?type="
                  key = "urls"
                elif catergory.lower() in ["waifu", "blowjob", "neko", "trap"]:
                  link = "https://api.waifu.pics/nsfw/"
                  key = "url"
                async with aiohttp.ClientSession() as session:
                    async with session.get(link+catergory) as resp:
                        res = await resp.json()
                em = discord.Embed(color=0xffffff)
                if catergory in ["anal", "asian", "ass", "bdsm", "boobs", "cum", "ebony", "creampie", "gay", "hentai", "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
                  em.set_image(url=res[key][0])
                else:
                  em.set_image(url=res[key])
                await interaction.response.send_message(embed=em)
              else:
                embed=discord.Embed(title="NSFW Error...", description="```Catergory not available, check available catergory using /nsfw without any catergory behind.```")
                await interaction.response.send_message(embed=embed)

          else:
            embed = discord.Embed(title="Equinox - NSFW Commands List", description=":bangbang: 18+ only, equinox team are not responsible for underage children who view the content as it it intially cautioned!", color=0xffffff)
            embed.add_field(name="> **Catergories**", value="```anal, asian, ass, bdsm, blowjob, boobs, cum, creampie, ebony, gay, hentai, korean, latex, latina, lesbian, neko, nsfw, penis, pussy, redhead, short, thigh, toys, trap, waifu.```")
            await interaction.response.send_message(embed=embed)
        else:
          embed=discord.Embed(title="NSFW Error...", description="```This is a nsfw related commands, and must only execute in nsfw channel.```", color=0xffffff)
          await interaction.response.send_message(embed=embed)
      else:
        await interaction.response.send_message(embed=discord.Embed(title="You are being restricted", description="This nsfw command is only available to our elite users.\nConsider use the normal </nsfw:1243128625398546584> command or buy our useful premium!\nUse </help:1242738769099231302> to check out our premium perks.", color=0xffffff), view=BuyPremium())


    @app_commands.command(name="nsfw", description="Displays various catergories of nsfw contents (for normal users)")
    @app_commands.checks.cooldown(10, 3600, key=lambda i: (i.user.id))
    async def nsfw(self, interaction: discord.Interaction, catergory: Optional[str]):
      from state import refresh, is_premium
      refresh()
      active, tier, expires = await is_premium(interaction.user.id)
      if interaction.channel.is_nsfw():
        caution = None
        if active:
          caution = "You seems to have premium, do you know that premium users are eligible to use our premium nsfw command?"
        if catergory != None:
            if catergory.lower() in ["anal", "asian", "ass", "bdsm", "blowjob", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys", "waifu", "neko", "trap"]:
              if catergory.lower() in ["anal", "asian", "ass", "bdsm", "boobs", "creampie", "cum", "ebony", "gay", "hentai",  "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
                link = "https://api-popcord.vercel.app/img/nsfw?type="
                key = "urls"
              elif catergory.lower() in ["waifu", "blowjob", "neko", "trap"]:
                link = "https://api.waifu.pics/nsfw/"
                key = "url"
              await interaction.response.defer()
              async with aiohttp.ClientSession() as session:
                  async with session.get(link+catergory) as resp:
                      res = await resp.json()
              em = discord.Embed(color=0xffffff)
              if catergory in ["anal", "asian", "ass", "bdsm", "boobs", "cum", "ebony", "creampie", "gay", "hentai", "korean", "latex", "latina", "lesbian", "nsfw", "penis", "pussy", "redhead", "short", "thigh", "toys"]:
                em.set_image(url=res[key][0])
              else:
                em.set_image(url=res[key])
              if caution != None:
                await interaction.channel.send(caution)
              await interaction.followup.send(embed=em)
            else:
              embed=discord.Embed(title="NSFW Error...", description="```Catergory not available, check available catergory using /nsfw without any catergory behind.```")
              await interaction.response.send_message(embed=embed)

        else:
          embed = discord.Embed(title="Equinox - NSFW Commands List", description=":bangbang: 18+ only, equinox team are not responsible for underage children who view the content as it it intially cautioned!", color=0xffffff)
          embed.add_field(name="> **Catergories**", value="```anal, asian, ass, bdsm, blowjob, boobs, cum, creampie, ebony, gay, hentai, korean, latex, latina, lesbian, neko, nsfw, penis, pussy, redhead, short, thigh, toys, trap, waifu.```")
          await interaction.response.send_message(embed=embed)
      else:
        embed=discord.Embed(title="NSFW Error...", description="```This is a nsfw related commands, and must only execute in nsfw channel.```", color=0xffffff)
        await interaction.response.send_message(embed=embed)

                                                                                                  
    

    @app_commands.command(name="email", description="Sends email (Devs only)")
    async def email(self, interaction: discord.Interaction, email: str, code: str):
      from state import devs, EmailCheck
      codetype = None
      if code in self.bot.monthly_codes:
        codetype = "monthly"
      elif code in self.bot.yearly_codes:
        codetype = "yearly"
      if interaction.user.id in devs:
        await interaction.response.defer()
        embed=discord.Embed(title="Email Check", description=f"```Are you sure the following email is right?```", color=0xffffff)
        embed.add_field(name="> Email:", value=f"```{email}```", inline=False)
        embed.set_footer(text=f"Ignore to cancel.", icon_url=interaction.user.avatar)
        view = EmailCheck(email, code, codetype)
        msg = await interaction.followup.send(embed=embed, view=view)
        view.message = msg
      else:
        await interaction.response.send_message(embed=discord.Embed(title="Devs only!", color=0xffffff))
    

    @app_commands.command(name="gen_code", description="Generate premium code(s) (Devs only)")
    # @app_commands.describe(tier="Choose the premium tier", amount="How many codes to generate (default 1, no limit)")
    async def gen_code(
        self,
        interaction: discord.Interaction,
        tier: str,
        amount: Optional[int] = 1
    ):
        from state import devs, replenish_codes
        if interaction.user.id not in devs:
            return await interaction.response.send_message("Devs only.", ephemeral=True)

        tier_value = tier.lower()
        count = 1 if amount is None else max(1, int(amount))

        await interaction.response.defer(ephemeral=True)

                        
        try:
            new_codes = replenish_codes(tier_value, count)
        except Exception as e:
            return await interaction.followup.send(f"Error: {e}", ephemeral=True)

                                 
        if len(new_codes) > 10:
            buf = io.BytesIO(("\n".join(new_codes) + "\n").encode("utf-8"))
            file = discord.File(buf, filename=f"{tier_value}_codes_{len(new_codes)}.txt")
            await interaction.followup.send(
                content=f"✅ Generated **{len(new_codes)}** {tier_value.title()} code(s). See attachment.",
                file=file,
                ephemeral=True
            )
        else:
            emb = discord.Embed(
                title=f"✅ Generated {len(new_codes)} {tier_value.title()} code(s)",
                color=0xFFFFFF
            )
            for i, c in enumerate(new_codes, 1):
                emb.add_field(name=str(i), value=f"```{c}```", inline=False)
            await interaction.followup.send(embed=emb, ephemeral=True)

                                       
        try:
            log_channel = self.bot.get_channel(1242633669890277456)
            if log_channel:
                msg = discord.Embed(
                    title=f"{interaction.user} generated {len(new_codes)} {tier_value.title()} code(s)",
                    color=0xFFFFFF
                )
                preview = "\n".join(f"`{c}`" for c in new_codes[:50])
                if preview:
                    msg.description = preview if len(new_codes) <= 50 else (preview + f"\n…(+{len(new_codes)-50} more)")
                await log_channel.send(embed=msg)
        except Exception:
            pass



    @app_commands.command(name="remove_premium", description="Remove premium from users (Devs only)")
    async def remove_premium(self, interaction: discord.Interaction, member: discord.Member):
        from state import devs, SUB_FILES, load_json, remove_subscription
        if interaction.user.id not in devs:
            return await interaction.response.send_message("Devs only.", ephemeral=True)

        removed_tier = None
        for tier, file_path in SUB_FILES.items():
            data = load_json(file_path)
            users = data.get("users", [])
            if any(u.get("user_id") == member.id for u in users):
                remove_subscription(member.id, tier)
                removed_tier = tier
                break

        if removed_tier:
            embed = discord.Embed(color=0xFFFFFF)
            embed.set_author(name=f"Successfully removed premium from {member}")
            embed.add_field(name="Premium Plan", value=f"**> {removed_tier.title()}**", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(color=0xFFFFFF)
            embed.set_author(name=f"{member} has no active premium plan")
            embed.add_field(name="Premium Plan", value=f"**> None**", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)


    @app_commands.command(name="export_codes", description="Export premium codes to .txt for SellAuth (Devs only)")
    async def export_codes(self, interaction: discord.Interaction, tier: str):
        from state import devs, _load_codes_for_tier, _as_txt_file
        if interaction.user.id not in devs:
            return await interaction.response.send_message("Devs only.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        tiers = ("monthly", "yearly", "lifetime") if tier == "all" else (tier,)

        files: list[discord.File] = []
        summary_lines: list[str] = []
        empty_tiers: list[str] = []

        for t in tiers:
                                                    
            codes = _load_codes_for_tier(t)
            if codes:
                files.append(_as_txt_file(f"{t}_codes.txt", codes))
                summary_lines.append(f"- {t.title()}: {len(codes)} code(s)")
            else:
                empty_tiers.append(t)
                summary_lines.append(f"- {t.title()}: 0 code(s)")

        if not files:
            return await interaction.followup.send(
                "No available codes found for the requested tier(s).",
                ephemeral=True
            )

        await interaction.followup.send(
            content="Here are the current code lists for SellAuth:\n" + "\n".join(summary_lines),
            files=files,
            ephemeral=True
        )


    @app_commands.command(name="stats", description="Shows Equinox' stats (Devs only)")
    async def stats(self, interaction: discord.Interaction):
        from state import devs, load_stats, IGNORED_USER_IDS
        if interaction.user.id not in devs:
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Devs only.")
            return

        data = load_stats()
        events = data.get("events", [])

                                 
        now = datetime.now(timezone.utc)
        day_ago   = now - timedelta(days=1)
        week_ago  = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        year_ago  = now - timedelta(days=365)

        count_day = count_week = count_month = count_year = 0
        unique_users: set[int] = set()
        per_command: dict[str, int] = {}
        per_day: dict[str, int] = {}                          

        for e in events:
            try:
                ts_raw = e.get("ts")
                user_id = int(e.get("user_id"))
                cmd = str(e.get("command"))
                ts = datetime.fromisoformat(ts_raw)
            except Exception:
                continue

                                                              
            if user_id in IGNORED_USER_IDS:
                continue

            unique_users.add(user_id)

                           
            if ts >= day_ago:
                count_day += 1
            if ts >= week_ago:
                count_week += 1
            if ts >= month_ago:
                count_month += 1
            if ts >= year_ago:
                count_year += 1

                     
            per_command[cmd] = per_command.get(cmd, 0) + 1

                                    
            day_key = ts.date().isoformat()
            per_day[day_key] = per_day.get(day_key, 0) + 1

                       
        if per_command:
            top_cmd, top_count = max(per_command.items(), key=lambda kv: kv[1])
        else:
            top_cmd, top_count = "None", 0

                                                
        import cogs.database as db
        verify_count = len(db.get_verify_configs())

        guild_count  = len(self.bot.guilds)
        user_count   = len(set(self.bot.get_all_members()))
        py_version   = sys.version.split()[0]
        ticket_count = max(
            0,
            len([n for n in os.listdir(ticket)
                 if os.path.isfile(os.path.join(ticket, n))]) - 1
        )

                           
        desc = (
            "```js\n"
            f"Guilds: {guild_count}\n"
            f"Users (cached): {user_count}\n"
            f"Python Version: {py_version}\n"
            f"Guild Ticket Deployed: {ticket_count}\n"
            f"Verify System Deployed: {verify_count}\n"
            "-------------------------\n"
            f"Commands (last 24h): {count_day}\n"
            f"Commands (last 7d):  {count_week}\n"
            f"Commands (last 30d): {count_month}\n"
            f"Commands (last 365d): {count_year}\n"
            f"Unique users (all time, non-dev): {len(unique_users)}\n"
            f"Top command: {top_cmd} ({top_count} uses)\n"
            "```"
        )

        embed = discord.Embed(
            title="🤍 Equinox Stats",
            description=desc,
            color=0xFFFFFF
        )
        embed.set_footer(text="Command analytics (dev-only, devs excluded from stats)")

                                            
                                    
        last_30_days = [(now.date() - timedelta(days=i)).isoformat()
                        for i in range(29, -1, -1)]
        counts = [per_day.get(d, 0) for d in last_30_days]

                                                     
        file = None
        if any(counts):
            plt.figure(figsize=(9, 4))
            plt.plot(last_30_days, counts, marker="o")
            plt.xticks(rotation=45, ha="right", fontsize=7)
            plt.ylabel("Commands")
            plt.xlabel("Date")
            plt.title("Commands per day (last 30 days)")
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format="png")
            plt.close()
            buf.seek(0)

            file = discord.File(buf, filename="commands_over_time.png")
            embed.set_image(url="attachment://commands_over_time.png")

                    
        if file:
            await interaction.response.send_message(embed=embed, file=file)
        else:
            await interaction.response.send_message(embed=embed)



async def setup(bot):
    await bot.add_cog(PremiumCog(bot))
