import disnake
from disnake.ext import commands
import json
from helper_functions import *
from shared_data import Data, INFO_FILE
from attr_classes import Ability, Perk

def setup(bot):
    #Code for managing roles
    @bot.slash_command(name='role', description="Manage confessional roles.")
    async def role(ctx):
        check_active_game(ctx.guild)

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

        channel = ctx.channel

        if (not Data.game_data.has_player(channel.name)):
            Data.game_data.add_player(channel.name, channel.id)
        player = Data.game_data.get_player(channel.name)
        if player.has_role():
            await ctx.send("A role already exists for this confessional. Please delete/forget it first if you want to create a new one.")
            return
        
        player.add_role(roleName, roleInfo)

        roleStrings = generateRoleStrings(player.role, info)
        for roleString in roleStrings:
            message = await channel.send(roleString)
            player.role.message_ids.append(message.id)

        save_game_data()
        await ctx.send(f'Role "{roleName}" created for this confessional.')

    @role.sub_command(name='forget', description="Forgets the role for the confessional this command is sent in.")
    async def role_forget(ctx):
        channel = ctx.channel
        if (not Data.game_data.has_player(channel.name)) or (not Data.game_data.get_player(channel.name).has_role()):
            await ctx.send("No role found for this confessional.")
            return

        Data.game_data.get_player(channel.name).remove_role()

        save_game_data()
        await ctx.send("Role forgotten.")

    @role.sub_command(name='delete', description="Deletes the role for the confessional this command is sent in.")
    async def role_delete(ctx):
        channel = ctx.channel
        if (not Data.game_data.has_player(channel.name)) or (not Data.game_data.get_player(channel.name).has_role()):
            await ctx.send("No role found for this confessional.")
            return

        player = Data.game_data.get_player(channel.name)
        for messageId in player.role.message_ids:
            try:
                message = await channel.fetch_message(messageId)
                await message.delete()
            except:
                pass

        player.remove_role()

        save_game_data()
        await ctx.send("Role deleted.")

    @role.sub_command(name='refresh', description="Refreshes the role messages for the confessional this command is sent in.")
    async def role_refresh(ctx):
        channel = ctx.channel
        if (not Data.game_data.has_player(channel.name)) or (not Data.game_data.get_player(channel.name).has_role()):
            await ctx.send("No role found for this confessional.")
            return

        player = Data.game_data.get_player(channel.name)
        newMessages = []
        for messageId in player.role.message_ids:
            try:
                message = await channel.fetch_message(messageId)
                await message.delete()
                newId = await ctx.channel.send(message.content)
                newMessages.append(newId.id)
            except:
                pass

        player.role.message_ids = newMessages

        save_game_data()
        await ctx.send("Role messages refreshed.")

    @role.sub_command(name='view', description="Views the role for the confessional this command is sent in.")
    async def role_view(ctx):
        channel = ctx.channel
        if (not Data.game_data.has_player(channel.name)) or (not Data.game_data.get_player(channel.name).has_role()):
            await ctx.send("No role found for this confessional.")
            return

        player_role = Data.game_data.get_player(channel.name).role
        for messageId in player_role.message_ids:
            try:
                message = await channel.fetch_message(messageId)
                await ctx.send(message.content)
            except:
                pass

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
        channel = ctx.channel
        if (not Data.game_data.has_player(channel.name)) or (not Data.game_data.get_player(channel.name).has_role()):
            await ctx.send("No role found for this confessional.")
            return

        player_role = Data.game_data.get_player(channel.name).role

        player_role.alignment = alignment.capitalize()

        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Role alignment changed to {alignment}.')

    @role.sub_command_group(name='ability', description="Manage abilities for the role of the confessional this command is sent in.")
    async def role_ability(ctx):
        channel = ctx.channel
        if (not Data.game_data.has_player(channel.name)) or (not Data.game_data.get_player(channel.name).has_role()):
            await ctx.send("No role found for this confessional.")
            return

    @role_ability.sub_command(name='add', description="Adds an ability to the role for the confessional this command is sent in.")
    async def role_ability_add(ctx, ability: str, charges: int = 1):
        channel = ctx.channel
        info = openJson(INFO_FILE)
        abilityName = findIgnoringCase(ability, info["abilities"].keys())

        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return

        player_role = Data.game_data.get_player(channel.name).role
        player_role.add_ability(abilityName, charges)
        
        roleStrings = generateRoleStrings(player_role, info)
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Ability "{ability}" added/updated for this role.')

    @role_ability.sub_command(name='remove', description="Removes an ability from the role for the confessional this command is sent in.")
    async def role_ability_remove(ctx, ability: str, charges: int = 1):
        channel = ctx.channel
        info = openJson(INFO_FILE)
        abilityName = findIgnoringCase(ability, info["abilities"].keys())

        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return

        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_ability(abilityName):
            await ctx.send(f"Ability \"{abilityName}\" not found for this role.")
            return
        
        player_role.add_ability(abilityName, -charges)
        
        roleStrings = generateRoleStrings(player_role, info)
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Ability "{ability}" lost {charges} for this role.')

    @role_ability.sub_command(name='upgrade', description="Upgrades an ability for the role of the confessional this command is sent in.")
    async def role_ability_upgrade(ctx, ability: str, upgrade: int):
        channel = ctx.channel

        info = openJson(INFO_FILE) 
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return
        
        if upgrade < 0 or upgrade > len(info["abilities"][abilityName]["upgrades"]):
            await ctx.send(f'Upgrade number {upgrade} is out of bounds for ability "{abilityName}".')
            return

        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_ability(abilityName):
            await ctx.send(f"Ability \"{abilityName}\" not found for this role.")
            return

        player_role.get_ability(abilityName).upgrade = upgrade
        
        roleStrings = generateRoleStrings(player_role, info)
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Ability "{abilityName}" upgraded to upgrade {upgrade} for this role.')

    @role_ability.sub_command(name='degrade', description="Degrades an ability for the role of the confessional this command is sent in.")
    async def role_ability_degrade(ctx, ability: str, degrade: int):
        channel = ctx.channel

        info = openJson(INFO_FILE) 
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return
        
        if degrade < 0 or degrade > len(info["abilities"][abilityName]["degrades"]):
            await ctx.send(f'Degrade number {degrade} is out of bounds for ability "{abilityName}".')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_ability(abilityName):
            await ctx.send(f"Ability \"{abilityName}\" not found for this role.")
            return

        player_role.get_ability(abilityName).upgrade = -degrade
        
        roleStrings = generateRoleStrings(player_role, info)
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Ability "{abilityName}" degraded to degrade {degrade} for this role.')

    @role_ability.sub_command(name='delete', description="Deletes the ability from the role for the confessional this command is sent in.")
    async def role_ability_delete(ctx, ability: str):
        channel = ctx.channel

        info = openJson(INFO_FILE) 
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_ability(abilityName):
            await ctx.send(f"Ability \"{abilityName}\" not found for this role.")
            return

        player_role.remove_ability(abilityName)

        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Ability "{abilityName}" removed from this role.')

    @role_ability.sub_command(name='alternate', description="Sets a ability for the role of the confessional this command is sent in to its alternate version.")
    async def role_ability_alternate(ctx, ability: str):
        channel = ctx.channel

        info = openJson(INFO_FILE)
        abilityName = findIgnoringCase(ability, info["abilities"].keys())
        if abilityName == None:
            await ctx.send(f'Ability "{ability}" not found.')
            return
        if ["alternate"] not in info["abilities"][abilityName]:
            await ctx.send(f'Ability does not have an alternate form.')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_ability(abilityName):
            await ctx.send(f"Ability \"{abilityName}\" not found for this role.")
            return

        player_role.get_ability(abilityName).upgrade = 100

        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Ability "{abilityName}" set to alternate version.')

    @role.sub_command_group(name='perk', description="Manage perks for the role of the confessional this command is sent in.")
    async def role_perk(ctx):
        channel = ctx.channel
        if (not Data.game_data.has_player(channel.name)) or (not Data.game_data.get_player(channel.name).has_role()):
            await ctx.send("No role found for this confessional.")
            return

    @role_perk.sub_command(name='add', description="Adds a perk to the role for the confessional this command is sent in.")
    async def role_perk_add(ctx, perk: str):
        channel = ctx.channel
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())

        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        player_role.add_perk(perkName)

        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Perk "{perk}" added/updated for this role.')

    @role_perk.sub_command(name='remove', description="Removes a perk from the role for the confessional this command is sent in.")
    async def role_perk_remove(ctx, perk: str):
        channel = ctx.channel
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())

        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_perk(perkName):
            await ctx.send(f"Perk \"{perk}\" not found for this role.")
            return
        player_role.remove_perk(perkName)

        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Perk "{perk}" lost 1 copy for this role.')

    @role_perk.sub_command(name='upgrade', description="Upgrades a perk for the role of the confessional this command is sent in.")
    async def role_perk_upgrade(ctx, perk: str, upgrade: int):
        channel = ctx.channel
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())

        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        
        if upgrade < 0 or upgrade > len(info["perks"][perkName]["upgrades"]):
            await ctx.send(f'Upgrade number {upgrade} is out of bounds for perk "{perkName}".')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_perk(perkName):
            await ctx.send(f"Perk \"{perk}\" not found for this role.")
            return
        player_role.get_perk(perkName).upgrade = upgrade

        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Perk "{perkName}" upgraded to upgrade {upgrade} for this role.')

    @role_perk.sub_command(name='degrade', description="Degrades a perk for the role of the confessional this command is sent in.")
    async def role_perk_degrade(ctx, perk: str, degrade: int):
        channel = ctx.channel
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())

        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        
        if degrade < 0 or degrade > len(info["perks"][perkName]["degrades"]):
            await ctx.send(f'Degrade number {degrade} is out of bounds for perk "{perkName}".')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_perk(perkName):
            await ctx.send(f"Perk \"{perk}\" not found for this role.")
            return
        player_role.get_perk(perkName).upgrade = -degrade

        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Perk "{perkName}" degraded to degrade {degrade} for this role.')
    
    @role_perk.sub_command(name='alternate', description="Sets a perk for the role of the confessional this command is sent in to its alternate version.")
    async def role_perk_alternate(ctx, perk: str):
        channel = ctx.channel
        info = openJson(INFO_FILE)
        perkName = findIgnoringCase(perk, info["perks"].keys())

        if perkName == None:
            await ctx.send(f'Perk "{perk}" not found.')
            return
        
        if ["alternate"] not in info["perks"][perkName]:
            await ctx.send(f'Perk does not have an alternate form.')
            return
        
        player_role = Data.game_data.get_player(channel.name).role
        if not player_role.has_perk(perkName):
            await ctx.send(f"Perk \"{perk}\" not found for this role.")
            return
        player_role.get_perk(perkName).upgrade = 100
        
        roleStrings = generateRoleStrings(player_role, openJson(INFO_FILE))
        await updateRoleStrings(roleStrings, player_role.message_ids, channel)

        save_game_data()
        await ctx.send(f'Perk "{perkName}" set to alternate version.')
    #End of role management code