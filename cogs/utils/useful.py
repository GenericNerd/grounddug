#GroundDug Useful Utility

import discord
import asyncio
import cogs.utils.dbhandle as db
from bson.objectid import ObjectId

async def getPrefix(bot,message):
    # return "gb!"
    if not message.guild:
        return "g!"
    else:
        guild = (await db.dbFind("guilds",{"id": message.guild.id}))
        return guild["prefix"]

async def getPermissions(guild,member):
    perms = await db.dbFind("users",{"guild": guild.id,"user": member.id})
    return perms["permissions"]