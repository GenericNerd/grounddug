# GroundDug Core Bot File

import uvloop
uvloop.install()

import discord
from discord.ext import commands
import asyncio
import os
import cogs.utils.misc as misc
import cogs.utils.db as db
import cogs.utils.logger as logger
import cogs.utils.embed as embed
from bson.objectid import ObjectId

import voteserver

# Find current environment
environment = os.getenv("GD_ENV","beta")

# Get the current bot settings
botSettings = db.nsyncFind("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})

# Load sentry to receive tracebacks
import sentry_sdk
from sentry_sdk import capture_exception, capture_message
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.sanic import SanicIntegration
sentry_sdk.init(
    "https://23777185a8e64fa3a7084b05ee68b2bd@sentry.grounddug.xyz/3",
    release=botSettings["version"],
    integrations=[FlaskIntegration(),
                  AioHttpIntegration(),
                  SanicIntegration()])

# Cogs to load on bot ready
startupExtensions = ["events","perms","core","admin","mod","developer","logs","automod","boundary","directoryAPI"]
# Get prefix depending on message context
bot = commands.AutoShardedBot(command_prefix=misc.getPrefix)

bot.remove_command("help")

for module in startupExtensions:
    try:
        bot.load_extension(f"cogs.{module}")
    except Exception as e:
        capture_exception(e)
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

@bot.event
async def on_error(event,*args,**kwargs):
    if isinstance(event,Exception):
        capture_exception(event)
    else:
        capture_message(f"{event}: {args} passed, {kwargs} passed")
    await bot.get_channel(664541295448031295).send(embed=(await embed.generate("Error raised! Sentry issue created",None,0xff0000)))

loop = asyncio.get_event_loop()

# Check current environment, and run appropriate instance
if environment == "beta":
    logger.info("Running GroundDugBeta")
    voteserver.registerVoteServer(loop, 42070)
    loop.run_until_complete(bot.start("NjY3MDgzMTM3OTMwNjI1MDI0.Xh9jpw.KygIs_cyCxF6n--bKkvOSATlsB4"))
elif environment == "production":
    logger.info("Running GroundDug")
    voteserver.registerVoteServer(loop)
    loop.run_until_complete(bot.start(botSettings["token"]))
else:
    logger.error("Invalid environment, aborting instance")
    exit()