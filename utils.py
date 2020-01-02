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
# FUNCTIONS #
# # # # # # #

def getToken():
    #Production Token
    return db.dbNSyncFind("settings",{"_id": ObjectId("5dfa4f75baf44abfa409b0d7")})["token"]

async def embedGen(title,desc,cl=None):
    if cl is None:
        return discord.Embed(title=title,description=desc,color=0x0088ff).set_footer(text="GroundDug | 2020")
    else:
        return discord.Embed(title=title,description=desc,color=cl).set_footer(text="GroundDug | 2020")

async def getPrefix(bot,message):
	if not message.guild:
		return "p!"
	else:
		guild = (await db.dbFind("guilds",{"id": message.guild.id}))
		return guild["prefix"]

async def error(ctx,error):
    msg = (await embedGen("Something went wrong!",f"`{error}`",0xff0000))
    msg = await ctx.send(embed=msg)
    await asyncio.sleep(5)
    await msg.delete()

async def checkDev(ctx):
    if ctx.author.id in (await db.dbFind("settings",{"_id": ObjectId("5dfa4f75baf44abfa409b0d7")}))["developers"]:
        return True
    else:
        return False