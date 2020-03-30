# GroundDug Misc Utility Functions

import asyncio
import cogs.utils.db as db
import os

environment = os.getenv("GD_ENV", "beta")

async def getPrefix(bot,message):
    # Return gb! prefix if files are in beta environment
    if environment == "beta":
        return "gb!"
    # Return g! prefix for status
    elif message == None:
        return "g!"
    # Return g! prefix if not in a guild (e.g. DMs)
    elif not message.guild:
        return "g!"
    # Get guild prefix from DB
    else:
        guild = await db.find("guilds",{"id": message.guild.id})
        return guild["prefix"]