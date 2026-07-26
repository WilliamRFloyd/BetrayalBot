#Dependencies
import os
import disnake
import random
import json
import re
import asyncio
from dotenv import load_dotenv
from disnake.ext import commands
from disnake import utils
from disnake import TextInputStyle
import datetime
from helper_functions import *
from attr_classes import Game
from shared_data import *

#Category name constants
CONFESSIONALS_CATEGORY = "Confessionals"
ALLIANCES_CATEGORY = "Alliances"

#Creating connenction to discord
load_dotenv()
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='/', intents=intents, case_insensitive=True)

import role_slash_commands
import luck_slash_commands
import info_server
from luck_slash_commands import determine_alliances, set_player_statuses
role_slash_commands.setup(bot, INFO_FILE, GAME_FILE)
luck_slash_commands.setup(bot, INFO_FILE, GAME_FILE, ALLIANCES_CATEGORY, CONFESSIONALS_CATEGORY)
info_server.setup(bot, INFO_FILE)

#Rolls a random item based off luck/rarity and returns it
def itemGen(luckOrRarity):
    data = openJson(INFO_FILE)
    commonItems = [x for x, y in data["items"].items() if y["rarity"] == "Common"]
    uncommonItems = [x for x, y in data["items"].items() if y["rarity"] == "Uncommon"]
    rareItems = [x for x, y in data["items"].items() if y["rarity"] == "Rare"]
    epicItems = [x for x, y in data["items"].items() if y["rarity"] == "Epic"]
    legendaryItems = [x for x, y in data["items"].items() if y["rarity"] == "Legendary"]
    mythicalItems = [x for x, y in data["items"].items() if y["rarity"] == "Mythical"]
    allItems = (commonItems, uncommonItems, rareItems, epicItems, legendaryItems, mythicalItems)

    if type(luckOrRarity) is int:
        return random.choice(allItems[getLuck(luckOrRarity)])
    elif luckOrRarity[-1] == "+":
        newItemsList = []
        for i in range(rarityToNum(luckOrRarity[:-1]), len(allItems)):
            newItemsList += allItems[i]
        return random.choice(newItemsList)
    else:
        return random.choice(allItems[rarityToNum(luckOrRarity)])

#Rolls a random any ability based off luck and returns it
def anyAbilityGen(luckOrRarity, playerRole=None):
    if playerRole != None:
        role = playerRole.role_name
        perks = []
        for perk in playerRole.perks:
            perks.append(perk.name)
    else:
        role = None
        perks = []
    data = openJson(INFO_FILE)
    #Legendary listed twice as for aas legendaries can roll on a legendary or mythical result
    rarities = ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Legendary")
    allAAs = []
    for rarity in rarities:
        rarityAbilities = []
        for x, y in data["abilities"].items():
            if y["rarity"] == rarity and not y["removed"]:
                abilityName = x
                if y["exclusive"]:
                    if role == None:
                        abilityName += f' [{y["role"]}]'
                    elif role != y["role"] and "Eternal Hunger" not in perks:
                        continue
                rarityAbilities.append(abilityName)
        allAAs.append(rarityAbilities)
    

    if type(luckOrRarity) is int:
        return random.choice(allAAs[getLuck(luckOrRarity)])
    elif luckOrRarity[-1] == "+":
        newAAsList = []
        for i in range(rarityToNum(luckOrRarity[:-1]), len(allAAs)):
            newAAsList += allAAs[i]
        return random.choice(newAAsList)
    else:
        return random.choice(allAAs[rarityToNum(luckOrRarity)])


#Event handler

#Code that runs when bot first runs
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connencted to Discord!')

    if not os.path.exists(GAME_FILE):
        with open(GAME_FILE, "w") as f:
            json.dump({}, f, indent=4)
        print(f'{GAME_FILE} not found, created.')

    betrayal_main_server_id = 490904847701245952

    data = openJson(GAME_FILE)

    if str(betrayal_main_server_id) in data.keys():
        Data.game_data = Game.load_data(betrayal_main_server_id, data[str(betrayal_main_server_id)])
    else:
        Data.game_data = Game(betrayal_main_server_id, "Betrayal")
        save_game_data()

    #with open('betrayal.png', 'rb') as f:
    #    icon = f.read()
    #await guild.edit(icon=icon)


#Code that runs upon someone joining the server
@bot.event
async def on_member_join(member):
    pass

#Things actually relavant to betrayal
#Checks
@bot.slash_command(description="List all objects of the category that don't have the attribute filled out in the info file")
async def listmissing(ctx, obj_type: str, attribute: str):
    data = openJson(INFO_FILE)

    if obj_type not in data.keys():
        await ctx.send("Object type not found")
        return

    objList = []
    for obj, info in data[obj_type].items():
        if attribute not in info.keys():
            await ctx.send("Attribute not found")
            return
        if not info[attribute]:
            objList.append(obj)
    objString = "\n".join(objList)

    start = 0
    while start < len(objString):
        end = start + 2000
        if end >= len(objString):
            await ctx.send(objString[start:])
            break
        while objString[end] != "\n":
            end -= 1
        await ctx.send(objString[start:end])
        start = end + 1
    return

#Checking if luck gen is working correctly
@bot.command(name='itemcheck')
async def itemCheck(ctx, arg1):
    #print("test")
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    arg1 = int(arg1)
    numChecks = 10000
    countDict = {}
    for i in range(numChecks):
        item = itemGen(arg1)
        rarity = data["items"][item]["rarity"]
        countDict[rarity] = countDict.get(rarity, 0) + 1
    print(f'Count Dict {countDict}')
    await ctx.send(str(countDict))
        

