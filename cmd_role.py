from enum import Enum
import json
import disnake

# CUSTOM MODULES
from util import AlignmentColours, find_most_similar_string

async def create_embed(role: str, info: dict):
    name = role
    alignment = info["alignment"]
    description = info["description"]
    abilities = info["abilities"]
    perks = info["perks"]
    achievements = info["achievements"]
        
    embed = disnake.Embed(title=f'{name}', description=f'**{alignment}**\n{description}\n\n**Abilities:**', color=AlignmentColours[alignment])
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
    return embed

async def role(inter, req_role: str, hidden: bool = False):
    file = open("info.json")
    data = json.load(file)
    file.close()

    role_list = []

    for role, info in data["classes"].items():
        if req_role.lower() == role.lower():
            embed = await create_embed(role, info)
            await inter.send(embed=embed, ephemeral=hidden)
            return
        else:
            role_list.append(role)


    closest_role = find_most_similar_string(req_role, role_list)
    embed = await create_embed(closest_role, data["classes"][closest_role])

    response = "Role not found, did you mean __%s__?" % (closest_role)

    await inter.send(response, embed=embed, ephemeral=hidden)