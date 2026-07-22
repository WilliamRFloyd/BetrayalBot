import disnake
from disnake.ext import commands
import json
from helper_functions import *
import attr_classes
import os

codePath = os.path.dirname(os.path.realpath(__file__))

GAME_FILE = codePath + "/inventoryInfo.json"

alignment_index_dict = {
    "Good": 0,
    "Neutral": 1,
    "Evil": 2
}

async def determine_alliances(server: disnake.Guild) -> dict:
    data = openJson(GAME_FILE)
    allianceCategory = disnake.utils.find(lambda c: c.name == "Alliances", server.categories)
    confCategory = disnake.utils.find(lambda c: c.name == "Confessionals", server.categories)
    alliances = {}
    for channel in allianceCategory.channels:
        alliances[channel.name] = []
        for member in channel.members:
            if compareLists(member.roles, ["Participant"]):
                playerConf = data["confLinks"].get(str(member.id), None)
                if playerConf and playerConf not in alliances[channel.name]:
                    alliances[channel.name].append(playerConf)
    
    print(alliances)
    return alliances

def base_luck_calculation(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
    alignment = player_info.get(player_conf_name, {}).get("role", {}).get("alignment", "Neutral")
    luck_modify = 0
    for alliance_name, members in alliances.items():
        if player_conf_name in members:
            for ally_conf in members:
                if ally_conf == player_conf_name:
                    continue
                ally_alignment = player_info.get(ally_conf, {}).get("role", {}).get("alignment", "Neutral").capitalize()
                #print(alignment_index_dict)
                if ally_alignment in alignment_index_dict.keys():
                    luck_modify += alignment_amount[player_conf_name][alignment_index_dict[ally_alignment]]
    
    for item in player_info.get(player_conf_name, {}).get("inventory", {}).get("items", []):
        if item.lower() == "lucky coin":
            luck_modify += 4
        elif item.lower() == "lucky trinket":
            luck_modify += 1
        elif item.lower() == "lucky charm":
            luck_modify += 3

    luck_dict[player_conf_name] += luck_modify

def status_luck_calculation(player_conf_name: str, player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
    statuses = [x.lower() for x in player_info.get(player_conf_name, {}).get("inventory", {}).get("statuses", [])]
    if "lucky" in statuses:
        luck_dict[player_conf_name] *= 2
    if "unlucky" in statuses:
        luck_dict[player_conf_name] = int(luck_dict[player_conf_name] * 0.5)

def set_luck_functions(player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict) -> None:
    for player_conf_name in luck_calc_dict.keys():
        perks = player_info.get(player_conf_name, {}).get("role", {}).get("perks", {})
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.LUCK_CALC, []).append(base_luck_calculation)
        luck_calc_dict.setdefault(player_conf_name, {}).setdefault(attr_classes.LuckCalcOrder.STATUSES, []).append(status_luck_calculation)
        for perk_name, info in perks.items():
            upgrade = info.get("upgrade", 0)
            amount = info.get("copies", 1)
            perk = attr_classes.Perk.load_perk(perk_name, upgrade)
            #print(perk)
            if perk == None:
                continue
            for _ in range(amount):
                #print(perk)
                perk.set_luck_functions(player_conf_name, player_info, alliances, luck_calc_dict, alignment_amount, luck_dict)

def do_luck_calcs(player_info: dict, alliances: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict):
    for stage in attr_classes.LuckCalcOrder:
        #print(stage, luck_dict)
        for player, calc_dict in luck_calc_dict.items():
            if stage in calc_dict.keys():
                for func in calc_dict[stage]:
                    func(player, player_info, alliances, luck_calc_dict, alignment_amount, luck_dict)

    luck_calc_dict.clear()

def setup_calcs(aliveConfs: list, player_info: dict, luck_calc_dict: dict, alignment_amount: dict, luck_dict: dict):
    for conf in aliveConfs:
        luck_calc_dict[conf] = {}
        alignment = player_info[conf]["role"]["alignment"]
        if alignment == "Good":
            alignment_amount[conf] = [2, 1, 0]
        elif alignment == "Evil":
            alignment_amount[conf] = [0, 1, 2]
        else:
            alignment_amount[conf] = [1, 1, 1]
        luck_dict[conf] = 0

def setup(bot, INFO_FILE="info.json", GAME_FILE="inventoryInfo.json", ALLIANCES_CATEGORY="Alliances", CONFESSIONALS_CATEGORY="Confessionals"):
    #Luck calculation
    @bot.slash_command(name='luck', description="Calculates and manages confessional luck.")
    @commands.default_member_permissions(administrator=True)
    async def luck(ctx):
        pass



    @luck.sub_command(name='calculate', description="Calculates luck for each confessional based on their alignment and allies.")
    async def luck_calculate(ctx):
        alliances = await determine_alliances(ctx.guild)
        confCategory = disnake.utils.find(lambda c: c.name == CONFESSIONALS_CATEGORY, ctx.guild.categories)
        aliveConfs = [x.name for x in confCategory.channels]
        data = openJson(GAME_FILE)
        player_info = data["confessionals"]
        luck_calc_dict = {}
        alignment_amount = {}
        luck_dict = {}
        setup_calcs(aliveConfs, player_info, luck_calc_dict, alignment_amount, luck_dict)
        #print(alignment_amount, luck_dict)
        set_luck_functions(player_info, alliances, luck_calc_dict, alignment_amount, luck_dict)
        #print(luck_calc_dict)
        do_luck_calcs(player_info, alliances, luck_calc_dict, alignment_amount, luck_dict)
        #print(alignment_amount, luck_dict)

        for conf_name, luck_amount in luck_dict.items():
            player_info[conf_name]["luck"] = luck_amount
        
        writeJson(GAME_FILE, data)
        await ctx.send("Luck calculation complete.")

    @luck.sub_command(name='view', description="Views the luck of all confessionals.")
    async def luck_view(ctx):
        confCategory = disnake.utils.find(lambda c: c.name == CONFESSIONALS_CATEGORY, ctx.guild.categories)
        aliveConfs = [x.name for x in confCategory.channels]
        data = openJson(GAME_FILE)
        if "confessionals" not in data:
            await ctx.send("No confessionals found.")
            return
        message = "Confessional Luck:\n"
        for confName, confData in data["confessionals"].items():
            if confName not in aliveConfs:
                continue
            luckValue = confData.get("luck", 0)
            message += f'"{confName}": {luckValue}\n'
        await ctx.send(message)

    @luck.sub_command(name='set', description="Sets the luck of a confessional linked to the specified user.")
    async def luck_set(ctx, user: disnake.User, luck: int):
        data = openJson(GAME_FILE)
        confName = data.get("confLinks", {}).get(str(user.id), None)
        if not confName:
            await ctx.send(f'No confessional link found for user {user.name}.')
            return
        if "confessionals" not in data or confName not in data["confessionals"]:
            await ctx.send(f'No confessional found for "{confName}".')
            return
        data["confessionals"][confName]["luck"] = luck
        writeJson(GAME_FILE, data)
        await ctx.send(f'Luck for confessional "{confName}" set to {luck}.')
    #End of luck section