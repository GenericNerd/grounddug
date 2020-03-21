# GroundDug Level Finder Utility

import discord
import asyncio
from bson.objectid import ObjectId
import cogs.utils.db

level_Object = ObjectId("5e18fd4d123a50ef10d8332e")

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
    level_DB_Object = await db.find("settings",{"_id": level_Object})
    level_DB_Object = level_DB_Object["levels"]

    # Return which level user is, if no level, return 0
    if user.id in level_DB_Object["5"]:
        return 5
    elif user.id in level_DB_Object["4"]:
        return 4
    elif user.id in level_DB_Object["3"]:
        return 3
    elif user.id in level_DB_Object["2"]:
        return 2
    elif user.id in level_DB_Object["1"]:
        return 1
    else:
        return 0