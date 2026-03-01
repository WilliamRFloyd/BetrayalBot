import disnake
from disnake.ext import commands
from helper_functions import *

INFO_SERVER_ID = 1477768437739688228

def create_role_message(role:str, info_file: str) -> str:
    data = openJson(info_file)
    role_info = data["roles"].get(role, None)
    if not role_info:
        return "Role not found."

    alignment = role_info.get("alignment", "Neutral")
    description = role_info.get("description", "No description available.")

    message = "```"
    if alignment != "Neutral":
        message += "Diff"
    
    message += "\n"

    if alignment == "Good":
        message += "+"
    elif alignment == "Evil":
        message += "-"
    
    message += f'{alignment.upper()}\n{role}\n{description}\n\nAbilities:\n'

    for ability_name, charges in role_info.get("abilities", {}).items():
        message += f'{ability_name} ['
        if charges == "inf":
            message += "∞"
        else:
            message += f'x{charges}'
        message += "]"
        ability_info = data["abilities"].get(ability_name, {})
        if ability_info.get("rarity", "Not an Any Ability") != "Not an Any Ability":
            if ability_info.get("exclusive", False):
                message += "^"
            else:
                message += "*"
        
        message += f' - {ability_info.get("effect", "N/A")}\n\n'

    message += "Perks:\n"

    for perk_name in role_info.get("perks", []):
        perk_info = data["perks"].get(perk_name, {})
        message += f'{perk_name} - {perk_info.get("effect", "N/A")}\n\n'

    message += "```"
    #print(len(message))
    return message



def setup(bot, INFO_FILE="info.json"):
    @bot.slash_command(name='roleinfo', description="Generates the rolecard for the given role.", guild_ids=[INFO_SERVER_ID])
    @commands.default_member_permissions(administrator=True)
    async def role_info(ctx, role: str):
        message = create_role_message(role, INFO_FILE)
        await ctx.send(message)

    @bot.slash_command(name='createcards', description="Generates the channels/rolecards for each role.", guild_ids=[INFO_SERVER_ID])
    @commands.default_member_permissions(administrator=True)
    async def create_cards(ctx):
        info = openJson(INFO_FILE)

        guild_channel_names = [x.name for x in ctx.guild.channels]

        for role, role_info in info["roles"].items():
            if role_info["alignment"] in ("Good", "Neutral", "Evil"):
                channel_name = role.lower().replace(" ", "-")
                message = create_role_message(role, INFO_FILE)
                if channel_name not in guild_channel_names:
                    alignment_category = disnake.utils.find(lambda c: c.name == role_info["alignment"], ctx.guild.categories)
                    role_channel = await ctx.guild.create_text_channel(name=channel_name, category=alignment_category)
                    await role_channel.set_permissions(ctx.guild.default_role, send_messages=False)
                    await role_channel.send(message)
                    

    @bot.slash_command(name='createitemembeds', description="Generates the item embeds for each rarity.", guild_ids=[INFO_SERVER_ID])
    @commands.default_member_permissions(administrator=True)
    async def itemembed(ctx):
        data = openJson(INFO_FILE)

        guild_channel_names = [x.name for x in ctx.guild.channels]

        rarityColors = {
            "Common": 0x00FF00,
            "Uncommon": 0x00FFFF,
            "Rare": 0x0000FF,
            "Epic": 0xFF00FF,
            "Legendary": 0xFF0000,
            "Mythical": 0xBF40BF,
            "Unique": 0xFFFFFF
            }
        
        for rarity in ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythical", "Unique"):
            channel_name = rarity.lower() + "-items"
    
            embed = disnake.Embed(title=f'{rarity} Items', color=rarityColors[rarity])
            for item, info in data["items"].items():
                if info["rarity"] == rarity:
                    if info["cost"] == 0:
                        cost = "Cannot Be Bought"
                    else:
                        cost = str(info["cost"]) + " coins"
                    embed.add_field(name=f'{item} - [{cost}]', value=f'*{info["effect"]}*', inline=False)
            if channel_name not in guild_channel_names:
                alignment_category = disnake.utils.find(lambda c: c.name == "Items", ctx.guild.categories)
                item_channel = await ctx.guild.create_text_channel(name=channel_name, category=alignment_category)
                await item_channel.set_permissions(ctx.guild.default_role, send_messages=False)
                await item_channel.send(embed=embed)

        
        await ctx.send("Created all item channels.")

    @bot.slash_command(name='createaaslist', description="Generates the aa list for each rarity.", guild_ids=[INFO_SERVER_ID])
    @commands.default_member_permissions(administrator=True)
    async def aalist(ctx):
        data = openJson(INFO_FILE)

        guild_channel_names = [x.name for x in ctx.guild.channels]
        
        title = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
        for i in range(len(title)):
            rarity = title[i]
            channel_name = rarity.lower() + "-aas"

            message = "```\n"
            message += rarity + " AAs\n"
            nonExclusive = []
            exclusive = []
            for ability, aInfo in data["abilities"].items():
                if not aInfo["removed"] and aInfo["rarity"] == rarity:
                    if aInfo["exclusive"]:
                        exclusive.append(f'{ability} [{aInfo["role"]}]')
                    else:
                        nonExclusive.append(ability)
            nonExclusive.sort()
            exclusive.sort()
            for aa in nonExclusive:
                message += aa + "\n"
            for aa in exclusive:
                message += aa + "\n"

            message += "```"

            if channel_name not in guild_channel_names:
                alignment_category = disnake.utils.find(lambda c: c.name == "Any Abilities", ctx.guild.categories)
                item_channel = await ctx.guild.create_text_channel(name=channel_name, category=alignment_category)
                await item_channel.set_permissions(ctx.guild.default_role, send_messages=False)
                await item_channel.send(message)