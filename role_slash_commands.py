import disnake
from disnake.ext import commands
import json
from helper_functions import *

def setup(bot, INFO_FILE="info.json", GAME_FILE="inventoryInfo.json"):
    #Code for managing roles
    @bot.slash_command(name='role', description="Manage confessional roles.")
    async def role(ctx):
        pass

    @role.sub_command(name='create', description="Creates a role for the confessional this command is sent in.")
    async def role_create(ctx, role_name: str):
        info = openJson(INFO_FILE)
        roleInfo = {}
        roleName = ""
        for role, rInfo in info["roles"].items():
            if role_name.lower() == role.lower():
                roleName = role
                roleInfo = rInfo
                break
        
        if roleName == "":
            await ctx.send(f'Role "{role_name}" not found.')
            return
        
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data:
            data["confessionals"] = {}
        if channel.name not in data["confessionals"]:
            data["confessionals"][channel.name] = {"channelId": channel.id}
        if "role" in data["confessionals"][channel.name]:
            await ctx.send("A role already exists for this confessional. Please delete/forget it first if you want to create a new one.")
            return

        roleData = {
            "name": roleName,
            "alignment": roleInfo["alignment"],
            "abilities": {},
            "perks": {},
            "messageIds": []
        }
        for ability in roleInfo["abilities"]:
            roleData["abilities"][ability] = {"charges": roleInfo["abilities"][ability], "upgrade": 0}
        for perk in roleInfo["perks"]:
            roleData["perks"][perk] = {"copies": 1, "upgrade": 0}
        
        data["confessionals"][channel.name]["role"] = roleData
        roleStrings = generateRoleStrings(roleData, info)
        for roleString in roleStrings:
            message = await channel.send(roleString)
            data["confessionals"][channel.name]["role"]["messageIds"].append(message.id)

        writeJson(GAME_FILE, data)
        await ctx.send(f'Role "{roleName}" created for this confessional.')

    @role.sub_command(name='forget', description="Forgets the role for the confessional this command is sent in.")
    async def role_forget(ctx):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return

        data["confessionals"][channel.name].pop("role")
        writeJson(GAME_FILE, data)
        await ctx.send("Role forgotten.")

    @role.sub_command(name='delete', description="Deletes the role for the confessional this command is sent in.")
    async def role_delete(ctx):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        for messageId in roleData["messageIds"]:
            try:
                message = await channel.fetch_message(messageId)
                await message.delete()
            except:
                pass
        data["confessionals"][channel.name].pop("role")
        writeJson(GAME_FILE, data)
        await ctx.send("Role deleted.")

    @role.sub_command(name='refresh', description="Refreshes the role messages for the confessional this command is sent in.")
    async def role_refresh(ctx):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return 
        
        roleData = data["confessionals"][channel.name]["role"]
        newMessages = []
        for messageId in roleData["messageIds"]:
            try:
                message = await channel.fetch_message(messageId)
                await message.delete()
                newId = await ctx.channel.send(message.content)
                newMessages.append(newId.id)
            except:
                pass
        data["confessionals"][channel.name]["role"]["messageIds"] = newMessages
        writeJson(GAME_FILE, data)
        await ctx.send("Role messages refreshed.")

    @role.sub_command(name='view', description="Views the role for the confessional this command is sent in.")
    async def role_view(ctx):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        for messageId in roleData["messageIds"]:
            try:
                message = await channel.fetch_message(messageId)
                await ctx.send(message.content)
            except:
                pass
        ctx.send("End of role view.")

    async def updateRoleStrings(newStrings, messageIds, channel):
        if len(newStrings) > len(messageIds):
            for i in range(len(messageIds)):
                message = await channel.fetch_message(messageIds[i])
                await message.edit(content=newStrings[i])
            for i in range(len(messageIds), len(newStrings)):
                message = await channel.send(newStrings[i])
                messageIds.append(message.id)
        
        elif len(newStrings) < len(messageIds):
            for i in range(len(newStrings)):
                message = await channel.fetch_message(messageIds[i])
                await message.edit(content=newStrings[i])
            for i in range(len(newStrings), len(messageIds)):
                message = await channel.fetch_message(messageIds[i])
                await message.delete()
            del messageIds[len(newStrings):]
        
        else:
            for i in range(len(newStrings)):
                message = await channel.fetch_message(messageIds[i])
                await message.edit(content=newStrings[i])

        return messageIds

    @role.sub_command(name='alignment', description="Changes the alignment of the role for the confessional this command is sent in.")
    async def role_alignment(ctx, alignment: str):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        roleData["alignment"] = alignment
        roleStrings = generateRoleStrings(roleData, openJson(INFO_FILE))
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Role alignment changed to {alignment}.')

    @role.sub_command_group(name='ability', description="Manage abilities for the role of the confessional this command is sent in.")
    async def role_ability(ctx):
        pass

    @role_ability.sub_command(name='add', description="Adds an ability to the role for the confessional this command is sent in.")
    async def role_ability_add(ctx, ability: str, charges: int = 1):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        
        info = openJson(INFO_FILE)
        abilityName = findIgnoringCase(ability, info["abilities"].keys())

        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return

        roleData = data["confessionals"][channel.name]["role"]
        if abilityName in roleData["abilities"]:
            roleData["abilities"][abilityName]["charges"] += charges
        else:
            roleData["abilities"][abilityName] = {"charges": charges, "upgrade": 0}
        
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Ability "{ability}" added/updated for this role.')

    @role_ability.sub_command(name='remove', description="Removes an ability from the role for the confessional this command is sent in.")
    async def role_ability_remove(ctx, ability: str, charges: int = 1):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        
        info = openJson(INFO_FILE)
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return

        roleData = data["confessionals"][channel.name]["role"]
        matchingAbility = findIgnoringCase(ability, roleData["abilities"].keys())
        if matchingAbility != None:
            roleData["abilities"][matchingAbility]["charges"] -= charges
        else:
            await ctx.send(f'Ability "{ability}" not found for this role.')
            return
        
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Ability "{ability}" lost {charges} for this role.')

    @role_ability.sub_command(name='upgrade', description="Upgrades an ability for the role of the confessional this command is sent in.")
    async def role_ability_upgrade(ctx, ability: str, upgrade: int):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return

        info = openJson(INFO_FILE) 
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return
        
        if upgrade < 0 or upgrade > len(info["abilities"][abilityName]["upgrades"]):
            await ctx.send(f'Upgrade number {upgrade} is out of bounds for ability "{abilityName}".')
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        matchingAbility = findIgnoringCase(ability, roleData["abilities"].keys())
        if matchingAbility != None:
            roleData["abilities"][matchingAbility]["upgrade"] = upgrade
        else:
            await ctx.send(f'Ability "{ability}" not found for this role.')
            return
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Ability "{matchingAbility}" upgraded to upgrade {upgrade} for this role.')

    @role_ability.sub_command(name='degrade', description="Degrades an ability for the role of the confessional this command is sent in.")
    async def role_ability_degrade(ctx, ability: str, degrade: int):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return

        info = openJson(INFO_FILE) 
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return
        
        if degrade < 0 or degrade > len(info["abilities"][abilityName]["degrades"]):
            await ctx.send(f'Degrade number {degrade} is out of bounds for ability "{abilityName}".')
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        matchingAbility = findIgnoringCase(ability, roleData["abilities"].keys())
        if matchingAbility != None:
            roleData["abilities"][matchingAbility]["upgrade"] = -degrade
        else:
            await ctx.send(f'Ability "{ability}" not found for this role.')
            return
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Ability "{matchingAbility}" degraded to degrade {degrade} for this role.')

    @role_ability.sub_command(name='delete', description="Deletes the ability from the role for the confessional this command is sent in.")
    async def role_ability_delete(ctx, ability: str):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        abilityName = findIgnoringCase(ability, roleData["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found for this role.')
            return
        roleData["abilities"].pop(abilityName)
        roleStrings = generateRoleStrings(roleData, openJson(INFO_FILE))
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Ability "{abilityName}" removed from this role.')

    @role_ability.sub_command(name='alternate', description="Sets a ability for the role of the confessional this command is sent in to its alternate version.")
    async def role_ability_alternate(ctx, ability: str):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        info = openJson(INFO_FILE)
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return
        if ["alternate"] not in info["abilities"][abilityName]:
            await ctx.send(f'Ability does not have an alternate form.')
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        if abilityName in roleData["abilities"]:
            roleData["abilities"][abilityName]["upgrade"] = 100
        else:
            await ctx.send(f'Abilitiy "{ability}" not found for this role.')
            return
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Ability "{abilityName}" set to alternate version.')

    @role.sub_command_group(name='perk', description="Manage perks for the role of the confessional this command is sent in.")
    async def role_perk(ctx):
        pass

    @role_perk.sub_command(name='add', description="Adds a perk to the role for the confessional this command is sent in.")
    async def role_perk_add(ctx, perk: str):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())
        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        roleData = data["confessionals"][channel.name]["role"]
        if perkName in roleData["perks"]:
            roleData["perks"][perkName]["copies"] += 1
        else:
            roleData["perks"][perkName] = {"copies": 1, "upgrade": 0}
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Perk "{perk}" added/updated for this role.')

    @role_perk.sub_command(name='remove', description="Removes a perk from the role for the confessional this command is sent in.")
    async def role_perk_remove(ctx, perk: str):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())
        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        roleData = data["confessionals"][channel.name]["role"]
        if perkName in roleData["perks"]:
            roleData["perks"][perkName]["copies"] -= 1
            if roleData["perks"][perkName]["copies"] <= 0:
                roleData["perks"].pop(perkName)
        else:
            await ctx.send(f'Perk "{perk}" not found for this role.')
            return
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Perk "{perk}" lost 1 copy for this role.')

    @role_perk.sub_command(name='upgrade', description="Upgrades a perk for the role of the confessional this command is sent in.")
    async def role_perk_upgrade(ctx, perk: str, upgrade: int):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        info = openJson(INFO_FILE) 
        perkName = findIgnoringCase(perk, info["perks"].keys())
        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        
        if upgrade < 0 or upgrade > len(info["perks"][perkName]["upgrades"]):
            await ctx.send(f'Upgrade number {upgrade} is out of bounds for perk "{perkName}".')
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        if perkName in roleData["perks"]:
            roleData["perks"][perkName]["upgrade"] = upgrade
        else:
            await ctx.send(f'Perk "{perk}" not found for this role.')
            return
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Perk "{perkName}" upgraded to upgrade {upgrade} for this role.')

    @role_perk.sub_command(name='degrade', description="Degrades a perk for the role of the confessional this command is sent in.")
    async def role_perk_degrade(ctx, perk: str, degrade: int):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())
        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        if degrade < 0 or degrade > len(info["perks"][perkName]["degrades"]):
            await ctx.send(f'Degrade number {degrade} is out of bounds for perk "{perkName}".')
            return
        roleData = data["confessionals"][channel.name]["role"]
        if perkName in roleData["perks"]:
            roleData["perks"][perkName]["upgrade"] = -degrade
        else:
            await ctx.send(f'Perk "{perk}" not found for this role.')
            return
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Perk "{perkName}" degraded to degrade {degrade} for this role.')
    
    @role_perk.sub_command(name='alternate', description="Sets a perk for the role of the confessional this command is sent in to its alternate version.")
    async def role_perk_alternate(ctx, perk: str):
        data = openJson(GAME_FILE)
        channel = ctx.channel
        if "confessionals" not in data or channel.name not in data["confessionals"] or "role" not in data["confessionals"][channel.name]:
            await ctx.send("No role found for this confessional.")
            return
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())
        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        if ["alternate"] not in info["perks"][perkName]:
            await ctx.send(f'Perk does not have an alternate form.')
            return
        
        roleData = data["confessionals"][channel.name]["role"]
        if perkName in roleData["perks"]:
            roleData["perks"][perkName]["upgrade"] = 100
        else:
            await ctx.send(f'Perk "{perk}" not found for this role.')
            return
        roleStrings = generateRoleStrings(roleData, info)
        roleData["messageIds"] = await updateRoleStrings(roleStrings, roleData["messageIds"], channel)
        writeJson(GAME_FILE, data)
        await ctx.send(f'Perk "{perkName}" set to alternate version.')
    #End of role management code