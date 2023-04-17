from enum import Enum
import disnake
import json

class Status(str, Enum):
    Cursed = "cursed"
    Frozen = "frozen"
    Paralyzed = "paralyzed"
    Burned = "burned"
    Empowered = "empowered"
    Drunk = "drunk"
    Restrained = "restrained"
    Disabled = "disabled"
    Blackmailed = "blackmailed"
    Despaired = "despaired"
    Lucky = "lucky"
    Unlucky = "unlucky"

async def status(inter, arg: Status, hidden: bool = False):
    statusColors = {
        "Lucky": 0x00FF00, #Green
        "Unlucky": 0xFF0000, #Red
        "Cursed": 0x888888, #Gray
        "Frozen": 0xA5F2F3, #Ice color
        "Paralyzed": 0xFFFF00, #Yellow
        "Burned": 0xE25822, #Orangeish
        "Empowered": 0xFFFF33, #Neon Yellow
        "Drunk": 0x964B00, #Brown
        "Restrained": 0x222222, #Darker Gray
        "Disabled": 0xCCCCCC, #Light Gray
        "Despaired": 0x555555, #Dark Gray
        "Blackmailed": 0x000000 #Black
        }
    
    file = open("info.json")
    data = json.load(file)
    file.close()
    for status, info in data["statuses"].items():
        if arg.lower() == status.lower() or arg.lower() + "ed" == status.lower() or arg.lower() + "d" == status.lower():
            embed = disnake.Embed(title=f'{status}', description=f'{info}', color=statusColors[status])
            await inter.send(embed=embed, ephemeral = hidden)
            return
    await inter.send("Status not found", ephemeral = hidden)
    