#GroundDug Useful Utility Functions

import discord
import asyncio
import cogs.utils.dbhandle as db
from bson.objectid import ObjectId
import os

environment = os.getenv("GD_ENV", "beta")

async def getPrefix(bot,message):
    if environment == "beta":
        return "gb!"
    if not message.guild:
        return "g!"
    else:
        guild = (await db.dbFind("guilds",{"id": message.guild.id}))
        return guild["prefix"]

async def getPermissions(guild,member):
    perms = await db.dbFind("users",{"guild": guild.id,"user": member.id})
    return perms["permissions"]