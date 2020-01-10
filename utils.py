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

mainDbObject = ObjectId("5e18fd4d123a50ef10d8332e")

# # # # # #
# CLASSES #
# # # # # #

class PermissionsError(commands.CheckFailure):
    def __init__(self,required,current):
        self.required = required
        self.current = current

# # # # # # #
# FUNCTIONS #
# # # # # # #

def getToken():
    #Production Token
    return db.dbNSyncFind("settings",{"_id": mainDbObject})["token"]

async def getLevel(ctx,user:discord.Member):
    if user.id in (await db.dbFind("settings",{"5": user.id})):
        return 5
    elif user.id in (await db.dbFind("settings",{"4": user.id})):
        return 4
    elif user.id in (await db.dbFind("settings",{"3": user.id})):
        return 3
    elif user.id in (await db.dbFind("settings",{"2": user.id})):
        return 2
    elif user.id in (await db.dbFind("settings",{"1": user.id})):
        return 1

def has_level(required: int = 0):
    async def calculate(ctx) -> bool:
        level = await getLevel(ctx,ctx.message.author)
        if level >= required:
            return True
        else:
            raise PermissionsError(required=required,current=level)
    return commands.check(calculate)

async def embedGen(title,desc,cl=None):
    if cl is None:
        return discord.Embed(title=title,description=desc,color=0x0088ff).set_footer(text="GroundDug | 2020",icon_url="https://cdn.discordapp.com/avatars/553602353962549249/641fcc61b43b5ce4b4cbe94c8c0270fa.webp?size=128")
    else:
        return discord.Embed(title=title,description=desc,color=cl).set_footer(text="GroundDug | 2020",icon_url="https://cdn.discordapp.com/avatars/553602353962549249/641fcc61b43b5ce4b4cbe94c8c0270fa.webp?size=128")

async def getPrefix(bot,message):
	if not message.guild:
		return "g!"
	else:
		guild = (await db.dbFind("guilds",{"id": message.guild.id}))
		return guild["prefix"]

async def error(ctx,error):
    await ctx.send(embed=(await embedGen("Something went wrong!",f"`{error}`",0xff0000)))