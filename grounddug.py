# GroundDug Core Bot File

import discord
from discord.ext import commands
import asyncio
import os
import cogs.utils.misc as misc
import cogs.utils.db as db
import cogs.utils.logger as logger

# Find current environment
environment = os.getenv("GD_ENV","beta")

# Cogs to load on bot ready
startupExtensions = ["events","perms","core","admin","mod","developer"]
# Get prefix depending on message context
bot = commands.AutoShardedBot(command_prefix=misc.getPrefix)

bot.remove_command("help")

for module in startupExtensions:
    try:
        bot.load_extension(f"cogs.{module}")
    except Exception as e:
        logger.error(f"Failed to load module {module} - {e}")

# Check if channel is blacklisted before running command
@bot.check
async def blacklistChannelCheck(ctx):
    if ctx.guild is not None:
        guildObject = await db.find("guilds",{"id": ctx.guild.id})
        # Check if channel ID is in guilds' blacklisted channels
        if ctx.channel.id not in guildObject["blacklistChannels"]:
            return True
        else:
            # Raise CommandNotFound, which should not cause an eh event handle
            raise commands.CommandNotFound()
    else:
        return True

# Check current environment, and run appropriate instance
if environment == "beta":
    logger.info("Running GroundDugBeta")
    bot.run("NjY3MDgzMTM3OTMwNjI1MDI0.Xh9jpw.KygIs_cyCxF6n--bKkvOSATlsB4")
elif environment == "production":
    logger.info("Running GroundDug")
    bot.run(db.nsyncfind("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})["token"])
else:
    logger.error("Invalid environment, aborting instance")
    exit()