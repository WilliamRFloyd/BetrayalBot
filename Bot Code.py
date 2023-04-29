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
    commonAAs = ("Search", "Vibe Check", "Silence", "Gag", "Disable", "Black Cloak", "Curse", "Freeze", "Electrify", "Disrespectful Peek", "Bond", "Follow", "Spy", "Mask", "Allure", "Off The Beaten Path", "Venture", "On The House", "Demon Hunt", "Jokester", "Soul Seeking [Doll]", "Abyssal Blessings")
    uncommonAAs = ("Chomp", "Safeguard", "Interrogate", "False Result", "Investigate", "Redirect", "Vaccinate", "Cure", "Heal", "Fireball", "Body Examine", "Peek Of The Grave", "Confiscate", "Deduct", "Hidden", "Preserve", "Charisma Chant", "Opening Act", "Protective Prance", "Gentle Holdings [Incubus]",
                     "Protection", "Surveillance", "Solve", "Contract", "Discount", "Serene State", "Body Swap", "Coin Flip", "Forbidden Knowledge", "Restrain", "Luck Up", "Peek Of The Living", "Inheritance Tax", "Silver-Tongue", "Douse [Arsonist]", "Down-Surge [Tinkerer]",
                     "Kick", "Reel", "Invisibility", "Chemistry", "Subtraction", "Inspection Zone", "Ascend", "Purification", "Holy Light", "Wall Breaker", "Bloody Knuckles", "Bend", "Interception", "Corpse Shield", "Cross Eyes [Maso]", "Force Ability [GK]", "Inflate [Banker]", "Soul Seer [Medium]",
                     "Lunch Break [Biker]", "Side-Show [Entertainer]", "Upsurge [Tinkerer]")
    rareAAs = ("Discover", "Man's Blessing", "Bless", "Bloody Escape", "Last Will", "Payday", "Silver Finger", "Forceful Resignation", "Depressing Ballad", "Luck Transfer", "Soul Swap", "Degrade", "Overclock", "Fishing Trip", "Bury Alive", "Intoxication [Bartender]", "Moonshine", "Steal", "Replay", "Entrapment",
               "Reaction", "Smoke Grenade", "Blackened Chains", "Isolate", "Imperium", "Lava Wall", "Rewind", "Bone Breaker", "Tear-Out [Hydra]", "Head Slam [Hydra]", "Skinning [Slaughterer]", "Impish Grin [Imp]", "Mischief [Imp]", "Purge [Anarchist]", "Ready Stance [Neph]", "Repulse [Maso]", "Scent Marker [Hunter]", "Spacial Followings [Neph]",
               "Burning Rubber", "Damage Dance", "Encapsulate", "Gaslighted Discussion", "Hammer", "Ignorance Bubble", "Matter Reconstruction", "Sheltered In Ice", "Hair Pulling [Incubus", "Ignite [Arsonist]", "Shadowed Hands [Phantom]", "Twist [Entertainer]")
    epicAAs = ("Troll", "Shutdown", "Survivalist's Threaten", "Fatality", "Lawful", "Overrule", "Hold-Up", "Hex", "Mentor", "Gas Bomb", "Tagger Bomb", "Clink", "Survival Swap", "Upgrade", "Steel Guard", "Hooked", "Re-Enact", "Reuse", "Last Resort", "Override", "Stick With the Pack", "Erasure", "Broken Blade", "Sunder",
               "Fire Guard", "Ethereal Healing", "Visceral Roar", "Entire Circus", "Head-Shield [Hydra]", "Brute Force [Neph]", "Iron Will [Neph]", "Submission [Maso]", "Target Fire [Mecha]", "Gathering Trick", "Abyssal Curse [Phantom]", "Assimilate [Tinkerer]", "Charm [Succubus]", "Chemical [Arsonist]", "Embrace [Incubus]", "Inceneration [Arsonist]")
    legendaryAAs = ("Empower", "Resilient Aura", "Reanimate", "Soul Binding", "Disappear", "Break", "Bait", "Hyperdrive", "Voodoo Doll", "Act Out", "Ban", "Tactical Tune")
    allAAs = (commonAAs, uncommonAAs, rareAAs, epicAAs, legendaryAAs, legendaryAAs)

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

