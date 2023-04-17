from enum import Enum
import cmd_status
import cmd_role

# Initialize all the slash commands
def initialize_slash_commands(bot):
    @bot.slash_command(description="View the effects of the specified status.")
    async def viewstatus(inter, status: cmd_status.Status, hidden: bool = False):
        await cmd_status.status(inter, status, hidden)

    @bot.slash_command(description="View a Betrayal role")
    async def viewrole(inter, role: str, hidden: bool = False):
        await cmd_role.role(inter, role, hidden)