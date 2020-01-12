#GroundDug Level Handler

import discord
import asyncio
from bson.objectid import ObjectId
from cogs.utils.dbhandle import dbFind

dbOject = ObjectId("5e18fd4d123a50ef10d8332e")

async def get_level(user:discord.Member):
    #Level 5 - Bot Owner
    #Level 4 - Reserved for further use
    #Level 3 - Bot Moderators
    #Level 2 - Reserved for further use
    #Level 1 - Reserved for further use

    levelObject = await dbFind("settings",{"_id": dbOject})
    levelObject = levelObject["levels"]

    if user.id in levelObject["5"]:
        return 5
    elif user.id in levelObject["4"]:
        return 4
    elif user.id in levelObject["3"]:
        return 3
    elif user.id in levelObject["2"]:
        return 2
    elif user.id in levelObject["1"]:
        return 1
    else:
        return 0