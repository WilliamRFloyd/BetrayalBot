from enum import Enum

class Status(str, Enum):
    Cursed = "cursed"
    Frozen = "Frozen"

async def status(inter, status: Status, hidden: bool = False):
    await inter.response.send_message("Imagine a description of %s" % (status), ephemeral=hidden)
