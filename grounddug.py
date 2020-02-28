#GroundDug Core Bot File

import discord
from discord.ext import commands
import asyncio
import cogs.utils.useful as useful
import cogs.utils.dbhandle as db
from bson.objectid import ObjectId
import os

environment = os.getenv("GD_ENV", "beta")

startupExtensions = ["core","mod","logs","perms","developer","events","automod","admin"]
bot = commands.AutoShardedBot(command_prefix=useful.getPrefix)

bot.remove_command("help")

for module in startupExtensions:
    try:
        bot.load_extension(f"cogs.{module}")
    except Exception as e:
        print(f"Failed to load module {module}\n{e}")

@bot.check
async def blacklistCalculate(ctx):
    if ctx.guild is not None:
        dbObject = await db.dbFind("guilds",{"id": ctx.guild.id})
        if ctx.channel.id not in dbObject["blacklistChannels"]:
            return True
        else:
            raise commands.CommandNotFound()
    else:
        return True

if environment == "beta":
    print("Running beta")
    bot.run("NjY3MDgzMTM3OTMwNjI1MDI0.Xh9jpw.KygIs_cyCxF6n--bKkvOSATlsB4")
elif environment == "prod":
    print("Running prod")
    bot.run(
        db.dbNSyncFind("settings",
                       {"_id": ObjectId("5e18fd4d123a50ef10d8332e")})["token"])
else:
    print("What the fuck is this environment? GD_ENV is not set or is not beta/prod.")