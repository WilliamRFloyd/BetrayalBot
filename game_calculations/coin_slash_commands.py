import disnake
from disnake.ext import commands
import json
from helper_functions import *
from .alliance_commands import determine_alliances
import attr_classes
import os
from shared_data import Data, GAME_FILE

def base_coin_calculation(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]]) -> None:
    coin_base = 200
    for members in alliances.values():
        if player in members:
            numMembers = len(members)
            if numMembers == 2:
                coin_base += 20
            elif numMembers == 3:
                coin_base += 40
            elif numMembers >= 4:
                coin_base += 100

    if player.inventory is not None:
        coin_bonus = player.inventory.get_section("bonus").contents
        coin_base += int(coin_bonus * 2)

    player.calced_coins = coin_base

def status_coin_calculation(player: attr_classes.Player, alliances: dict[str, list[attr_classes.Player]]) -> None:
    if player.inventory is None:
        return
    statuses = [x.lower() for x in player.inventory.get_section("status").contents]
    if "lucky" in statuses:
        player.calced_coins = int(player.calced_coins * 1.5)
    if "unlucky" in statuses:
        player.calced_coins = int(player.calced_coins * 0.5)

def set_coin_functions(alliances: dict, coin_calc_dict: dict) -> None:
    for player in Data.game_data.players:
        if not player.can_gain():
            continue
        perks = []
        if player.has_role():
            perks = player.role.perks
        coin_calc_dict.setdefault(player, {}).setdefault(attr_classes.CoinCalcOrder.COIN_CALC, []).append(base_coin_calculation)
        coin_calc_dict.setdefault(player, {}).setdefault(attr_classes.CoinCalcOrder.STATUSES, []).append(status_coin_calculation)

        for perk in perks:
            perk.set_coin_functions(coin_calc_dict)

def do_coin_calcs(alliances: dict, coin_calc_dict: dict):
    for stage in attr_classes.CoinCalcOrder:
        for player, calc_dict in coin_calc_dict.items():
            if stage in calc_dict.keys():
                for func in calc_dict[stage]:
                    func(player, alliances)

    coin_calc_dict.clear()

def setup_calcs(coin_calc_dict: dict):
    for player in Data.game_data.players:
        if not player.can_gain():
            continue
        if not player.has_role():
            continue

        coin_calc_dict[player] = {}
        player.calced_coins = 0

def perform_coin_calculation(alliances: dict):
    coin_calc_dict = {}
    setup_calcs(coin_calc_dict)
    set_coin_functions(alliances, coin_calc_dict)
    do_coin_calcs(alliances, coin_calc_dict)
    save_game_data()

def make_coin_string() -> str:
    coinString = "Calculated Coins:\n"
    for player in Data.game_data.players:
        if not player.can_gain() or player.inventory is None:
            continue
        coinString += f'{player.conf_name}: {int(player.calced_coins)}\n'    
    return coinString

def setup(bot):
    #Coin calculation
    @bot.slash_command(name='coin', description="Calculates and manages confessional coin gain.")
    @commands.default_member_permissions(administrator=True)
    async def coin(ctx):
        check_active_game(ctx.guild)

    @coin.sub_command(name='calculate', description="Calculates coin gain for each confessional based on their allies.")
    async def coin_calculate(ctx):
        perform_coin_calculation(determine_alliances(ctx.guild))

        await ctx.send("Coin calculation complete.")

    @coin.sub_command(name='view', description="Views the predicted coin gain of all confessionals.")
    async def coin_view(ctx):
        message = "Confessional Coin Gain:\n"
        for player in Data.game_data.players:
            if not player.can_gain():
                continue
            coinValue = player.calced_coins
            message += f'"{player.conf_name}": {coinValue}\n'
        await ctx.send(message)

    @coin.sub_command(name='set', description="Sets the coin gain of a confessional linked to the specified user.")
    async def coin_set(ctx, user: disnake.User, coins: int):
        player = Data.game_data.get_player_from_link(user.id)
        if player is None:
            await ctx.send(f'No confessional link found for user {user.name}.')
            return

        player.calced_coins = coins

        save_game_data()
        await ctx.send(f'Coin gain for confessional "{player.conf_name}" set to {coins}.')

    @coin.sub_command(name='send', description="Displays calced coins and gives the option to send them.")
    async def coin_send(ctx):
        coinString = make_coin_string()
            
        await ctx.send(coinString, components=[
            disnake.ui.Button(label="Distribute", style=disnake.ButtonStyle.success, custom_id="send_coins"),
        ])
    #End of coin section