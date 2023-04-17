from enum import Enum

class Status(str, Enum):
    Cursed = "cursed"
    Frozen = "Frozen"

class Role(str, Enum):
    Terminal = "terminal"
    Gunman = "gunman"


# Initialize all the slash commands
def initialize_slash_commands(bot):
    @bot.slash_command()
    async def status(inter, status: Status, hidden: bool = False):
        await inter.response.send_message("Imagine a description of %s" % (status), ephemeral=hidden)

    @bot.slash_command()
    async def role(inter, role: Role, hidden: bool = False):
        await inter.response.send_message("Imagine a description of %s" % (status), ephemeral=hidden)

