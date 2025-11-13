#Dependencies
import os
import random
import json
import re
import datetime
import helper_functions

#Constants
CHARACTER_LIMIT = 2000

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
        data = json.load(file)
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
def generateRoleStrings(roleData, info):
    #Basics
    roleInfo = info["roles"][roleData["name"]]
    allStrings = []
    currentString = f'```'
    endString = '```'
    if roleData["alignment"].lower() == "good":
        currentString += f'Diff\n+'
    elif roleData["alignment"].lower() == "evil":
        currentString += f'Diff\n-'
    else:
        currentString += f'\n'

    currentString += f'{roleData["alignment"].upper()}\n{roleData["name"]}\n{roleInfo["description"]}\n\nAbilities:\n'

    #Abilites
    for ability, abilityData in roleData["abilities"].items():
        abilityInfo = info["abilities"][ability]
        abilityString = f'{ability} [x'
        if abilityData["charges"] != "inf":
            abilityString += f'{abilityData["charges"]}'
        else:
            abilityString += '∞'
        abilityString += f'] - '

        if (abilityData["upgrade"] > 0 and abilityData["upgrade"] > len(abilityInfo["upgrades"])) or (abilityData["upgrade"] < 0 and abs(abilityData["upgrade"]) > len(abilityInfo["downgrades"])):
            abilityData["upgrade"] = 0

        if abilityData["upgrade"] == 0:
            abilityString += f'{abilityInfo["effect"]}'
        elif abilityData["upgrade"] == 100: #for alteranate versions of abilities that can't be directly copied
            abilityString += f'{abilityInfo["alternate"]}'
        elif abilityData["upgrade"] > 0:
            abilityString += f'{abilityInfo["upgrades"][abilityData["upgrade"] - 1]}'
        else:
            abilityString += f'{abilityInfo["downgrades"][abs(abilityData["upgrade"]) - 1]}'
        
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

    for perk, perkData in roleData["perks"].items():
        perkInfo = info["perks"][perk]
        perkString = f'{perk} '
        if perkData["copies"] > 1:
            perkString += f'[x{perkData["copies"]}] - '
        else:
            perkString += f'- '

        if (perkData["upgrade"] > 0 and perkData["upgrade"] > len(perkInfo["upgrades"])) or (perkData["upgrade"] < 0 and abs(perkData["upgrade"]) > len(perkInfo["downgrades"])):
            perkData["upgrade"] = 0

        if perkData["upgrade"] == 0:
            perkString += f'{perkInfo["effect"]}'
        elif perkData["upgrade"] > 0:
            perkString += f'{perkInfo["upgrades"][perkData["upgrade"] - 1]}'
        else:
            perkString += f'{perkInfo["downgrades"][abs(perkData["upgrade"]) - 1]}'
        
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
