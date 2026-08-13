import disnake
from disnake.ext import commands
import json
from helper_functions import *
import attr_classes
import os
from shared_data import Data, GAME_FILE

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

def setup(bot):
    @bot.slash_command(name='check_alliances', description="Checks what the bot thinks the alliances are.")
    #@commands.default_member_permissions(administrator=True)
    async def check_alliances(ctx):
        check_active_game(ctx.guild)
        alliances = determine_alliances(ctx.guild)
        message = "Alliances:\n"
        for alliance_name, players in alliances.items():
            message += f"{alliance_name}: {[player.conf_name.replace("-confessional", "") for player in players]}\n"
        await ctx.send(message)