#Code for item rain
@bot.command(name='item', help="Proper format: '/item [luck]'. If no luck is specified, it defaults to 0.")
async def itemRain(ctx, arg1="0", arg2="1", arg3=0):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not "confessional" in ctx.channel.name and not ctx.author.name == "bluedetroyer":
        await ctx.send(f'Do this is bots channel')
        return
    arg2 = int(arg2)
    if arg2 > 50:
        await ctx.send(f'Capped at 50')
        arg2 = 50
    if arg1.isdigit():
        arg1 = int(arg1)
        for i in range(arg2):
            numItems = random.randint(1,6)
            if numItems <= 3:
                numItems = 1
            elif numItems <= 5:
                numItems = 2
            else:
                numItems = 3
            if arg3 != 0:
                numItems = 4 - numItems
            itemList = []
            for i in range(numItems):
                itemList.append(itemGen(arg1))   
            await ctx.send(f'Items:{formatList(itemList)}')
    else:
        for i in range(arg2):
            item = itemGen(arg1)
            await ctx.send(f'Item: {item}')

#Code for rolling any abilities
@bot.command(name='aa', help="Proper format: '/aa [luck]'. If no luck is specified, it defaults to 0.")
async def anyAbility(ctx, arg1="0", arg2="1"):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not "confessional" in ctx.channel.name:
        await ctx.send(f'Do this is bots channel')
        return
    arg2 = int(arg2)
    if arg2 > 50:
        await ctx.send(f'Capped at 50')
        arg2 = 50
    if arg1.isdigit():
        arg1 = int(arg1)
        for i in range(arg2):
            anyAbility = anyAbilityGen(arg1)
            await ctx.send(f'Any Ability: {anyAbility}')
    else:
        for i in range(arg2):
            anyAbility = anyAbilityGen(arg1)
            await ctx.send(f'Any Ability: {anyAbility}')

#Code for rolling carepackages
#@bot.slash_command(description="Generate a carepackage with the appropriate luck")
@bot.command(name='carepackage', help="Proper format: '/carepackage [luck]'. If no luck is specified, it defaults to 0.")
async def carepackage(ctx, arg1 = "0", arg2 = "1"):
    arg1 = int(arg1)
    arg2 = int(arg2)
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not "confessional" in ctx.channel.name:
        await ctx.send(f'Do this is bots channel')
        return
    if arg2 > 50:
        await ctx.send(f'Capped at 50')
        arg2 = 50
    for i in range(arg2):
        item = itemGen(arg1)
        anyAbility = anyAbilityGen(arg1)
        await ctx.send(f'Carepackage:\nItem: {item}\nAny Ability: {anyAbility}')
    return

#Code for viewing information of a specific item
@bot.slash_command(description="View the information about the specified item")
async def viewitem(ctx, item: str, additional_info: bool = False, hidden: bool = False):
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    rarityColors = {
        "Common": 0x00FF00,
        "Uncommon": 0x00FFFF,
        "Rare": 0x0000FF,
        "Epic": 0xFF00FF,
        "Legendary": 0xFF0000,
        "Mythical": 0xBF40BF,
        "Unique": 0xFFFFFF,
        "Special": 0xFAED27
        }

    response = ""
    itemList = []
    closestItem = ""
    for i, info in data["items"].items():
        if item.lower() == i.lower():
            closestItem = i
            break
        else:
            itemList.append(i)

    if closestItem == "":
        closestItem = find_most_similar_string(item, itemList)
        response = f'Item not found, did you mean __{closestItem}__?'
    
    name = closestItem
    info = data["items"][closestItem]
    rarity = info["rarity"]
    cost = info["cost"]
    if cost == 0:
        cost = "Cannot Be Bought"
    else:
        cost = str(cost) + " coins"
    effect = info["effect"]
    embed = disnake.Embed(title=f'{name}', description=f'{rarity}', color=rarityColors[rarity])
    embed.add_field(name=f'Cost:', value=f'{cost}', inline=False)
    embed.add_field(name=f'Effect:', value=f'*{effect}*', inline=False)
    if additional_info:
        upgradeStr = f''
        upgrades = info["upgrades"]
        '''
        if "Cannot be burnt" not in effect:
            upgrades.append(f'{effect} Cannot be burnt.')
        if "Cannot be stolen" not in effect:
            upgrades.append(f'{effect} Cannot be stolen.')
        '''
        for upgrade in upgrades:
            upgradeStr += f'\n*{upgrade}*'
        embed.add_field(name=f'Upgrades:', value=f'{upgradeStr}', inline=False)
        targeting = info["targeting"]
        if targeting == "":
            targeting = "Unspecified"
        embed.add_field(name=f'Targeting:', value=f'{targeting}', inline=False)
        actionTypes = ", ".join(info["actionTypes"])
        if actionTypes == "":
            actionTypes = "Not Applicable"
        embed.add_field(name=f'Action Types:', value=f'{actionTypes}', inline=False)
        additionalInfo = info["additionalInfo"]
        if additionalInfo != "":
            embed.add_field(name=f'Additional Information:', value=f'{additionalInfo}', inline=False)
    await ctx.send(response, embed=embed, ephemeral=hidden)
    return

