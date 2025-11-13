import disnake
from disnake.ext import commands
import json
from helper_functions import *

async def determine_alliances(server: disnake.Guild) -> dict:
    data = openJson("inventoryInfo.json")
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
        for confName, confData in data.get("confessionals", {}).items():
            if confName not in aliveConfs:
                continue
            roleAlignment = confData.get("role", {}).get("alignment", "Neutral").lower()
            confLuck = 0
            for allianceName, members in alliances.items():
                if confName in members:
                    for allyConf in members:
                        if allyConf == confName:
                            continue
                        allyAlignment = data.get("confessionals", {}).get(allyConf, {}).get("role", {}).get("alignment", "Neutral").lower()
                        if roleAlignment == "good":
                            if allyAlignment == "good":
                                confLuck += 2
                            elif allyAlignment == "evil":
                                confLuck += 0
                            else:
                                confLuck += 1
                        elif roleAlignment == "evil":
                            if allyAlignment == "evil":
                                confLuck += 2
                            elif allyAlignment == "good":
                                confLuck += 0
                            else:
                                confLuck += 1
                        else:
                            confLuck += 1

            if "lucky" in [x.lower() for x in confData["inventory"]["statuses"]]:
                confLuck *= 2
            if "unlucky" in [x.lower() for x in confData["inventory"]["statuses"]]:
                confLuck *= .5
            confData["luck"] = int(confLuck)
        
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