import disnake
from disnake.ext import commands
import json
from helper_functions import *
import attr_classes
import os
from shared_data import Data, GAME_FILE

alignment_index_dict = {
    "Good": 0,
    "Neutral": 1,
    "Evil": 2
}

def set_player_statuses(server: disnake.Guild):
    for player in Data.game_data.players:
        conf_channel = server.get_channel(player.channel_id)
        if conf_channel is None:
            player.status = attr_classes.PlayerStatus.NULL
        elif conf_channel.category.name == Data.game_data.conf_category_name:
            player.status = attr_classes.PlayerStatus.ALIVE
        elif conf_channel.category.name == Data.game_data.dead_conf_category_name:
            player.status = attr_classes.PlayerStatus.DEAD
        else:
            player.status = attr_classes.PlayerStatus.NULL

    save_game_data()

def determine_alliances(server: disnake.Guild) -> dict:
    set_player_statuses(server)
    allianceCategory = disnake.utils.find(lambda c: c.name == Data.game_data.alliance_category_name, server.categories)

    alliances = {}
    for channel in allianceCategory.channels:
        alliances[channel.name] = []
        for member in channel.members:
            if compareLists(member.roles, ["Participant"]):
                player = Data.game_data.get_player_from_link(member.id)
                if player is not None and player not in alliances[channel.name]:
                    alliances[channel.name].append(player)
                    
    return alliances

def base_luck_calculation(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
    alignment = player.role.alignment
    luck_modify = 0
    for alliance_name, members in alliances.items():
        if player in members:
            for ally in members:
                if ally is player:
                    continue
                ally_alignment = ally.role.alignment
                #print(alignment_index_dict)
                if ally_alignment in alignment_index_dict.keys():
                    luck_modify += alignment_amount[player][alignment_index_dict[ally_alignment]]

    if player.inventory is not None:
        for item in player.inventory.get_section("items").contents:
            if item.lower() == "lucky coin":
                luck_modify += 4
            elif item.lower() == "lucky trinket":
                luck_modify += 1
            elif item.lower() == "lucky charm":
                luck_modify += 3

    player.luck += luck_modify

def status_luck_calculation(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]], luck_calc_dict: dict, alignment_amount: dict) -> None:
    if player.inventory is None:
        return
    statuses = [x.lower() for x in player.inventory.get_section("status").contents]
    if "lucky" in statuses:
        player.luck *= 2
    if "unlucky" in statuses:
        player.luck = int(player.luck * 0.5)

def set_luck_functions(alliances: dict, luck_calc_dict: dict, alignment_amount: dict) -> None:
    for player in Data.game_data.players:
        perks = []
        if player.has_role():
            perks = player.role.perks
        luck_calc_dict.setdefault(player, {}).setdefault(attr_classes.LuckCalcOrder.LUCK_CALC, []).append(base_luck_calculation)
        luck_calc_dict.setdefault(player, {}).setdefault(attr_classes.LuckCalcOrder.STATUSES, []).append(status_luck_calculation)

        for perk in perks:
            #print(perk)
            if perk == None:
                continue
            perk.set_luck_functions(luck_calc_dict)

def do_luck_calcs(alliances: dict, luck_calc_dict: dict, alignment_amount: dict):
    for stage in attr_classes.LuckCalcOrder:
        #print(stage, luck_dict)
        for player, calc_dict in luck_calc_dict.items():
            if stage in calc_dict.keys():
                for func in calc_dict[stage]:
                    func(player, alliances, luck_calc_dict, alignment_amount)

    luck_calc_dict.clear()

def setup_calcs(luck_calc_dict: dict, alignment_amount: dict):
    for player in Data.game_data.players:
        if not player.has_role():
            continue

        luck_calc_dict[player] = {}
        alignment = player.role.alignment
        player.luck = 0

        if alignment == "Good":
            alignment_amount[player] = [2, 1, 0]
        elif alignment == "Evil":
            alignment_amount[player] = [0, 1, 2]
        else:
            alignment_amount[player] = [1, 1, 1]

def setup(bot, INFO_FILE="info.json", GAME_FILE="inventoryInfo.json", ALLIANCES_CATEGORY="Alliances", CONFESSIONALS_CATEGORY="Confessionals"):
    #Luck calculation
    @bot.slash_command(name='luck', description="Calculates and manages confessional luck.")
    @commands.default_member_permissions(administrator=True)
    async def luck(ctx):
        pass



    @luck.sub_command(name='calculate', description="Calculates luck for each confessional based on their alignment and allies.")
    async def luck_calculate(ctx):
        check_active_game(ctx.guild)
        alliances = determine_alliances(ctx.guild)

        luck_calc_dict = {}
        alignment_amount = {}
        luck_dict = {}
        setup_calcs(luck_calc_dict, alignment_amount)
        #print(alignment_amount, luck_dict)
        set_luck_functions(alliances, luck_calc_dict, alignment_amount)
        #print(luck_calc_dict)
        do_luck_calcs(alliances, luck_calc_dict, alignment_amount)
        #print(alignment_amount, luck_dict)
        
        save_game_data()
        await ctx.send("Luck calculation complete.")

    @luck.sub_command(name='view', description="Views the luck of all confessionals.")
    async def luck_view(ctx):
        check_active_game(ctx.guild)

        message = "Confessional Luck:\n"
        for player in Data.game_data.players:
            if not player.can_gain():
                continue
            luckValue = player.luck
            message += f'"{player.conf_name}": {luckValue}\n'
        await ctx.send(message)

    @luck.sub_command(name='set', description="Sets the luck of a confessional linked to the specified user.")
    async def luck_set(ctx, user: disnake.User, luck: int):
        check_active_game(ctx.guild)

        player = Data.game_data.get_player_from_link(user.id)
        if player is None:
            await ctx.send(f'No confessional link found for user {user.name}.')
            return

        player.luck = luck

        save_game_data
        await ctx.send(f'Luck for confessional "{player.conf_name}" set to {luck}.')
    #End of luck section