#Code that runs upon someone joining the server
@bot.event
async def on_member_join(member):
    pass

#Things actually relavant to betrayal

#Code for item rain
@bot.command(name='item', help="Proper format: '/item [luck]'. If no luck is specified, it defaults to 0.")
async def itemRain(ctx, arg1="0", arg2="1"):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not ctx.author.name == "Bluedetroyer":
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
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name:
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
@bot.command(name='carepackage', help="Proper format: '/carepackage [luck]'. If no luck is specified, it defaults to 0.")
async def carepackage(ctx, arg1=0, arg2=1):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name:
        await ctx.send(f'Do this is bots channel')
        return
    arg2 = int(arg2)
    if arg2 > 50:
        await ctx.send(f'Capped at 50')
        arg2 = 50
    arg1 = int(arg1)
    for i in range(arg2):
        item = itemGen(arg1)
        anyAbility = anyAbilityGen(arg1)
        await ctx.send(f'Carepackage:\nItem: {item}\nAny Ability: {anyAbility}')

#Code for viewing information of a specific item
@bot.slash_command(description="View the information about the specified item")
async def viewitem(ctx, item: str, hidden: bool = False):
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

    itemList = []
    for i, info in data["items"].items():
        if item.lower() == i.lower():
            name = i
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
            await ctx.send(embed=embed)
            return
        else:
            itemList.append(i)
        
    closestItem = find_most_similar_string(item, itemList)
    response = "Item not found, did you mean __%s__?" % (closestItem)
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
        "Evil": 0xFF0000,
        "Ball": 0xFFFFFF,
        "Traveller": 0xFFFF00
        }

    roleList = []
    for r, info in data["classes"].items():
        if role.lower() == r.lower():
            name = r
            alignment = info["alignment"]
            description = info["description"]
            abilities = info["abilities"]
            perks = info["perks"]
            achievements = info["achievements"]
            
            embed = disnake.Embed(title=f'{name}', description=f'**{alignment}**\n{description}\n\n**Abilities:**', color=alignmentColors[alignment])
            i = 0
            for ability, info in abilities.items():
                extra = ""
                i += 1
                if i == len(abilities):
                    extra = "\n\n**Perks:**"
                embed.add_field(name=f'{ability} [x{info["charges"]}]', value=f'{info["effect"]}{extra}', inline=False)
            i = 0
            for perk, info in perks.items():
                extra = ""
                i += 1
                if i == len(perks):
                    extra = "\n\n**Achievements:**"
                embed.add_field(name=f'{perk}', value=f'{info}{extra}', inline=False)
            for achievement, info in achievements.items():
                embed.add_field(name=f'{achievement}', value=f'{info}', inline=False)
            await ctx.send(embed=embed, ephemeral=hidden)
            return
        else:
            roleList.append(r)
    closestRole = find_most_similar_string(role, roleList)
    response = "Role not found, did you mean __%s__?" % (closestRole)
    info = data["classes"][closestRole]
    name = closestRole
    alignment = info["alignment"]
    description = info["description"]
    abilities = info["abilities"]
    perks = info["perks"]
    achievements = info["achievements"]
    
    embed = disnake.Embed(title=f'{name}', description=f'**{alignment}**\n{description}\n\n**Abilities:**', color=alignmentColors[alignment])
    i = 0
    for ability, info in abilities.items():
        extra = ""
        i += 1
        if i == len(abilities):
            extra = "\n\n**Perks:**"
        embed.add_field(name=f'{ability} [x{info["charges"]}]', value=f'{info["effect"]}{extra}', inline=False)
    i = 0
    for perk, info in perks.items():
        extra = ""
        i += 1
        if i == len(perks):
            extra = "\n\n**Achievements:**"
        embed.add_field(name=f'{perk}', value=f'{info}{extra}', inline=False)
    for achievement, info in achievements.items():
        embed.add_field(name=f'{achievement}', value=f'{info}', inline=False)
    await ctx.send(response, embed=embed, ephemeral=hidden)

