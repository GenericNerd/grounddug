#GroundDug Core

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime
import utils
from bson.objectid import ObjectId
import db_handle as db
import permissions_cog as perms

# # # # # # #
# VARIABLES #
# # # # # # #

startExternalExtensions = ["admin","logs","permissions","events","core"]
startInternalExtensions = ["dev"]
bot = commands.Bot(command_prefix=utils.getPrefix)
cwd = os.getcwd()

# # # # # # #
# FUNCTIONS #
# # # # # # #

async def reloadAllModules():
	modules = []
	for extension in os.listdir(cwd):
		if os.path.isfile(extension):
			if extension[-7:] == "_cog.py":
				modules.append(extension[:-7])
	embed = (await utils.embedGen("All modules reloaded","The following modules have been reloaded"))
	for module in modules:
		bot.unload_extension(f"{module}_cog")
		bot.load_extension(f"{module}_cog")
		embed.add_field(name=module,value="Successfully reloaded",inline=True)
	return embed

# # # # # # # # # #
# DEVELOPER CLASS #
# # # # # # # # # #

bot.remove_command("help")

class dev(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.group(name="developer",alias=["dev"],hidden=True)
	@commands.check(utils.checkDev)
	async def developer(self,ctx):
		if ctx.invoked_subcommand is None:
			(await utils.error(ctx,"NO INVOKED SUBCOMMAND"))

	@developer.command(name="restart",hidden=True)
	async def _restart(self,ctx):
		await ctx.send(embed=(await utils.embedGen("Bot is restarting",None)))
		os._exit(100)

	@developer.command(name="eval",hidden=True)
	async def _eval(self,ctx,cmd:str):
		try:
			result = (await eval(cmd))
		except:
			result = (eval(cmd))
		await ctx.send(result)
	
	@developer.command(name="modulereload",alias=["mreload"],hidden=True)
	async def _reload(self,ctx,module):
		try:
			self.bot.unload_extension(f"{module}_cog")
			self.bot.load_extension(f"{module}_cog")
		except:
			self.bot.unload_extension(module)
			self.bot.load_extension(module)
		finally:
			await ctx.send(embed=(await utils.embedGen("Module reloaded",module)))

	@developer.command(name="modulereloadall",alias=["mreloadall","mre"],hidden=True)
	async def _reloadall(self,ctx):
		embed = await reloadAllModules()
		await ctx.send(embed=embed)

	@developer.command(name="moduleload",alias=["mload"],hidden=True)
	async def _load(self,ctx,module):
		try:
			self.bot.load_extension(f"{module}_cog")
		except:
			self.bot.load_extension(module)
		finally:
			await ctx.send(embed=(await utils.embedGen("Module loaded",module)))

	@developer.command(name="moduleunload",alias=["munload"],hidden=True)
	async def _unload(self,ctx,module):
		try:
			self.bot.unload_extension(f"{module}_cog")
		except:
			self.bot.unload_extension(module)
		finally:
			await ctx.send(embed=(await utils.embedGen("Module unloaded",module)))

for module in startExternalExtensions:
	bot.load_extension(f"{module}_cog")
bot.add_cog(dev(bot))

bot.run(utils.getToken())