#Code for viewing information of a specific role
#@bot.command(name='viewrole', help="View the information about the specified role")
@bot.slash_command(description="View the information about the specified role")
async def viewrole(ctx, role: str, hidden: bool = False):
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    alignmentColors = {
        "Good": 0x00FF00,
        "Neutral": 0x888888,
        "Neutral (Removed)": 0x888888,
        "Evil": 0xFF0000,
        "Ball": 0xFFFFFF,
        "Traveller": 0xFFFF00
        }

    response = ""
    roleList = []
    closestRole = ""
    for r, info in data["roles"].items():
        if role.lower() == r.lower():
            closestRole = r
            break
        else:
            roleList.append(r)
            
    if closestRole == "":
        closestRole = find_most_similar_string(role, roleList)
        response = f'Item not found, did you mean __{closestRole}__?'
        
    info = data["roles"][closestRole]
    name = closestRole
    alignment = info["alignment"]
    description = info["description"]
    abilities = info["abilities"]
    perks = info["perks"]
    
    embed = disnake.Embed(title=f'{name}', description=f'**{alignment}**\n{description}\n\n**Abilities:**', color=alignmentColors[alignment])
    i = 0
    for ability, charges in abilities.items():
        if charges == -1:
            charges = "inf"
        aInfo = data["abilities"][ability]
        extra = ""
        aamarker = ""
        i += 1
        if not aInfo["exclusive"]:
            aamarker = "*"
        elif aInfo["rarity"] != "Not an Any Ability":
            aamarker = "^"
        if i == len(abilities):
            extra = "\n\n**Perks:**"
        embed.add_field(name=f'{ability} [x{charges}]{aamarker}', value=f'{aInfo["effect"]}{extra}', inline=False)
    i = 0
    for perk in perks:
        i += 1
        embed.add_field(name=f'{perk}', value=f'{data["perks"][perk]["effect"]}', inline=False)
    await ctx.send(response, embed=embed, ephemeral=hidden)

#Code for viewing information of a specific ability
@bot.slash_command(description="View the information about the specified ability")
async def viewability(ctx, ability: str, additional_info: bool = False, hidden: bool = False):
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    rarityColors = {
        "Common": 0x00FF00,
        "Uncommon": 0x00FFFF,
        "Rare": 0x0000FF,
        "Epic": 0xFF00FF,
        "Legendary": 0xFF0000,
        "Not an Any Ability": 0x888888
        }

    response = ""
    abilityList = []
    closestAbility = ""
    for a, info in data["abilities"].items():
        if ability.lower() == a.lower():
            closestAbility = a
            break
        else:
            abilityList.append(a)

    if closestAbility == "":
        closestAbility = find_most_similar_string(ability, abilityList)
        response = f'Ability not found, did you mean __{closestAbility}__?'

    
    abilityInfo = data["abilities"][closestAbility]
    name = closestAbility
    rarity = abilityInfo["rarity"]
    abilityColor = rarityColors[rarity]
    if rarity != "Not an Any Ability" and abilityInfo["exclusive"]:
        rarity += " (Role Exclusive)"
    effect = abilityInfo["effect"]
    embed = disnake.Embed(title=f'{name}', description=f'{rarity}', color=abilityColor)
    embed.add_field(name=f'Effect:', value=f'{effect}', inline=False)
    embed.add_field(name=f'From Role:', value=f'{abilityInfo["role"]}', inline=False)
    if additional_info:
        
        
        upgradeStr = f''
        upgrades = abilityInfo["upgrades"]
        for upgrade in upgrades:
            upgradeStr += f'\n*{upgrade}*'
        embed.add_field(name=f'Upgrades:', value=f'{upgradeStr}', inline=False)

        degradeStr = f''
        degrades = abilityInfo["degrades"]
        for degrade in degrades:
            degradeStr += f'\n{degrade}'
        embed.add_field(name=f'Degrades:', value=f'{degradeStr}', inline=False)
        
        targeting = abilityInfo["targeting"]
        if targeting == "":
            targeting = "Unspecified"
        embed.add_field(name=f'Targeting:', value=f'{targeting}', inline=False)
        
        actionTypes = ", ".join(abilityInfo["actionTypes"])
        if actionTypes == "":
            actionTypes = "Not Applicable"
        embed.add_field(name=f'Action Types:', value=f'{actionTypes}', inline=False)
        additionalInfo = abilityInfo["additionalInfo"]
        if additionalInfo != "":
            embed.add_field(name=f'Additional Information:', value=f'{additionalInfo}', inline=False)
    await ctx.send(response, embed=embed, ephemeral=hidden)

#Code for viewing information of a specific perk
@bot.slash_command(description="View the information about the specified perk")
async def viewperk(ctx, perk: str, additional_info: bool = False, hidden: bool = False):
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()

    response = ""
    perkList = []
    closestPerk = ""
    for p, effect in data["perks"].items():
        if perk.lower() == p.lower():
            closestPerk = p
            break
        else:
            perkList.append(p)
    
    if closestPerk == "":
        closestPerk = find_most_similar_string(perk, perkList)
        response = f'Perk not found, did you mean __{closestPerk}__?'

    info = data["perks"][closestPerk]
    
    embed = disnake.Embed(title=f'{closestPerk}', description=f'{info["effect"]}')
    embed.add_field(name=f'From Role:', value=f'{info["role"]}', inline=False)
    if additional_info:
        upgradeStr = f''
        upgrades = info["upgrades"]
        for upgrade in upgrades:
            upgradeStr += f'\n{upgrade}'
        embed.add_field(name=f'Upgrades:', value=f'{upgradeStr}', inline=False)

        degradeStr = f''
        degrades = info["degrades"]
        for degrade in degrades:
            degradeStr += f'\n{degrade}'
        embed.add_field(name=f'Degrades:', value=f'{degradeStr}', inline=False)
        
        additionalInfo = info["additionalInfo"]
        if additionalInfo != "":
            embed.add_field(name=f'Additional Information:', value=f'{additionalInfo}', inline=False)
    await ctx.send(response, embed=embed, ephemeral=hidden)
    return

