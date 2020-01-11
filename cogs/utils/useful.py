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

def getToken():
    #Production Token
    return db.dbNSyncFind("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})["token"]

async def getPermissions(guild,member):
    return db.dbFind("permissions",{"guild": guild.id,"user": member.id})["permissions"]