#Code for viewing information of a specific ability
@bot.slash_command(description="View the information about the specified ability")
async def viewability(ctx, ability: str, hidden: bool = False):
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

    abilityList = []
    for role, info in data["classes"].items():
        for a, abilityinfo in info["abilities"].items():
            if ability.lower() == a.lower():
                name = a
                rarity = abilityinfo["rarity"]
                effect = abilityinfo["effect"]
                embed = disnake.Embed(title=f'{name}', description=f'{rarity}', color=rarityColors[rarity])
                embed.add_field(name=f'Effect:', value=f'{effect}', inline=False)
                await ctx.send(embed=embed, ephemeral=hidden, components=[disnake.ui.Button(label=f'View {role}', style=disnake.ButtonStyle.secondary, custom_id=f'viewrole_{role}')])
                return
            else:
                abilityList.append(a)
        
    closestAbility = find_most_similar_string(ability, abilityList)
    response = "Ability not found, did you mean __%s__?" % (closestAbility)
    
    for role, info in data["classes"].items():
        for a, abilityinfo in info["abilities"].items():
            if closestAbility.lower() == a.lower():
                name = closestAbility
                rarity = abilityinfo["rarity"]
                effect = abilityinfo["effect"]
                embed = disnake.Embed(title=f'{name}', description=f'{rarity}', color=rarityColors[rarity])
                embed.add_field(name=f'Effect:', value=f'{effect}', inline=False)
                await ctx.send(response, embed=embed, ephemeral=hidden, components=[disnake.ui.Button(label=f'View {role}', style=disnake.ButtonStyle.secondary, custom_id=f'viewrole_{role}')])


#Code for viewing information of a specific perk
@bot.slash_command(description="View the information about the specified perk")
async def viewperk(ctx, perk: str, hidden: bool = False):
    file = open("info.json")
    data = json.load(file)
    file.close()

    perkList = []
    for role, info in data["classes"].items():
        for p, effect in info["perks"].items():
            if perk.lower() == p.lower():
                embed = disnake.Embed(title=f'{p}', description=f'{effect}')
                await ctx.send(embed=embed, ephemeral=hidden, components=[disnake.ui.Button(label=f'View {role}', style=disnake.ButtonStyle.secondary, custom_id=f'viewrole_{role}')])
                return
            else:
                perkList.append(p)
        
    closestPerk = find_most_similar_string(perk, perkList)
    response = "Perk not found, did you mean __%s__?" % (closestPerk)

    for role, info in data["classes"].items():
        for p, effect in info["perks"].items():
            if closestPerk.lower() == p.lower():
                embed = disnake.Embed(title=f'{p}', description=f'{effect}')
                await ctx.send(response, embed=embed, ephemeral=hidden, components=[disnake.ui.Button(label=f'View {role}', style=disnake.ButtonStyle.secondary, custom_id=f'viewrole_{role}')])
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

    statusList = []
    for s, info in data["statuses"].items():
        if status.lower() == s.lower() or status.lower() + "ed" == s.lower() or status.lower() + "d" == s.lower():
            embed = disnake.Embed(title=f'{s}', description=f'{info}', color=statusColors[s])
            await ctx.send(embed=embed, ephemeral=hidden)
            return
        else:
            statusList.append(s)
        
    closestStatus = find_most_similar_string(status, statusList)
    response = "Perk not found, did you mean __%s__?" % (closestStatus)

    embed = disnake.Embed(title=f'{closestStatus}', description=f'{data["statuses"][closestStatus]}', color=statusColors[s])
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

#Code for creating and editing player list
@bot.command(name='playerlist', help="First argument is either create to make the player list with the game number & specified players, kill to show deceased next to specified players, revive to show particpant next to specified players, and truekill to show true deceased next to specfied players, then a list of player(s)")
async def playerlist(ctx, arg1="", *arg2):
    #Authorization check
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and ctx.author.name != "Bluedetroyer"):
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
        if role.name == "True Deceased":
            trueDeceasedRole = role
    #Creating a player list
    if arg1.lower() == "create":
        playerStartIndex = arg2.index("Players") + 1
        master = ""
        if "Master" in arg2:
            master = arg2[arg2.index("Master") + 1] + " " + arg2[arg2.index("Master") + 2]
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

