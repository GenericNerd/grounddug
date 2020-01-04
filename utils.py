#GroundDug Utility Module

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
from bson.objectid import ObjectId
import db_handle as db

# # # # # # #
# VARIABLES #
# # # # # # #

mainDbObject = ObjectId("5e0e79e9610b77df8202a1e7")

# # # # # # #
# FUNCTIONS #
# # # # # # #

def getToken():
    #Production Token
    return db.dbNSyncFind("settings",{"_id": mainDbObject})["token"]

async def embedGen(title,desc,cl=None):
    if cl is None:
        return discord.Embed(title=title,description=desc,color=0x0088ff).set_footer(text="GroundDug | 2020")
    else:
        return discord.Embed(title=title,description=desc,color=cl).set_footer(text="GroundDug | 2020")

async def getPrefix(bot,message):
	if not message.guild:
		return "g!"
	else:
		guild = (await db.dbFind("guilds",{"id": message.guild.id}))
		return guild["prefix"]

async def error(ctx,error):
    await ctx.send(embed=(await embedGen("Something went wrong!",f"`{error}`",0xff0000)))

async def checkDev(ctx):
    if ctx.author.id in (await db.dbFind("settings",{"_id": mainDbObject}))["developers"]:
        return True
    else:
        return False