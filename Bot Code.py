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

#Creating connenction to discord
load_dotenv()
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
token = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='/', intents=intents, case_insensitive=True)

#Nerd Stuff idk
def levenshtein_distance(s, t):
    m, n = len(s), len(t)
    d = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        d[i][0] = i

    for j in range(n + 1):
        d[0][j] = j

    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if s[i - 1] == t[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                d[i][j] = min(d[i - 1][j], d[i][j - 1], d[i - 1][j - 1]) + 1

    return d[m][n]


def find_most_similar_string(string, string_array):
    closest_string = None
    closest_distance = float('inf')

    for candidate_string in string_array:
        distance = levenshtein_distance(string, candidate_string)
        if distance < closest_distance:
            closest_distance = distance
            closest_string = candidate_string

    return closest_string

#Coverts rarity to numeric value
def rarityToNum(rarity: str) -> int:
    rarity = rarity.lower()
    if rarity == "common":
        return 0
    elif rarity == "uncommon":
        return 1
    elif rarity == "rare":
        return 2
    elif rarity == "epic":
        return 3
    elif rarity == "legendary":
        return 4
    elif rarity == "mythical":
        return 5

#Takes a luck value and returns a corresponding rarity number. 0 = common, 1 = uncommon, etc.
def getLuck(luck: int) -> int:
    luckCap: int = 398
    if luck > luckCap:
        luck = luckCap
        
    commonOdds = 8000 - 500 * luck
    if commonOdds < 0:
        commonOdds = 0

    uncommonOdds = 1500 + 300 * luck
    if luck > 16:
        uncommonOdds -= 500 * (luck - 16)
    if uncommonOdds < 0:
        uncommonOdds = 0

    rareOdds = 200 + luck * 100
    if luck >= 48:
        rareOdds -= 100 * (luck - 47)
    if luck > 48:
        rareOdds -= 100 * (luck - 48)
    if rareOdds < 0:
        rareOdds = 0

    epicOdds = 150 + luck * 50
    if luck > 97:
        epicOdds -= 100 * (luck - 97)
    if epicOdds < 0:
        epicOdds = 0

    legendaryOdds = 100 + luck * 25
    if luck > 197:
        legendaryOdds -= 50 * (luck - 197)

    mythicalOdds = 50 + luck * 25
    
    randNum = random.randint(1,10000)
    currentLuckPool = (commonOdds, uncommonOdds, rareOdds, epicOdds, legendaryOdds, mythicalOdds)

    total = 0
    for i in range(6):
        total += currentLuckPool[i]
        if randNum <= total:
            return i

#Rolls a random item based off luck/rarity and returns it
def itemGen(luckOrRarity):
    file = open("info.json")
    data = json.load(file)
    file.close()
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
def anyAbilityGen(luckOrRarity):
    file = open("info.json")
    data = json.load(file)
    file.close()
    #Legendary listed twice as for aas legendaries can roll on a legendary or mythical result
    rarities = ("Common", "Uncommon", "Rare", "Epic", "Legendary", "Legendary")
    allAAs = []
    for rarity in rarities:
        rarityAbilities = []
        for x, y in data["abilities"].items():
            if y["rarity"] == rarity and not y["removed"]:
                abilityName = x
                if y["exclusive"]:
                    abilityName += f' [{y["role"]}]'
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
    
#Take a list and returns a string with each of the list's items on it's own line
def formatList(list):
    string = ""
    for i in range(len(list)):
        string += f'\n{list[i]}'
    return string

#Takes two lists and returns true if they share any elements
def compareLists(list1, list2):
    for i in list1:
        if str(i) in list2:
            return True
    return False

#Code for making the inventory string
def inventoryString(inventory):
    string = f'```Coins: {inventory["coins"]} [{inventory["bonus"]}%]\nInventory: '
    for i in range(len(inventory["items"])):
        string += inventory["items"][i]
        if i != len(inventory["items"]) - 1:
            string += ", "
    string += "\nAA: "
    i = 1
    for k, v in inventory["aas"].items():
        string += f'{k} [{v}]'
        if i != len(inventory["aas"]):
            string += ", "
        i += 1
    string += "\nStatuses: "
    for i in range(len(inventory["statuses"])):
        string += inventory["statuses"][i]
        if i != len(inventory["statuses"]) - 1:
            string += ", "
    string += "\nEffects: "
    for i in range(len(inventory["effects"])):
        string += inventory["effects"][i]
        if i != len(inventory["effects"]) - 1:
            string += ", "
    string += "\nImmunities: "
    for i in range(len(inventory["immunities"])):
        string += inventory["immunities"][i]
        if i != len(inventory["immunities"]) - 1:
            string += ", "
    for k, v in inventory.items():
        if k not in ("coins", "bonus", "items", "statuses", "effects", "aas", "id", "immunities", "vote"):
            string += f'\n{k}: '
            for i in range(len(v)):
                string += v[i]
                if i != len(v) - 1:
                    string += ", "
    string += "\nVote(s): "
    for i in range(len(inventory["vote"])):
        string += inventory["vote"][i]
        if i != len(inventory["vote"]) - 1:
            string += ", "
    string += "```"
    return string

#Event handler

#Code that runs when bot first runs
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connencted to Discord!')
    #with open('betrayal.png', 'rb') as f:
    #    icon = f.read()
    #await guild.edit(icon=icon)
    print(bot.guilds[1].name)

#Code that runs upon someone joining the server
@bot.event
async def on_member_join(member):
    pass

#Things actually relavant to betrayal
#Checks
@bot.slash_command(description="List all objects of the category that don't have the attribute filled out in the info file")
async def listmissing(ctx, obj_type: str, attribute: str):
    file = open("info.json")
    data = json.load(file)
    file.close()

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
    print("test")
    file = open("info.json")
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
    file = open("info.json")
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
        if "Cannot be burnt" not in effect:
            upgrades.append(f'{effect} Cannot be burnt.')
        if "Cannot be stolen" not in effect:
            upgrades.append(f'{effect} Cannot be stolen.')
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
    file = open("info.json")
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
    file = open("info.json")
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
    file = open("info.json")
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
    file = open("info.json")
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

    embed = disnake.Embed(title=f'{closestStatus}', description=f'{data["statuses"][closestStatus]["effect"]}', color=statusColors[s])
    await ctx.send(response, embed=embed, ephemeral=hidden)
    return


@bot.command(name='itemslist')
async def itemembed(ctx):
    file = open("info.json")
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
    file = open("info.json")
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
        

#Code for creating and editing player list
@bot.command(name='playerlist', help="First argument is either create to make the player list with the game number & specified players, kill to show deceased next to specified players, revive to show particpant next to specified players, and truekill to show true deceased next to specfied players, then a list of player(s)")
async def playerlist(ctx, arg1="", *arg2):
    #Authorization check
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and ctx.author.name != "bluedetroyer"):
        await ctx.send("You need to be a host to use this command")
        return
    #Getting discord roles
    for role in ctx.guild.roles:
        if role.name == "Participant":
            participantRole = role
    for role in ctx.guild.roles:
        if role.name == "Deceased":
            deceasedRole = role
    for role in ctx.guild.roles:
        if role.name == "True Dead":
            trueDeceasedRole = role
    #Creating a player list
    if arg1.lower() == "create":
        playerStartIndex = arg2.index("Players") + 1
        master = ""
        if "Master" in arg2:
            master = arg2[arg2.index("Master") + 1]
        mode = ""
        if "Mode" in arg2:
            mode = arg2[arg2.index("Mode") + 1]
        hosts = []
        if "Hosts" in arg2:
            for i in range(arg2.index("Hosts") + 1, len(arg2)):
                if arg2[i] in ["Players", "Master", "Mode"]:
                    break
                else:
                    hosts.append(arg2[i])
        gameNum = arg2[0]
        playerListStr = f'**Game {gameNum}**\n'
        if master != "":
            playerListStr += f'Master: **{master}**\n'
        if hosts != []:
            playerListStr += f'Hosts: **{hosts[0]}'
            for i in range(1, len(hosts)):
                playerListStr += f'/{hosts[i]}'
            playerListStr += f'**\n'
        if mode != "":
            playerListStr += f'Mode: **{mode}**\n'
        playerListStr += "```Players:```\n\n"
        for i in range(playerStartIndex, len(arg2)):
            player = arg2[i]
            for member in ctx.guild.members:
                if member.name == player or member.mention == player or member.mention == "<@" + "!" + player[2:]:
                    player = member
                    break
            playerListStr += f'{participantRole.mention} {member.mention}\n'
        remaining = len(re.findall(participantRole.mention, playerListStr))
        playerListStr += f'\n```{remaining} REMAIN```'
        listId = await ctx.send(playerListStr)
        listId = listId.id
        f = open("playerlistid.txt", "w")
        f.write(str(listId) + " " + ctx.channel.name)
        f.close()
    #Adding players to the player list
    elif arg1.lower() == "add":
        f = open("playerlistid.txt", "r")
        line = f.readline()
        f.close()
        listId = line.split()[0]
        channelName = line.split()[1]
        listId = int(listId)
        found = False
        for channel in ctx.guild.text_channels:
            if channel.name == channelName:
                async for message in channel.history(limit=100):
                    if message.id == listId:
                        playerList = message
                        found = True
                        break
            if found:
                break
        content = playerList.content
        for player in arg2:
            splitIndex = content.rfind(">") + 2
            for member in ctx.guild.members:
                if member.name == player or member.mention == player or member.mention == "<@" + "!" + player[2:]:
                    player = member
                    break
            content = content[:splitIndex] + f'{participantRole.mention} {member.mention}\n' + content[splitIndex:]
            remaining = len(re.findall(participantRole.mention, content))
            content = content[:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        remaining = len(re.findall(participantRole.mention, content))
        content = content[:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        await playerList.edit(content=content)
    #Setting players to deceased on the player list
    elif arg1.lower() == "kill":
        f = open("playerlistid.txt", "r")
        line = f.readline()
        f.close()
        listId = line.split()[0]
        channelName = line.split()[1]
        listId = int(listId)
        found = False
        for channel in ctx.guild.text_channels:
            if channel.name == channelName:
                async for message in channel.history(limit=100):
                    if message.id == listId:
                        playerList = message
                        found = True
                        break
            if found:
                break
        content = playerList.content
        for player in arg2:
            if player in content:
                playerMention = player
            else:
                for member in ctx.guild.members:
                    if member.name == player or member.mention == player or member.mention == "<@" + "!" + player[2:]:
                        playerMention = member.mention
            index = content.find(playerMention)
            remaining = len(re.findall(participantRole.mention, content))
            if playerMention in content:
                content = content[:index-len(participantRole.mention)-1] + deceasedRole.mention + content[index-1:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        remaining = len(re.findall(participantRole.mention, content))
        content = content[:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        await playerList.edit(content=content)
    #Setting players to true deceased on the player list
    elif arg1.lower() == "truekill":
        f = open("playerlistid.txt", "r")
        line = f.readline()
        f.close()
        listId = line.split()[0]
        channelName = line.split()[1]
        listId = int(listId)
        found = False
        for channel in ctx.guild.text_channels:
            if channel.name == channelName:
                async for message in channel.history(limit=100):
                    if message.id == listId:
                        playerList = message
                        found = True
                        break
            if found:
                break
        content = playerList.content
        for player in arg2:
            for member in ctx.guild.members:
                if member.name == player or member.mention == player or member.mention == "<@" + "!" + player[2:]:
                    playerMention = member.mention
            index = content.find(playerMention)
            remaining = len(re.findall(participantRole.mention, content))
            content = content[:index-len(participantRole.mention)-1] + trueDeceasedRole.mention + content[index-1:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        remaining = len(re.findall(participantRole.mention, content))
        if playerMention in content:
            content = content[:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        await playerList.edit(content=content)
    #Setting players to participant on the player list
    elif arg1.lower() == "revive":
        f = open("playerlistid.txt", "r")
        line = f.readline()
        f.close()
        listId = line.split()[0]
        channelName = line.split()[1]
        listId = int(listId)
        found = False
        for channel in ctx.guild.text_channels:
            if channel.name == channelName:
                async for message in channel.history(limit=100):
                    if message.id == listId:
                        playerList = message
                        found = True
                        break
            if found:
                break
        content = playerList.content
        for player in arg2:
            for member in ctx.guild.members:
                if member.name == player or member.mention == player or member.mention == "<@" + "!" + player[2:]:
                    playerMention = member.mention
            index = content.find(playerMention)
            remaining = len(re.findall(participantRole.mention, content))
            content = content[:index-len(participantRole.mention)-1] + participantRole.mention + content[index-1:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        remaining = len(re.findall(participantRole.mention, content))
        if playerMention in content:
            content = content[:len(content) - len(content.split()[-2]) - 7] + f'{remaining} REMAIN```'
        await playerList.edit(content=content)
    #Invalid arguments
    elif arg1 == "":
        await ctx.send("No argument found")
    else:
        await ctx.send("Argument " + arg1 + " not recognized for player list")

#Vote moment
@bot.command(help="")
async def vote(ctx, *args):
    arg2 = ("set",) + args
    await inventories(ctx, "vote", *arg2)


@bot.slash_command(description="Lists the contents of the specified section of each player's inventories.", guild_ids=[490904847701245952, 379383629010436096])
@commands.default_member_permissions(administrator=True)
async def view(
    ctx,
    section: str = commands.Param(choices={"Items": "items", "AAs": "aas", "Statuses": "statuses", "Effects": "effects", "Immunities": "immunities", "Votes": "vote"}),
    search_for: str = "",
    alive_only: bool = True):
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"])):
        await ctx.send("Nice Try")
        return
    file = open("inventoryinfo.json")
    data = json.load(file)
    file.close()
    listStr = f'{section.capitalize()}\n'
    for k, v in data.items():
        if "confessional" in k and section in v:
            for channel in ctx.guild.channels:
                if channel.name == k:
                    if channel.category.name == "Confessionals" or (channel.category.name == "Dead confessionals" and not alive_only):
                        listStr += f'{k[0:-13]}: '
                        strAddition = ""
                        for item in v[section]:
                            if search_for.lower() in item.lower():
                                if strAddition != "":
                                    strAddition += ", "
                                strAddition += item
                        listStr += strAddition + "\n" 
    await ctx.send(listStr)

@bot.command(help='')
async def clearvotes(ctx, arg1="alive"):
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"])):
        await ctx.send("Nice Try")
        return
    file = open("inventoryinfo.json")
    data = json.load(file)
    file.close()
    for k, v in data.items():
        if "confessional" in k and "vote" in v:
            for channel in ctx.guild.channels:
                if channel.name == k:
                    if arg1 == "alive" and channel.category.name == "Confessionals":
                        v["vote"] = []

    file = open("inventoryinfo.json", "w")
    file.write(json.dumps(data, indent=4))
    file.close()
    await ctx.send("Votes cleared")

@bot.command(help='')
async def clearinvs(ctx, arg1="alive"):
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"])):
        await ctx.send("Nice Try")
        return
    
    file = open("inventoryinfo.json", "w")
    file.write(json.dumps({}, indent=4))
    file.close()
    await ctx.send("Inventories cleared")

#Code for managing inventories
@bot.command(aliases=['inventory', 'inv'], help='')
async def inventories(ctx, arg1="", *arg2):
    #Getting discord roles
    for role in ctx.guild.roles:
        if role.name == "Participant":
            participantRole = role
    for role in ctx.guild.roles:
        if role.name == "Deceased":
            deceasedRole = role
    
    channel = ctx.channel
    allowed = "bluedetroyer"
    gameMembers = []
    for x in channel.members:
        if compareLists(x.roles, ["Participant", "Deceased"]) and (not compareLists(x.roles, ["Master", "Host", "Co-Host", "True Deceased"])):
            gameMembers.append(x)
    if len(gameMembers) == 1:
        allowed = gameMembers[0].name
    #Authorization check
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not (ctx.author in channel.members)):
        await ctx.send("You don't have permession to edit inventories in this channel")
        return
    #Creating inventory
    if arg1.lower() == "create":
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        if channel.name in data:
            await ctx.send("There's already an inventory for that channel. Please delete/forget it if you want to make a new one")
            return
        newInventory = {"coins": 0, "bonus": 0, "items": [], "aas": {}, "statuses": [], "effects": [], "immunities": [], "vote": []}
        inventoryId = await channel.send(inventoryString(newInventory))
        newInventory["id"] = inventoryId.id
        data[channel.name] = newInventory
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    #Editing coins/coin bonus
    elif arg1.lower() in ("coins", "coin", "bonus"):
        if arg1.lower() == "coin":
            arg1 = "coins"
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await channel.fetch_message(inventory["id"])
        if arg1.lower() == "bonus":
            amount = float(arg2[1])
        else:
            amount = int(arg2[1])
        if arg2[0].lower() in ("remove", "subtract", "delete"):
            amount *= -1
        if arg2[0].lower() in ("remove", "subtract", "delete", "add"):
            inventory[arg1.lower()] += amount
        elif arg2[0].lower() == "set":
            inventory[arg1.lower()] = amount
        await message.edit(content=inventoryString(inventory))
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    #Editing items/statuses/effects
    elif arg1.lower() in ("items", "statuses", "effect", "effects", "item", "status", "immunities", "immunity", "vote", "votes"):
        if arg1.lower() == "item":
            arg1 = "items"
        if arg1.lower() == "status":
            arg1 = "statuses"
        if arg1.lower() == "immunity":
            arg1 = "immunities"
        if arg1.lower() == "effect":
            arg1 = "effects"
        if arg1.lower() == "votes":
            arg1 = "vote"
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await channel.fetch_message(inventory["id"])
        if arg2[0].lower() == "add":
            for thing in arg2[1:]:
                inventory[arg1.lower()].append(thing)
        elif arg2[0].lower() == "remove":
            for thing in arg2[1:]:
                for item in inventory[arg1.lower()]:
                    if item.lower() == thing.lower():
                        inventory[arg1.lower()].remove(item)
                        break
        elif arg2[0].lower() == "clear":
            inventory[arg1.lower()].clear()
        elif arg2[0].lower() == "set":
            inventory[arg1.lower()].clear()
            for thing in arg2[1:]:
                inventory[arg1.lower()].append(thing)
        await message.edit(content=inventoryString(inventory))
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    elif arg1.lower() in ("aa", "aas"):
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await channel.fetch_message(inventory["id"])
        if arg2[0].lower() in ("add", "set"):
            for i in range(1, len(arg2)):
                if arg2[i].isdigit():
                    continue
                charges = 1
                if i < len(arg2) - 1:
                    if arg2[i+1].isdigit():
                        charges = int(arg2[i+1])
                inventory["aas"][arg2[i]] = charges
        elif arg2[0].lower() == "remove":
            for thing in arg2[1:]:
                for aa in inventory["aas"]:
                    if aa.lower() == thing.lower():
                        inventory["aas"].pop(aa)
                        break
        elif arg2[0].lower() == "clear":
            inventory["aas"].clear()
        await message.edit(content=inventoryString(inventory))
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    #Checks if the inventory has the proper amount of coins then removes those coins and adds the item to the inventory
    elif arg1.lower() == "buy":
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await channel.fetch_message(inventory["id"])
        file = open("info.json")
        items = json.load(file)
        file.close()
        purchase  = " ".join(arg2)
        for i, info in items["items"].items():
            if purchase.lower() == i.lower():
                name = i
                cost = info["cost"]
                if cost == 0:
                    response = "Item cannot be purchased."
                elif inventory["coins"] < cost:
                    response = "Not enough coins."
                else:
                    inventory["coins"] -= cost
                    inventory["items"].append(name)
                    response = f'{name} purchased for {cost} coins'
        await message.edit(content=inventoryString(inventory))
        await ctx.send(response)
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
        
    #Deletes the inventory message from the channel and removes it from the json file
    elif arg1.lower() == "delete":
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await channel.fetch_message(inventory["id"])
        data.pop(channel.name)
        await message.delete()
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    #Removes the inventory from the json file but leaves the message
    elif arg1.lower() == "forget":
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        data.pop(channel.name)
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    #Prints a copy of the inventory that doesn't get updated
    elif arg1.lower() == "send":
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        await ctx.send(content=inventoryString(inventory))
    elif arg1.lower() == "refresh":
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await ctx.send(content=inventoryString(inventory))
        data[channel.name]["id"] = message.id
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    elif arg1.lower() == "section":
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await channel.fetch_message(inventory["id"])
        if arg2[0].lower() in ("create", "add"):
            inventory[arg2[1]] = []
        if arg2[0].lower() == "remove":
            inventory.pop(arg2[1])
        await message.edit(content=inventoryString(inventory))
        file = open("inventoryinfo.json", "w")
        file.write(json.dumps(data, indent=4))
        file.close()
    #Invalid arguments
    elif arg1 == "":
        await ctx.send("No argument found")
    else:
        file = open("inventoryinfo.json")
        data = json.load(file)
        file.close()
        inventory = data[channel.name]
        message = await channel.fetch_message(inventory["id"])
        if arg1 in inventory:
            if arg2[0].lower() == "add":
                for thing in arg2[1:]:
                    for item in inventory[arg1]:
                        if item.lower() == thing:
                            inventory[arg1].remove(item)
                    inventory[arg1].append(thing)
            elif arg2[0].lower() == "remove":
                for thing in arg2[1:]:
                    for item in inventory[arg1]:
                        if item.lower() == thing.lower():
                            inventory[arg1].remove(item)
                            break
            elif arg2[0].lower() == "clear":
                inventory[arg1].clear()
            elif arg2[0].lower() == "set":
                inventory[arg1].clear()
                for thing in arg2[1:]:
                    inventory[arg1].append(thing)
            await message.edit(content=inventoryString(inventory))
            file = open("inventoryinfo.json", "w")
            file.write(json.dumps(data, indent=4))
            file.close()
        else:
            await ctx.send("Argument " + arg1 + " not recognized for inventory")

#Code for picking a random role
@bot.command(name='randomrole', help='You people keep pasting in super long messages to do this please stop')
async def randomRole(ctx, arg1=""):
    if arg1.lower() in ("decept", "deceptionist"):
        await randomRole(ctx, "good")
        await randomRole(ctx, "neutral")
        await randomRole(ctx, "evil")
    file = open("info.json")
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

    if "Host" not in guildRoleNames:
        await ctx.guild.create_role(name="Host", permissions=disnake.Permissions(administrator=True))
    if "Spectator" not in guildRoleNames:
        await ctx.guild.create_role(name="Spectator")
    if "Participant" not in guildRoleNames:
        await ctx.guild.create_role(name="Participant")
    if "Dead" not in guildRoleNames:
        await ctx.guild.create_role(name="Dead")

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

@bot.command(name='change')
async def change(ctx, arg1):
    if ctx.author.name == 'bluedetroyer':
        for member in bot.guilds[1].members:
            if member.name == "Bluedetroyer":
                await member.edit(nick=arg1)

@bot.command(name='takethat')
async def editmes(ctx):
    for guild in bot.guilds:
        if guild.name ==  "Betrayaled":
            for channel in guild.text_channels:
                if channel.name == "sign-ups":
                    async for message in channel.history(limit=20):
                        if message.author.name == "Betrayal Bot":
                            await message.edit(content="Items:\nDepower")
                            
                
    

@bot.command(name='mario')
async def spamMario(ctx, arg1=10):
    if ctx.author.name == '' or ctx.author.name == "bluedetroyer":
        for member in bot.guilds[1].members:
            if member.name == 'Duncan':
                for i in range(int(arg1)):
                    await ctx.send(f'{member.mention}')
@bot.command(name='removeto')
async def removeTimeOut(ctx):
        for member in bot.guilds[1].members:
            if member.name == 'duncandont':
                time = datetime.datetime(year=2025, month=8, day = 27, hour = 12, minute = 20, second=30)
                await member.timeout(until=time)

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
    file = open("info.json")
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

#Runs bot
bot.run(token)
