#GroundDug Useful Utility

import discord
import asyncio
import cogs.utils.dbhandle as db
from bson.objectid import ObjectId

async def getPrefix(bot,message):
    if not message.guild:
        return "g!"
    else:
        guild = (await db.dbFind("guilds",{"id": message.guild.id}))
        return guild["prefix"]

async def getPermissions(guild,member):
    perms = await db.dbFind("permissions",{"guild": guild.id,"user": member.id})
    return perms["permissions"]