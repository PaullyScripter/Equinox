import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput, Select
from typing import Optional
from datetime import datetime, timezone, timedelta
import json, random, asyncio, re, math, io, os
from asyncio import sleep
import matplotlib
import matplotlib.pyplot as plt
plt.set_loglevel("critical")
import numpy


@app_commands.context_menu(name="Gacha Stats")
async def gacha_stats(interaction: discord.Interaction, member: discord.Member):
    from state import FlexButton
    await interaction.response.defer(ephemeral=True)
    msg = await interaction.followup.send("Retrieving your data please wait... <a:loading_symbol:1295113412564615249>")
    with open(f'data/userinventory.json', 'r') as f:
        user_data = json.load(f)

    userid = []

    for user_data_index in range(len(user_data['user'])):
        userid.append(user_data['user'][user_data_index]['userid'])

    if member.id not in userid:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{member.name} has no items to flex.", description="This user has no items\nIf this is you, you can start collecting items by running /roll", color = 0xffffff))
    else:
        roll_amount = 0
        best_roll = None
        best_item = None

        roll_name_gif_name = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
        roll_name_gif = [
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXN2ZmhsdDE5ajFpamY4YmJ4cnBrM2F1OGczM3ZmODl2N3VmcGhtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dfAXMYZfSmUjYttjqM/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXE2ZHcxd3EwdDFwOGV6M3JxYmJwbzRyMGVhMjl6Ynl2d2hkcmplMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5EG56vzNYvfgJWldgS/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDNndGxyMXFsY3EzZ3djNWJrMHgwZ204aWE2NTA3eGdiNXBsd2l2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9f3OzkeQ6h0tbyKlTr/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXFkbm9wNmRkOXp4c2E1eTFiZ2FqZnZ1aHIxMjNhZnFqd2swNDA2OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/smZYhZ2Bwz8mPCwDPl/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXlza3gxYno2Z2I2NGNrdnNyMDlneGQwdmZicWxudGVzZmk3cTQ4NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mGl6JhTtCc0ukOugQ5/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3UxdWZrbDVvc281N2swc202cGR6Zmp4MGUyNmhuYjk0NWhvdXYyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cbhVQuTa5BFS5RlHFG/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDAxcm10MThzajBwbGYwOGhxMWdzZDYyazJ6OHg0dm05bWNpYW83NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FPjwcGYUkDO3kok4PP/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTRmYXA4YWl3NHdwY3k1ZGNrYjh2bzZxY2ZhZzY3eXp4a2p3eHoybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gsp2q6vt6KPZeyJgQd/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGNoa3FmYnNxc3M4Nm90ZTF0cDg4NTFpMjU0aWdndjN4ZXN2cHJzZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Xpb7aXuOuormG3MfnL/giphy.gif",
            "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ptYXg5Ymc2NHRuZmkzdDQ3YTJoN3JrZ3RiZXczMXdyd2tiZjRjbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jbsoD38dcXoEmjfNQQ/giphy.gif"
        ]
        items = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]
        rarity_name = ["1/2", "1/3", "1/4", "1/10", "1/100", "1/500", "1/1,000", "1/10,000", "1/10,000", "1/10,000"]
        user_rolls = []
        user_rolls_order = []
        user_items = []
        user_items_order = []
        gif = 0
        with open(f'data/userinventory.json', 'r') as f:
            user_data = json.load(f)

        for user_data_flex in range(len(user_data['user'])):
            if member.id == user_data['user'][user_data_flex]['userid']:
                roll_amount = user_data['user'][user_data_flex]['roll']
                for key in user_data['user'][user_data_flex]['inventory'][0]:
                    if key in roll_name_gif_name:
                        user_rolls.append(key)
                    elif key in items:
                        user_items.append(key)
        if len(user_rolls) != 0:
            for roll_name in range(len(roll_name_gif_name)):
                for user_roll_name in range(len(user_rolls)):
                    if roll_name_gif_name[roll_name] == user_rolls[user_roll_name]:
                        user_rolls_order.append(roll_name_gif_name[roll_name])
            best_roll = user_rolls_order[-1]
        if len(user_items) != 0:
            for item_name in range(len(items)):
                for user_item_name in range(len(user_items)):
                    if items[item_name] == user_items[user_item_name]:
                        user_items_order.append(items[item_name])
            best_item = user_items_order[-1]
        gif = roll_name_gif[roll_name_gif_name.index(best_roll)]
        roll_rarity = rarity_name[roll_name_gif_name.index(best_roll)]

        secs = roll_amount*4
        yrs,secs=divmod(secs,secs_per_year:=60*60*24*30.5*12)
        mth,secs=divmod(secs,secs_per_month:=60*60*24*30)
        days,secs=divmod(secs,secs_per_day:=60*60*24)
        hrs,secs=divmod(secs,secs_per_hr:=60*60)
        mins,secs=divmod(secs,secs_per_min:=60)
        secs=round(secs, 2)
        playtime='{} secs'.format(secs)

        if secs > 60 or mins > 0:
            playtime='{} minute(s) and {} second(s)'.format(int(mins),secs)
            if mins > 60 or hrs > 0:
                playtime='{} hour(s), {} minute(s) and {} second(s).'.format(int(hrs),int(mins),secs)
                if hrs > 24 or days > 0:
                    playtime='{} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(days),int(hrs),int(mins),secs)
                    if days > 30 or mth > 0:
                        playtime='{} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(mth),int(days),int(hrs),int(mins),secs)
                        if mth > 12 or yrs > 0:
                            playtime='{} year(s), {} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(yrs),int(mth),int(days),int(hrs),int(mins),secs)

        all_roll = ', '.join(user_rolls_order)
        all_item = ', '.join(user_items_order)
        embed = discord.Embed(title=f"🤍 {member.name}'s Gacha Stats", description="Items shown are virtual items,\nand could not possibly resell or trade with real items.", color=0xffffff)
        embed.add_field(name=f"> Rolling Stats:", value=f"```{member.name} has rolled {roll_amount} time(s)```", inline=False)
        embed.add_field(name=f"> Playtime:", value=f"```{playtime}```", inline=False)
        embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
        embed.set_thumbnail(url=member.avatar)
        await msg.delete()
        view = FlexButton(interaction.user.id, best_roll, best_item, all_roll, all_item, member, gif, roll_rarity)
        respond = await interaction.channel.send(embed=embed, view=view)
        view.message = respond


class GachaCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roll", description="Gacha game")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    # @app_commands.describe(item="The item you want to roll with")
    @app_commands.choices(item=[
      discord.app_commands.Choice(name='Fortune Drink', value=1),
      discord.app_commands.Choice(name="Witch's Potion", value=2),
      discord.app_commands.Choice(name='Divine Fluid', value=3),
      discord.app_commands.Choice(name='Angel Dust', value=4),
      discord.app_commands.Choice(name='Me When Im Lucky', value=5),
      discord.app_commands.Choice(name='Touch of Divinity', value=6),
      discord.app_commands.Choice(name='Trio Charm', value=7),
    ])
    async def roll(self, interaction: discord.Interaction, item: Optional[discord.app_commands.Choice[int]]):
      from state import is_premium, refresh
      await interaction.response.defer()
      refresh()
      with open("data/userinventory.json") as f:
        users = json.load(f)
      userid_list = []
      for user in users["user"]:
        userid_list.append(user["userid"])
      if interaction.user.id not in userid_list:
        def add_json(new_data, filename='data/userinventory.json'):
          with open(filename,'r+') as file:
              file_data = json.load(file)
              file_data["user"].append(new_data)
              file.seek(0)
              json.dump(file_data, file, indent = 2)

        y = {
          "userid": interaction.user.id,
          "inventory": [
            {}
          ],
          "roll": 0
        }
        add_json(y)
      chances = []
      rarity_name = ["Common|(1/2)", "Uncommon|(1/3)", "Rare|(1/4)", "Epic|(1/10)", "Legendary|(1/100)", "Divine|(1/500)", "Myth in the Making|(1/1,000)", "Samantha|(1/10,000)", "Paully|(1/10,000)", "Tommy|(1/10,000)"]
      rarity_name_only = []
      for i in range(len(rarity_name)):
        rarity_name_only_split = rarity_name[i].split("|")
        rarity_name_only.append(rarity_name_only_split[0])
      rarity_probability = [1/2, 1/3, 1/4, 1/10, 1/100, 1/500, 1/1000, 1/10000, 1/10000, 1/10000]
      rarity_priority = 0
      probability = 1
      time = 5
      luck = 1
      refresh()
      active, tier, expires = await is_premium(interaction.user.id)
      if active:
        time = random.randint(1,2)
        luck = 2
      else: 
        time = 5
        luck = 1
      luck_boost_index = []
      able_to_roll = False
      if item == None:
        rarity_priority = [0] 
        probability = 1
        able_to_roll = True
      elif item != None:
        roll_item = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]
        user_inventory_item = []
        with open("data/userinventory.json") as f:
          users = json.load(f)
        for user in users["user"]:
          if user["userid"] == interaction.user.id:
            for key in user["inventory"]:
              for inventory_roll_name in key:
                if inventory_roll_name in roll_item:
                  user_inventory_item.append(inventory_roll_name)
        if item.name in user_inventory_item:
          def add_json(new_data, filename='data/userinventory.json'):
            with open(filename,'r+') as file:
                file_data = json.load(file)
                for users in file_data["user"]:
                  if users["userid"] == interaction.user.id:
                    for key in users["inventory"]:
                      return key[new_data]
                file.seek(0)
                json.dump(file_data, file, indent = 2)
          y = item.name
          if add_json(y) == 0:
            able_to_roll = False
          else:
            able_to_roll = True
            with open('data/userinventory.json', 'r') as f:
              json_data = json.load(f)

            index = 0
            for i in range(len(json_data['user'])):
              if json_data['user'][i]["userid"] == interaction.user.id:
                index = i 

            json_data['user'][index]['inventory'][0][item.name] -= 1

            with open('data/userinventory.json', 'w') as f:
              json.dump(json_data, f, indent=2)

            if item.name == "Fortune Drink":
              rarity_priority = [1]
              probability = 2
              able_to_roll = True
              luck_boost_index = [0,1]
            elif item.name == "Witch's Potion":
              rarity_priority = [2]
              probability = 3
              able_to_roll = True
              luck_boost_index = [1,2]
            elif item.name == "Divine Fluid":
              rarity_priority = [3]
              probability = 5
              able_to_roll = True
              luck_boost_index = [2,3]
            elif item.name == "Angel Dust":
              rarity_priority = [4]
              probability = 10
              able_to_roll = True
              luck_boost_index = [3,4]
            elif item.name == "Me When Im Lucky":
              rarity_priority = [5]
              probability = 50
              able_to_roll = True
              luck_boost_index = [4,5]
            elif item.name == "Touch of Divinity":
              rarity_priority = [6]
              probability = 100
              able_to_roll = True
              luck_boost_index = [4,5,6]
            elif item.name == "Trio Charm":
                rarity_priority = [7, 8, 9]
                probability = 500
                able_to_roll = True
                luck_boost_index = [7, 8, 9]
          
        else:
          able_to_roll = False
      
      for i in range(len(rarity_name)):
          if i in luck_boost_index:
              if i in rarity_priority:
                                                                                     
                  for j in range(math.ceil(int(10000 * probability * luck / 2))):
                      chances.append(rarity_name[i])
              else:
                                                                                   
                  for j in range(math.ceil(int(10000 * probability * luck / 1.5))):
                      chances.append(rarity_name[i])
          else:
                                                                                   
              for j in range(math.ceil(int(10000 * rarity_probability[i] * probability * luck))):
                  chances.append(rarity_name[i])
      if able_to_roll == True:
        rolled = random.choice(chances)
        name = rolled.split("|")
        rolle_name = name[0]
        embed=discord.Embed(title="Rolling...", color = 0xffffff)
        roll_name_gif_name = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
        roll_name_gif = [
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXN2ZmhsdDE5ajFpamY4YmJ4cnBrM2F1OGczM3ZmODl2N3VmcGhtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dfAXMYZfSmUjYttjqM/giphy.gif", 
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXE2ZHcxd3EwdDFwOGV6M3JxYmJwbzRyMGVhMjl6Ynl2d2hkcmplMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5EG56vzNYvfgJWldgS/giphy.gif", 
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDNndGxyMXFsY3EzZ3djNWJrMHgwZ204aWE2NTA3eGdiNXBsd2l2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9f3OzkeQ6h0tbyKlTr/giphy.gif", 
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXFkbm9wNmRkOXp4c2E1eTFiZ2FqZnZ1aHIxMjNhZnFqd2swNDA2OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/smZYhZ2Bwz8mPCwDPl/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXlza3gxYno2Z2I2NGNrdnNyMDlneGQwdmZicWxudGVzZmk3cTQ4NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mGl6JhTtCc0ukOugQ5/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3UxdWZrbDVvc281N2swc202cGR6Zmp4MGUyNmhuYjk0NWhvdXYyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cbhVQuTa5BFS5RlHFG/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDAxcm10MThzajBwbGYwOGhxMWdzZDYyazJ6OHg0dm05bWNpYW83NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FPjwcGYUkDO3kok4PP/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTRmYXA4YWl3NHdwY3k1ZGNrYjh2bzZxY2ZhZzY3eXp4a2p3eHoybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gsp2q6vt6KPZeyJgQd/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGNoa3FmYnNxc3M4Nm90ZTF0cDg4NTFpMjU0aWdndjN4ZXN2cHJzZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Xpb7aXuOuormG3MfnL/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ptYXg5Ymc2NHRuZmkzdDQ3YTJoN3JrZ3RiZXczMXdyd2tiZjRjbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jbsoD38dcXoEmjfNQQ/giphy.gif"
          ]
        roll_gif_url = ""
        roll_index = 0
        for i in range(len(roll_name_gif_name)):
          if rolle_name == roll_name_gif_name[i]:
            roll_index = i
            roll_gif_url = roll_name_gif[i]
        embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbWJjMml0Y3B5dmsydmVkZGtmNHl6cTZ3OG1vczQ5OHB1aGZsdXNpZCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/eFgDbfks97Mq906D3A/giphy.gif")
        await interaction.followup.send(embed=embed)
        name = rolled.split("|")
        if roll_index > 3:
          e=discord.Embed(title="Rolling...???", color = 0xffffff)
          e.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbW5yYjEwaGl2bzZ3cnNidDJtMnFscmkyNXY5MjVpZDZ4dXZpMTNkeCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FJM4c4RYkb72qvAcBt/giphy.gif")
          await sleep(3)
          await interaction.edit_original_response(embed=e)
        if item != None:
          potion = item.name
        else:
          potion = "None"
        mbed=discord.Embed(title="You Rolled:", description = f"**{rolle_name}** with the probability of **{name[1]}**\nItem used: **{potion}**", color=0xffffff)
        if active:
          mbed.add_field(name="Premium Perk:", value="**x2 Luck**")

        mbed.set_image(url=roll_gif_url)
        mbed.set_footer(text=f"Rolled by {interaction.user}", icon_url=interaction.user.avatar)
        await sleep(time)
        await interaction.edit_original_response(embed=mbed)
        with open(f'data/userinventory.json', 'r') as f:
          user_data = json.load(f)

        for user_data_index in range(len(user_data['user'])):
          if user_data['user'][user_data_index]['userid'] == interaction.user.id:
            user_data['user'][user_data_index]['roll'] += 1

        with open(f'data/userinventory.json', 'w') as f:
          json.dump(user_data, f, indent=2)      
        rolle_name = name[0]
        user_inventory_item = []
        with open("data/userinventory.json") as f:
          users = json.load(f)
        for user in users["user"]:
          if user["userid"] == interaction.user.id:
            for key in user["inventory"]:
              for inventory_roll_name in key:
                user_inventory_item.append(inventory_roll_name)
        if rolle_name not in user_inventory_item:
          def add_json(new_data, filename='data/userinventory.json'):
            with open(filename,'r+') as file:
                file_data = json.load(file)
                for users in file_data["user"]:
                  if users["userid"] == interaction.user.id:
                    for key in users["inventory"]:
                      key[new_data] = 1
                file.seek(0)
                json.dump(file_data, file, indent = 2)
          y = rolle_name
          add_json(y)
        else:
          def add_json(new_data, filename='data/userinventory.json'):
            with open(filename,'r+') as file:
                file_data = json.load(file)
                for users in file_data["user"]:
                  if users["userid"] == interaction.user.id:
                    for key in users["inventory"]:
                      key[new_data] += 1
                file.seek(0)
                json.dump(file_data, file, indent = 2)
          y = rolle_name
          add_json(y)
      else:
        embed=discord.Embed(title="Error in the rolling...", color=0xffffff)
        embed.add_field(name=f"{item.name}", value=f"> Missing: {item.name}", inline=False)
        await interaction.followup.send(embed=embed)


    @app_commands.command(name="flex", description="Show a member's gacha stats")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.user.id))
    async def flex(self, interaction: discord.Interaction, member: Optional[discord.Member]):
      from state import FlexButton
      await interaction.response.defer(ephemeral=True)
      msg = await interaction.followup.send("Retrieving your data please wait... <a:loading_symbol:1295113412564615249>")
      if member == None:
        member = interaction.user
      with open(f'data/userinventory.json', 'r') as f:
        user_data = json.load(f)

      userid = []

      for user_data_index in range(len(user_data['user'])):
        userid.append(user_data['user'][user_data_index]['userid'])

      if member.id not in userid:
        await msg.delete()
        await interaction.channel.send(embed=discord.Embed(title=f"{member.name} has no items to flex.", description="This user has no items\nIf this is you, you can start collecting items by running /roll", color = 0xffffff))
      else:
        roll_amount = 0
        best_roll = None
        best_item = None
    
        roll_name_gif_name = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
        roll_name_gif = [
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXN2ZmhsdDE5ajFpamY4YmJ4cnBrM2F1OGczM3ZmODl2N3VmcGhtZiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/dfAXMYZfSmUjYttjqM/giphy.gif", 
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXE2ZHcxd3EwdDFwOGV6M3JxYmJwbzRyMGVhMjl6Ynl2d2hkcmplMyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/5EG56vzNYvfgJWldgS/giphy.gif", 
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZDNndGxyMXFsY3EzZ3djNWJrMHgwZ204aWE2NTA3eGdiNXBsd2l2aCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/9f3OzkeQ6h0tbyKlTr/giphy.gif", 
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXFkbm9wNmRkOXp4c2E1eTFiZ2FqZnZ1aHIxMjNhZnFqd2swNDA2OSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/smZYhZ2Bwz8mPCwDPl/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExaXlza3gxYno2Z2I2NGNrdnNyMDlneGQwdmZicWxudGVzZmk3cTQ4NSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/mGl6JhTtCc0ukOugQ5/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3UxdWZrbDVvc281N2swc202cGR6Zmp4MGUyNmhuYjk0NWhvdXYyYyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/cbhVQuTa5BFS5RlHFG/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDAxcm10MThzajBwbGYwOGhxMWdzZDYyazJ6OHg0dm05bWNpYW83NCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/FPjwcGYUkDO3kok4PP/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbTRmYXA4YWl3NHdwY3k1ZGNrYjh2bzZxY2ZhZzY3eXp4a2p3eHoybyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/gsp2q6vt6KPZeyJgQd/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbGNoa3FmYnNxc3M4Nm90ZTF0cDg4NTFpMjU0aWdndjN4ZXN2cHJzZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Xpb7aXuOuormG3MfnL/giphy.gif",
          "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExM3ptYXg5Ymc2NHRuZmkzdDQ3YTJoN3JrZ3RiZXczMXdyd2tiZjRjbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/jbsoD38dcXoEmjfNQQ/giphy.gif"
          ]
        items = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]  
        rarity_name = ["1/2", "1/3", "1/4", "1/10", "1/100", "1/500", "1/1,000", "1/10,000", "1/10,000", "1/10,000"]
        user_rolls = []
        user_rolls_order = []
        user_items = []
        user_items_order = []
        gif = 0
        with open(f'data/userinventory.json', 'r') as f:
          user_data = json.load(f)

        for user_data_flex in range(len(user_data['user'])):
          if member.id == user_data['user'][user_data_flex]['userid']:
            roll_amount = user_data['user'][user_data_flex]['roll']
            for key in user_data['user'][user_data_flex]['inventory'][0]:
              if key in roll_name_gif_name:
                user_rolls.append(key)
              elif key in items:
                user_items.append(key)
        if len(user_rolls) != 0:
          for roll_name in range(len(roll_name_gif_name)):
            for user_roll_name in range(len(user_rolls)):
              if roll_name_gif_name[roll_name] == user_rolls[user_roll_name]:
                user_rolls_order.append(roll_name_gif_name[roll_name])
          best_roll = user_rolls_order[-1]
        if len(user_items) != 0:
          for item_name in range(len(items)):
            for user_item_name in range(len(user_items)):
              if items[item_name] == user_items[user_item_name]:
                user_items_order.append(items[item_name])
          best_item = user_items_order[-1]
        gif = roll_name_gif[roll_name_gif_name.index(best_roll)]
        roll_rarity = rarity_name[roll_name_gif_name.index(best_roll)]

        secs = roll_amount*4
        yrs,secs=divmod(secs,secs_per_year:=60*60*24*30.5*12)
        mth,secs=divmod(secs,secs_per_month:=60*60*24*30)
        days,secs=divmod(secs,secs_per_day:=60*60*24)
        hrs,secs=divmod(secs,secs_per_hr:=60*60)
        mins,secs=divmod(secs,secs_per_min:=60)
        secs=round(secs, 2)
        playtime='{} secs'.format(secs)
    
        if secs > 60 or mins > 0:
            playtime='{} minute(s) and {} second(s)'.format(int(mins),secs)
            if mins > 60 or hrs > 0:
                playtime='{} hour(s), {} minute(s) and {} second(s).'.format(int(hrs),int(mins),secs)
                if hrs > 24 or days > 0:
                    playtime='{} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(days),int(hrs),int(mins),secs)
                    if days > 30 or mth > 0:
                      playtime='{} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(mth),int(days),int(hrs),int(mins),secs)
                      if mth > 12 or yrs > 0:
                        playtime='{} year(s), {} month(s), {} day(s), {} hour(s), {} minute(s) and {} second(s).'.format(int(yrs),int(mth),int(days),int(hrs),int(mins),secs)

        all_roll = ', '.join(user_rolls_order)
        all_item = ', '.join(user_items_order)
        embed = discord.Embed(title=f"🤍 {member.name}'s Gacha Stats", description="Items shown are virtual items,\nand could not possibly resell or trade with real items.", color=0xffffff)
        embed.add_field(name=f"> Rolling Stats:", value=f"```{member.name} has rolled {roll_amount} time(s)```", inline=False)
        embed.add_field(name=f"> Playtime:", value=f"```{playtime}```", inline=False)
        embed.set_footer(text=f"Issued by {interaction.user}", icon_url=interaction.user.avatar)
        embed.set_thumbnail(url=member.avatar)
        await msg.delete()
        view = FlexButton(interaction.user.id, best_roll, best_item, all_roll, all_item, member, gif, roll_rarity)
        respond = await interaction.channel.send(embed=embed, view=view)
        view.message = respond
    

    @app_commands.command(name="inventory", description="Show a member's inventory")
    @app_commands.checks.cooldown(1, 2, key=lambda i: (i.user.id))
    @app_commands.choices(type=[
      discord.app_commands.Choice(name='Rolls', value=1),
      discord.app_commands.Choice(name="Items", value=2)
    ])
    async def inventory(self, interaction: discord.Interaction, member: Optional[discord.Member], type: discord.app_commands.Choice[int]):

      rarity = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Myth in the Making", "Samantha", "Paully", "Tommy"]
      items = ["Fortune Drink", "Witch's Potion", "Divine Fluid", "Angel Dust", "Me When Im Lucky", "Touch of Divinity", "Trio Charm"]

      if member is None:
        member = interaction.user

      embed = discord.Embed(
        title=f"{member}'s {type.name} Inventory",
        description="Items shown are virtual items,\nand could not possibly resell or trade with real items.",
        color=0xffffff
      )

      embed.set_thumbnail(url=member.display_avatar.url)

      with open("data/userinventory.json", "r") as f:
        json_data = json.load(f)

      target_user = next(
        (u for u in json_data["user"] if u["userid"] == member.id),
        None
      )

      if target_user is None:
        return await interaction.response.send_message(
          embed=discord.Embed(
            title="Inventory Not Found",
            description="This user does not have an inventory yet.",
            color=0xffffff
          ),
          ephemeral=True
        )

      if not target_user.get("inventory"):
        return await interaction.response.send_message(
          embed=discord.Embed(
            title="Inventory Not Found",
            description="This user has no inventory data.",
            color=0xffffff
          ),
          ephemeral=True
        )

      inventory = target_user["inventory"][0]

      if type.name == "Rolls":

        found_any = False

        for rarity_name in rarity:
          amount = inventory.get(rarity_name, 0)

          if amount > 0:
            found_any = True

            embed.add_field(
              name=f"🤍 {rarity_name}",
              value=f"> Amount: **{amount}**",
              inline=True
            )

        if not found_any:
          return await interaction.response.send_message(
            embed=discord.Embed(
              title=f"{member} has no rolls to show.",
              description="This user has no roll inventory.",
              color=0xffffff
            )
          )

      elif type.name == "Items":

        join_item = ""

        for item_name in items:
          amount = inventory.get(item_name, 0)

          if amount > 0:
            join_item += f"> {item_name} **(x{amount})**\n"

        if join_item:
          embed.add_field(
            name="🤍 Craftable Items",
            value=join_item,
            inline=False
          )
        else:
          return await interaction.response.send_message(
            embed=discord.Embed(
              title=f"{member} has no items to show.",
              description=(
                "This user has no items.\n"
                "If this is you, you can start collecting items by running /roll"
              ),
              color=0xffffff
            )
          )

      embed.set_footer(
        text="Equinox Inventory",
        icon_url=interaction.user.display_avatar.url
      )

      await interaction.response.send_message(embed=embed)



    @app_commands.command(name="shop", description="Show the gacha shop")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.user.id))
    async def shop(self, interaction: discord.Interaction):
      embed = discord.Embed(title="Equinox's Gacha Shop", description="Items shown are virtual items,\nand could not possibly resell or trade with real items.", color=0xffffff)
      embed.add_field(name=f"🤍 Fortune Drink", value=f"> Ingredients: **5 Commons, 3 Uncommons**\n> Stats: x2 Lucky", inline=True)
      embed.add_field(name=f"🤍 Witch's Potion", value=f"> Ingredients: **15 Commons, 10 Uncommons, 5 Rares**\n> Stats: x3 Lucky", inline=True)
      embed.add_field(name=f"🤍 Divine Fluid", value=f"> Ingredients: **30 Commons, 20 Uncommons, 10 Rares, 5 Epics**\n> Stats: x5 Lucky", inline=True)
      embed.add_field(name=f"🤍 Angel Dust", value=f"> Ingredients: **100 Commons, 70 Uncommons, 40 Rares, 20 Epics, 5 Legendaries**\n> Stats: x10 Lucky", inline=True)
      embed.add_field(name=f"🤍 Me When Im Lucky", value=f"> Ingredients: **250 Commons, 100 Uncommons, 70 Rares, 50 Epics, 25 Legendaries, 1 Divine**\n> Stats: x50 Lucky", inline=True)
      embed.add_field(name=f"🤍 Touch of Divinity", value=f"> Ingredients: **1000 Commons, 500 Uncommons, 400 Rares, 100 Epics, 70 Legendaries, 10 Divine**\n> Stats: x100 Lucky", inline=True)
      embed.add_field(name=f"🤍 Trio Charm", value=f"> Ingredients: **5000 Commons, 2500 Uncommons, 1000 Rares, 500 Epics, 300 Legendaries, 100 Divine, 10 Mythic in the Making**\n> Stats: x500 Lucky", inline=True)
      await interaction.response.send_message(embed=embed)


    @app_commands.command(name="daily", description="Daily chest of potions")
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.user.id))
    async def daily(self, interaction: discord.Interaction):
      from state import BuyPremium, is_premium, refresh
      refresh()
      active, tier, expires = await is_premium(interaction.user.id)
      if active:
        with open('data/userinventory.json', 'r') as f:
          json_data = json.load(f)
        user_id = []
        index = 0
        for i in range(len(json_data['user'])):
            user_id.append(json_data['user'][i]['userid'])

        if interaction.user.id not in user_id:
          await interaction.response.send_message(embed=discord.Embed(title="Daily Error...", description="You do not have a paired database.\nCreate a database by rolling\nUse **/roll**", color=0xffffff))
        else:
          with open('data/userinventory.json', 'r') as f:
            json_data = json.load(f)  

          index = None
          for i in range(len(json_data['user'])):
            if json_data['user'][i]["userid"] == interaction.user.id:
              index = i

          item_list = ["Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Fortune Drink", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Witch's Potion", "Divine Fluid", "Divine Fluid", "Divine Fluid", "Divine Fluid", "Angel Dust", "Angel Dust","Angel Dust","Me When Im Lucky", "Me When Im Lucky"]
          user_daily_item = []
          user_item = []
          for i in range(3):
            user_daily_item.append(random.choice(item_list))

          for key in json_data['user'][index]['inventory'][0]:
            user_item.append(key)

          for i in range(len(user_daily_item)):
            for key in json_data['user'][index]['inventory'][0]:
              user_item.append(key)
            if user_daily_item[i] in user_item:
              json_data['user'][index]['inventory'][0][user_daily_item[i]] += 1
            elif user_daily_item[i] not in user_item:
              json_data['user'][index]['inventory'][0][user_daily_item[i]] = 1
        
          with open(f'data/userinventory.json', 'w') as f:
            json.dump(json_data, f, indent=2)
          await interaction.response.defer()
          msg = await interaction.followup.send(embed=discord.Embed(title="Opening Chest...", color=0xffffff))
          await sleep(5)
          embed1=discord.Embed(title="In the chest you got:", description=f"x1 **{user_daily_item[0]}**", color=0xffffff)
          await msg.edit(embed=embed1)
          await sleep(2)
          embed2=discord.Embed(title="In the chest you got:", description=f"x1 **{user_daily_item[0]}**\nx1 **{user_daily_item[1]}**", color=0xffffff)
          await msg.edit(embed=embed2)
          await sleep(2)
          embed3=discord.Embed(title="In the chest you got:", description=f"x1 **{user_daily_item[0]}**\nx1 **{user_daily_item[1]}**\nx1 **{user_daily_item[2]}**", color=0xffffff)
          await msg.edit(embed=embed3)
      else:
        await interaction.response.send_message(embed=discord.Embed(title="You are being restricted", description="Daily command is only available to our elite users.\nConsider buying our useful premium with lots of perks?\nUse </help:1242738769099231302> to check out our premium perks.", color=0xffffff), view=BuyPremium())




    @app_commands.command(name="craft", description="Craft an item")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.user.id))
    # @app_commands.describe(item="The item you want to craft")
    @app_commands.choices(item=[
      discord.app_commands.Choice(name='Fortune Drink', value=1),
      discord.app_commands.Choice(name="Witch's Potion", value=2),
      discord.app_commands.Choice(name='Divine Fluid', value=3),
      discord.app_commands.Choice(name='Angel Dust', value=4),
      discord.app_commands.Choice(name='Me When Im Lucky', value=5),
      discord.app_commands.Choice(name='Touch of Divinity', value=6),
      discord.app_commands.Choice(name='Trio Charm', value=7),
    ])
    async def craft(self, interaction: discord.Interaction, item: discord.app_commands.Choice[int], amount: Optional[int] = 1):
        if amount <= 0:
            amount = 1

                                       
        crafting_recipes = {
            "Fortune Drink": (["Common", "Uncommon"], [5, 3]),
            "Witch's Potion": (["Common", "Uncommon", "Rare"], [15, 10, 5]),
            "Divine Fluid": (["Common", "Uncommon", "Rare", "Epic"], [30, 20, 10, 5]),
            "Angel Dust": (["Common", "Uncommon", "Rare", "Epic", "Legendary"], [100, 70, 40, 20, 5]),
            "Me When Im Lucky": (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine"], [250, 100, 70, 50, 25, 1]),
            "Touch of Divinity": (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine"], [1000, 500, 400, 100, 70, 10]),
            "Trio Charm": (["Common", "Uncommon", "Rare", "Epic", "Legendary", "Divine", "Mythic in the Making"], [5000, 2500, 1000, 500, 300, 100, 10]),
        }

                                                          
        requirements, required_amount = crafting_recipes.get(item.name, ([], []))

                             
        with open("data/userinventory.json") as f:
            users = json.load(f)

                               
        user_inventory = next((user for user in users["user"] if user["userid"] == interaction.user.id), None)
        if not user_inventory:
            await interaction.response.send_message("User data not found!")
            return

                                    
        user_inventory_items = [inventory_item for inventory in user_inventory["inventory"] for inventory_item in inventory]

                                                        
        missing_requirements = []
        for i, requirement in enumerate(requirements):
            required = required_amount[i] * amount
            current_amount = user_inventory_items.count(requirement)
            missing = required - current_amount
            if missing > 0:
                missing_requirements.append((requirement, missing))

        if missing_requirements:
            embed = discord.Embed(title="Error in Crafting", color=0xffffff)
            for req, missing in missing_requirements:
                embed.add_field(name=req, value=f"Missing: {missing}", inline=False)
            await interaction.response.send_message(embed=embed)
            return

                                              
                                 
        for i, requirement in enumerate(requirements):
            required = required_amount[i] * amount
            for _ in range(required):
                user_inventory_items.remove(requirement)

                          
        for _ in range(amount):
            user_inventory_items.append(item.name)

                                                 
        with open("data/userinventory.json", 'r+') as file:
            file_data = json.load(file)
            for user in file_data["user"]:
                if user["userid"] == interaction.user.id:
                    user["inventory"] = [dict(zip(user_inventory["inventory"][0].keys(), user_inventory_items))]
            file.seek(0)
            json.dump(file_data, file, indent=2)

                            
        embed = discord.Embed(title="🤍 Successfully Crafted", description=f"Item crafted: {item.name} (x{amount})", color=0xffffff)
        await interaction.response.send_message(embed=embed)

                                                                            


async def setup(bot):
    bot.tree.add_command(gacha_stats)
    await bot.add_cog(GachaCog(bot))