#Code for viewing information of a specific status
@bot.slash_command(description="View the information about the specified status")
async def viewstatus(ctx, status: str, hidden: bool = False):
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    statusColors = {
        "Lucky": 0x00FF00, #Green
        "Unlucky": 0xFF0000, #Red
        "Cursed": 0x888888, #Gray
        "Frozen": 0xA5F2F3, #Ice color
        "Paralyzed": 0xFFFF00, #Yellow
        "Burned": 0xE25822, #Orangeish
        "Empowered": 0xFFFF33, #Neon Yellow
        "Drunk": 0x964B00, #Brown
        "Restrained": 0x222222, #Darker Gray
        "Disabled": 0xCCCCCC, #Light Gray
        "Despaired": 0x555555, #Dark Gray
        "Blackmailed": 0x000000 #Black
        }

    response = ""
    statusList = []
    closestStatus = ""
    for s, info in data["statuses"].items():
        if status.lower() == s.lower() or status.lower() + "ed" == s.lower() or status.lower() + "d" == s.lower():
            closestStatus = s
            break
        else:
            statusList.append(s)

    if closestStatus == "":
        closestStatus = find_most_similar_string(status, statusList)
        response = f'Perk not found, did you mean __{closestStatus}__?'

    embed = disnake.Embed(title=f'{closestStatus}', description=f'{data["statuses"][closestStatus]["effect"]}', color=statusColors[closestStatus])
    await ctx.send(response, embed=embed, ephemeral=hidden)
    return


@bot.command(name='itemslist')
async def itemembed(ctx):
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
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
        embed = disnake.Embed(title=f'{rarity} Items', color=rarityColors[rarity])
        for item, info in data["items"].items():
            if info["rarity"] == rarity:
                if info["cost"] == 0:
                    cost = "Cannot Be Bought"
                else:
                    cost = str(info["cost"]) + " coins"
                embed.add_field(name=f'{item} - [{cost}]', value=f'*{info["effect"]}*', inline=False)
        await ctx.send(embed=embed)

@bot.command(name='aalist')
async def aalist(ctx):
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    
    title = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
    for i in range(len(title)):
        rarity = title[i]
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
        await ctx.send(message)
        

#Vote moment
@bot.command(help="")
async def vote(ctx, *args):
    arg2 = ("set",) + args
    await inventories(ctx, "vote", *arg2)

@bot.slash_command(description="List all roles of the specified alignment")
async def view_alignment(
    ctx,
    alignment: str = commands.Param(choices={"Good": "Good", "Neutral": "Neutral", "Evil": "Evil"})):
    info = openJson(INFO_FILE)
    roleList = []
    for k, v in info["roles"].items():
        if v["alignment"] == alignment:
            roleList.append(k)
    roleString = f'{alignment} Roles:\n'
    roleString += "\n".join(roleList)
    await ctx.send(roleString)


@bot.slash_command(description="Lists the contents of the specified section of each player's inventories.", guild_ids=[490904847701245952, 379383629010436096])
@commands.default_member_permissions(administrator=True)
async def view(
    ctx,
    section: str = commands.Param(choices={"Coins": "coins", "Bonus": "bonus", "Items": "items", "AAs": "aas", "Statuses": "statuses", "Effects": "effects", "Immunities": "immunities", "Votes": "vote"}),
    search_for: str = "",
    alive_only: bool = True):

    check_active_game(ctx.guild)

    set_player_statuses(ctx.guild)
    listStr = f'{section.capitalize()}\n'
    for player in Data.game_data.players:
        inventory = player.inventory
        if inventory is None:
            continue
        if not player.in_play():
            continue
        if not player.can_gain() and alive_only:
            continue

        if inventory.has_section(section):
            inv_section = inventory.get_section(section)
            player_name = player.conf_name.replace("-confessional", "")
            listStr += f"{player_name}: "
            if inv_section.category in ("dict", "list"):
                listStr += ", ".join([item for item in inv_section.contents if search_for.lower() in item.lower()])
            else:
                listStr += str(inv_section.contents)
            listStr += "\n"
    await ctx.send(listStr)

@bot.command(help='')
async def clearvotes(ctx):
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"])):
        await ctx.send("Nice Try")
        return
    check_active_game(ctx.guild)
    for player in Data.game_data.players:
        inventory = player.inventory
        if inventory is not None:
            inventory.get_section("vote").contents = []

    save_game_data()
    await ctx.send("Votes cleared")

#Code for retrieving game file (for when I'm away from my desktop so I can grab a backup in case it goes down)
@bot.slash_command(name="retrieve_file", description="Retrieve game file", guild_ids=[379383629010436096])
@commands.default_member_permissions(administrator=True)
async def retrieve_file(ctx):
    blueId = 323923179267555331
    if ctx.author.id != blueId:
        await ctx.send("no")
        return
    f = open(GAME_FILE, "rb")
    diFile = disnake.File(f, filename="inventoryInfo.json")
    await ctx.send(file=diFile)


#Code for managing all inventories
@bot.slash_command(name='all_invs', description="Manage all inventories.")
@commands.default_member_permissions(administrator=True)
async def all_invs(ctx):
    pass

@all_invs.sub_command(name='clear', description="Removes all inventories.")
async def clear_all_invs(ctx):
    await ctx.response.defer()
    check_active_game(ctx.guild)

    for player in Data.game_data.players:
        player.remove_inventory()

    save_game_data()
    await ctx.edit_original_response("Inventories cleared.")

@all_invs.sub_command(name='create', description="Creates blank inventories for all confessionals without one.")
async def create_all_invs(ctx):
    await ctx.response.defer()
    check_active_game(ctx.guild)

    for player in Data.game_data.players:
        player.add_inventory()

    save_game_data()
    await ctx.edit_original_response("Inventories created.")

