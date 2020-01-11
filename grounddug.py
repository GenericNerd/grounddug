#GroundDug Bot File

import discord
from discord.ext import commands
import asyncio
import cogs.utils.useful as useful
import cogs.utils.checks as checks

startupExtensions = ["core","admin","logs","perms","developer","events"]
bot = commands.AutoShardedBot(command_prefix=useful.getPrefix)

bot.remove_command("help")

for module in startupExtensions:
    try:
        bot.load_extension(f"cogs.{module}")
    except Exception as e:
        print(f"Failed to load module {module}\n{e}")

bot.run(useful.getToken())