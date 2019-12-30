#PXB Logs Module

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime
import sqlite3

# # # # # # #
# VARIABLES #
# # # # # # #

developers = []
cwd = os.getcwd()
directory = os.listdir(cwd)

# # # # # # #
# FUNCTIONS #
# # # # # # #

async def sqlexec(cmd):
    sql = sqlite3.connect("guilds.db")
    cursor = sql.cursor()
    cursor.execute(cmd)
    sql.commit()
    sql.close()

async def error(ctx,error):
    msg = await ctx.send(embed=discord.Embed(title=f"The command you have entered is invalid",description=f"{ctx.message.content} `{error}`",color=0xff0000).set_footer(text=f"{str(datetime.utcnow())[:-7]} UTC"))
    await asyncio.sleep(5)
    await msg.delete()

# # #### # #
# GET DEVS #
# # #### # #

with open("settings.json","r",encoding="UTF-8") as file:
    settings = json.loads(file.read())
    for developer in settings["badges"]["developers"]:
        developers.append(developer)

# # # # # # #
# SQL Setup #
# # # # # # #

try:
    directory.index("guilds.db")
except ValueError:
    with open("guilds.db","r",encoding="UTF-8") as file:
        file.close()
    sqlexec("""CREATE TABLE guilds
(
    guildID INTEGER,
    logChannel, INTEGER,
    adminLogs, BOOLEAN,
    logLogs, BOOLEAN,
    primary key (guildID)
)""")

# # # ## # # #
# LOGS CLASS #
# # # ## # # #

class Logs(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.group(name="logs",description="Define a channel to log all executed commands")
    async def logs(self, ctx):
        if ctx.invoked_subcommand is None:
            await error(ctx,"NO_INVOKED_SUBCOMMAND")

    @logs.command(name="setchannel",description="Set logging channel")
    async def _setchannel(self,ctx,channel:discord.Channel):
        pass

def setup(bot):
	bot.add_cog(Logs(bot))