#Code for managing inventories
@bot.command(aliases=['inventory', 'inv', "i"], help='')
async def inventories(ctx, arg1="", *arg2):
    if not isinstance(ctx, disnake.TextChannel):
        channel = ctx.channel
    else:
        channel = ctx
    #Authorization check
    #if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host", "Partcipant", "Deceased"])):
    #    await ctx.send("You don't have permession to edit inventories in this channel")
    #    return
    
    check_active_game(ctx.guild)

    name = channel.name

    if arg1.lower() != "create":
        if (not Data.game_data.has_player(name)) or (Data.game_data.get_player(name).inventory is None):
            await ctx.send("There's no inventory for this channel. Please create one first.")
            return
        
        player = Data.game_data.get_player(name)
        inventory = player.inventory
        message = await channel.fetch_message(inventory.message_id)

    #Creating inventory
    if arg1.lower() == "create":
        if (Data.game_data.has_player(name)) and (Data.game_data.get_player(name).inventory is not None):
            await ctx.send("There's already an inventory for that channel. Please delete/forget it if you want to make a new one")
            return

        if (not Data.game_data.has_player(name)):
            Data.game_data.add_player(name, channel.id)

        inventory = Data.game_data.get_player(name).add_inventory()
        inventoryId = await channel.send(str(inventory))
        inventory.message_id = inventoryId.id

        save_game_data()

        
    #Deletes the inventory message from the channel and removes it from the json file
    elif arg1.lower() == "delete":
        player.remove_inventory()
        await message.delete()

        save_game_data()
    #Removes the inventory from the json file but leaves the message
    elif arg1.lower() == "forget":
        player.remove_inventory()

        save_game_data()
    #Prints a copy of the inventory that doesn't get updated
    elif arg1.lower() in ("send", "s"):
        await ctx.send(content=str(inventory))
    #Sends a new message of the inventory that gets updated instead of the old one
    elif arg1.lower() == "refresh":
        message = await ctx.send(content=str(inventory))
        inventory.message_id = message.id

        save_game_data()
    #Invalid arguments
    elif arg1 == "":
        await ctx.send("No argument found")
    else:
        result = inventory.process_command(arg1, arg2)

        if result:
            await message.edit(str(inventory))
        else:
            await ctx.send("Command not recognized")

        save_game_data()
 
#Code for picking a random role
@bot.command(name='randomrole', help='You people keep pasting in super long messages to do this please stop')
async def randomRole(ctx, arg1=""):
    if arg1.lower() in ("decept", "deceptionist"):
        await randomRole(ctx, "good")
        await randomRole(ctx, "neutral")
        await randomRole(ctx, "evil")
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    roleList = []
    for roleName, info in data["roles"].items():
        if arg1 != "" and info["alignment"].lower() != arg1.lower():
            continue
        roleList.append(roleName)
    await ctx.send(random.choice(roleList))