@bot.command(help='')
async def viewvotes(ctx):
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"])):
        await ctx.send("Nice Try")
        return
    file = open("inventoryinfo.json")
    data = json.load(file)
    file.close()
    voteStr = ""
    for k, v in data.items():
        if "confessional" in k and "vote" in v:
            voteStr += f'{k[0:-13]}: {str(v["vote"])[1:-1]}\n'
    await ctx.send(voteStr)

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
    allowed = "Bluedetroyer"
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
    for roleName, info in data["classes"].items():
        if arg1 != "" and info["alignment"].lower() != arg1.lower():
            continue
        roleList.append(roleName)
    await ctx.send(random.choice(roleList))

#Channel Creation for 1-1 chats
@bot.command(name='genchats')
async def generateChats(ctx, arg1="20"):
    if (not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and ctx.author.name != "Bluedetroyer"):
        await ctx.send("no")
        return
    numPlayers = int(arg1)
    for i in range(1, numPlayers + 1):
        await ctx.guild.create_role(name=str(i))

    await ctx.guild.create_role(name="Host")
    await ctx.guild.create_role(name="Spectator")
    
    for i in range(1, numPlayers):
        currentCategory = await ctx.guild.create_category(name=f'{i}')
        for j in range(i+1, numPlayers + 1):
            overwrites = {
                ctx.guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                disnake.utils.find(lambda r: r.name == str(i), ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                disnake.utils.find(lambda r: r.name == str(j), ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                disnake.utils.find(lambda r: r.name == "Host", ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True),
                disnake.utils.find(lambda r: r.name == "Spectator", ctx.guild.roles): disnake.PermissionOverwrite(read_messages=True, send_messages=False)
            }
            channel = await ctx.guild.create_text_channel(f'{i}-{j}', overwrites=overwrites, category=currentCategory)

@bot.command(name='clearroles')
async def clearRoles(ctx):
    if ctx.guild.name == "Test Channel Creation" or ctx.guild.name == "Betrayal 38":
        for role in ctx.guild.roles:
            if role.name.isdigit() or role.name in ["Host", "Spectator"]:
                await role.delete()
        print("Roles done")
        for category in ctx.guild.categories:
            if category.name.isdigit():
                await category.delete()
        print("Categories done")
        for channel in ctx.guild.text_channels:
            if "-" in channel.name:
                await channel.delete()
        print("Channels done")

#Random Stuff

@bot.command(name='die', help='Perish')
async def death(ctx):
    await ctx.send(f'{ctx.author.mention} is now dead. You may pay your condolences.')

@bot.command(name='kill', help='Commit a murder')
async def kill(ctx, arg1):
    for member in ctx.guild.members:
        if member.name.lower() == arg1.lower() or member.name == arg1 or member.mention == arg1 or member.mention == "<@" + "!" + arg1[2:]:
            target = member
            if target.name == "Bluedetroyer":
                await ctx.send(f'I\'m afraid I can\'t do that {ctx.author.mention}')
            else:
                await ctx.send(f'{ctx.author.mention} brutally shot {target.mention} to death')

@bot.command(name='superkill', help='Commit a super murder')
async def superKill(ctx, *arg1):
    for arg in arg1:
        for member in ctx.guild.members:
            if member.name.lower() == arg.lower() or member.name == arg or member.mention == arg or member.mention == "<@" + "!" + arg[2:]:
                target = member
                if target.name == "Bluedetroyer":
                    await ctx.send(f'I\'m afraid I can\'t do that {ctx.author.mention}')
                else:
                    await ctx.send(f'{ctx.author.mention} super brutally shot {target.mention} to death like a super amount of times')

@bot.command(name='test', help='test')
async def sendMessage(ctx, arg1, arg2):
    if ctx.author.name == 'Bluedetroyer':
        guildChannels = bot.guilds[1].channels
        for channel in guildChannels:
            if channel.name == arg1:
                await channel.send(arg2)

@bot.command(name='change')
async def change(ctx, arg1):
    if ctx.author.name == 'Bluedetroyer':
        for member in bot.guilds[1].members:
            if member.name == "Bluedetroyer":
                await member.edit(nick=arg1)

@bot.command(name='mario')
async def spamMario(ctx, arg1=10):
    if ctx.author.name == '' or ctx.author.name == "Bluedetroyer":
        for member in bot.guilds[1].members:
            if member.name == 'Duncan':
                for i in range(int(arg1)):
                    await ctx.send(f'{member.mention}')
@bot.command(name='removeto')
async def removeTimeOut(ctx):
        for member in bot.guilds[1].members:
            if member.name == 'The Lukundo':
                time = datetime.datetime(year=2023, month=4, day = 1, hour = 15, minute = 25, second=30)
                await member.timeout(until=time)

@bot.command(name='button')
async def buttonTest(ctx: disnake.ApplicationCommandInteraction):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not ctx.author.name == "Bluedetroyer":
        await ctx.send(f'Do this in bots channel')
        return
    await ctx.send("Button", components=[
            disnake.ui.Button(label="Button", style=disnake.ButtonStyle.success, custom_id="yes"),
            disnake.ui.Button(label="Also Button", style=disnake.ButtonStyle.danger, custom_id="no"),
        ])

@bot.command(name='deceptPick')
async def deceptPick(ctx: disnake.ApplicationCommandInteraction):
    if ctx.guild.name == "Betrayal" and not compareLists(ctx.author.roles, ["Master", "Host", "Co-Host"]) and not "bots" in ctx.channel.name and not ctx.author.name == "Bluedetroyer":
        await ctx.send(f'Do this is bots channel')
        return
    file = open("info.json")
    data = json.load(file)
    file.close()
    data = data["classes"]
    goodRoles = []
    neutralRoles = []
    evilRoles = []
    for k, v in data.items():
        if v["alignment"] == "Good":
            goodRoles.append(k)
        elif v["alignment"] == "Neutral":
            neutralRoles.append(k)
        else:
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
    elif ctx.component.custom_id.startswith("viewrole_"):
        rolename = ctx.component.custom_id.split("_")[1]
        file = open("info.json")
        data = json.load(file)
        file.close()
        alignmentColors = {
            "Good": 0x00FF00,
            "Neutral": 0x888888,
            "Evil": 0xFF0000,
            "Ball": 0xFFFFFF,
            "Traveller": 0xFFFF00
            }

        roleList = []
        for r, info in data["classes"].items():
            if rolename.lower() == r.lower():
                name = r
                alignment = info["alignment"]
                description = info["description"]
                abilities = info["abilities"]
                perks = info["perks"]
                achievements = info["achievements"]
                
                embed = disnake.Embed(title=f'{name}', description=f'**{alignment}**\n{description}\n\n**Abilities:**', color=alignmentColors[alignment])
                i = 0
                for ability, info in abilities.items():
                    extra = ""
                    i += 1
                    if i == len(abilities):
                        extra = "\n\n**Perks:**"
                    embed.add_field(name=f'{ability} [x{info["charges"]}]', value=f'{info["effect"]}{extra}', inline=False)
                i = 0
                for perk, info in perks.items():
                    extra = ""
                    i += 1
                    if i == len(perks):
                        extra = "\n\n**Achievements:**"
                    embed.add_field(name=f'{perk}', value=f'{info}{extra}', inline=False)
                for achievement, info in achievements.items():
                    embed.add_field(name=f'{achievement}', value=f'{info}', inline=False)
                await ctx.send(embed=embed, ephemeral=True)
                return
            else:
                roleList.append(r)
        closestRole = find_most_similar_string(rolename, roleList)
        info = data["classes"][closestRole]
        name = closestRole
        alignment = info["alignment"]
        description = info["description"]
        abilities = info["abilities"]
        perks = info["perks"]
        achievements = info["achievements"]
        
        embed = disnake.Embed(title=f'{name}', description=f'**{alignment}**\n{description}\n\n**Abilities:**', color=alignmentColors[alignment])
        i = 0
        for ability, info in abilities.items():
            extra = ""
            i += 1
            if i == len(abilities):
                extra = "\n\n**Perks:**"
            embed.add_field(name=f'{ability} [x{info["charges"]}]', value=f'{info["effect"]}{extra}', inline=False)
        i = 0
        for perk, info in perks.items():
            extra = ""
            i += 1
            if i == len(perks):
                extra = "\n\n**Achievements:**"
            embed.add_field(name=f'{perk}', value=f'{info}{extra}', inline=False)
        for achievement, info in achievements.items():
            embed.add_field(name=f'{achievement}', value=f'{info}', inline=False)
        await ctx.send(embed=embed, ephemeral=True)
    else:
        await ctx.send("Unknown Button Interaction", ephemeral=True)


#Runs bot
bot.run(token)
