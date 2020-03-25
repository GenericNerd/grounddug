# GroundDug Level Finder Utility

import discord
import asyncio
from bson.objectid import ObjectId
import cogs.utils.db as db

levelObject = ObjectId("5e18fd4d123a50ef10d8332e")

# Returns the user level when called
async def getLevel(user:discord.Member):
    """
    Level 5 - Bot Owner
    Level 4 - Reserved for further use
    Level 3 - Bot Moderator
    Level 2 - Reserved for further use
    Level 1 - Bot Tester
    """

    # Obtain the object in the database which has levels stored
    levelDBObject = await db.find("settings",{"_id": levelObject})
    levelDBObject = levelDBObject["levels"]

    # Return which level user is, if no level, return 0
    if user.id in levelDBObject["5"]:
        return 5
    elif user.id in levelDBObject["4"]:
        return 4
    elif user.id in levelDBObject["3"]:
        return 3
    elif user.id in levelDBObject["2"]:
        return 2
    elif user.id in levelDBObject["1"]:
        return 1
    else:
        return 0