#Stuff related to the group chat server
#Channel Creation for 1-1 chats
@bot.slash_command(description="Creates roles and 1-1 chats for the specified number of players.")
@commands.default_member_permissions(administrator=True)
async def genchats(ctx, num_players: int):
    await ctx.send("Setting up chats/roles", ephemeral=True)
    guildRoleNames = [x.name for x in ctx.guild.roles]
    guildCategoryNames = [x.name for x in ctx.guild.categories]

    basicRoles = ["Spectator", "Partcipant", "Dead"]

    if "Host" not in guildRoleNames:
        await ctx.guild.create_role(name="Host", permissions=disnake.Permissions(administrator=True))
    for role in basicRoles:
        if role not in guildRoleNames:
            await ctx.guild.create_role(name=role)

    for i in range(1, num_players + 1):
        roleName = str(i)
        if roleName not in guildRoleNames:
            await ctx.guild.create_role(name=roleName)

    categoryName = "Confessionals"
    if categoryName in guildCategoryNames:
        currentCategory = disnake.utils.find(lambda c: c.name == categoryName, ctx.guild.categories)
    else:
        currentCategory = await ctx.guild.create_category(name=categoryName)
    for i in range(1, num_players + 1):
        channelName = str(i)
        categoryChannelNames = [x.name for x in currentCategory.channels]
        if channelName not in categoryChannelNames:
            overwrites = {
                ctx.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                disnake.utils.find(lambda r: r.name == str(i), ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                disnake.utils.find(lambda r: r.name == "Host", ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                disnake.utils.find(lambda r: r.name == "Spectator", ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True)
            }
            channel = await ctx.guild.create_text_channel(f'{i}', overwrites=overwrites, category=currentCategory)
    
    for i in range(1, num_players):
        categoryName = str(i)
        if categoryName in guildCategoryNames:
            currentCategory = disnake.utils.find(lambda c: c.name == categoryName, ctx.guild.categories)
        else:
            currentCategory = await ctx.guild.create_category(name=categoryName)
        for j in range(i+1, num_players + 1):
            categoryChannelNames = [x.name for x in currentCategory.channels]
            channelName = f'{i}-{j}'
            if channelName not in categoryChannelNames:
                overwrites = {
                    ctx.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                    disnake.utils.find(lambda r: r.name == str(i), ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                    disnake.utils.find(lambda r: r.name == str(j), ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                    disnake.utils.find(lambda r: r.name == "Host", ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                    disnake.utils.find(lambda r: r.name == "Spectator", ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True)
                }
                channel = await ctx.guild.create_text_channel(f'{i}-{j}', overwrites=overwrites, category=currentCategory)
    
#Empties out GC Server (For testing)
@bot.command(name='clearroles')
async def clearRoles(ctx):
    if ctx.guild.name == "Test Channel Creation" or ctx.guild.name == "Betrayal 38":
        for role in ctx.guild.roles:
            if role.name.isdigit() or role.name in ["Host", "Spectator", "Participant", "Dead"]:
                await role.delete()
        print("Roles done")
        for category in ctx.guild.categories:
            if category.name.isdigit() or category.name == "Confessionals":
                await category.delete()
        print("Categories done")
        for channel in ctx.guild.text_channels:
            if "-" in channel.name or channel.name.isdigit():
                await channel.delete()
        print("Channels done")

#Code for managing confessional links
@bot.slash_command(name='link', description="Manage links from users to their confessional.")
@commands.default_member_permissions(administrator=True)
async def link(ctx):
    check_active_game(ctx.guild)

@link.sub_command(name='clear', description="Clears all confLinks.")
async def link_clear(ctx):
    Data.game_data.remove_links()

    save_game_data()
    await ctx.send("confLinks cleared.")

@link.sub_command(name='confs', description="Generates confLinks based on current confessionals and their members.")
async def link_confs(ctx):
    if not Data.game_data.links_empty():
        await ctx.send("confLinks is not empty, please clear it first.")
        return

    conf_category_name = Data.game_data.conf_category_name
    conf_category = disnake.utils.find(lambda c: c.name == conf_category_name, ctx.guild.categories)
    if not conf_category:
        await ctx.send(f"No {conf_category_name} category found.")
        return
    for channel in conf_category.channels:
        for member in channel.members:
            if compareLists(member.roles, ["Participant"]):
                Data.game_data.add_link(member.id, channel.name)

    save_game_data()
    await ctx.send("confLinks generated from current confessionals.")

@link.sub_command(name='view', description="Views current confLinks.")
async def link_view(ctx):
    await ctx.response.defer()

    message = "Current confLinks:\n"
    for userId, channelName in Data.game_data.conf_links.items():
        user = await bot.fetch_user(int(userId))
        message += f'{user.name}: "{channelName}"\n'
    await ctx.edit_original_response(message)

@link.sub_command(name='add', description="Adds a confLink from the specified user to the specified channel.")
async def link_add(ctx, user: disnake.User, channel: str):
    if channel not in [c.name for c in ctx.guild.channels]:
        await ctx.send(f'Channel "{channel}" not found.')
        return
    if user.id in Data.game_data.conf_links.keys():
        await ctx.send(f'User {user.name} is already linked to "{Data.game_data.conf_links[user.id]}".')
        return

    Data.game_data.conf_links[user.id] = channel

    save_game_data()
    await ctx.send(f'Link added: {user.name} -> "{channel}".')

@link.sub_command(name='remove', description="Removes the confLink for the specified user.")
async def link_remove(ctx, user: disnake.User):
    user_existed = Data.game_data.remove_link(user.id)
    if not user_existed:
        await ctx.send(f'No confLink found for user {user.name}.')
        return

    save_game_data()
    await ctx.send(f'Link removed for user {user.name}.')
#End of confessional link code

#Sending code
@bot.slash_command(name='send', description="Manage automatic sending of coins, carepackages, items, and aas.")
@commands.default_member_permissions(administrator=True)
async def send(ctx):
    check_active_game(ctx.guild)

@send.sub_command(name="coins", description='Shows a list of how many coins each confessional should get, and shows button to approve it.')
async def send_coins(ctx):
    alliances = determine_alliances(ctx.guild)

    coinString = "Calculated Coins:\n"
    for player in Data.game_data.players:
        if not player.can_gain() or player.inventory is None:
            continue

        confCoins = 200
        bonus = player.inventory.get_section("bonus").contents
        confCoins += bonus * 2
        
        for allianceName, members in alliances.items():
            if player in members:
                numMembers = len(members)
                if numMembers == 2:
                    confCoins += 20
                elif numMembers == 3:
                    confCoins += 40
                elif numMembers >= 4:
                    confCoins += 100

        statuses = [x.lower() for x in player.inventory.get_section("status").contents]
        if "lucky" in statuses:
            confCoins *= 1.5
        if "unlucky" in statuses:
            confCoins *= .5 
        player.calced_coins = int(confCoins)
        coinString += f'{player.conf_name}: {int(confCoins)}\n'
    
    save_game_data()
    await ctx.send(coinString, components=[
            disnake.ui.Button(label="Distribute", style=disnake.ButtonStyle.success, custom_id="send_coins"),
        ])

@send.sub_command(name="carepackages", description='Shows a list of how what carepackage each confessional should get, and shows button to approve it.')
async def send_carepackages(ctx):
    lucky_coin_receiever = random.choice([player for player in Data.game_data.players if player.can_gain() and player.inventory is not None])
    carepackageString = "Calculated Carepackages:\n"
    for player in Data.game_data.players:
        if not player.can_gain() or player.inventory is None:
            continue

        luck = player.luck
        
        role = player.role

        item = itemGen(luck)
        aa = anyAbilityGen(luck, role)

        player.calced_items = [item]
        player.calced_aas = [aa]

        if player is lucky_coin_receiever:
            player.calced_items.append("Lucky Coin")

        carepackageString += f'{player.conf_name} ({luck}): {item}, {aa}\n'
    carepackageString += f'Lucky Coin: {lucky_coin_receiever.conf_name}'
    
    save_game_data()
    await ctx.send(carepackageString, components=[
            disnake.ui.Button(label="Distribute", style=disnake.ButtonStyle.success, custom_id="send_carepackages"),
        ])

@send.sub_command(name="items", description='Shows a list of how what items each confessional should get, and shows button to approve it.')
async def send_items(ctx):
    itemString = "Calculated Items:\n"
    for player in Data.game_data.players:
        if not player.can_gain() or player.inventory is None:
            continue
        luck = player.luck
        
        items = []
        i = random.randint(1,6)
        count = 3
        if i <= 3:
            count = 1
        elif i <=5:
            count = 2
        for j in range(count):
            items.append(itemGen(luck))

        player.calced_items = items

        itemString += f'{player.conf_name} ({luck}): {", ".join(items)}\n'
    
    save_game_data()
    await ctx.send(itemString, components=[
            disnake.ui.Button(label="Distribute", style=disnake.ButtonStyle.success, custom_id="send_items"),
        ])

@send.sub_command(name="aas", description='Shows a list of how what aas each confessional should get, and shows button to approve it.')
async def send_aas(ctx):
    aaString = "Calculated Items:\n"
    for player in Data.game_data.players:
        if not player.can_gain() or player.inventory is None:
            continue

        luck = player.luck
        
        role = player.role

        aa = anyAbilityGen(luck, role)

        player.calced_aas = [aa]

        aaString += f'{player.conf_name} ({luck}): {aa}\n'
    
    save_game_data()
    await ctx.send(aaString, components=[
            disnake.ui.Button(label="Distribute", style=disnake.ButtonStyle.success, custom_id="send_aas"),
        ])


async def distributeCoins(server: disnake.Guild):
    check_active_game(server)

    participant = disnake.utils.find(lambda r: r.name == "Participant", server.roles)
    for player in Data.game_data.players:
        if player.inventory is None:
            continue
        player.inventory.get_section("coins").contents += player.calced_coins

    save_game_data()

    for player in Data.game_data.players:
        channel = server.get_channel(player.channel_id)
        await inventories(channel, "coins", "add", "0") #To update inventory
        await channel.send(f'{participant.mention} You got {player.calced_coins} coins')

async def distributeCarepackages(server):
    check_active_game(server)

    participant = disnake.utils.find(lambda r: r.name == "Participant", server.roles)
    for player in Data.game_data.players:
        if player.inventory is None:
            continue
        player.inventory.get_section("items").contents += player.calced_items
        for aa in player.calced_aas:
            player.inventory.process_command("aa", ["add", aa])

    save_game_data()

    for player in Data.game_data.players:
        channel = server.get_channel(player.channel_id)
        await inventories(channel, "coins", "add", "0") #To update inventory
        await channel.send(f'{participant.mention} Item: {", ".join(player.calced_items)}\nAny Ability: {", ".join(player.calced_aas)}')

async def distributeItems(server):
    check_active_game(server)

    participant = disnake.utils.find(lambda r: r.name == "Participant", server.roles)
    for player in Data.game_data.players:
        if player.inventory is None:
            continue
        player.inventory.get_section("items").contents += player.calced_items

    save_game_data()

    for player in Data.game_data.players:
        channel = server.get_channel(player.channel_id)
        await inventories(channel, "coins", "add", "0") #To update inventory
        await channel.send(f'{participant.mention} You got {", ".join(player.calced_items)}')

async def distributeAas(server):
    check_active_game(server)

    participant = disnake.utils.find(lambda r: r.name == "Participant", server.roles)
    for player in Data.game_data.players:
        if player.inventory is None:
            continue
        for aa in player.calced_aas:
            player.inventory.process_command("aa", ["add", aa])

    save_game_data()

    for player in Data.game_data.players:
        channel = server.get_channel(player.channel_id)
        await inventories(channel, "coins", "add", "0") #To update inventory
        await channel.send(f'{participant.mention} You got {", ".join(player.calced_aas)}')

'''
Planned Commands:
/alias - Slash command base for managing confessional aliases (aliases are not cleared between games). Admin only.
    add {alias} {user} - Adds an alias for the specified user. Returns an error message if that alias is already taken.
    remove {alias} - Removes the specified alias
    view - Sends a message of the current aliases in a {alias}: {username} format
    clear - Clears all aliases

/send - Slash command base for automatically doing coins/carepackages/etc. Admin only
    coins - Shows a list of how many coins the bot thinks each confessional should get, and shows buttons for the host to approve it. If approved, the bot will distribute it to each confessional and alert the players.
    carepackages - Shows a list of rolled carepackages and luck for each confessional, and shows buttons for the host to either approve or reject it. If approved, the bot will distribute it to each confessional and alert the players.
    items - Shows a list of rolled item rains and luck for each confessional, and shows buttons for the host to either approve or reject it. If approved, the bot will distributetribute it to ea it to each confessional and alert the players.
    aas - Shows a list of rolled aas and luck for each confessional, and shows buttons for the host to either approve or reject it. If approved, the bot will disch confessional and alert the players.
    view {coins/aas/items} - Views last rolled {}
    last {coins/aas/items} - Adds last rolled {} to each person's inventory
    undo {coins/aas/items} - Removes the latest rolled {} from each person's inventory
    add {coins/aas/items} {player} {int for coins or string for aa/item} - Adds {} to the specified player's confessional {}
    remove {coins/aas/items} {player} {int for coins or string for aa/item} - Remoes {} from the specified player's confessional {}
'''



#Random Stuff
@bot.command(name='roll', help='[num]d[sides]')
async def roll(ctx, arg):
    numDice = int(arg.split("d")[0])
    diceSides = int(arg.split("d")[1])
    string = "Roll(s): "
    count = 0
    for i in range(numDice):
        value = random.randint(1, diceSides)
        string += str(value)
        count += value
        if i != numDice-1:
            string += ", "
    string += f'\nResult: {count}'

    await ctx.send(string)

@bot.command(name='die', help='Perish')
async def death(ctx):
    await ctx.send(f'{ctx.author.mention} is now dead. You may pay your condolences.')

@bot.command(name='kill', help='Commit a murder')
async def kill(ctx, arg1):
    for member in ctx.guild.members:
        if member.name.lower() == arg1.lower() or member.name == arg1 or member.mention == arg1 or member.mention == "<@" + "!" + arg1[2:]:
            target = member
            if target.name == "bluedetroyer":
                await ctx.send(f'I\'m afraid I can\'t do that {ctx.author.mention}')
            else:
                await ctx.send(f'{ctx.author.mention} brutally shot {target.mention} to death')

@bot.command(name='superkill', help='Commit a super murder')
async def superKill(ctx, *arg1):
    for arg in arg1:
        for member in ctx.guild.members:
            if member.name.lower() == arg.lower() or member.name == arg or member.mention == arg or member.mention == "<@" + "!" + arg[2:]:
                target = member
                if target.name == "bluedetroyer":
                    await ctx.send(f'I\'m afraid I can\'t do that {ctx.author.mention}')
                else:
                    await ctx.send(f'{ctx.author.mention} super brutally shot {target.mention} to death like a super amount of times')
@bot.command(name='kidneysnatch')
async def stealKidney(ctx, arg1):
    for member in ctx.guild.members:
        if member.name.lower() == arg1.lower() or member.name == arg1 or member.mention == arg1 or member.mention == "<@" + "!" + arg1[2:]:
            target = member
            file = open("kidneys.json")
            data = json.load(file)
            file.close()
            if target.name in data:
                data[target.name] -= 1
            else:
                data[target.name] = 1
            if ctx.author.name in data:
                data[ctx.author.name] += 1
            else:
                data[ctx.author.name] = 3
            file = open("kidneys.json", "w")
            file.write(json.dumps(data, indent=4))
            file.close()
            await ctx.send(f'{ctx.author.mention} has stolen {target.mention}\'s kidney. {ctx.author.mention} now has {data[ctx.author.name]} kidney(s) while {target.mention} has {data[target.name]}')
            

@bot.command(name='test', help='test')
async def sendMessage(ctx, arg1, arg2):
    if ctx.author.name == 'bluedetroyer':
        guildChannels = bot.guilds[1].channels
        #lostRole = disnake.utils.find(lambda r: r.name == "Lost", ctx.guild.roles)
        for channel in guildChannels:
            if channel.name == arg1:
                await channel.send(arg2)                       
                

@bot.command(name='button')
async def buttonTest(ctx: disnake.ApplicationCommandInteraction):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not ctx.author.name == "bluedetroyer":
        await ctx.send(f'Do this in bots channel')
        return
    await ctx.send("Button", components=[
            disnake.ui.Button(label="Button", style=disnake.ButtonStyle.success, custom_id="yes"),
            disnake.ui.Button(label="Also Button", style=disnake.ButtonStyle.danger, custom_id="no"),
        ])

@bot.command(name='deceptPick')
async def deceptPick(ctx: disnake.ApplicationCommandInteraction):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not ctx.author.name == "bluedetroyer":
        await ctx.send(f'Do this is bots channel')
        return
    file = open(INFO_FILE)
    data = json.load(file)
    file.close()
    data = data["roles"]
    goodRoles = []
    neutralRoles = []
    evilRoles = []
    for k, v in data.items():
        if v["alignment"] == "Good":
            goodRoles.append(k)
        elif v["alignment"] == "Neutral":
            neutralRoles.append(k)
        elif v["alignment"] == "Evil":
            evilRoles.append(k)
    goodRole = random.choice(goodRoles)
    neutralRole = random.choice(neutralRoles)
    evilRole = random.choice(evilRoles)
    await ctx.send("Pick your role", components=[
            disnake.ui.Button(label=goodRole, style=disnake.ButtonStyle.success, custom_id="good"),
            disnake.ui.Button(label=neutralRole, style=disnake.ButtonStyle.secondary, custom_id="neutral"),
            disnake.ui.Button(label=evilRole, style=disnake.ButtonStyle.danger, custom_id="evil"),
        ])


@bot.listen("on_button_click")
async def help_listener(ctx: disnake.MessageInteraction):
    await ctx.response.defer()
    #if ctx.component.custom_id not in ["yes", "no", "good", "neutral", "evil"]:
        # We filter out any other button presses except
        # the components we wish to process.
    #    return

    if ctx.component.custom_id == "yes":
        await ctx.send("Button")
    elif ctx.component.custom_id == "no":
        await ctx.send("Button Indeed")
    elif ctx.component.custom_id in ["good", "neutral", "evil"]:
        await ctx.send(ctx.component.label)
    elif ctx.component.custom_id == "send_coins":
        await distributeCoins(ctx.guild)
        await ctx.edit_original_response(components=[])
        await ctx.channel.send("Coins distributed")
    elif ctx.component.custom_id == "send_carepackages":
        await distributeCarepackages(ctx.guild)
        await ctx.edit_original_response(components=[])
        await ctx.channel.send("Carepackages distributed")
    elif ctx.component.custom_id == "send_items":
        await distributeItems(ctx.guild)
        await ctx.edit_original_response(components=[])
        await ctx.channel.send("Items distributed")
    elif ctx.component.custom_id == "send_aas":
        await distributeAas(ctx.guild)
        await ctx.edit_original_response(components=[])
        await ctx.channel.send("Aas distributed")

#Runs bot
bot.run(token)
