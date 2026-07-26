#Dependencies
import os
import random
import json
import re
import datetime
import helper_functions
from shared_data import Data, INFO_FILE, GAME_FILE
from attr_classes import Game, PlayerRole
import disnake

#Constants
CHARACTER_LIMIT = 2000

def save_game_data():
    data = openJson(GAME_FILE)
    data[str(Data.game_data.guild_id)] = Data.game_data.save_data()
    writeJson(GAME_FILE, data)

def check_active_game(guild: disnake.Guild):
    if (guild.id == Data.game_data.guild_id):
        return

    save_game_data()
    data = openJson(GAME_FILE)
    if str(guild.id) in data.keys():
        Data.game_data = Game.load_data(guild.id, data[str(guild.id)])
    else:
        Data.game_data = Game(guild.id, guild.name)
        save_game_data()

#Helper functions
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

def openJson(fileName: str) -> dict:
    with open(fileName, "r") as file:
        try:
            data = json.load(file)
        except:
            data = {}
    return data

def writeJson(fileName: str, data: dict):
    with open(fileName, "w") as file:
        file.write(json.dumps(data, indent=4))

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
    return -1
    

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

def findIgnoringCase(string: str, string_array: list) -> str:
    lower_string = string.lower()
    for candidate_string in string_array:
        if candidate_string.lower() == lower_string:
            return candidate_string
    return None

#Code for making a role string (possibly multiple if it exceeds character limits)
def generateRoleStrings(roleData: PlayerRole, info):
    #Basics
    roleInfo = info["roles"][roleData.role_name]
    allStrings = []
    currentString = f'```'
    endString = '```'
    if roleData.alignment.lower() == "good":
        currentString += f'Diff\n+'
    elif roleData.alignment.lower() == "evil":
        currentString += f'Diff\n-'
    else:
        currentString += f'\n'

    currentString += f'{roleData.alignment.upper()}\n{roleData.role_name}\n{roleInfo["description"]}\n\nAbilities:\n'

    #Abilites
    for ability in roleData.abilities:
        abilityInfo = info["abilities"][ability.name]
        abilityString = f'{ability.name} [x'
        if ability.charges != -1:
            abilityString += f'{ability.charges}'
        else:
            abilityString += '∞'
        abilityString += f'] - '

        if (ability.upgrade != 100 and ability.upgrade > 0 and ability.upgrade > len(abilityInfo["upgrades"])) or (ability.upgrade < 0 and abs(ability.upgrade) > len(abilityInfo["downgrades"])):
            ability.upgrade = 0

        if ability.upgrade == 0:
            abilityString += f'{abilityInfo["effect"]}'
        elif ability.upgrade == 100: #for alteranate versions of abilities that can't be directly copied
            abilityString += f'{abilityInfo["alternate"]}'
        elif ability.upgrade > 0:
            abilityString += f'{abilityInfo["upgrades"][ability.upgrade - 1]}'
        else:
            abilityString += f'{abilityInfo["downgrades"][abs(ability.upgrade) - 1]}'
        
        abilityString += f'\n\n'

        if len(currentString) + len(abilityString) + len(endString) > CHARACTER_LIMIT:
            currentString += endString
            allStrings.append(currentString)
            currentString = f'```Abilities (cont):\n{abilityString}'
        else:
            currentString += abilityString
    
    #Perks
    startingPerkString = f'Perks:\n'
    if len(currentString) + len(startingPerkString) + len(endString) > CHARACTER_LIMIT:
        currentString += endString
        allStrings.append(currentString)
        currentString = f'```'
    
    currentString += startingPerkString

    for perk in roleData.perks:
        perkInfo = info["perks"][perk.name]
        perkString = f'{perk.name} '
        perkString += f'- '

        if (perk.upgrade != 100 and perk.upgrade > 0 and perk.upgrade > len(perkInfo["upgrades"])) or (perk.upgrade < 0 and abs(perk.upgrade) > len(perkInfo["downgrades"])):
            perk.upgrade = 0

        if perk.upgrade == 0:
            perkString += f'{perkInfo["effect"]}'
        elif perk.upgrade == 100: #for alteranate versions of perks that can't be directly copied
            perkString += f'{perkInfo["alternate"]}'
        elif perk.upgrade > 0:
            perkString += f'{perkInfo["upgrades"][perk.upgrade - 1]}'
        else:
            perkString += f'{perkInfo["downgrades"][abs(perk.upgrade) - 1]}'
        
        perkString += f'\n\n'

        if len(currentString) + len(perkString) + len(endString) > CHARACTER_LIMIT:
            currentString += endString
            allStrings.append(currentString)
            currentString = f'```Perks (cont):\n{perkString}'
        else:
            currentString += perkString
    currentString += endString
    allStrings.append(currentString)
    return allStrings
