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

startExternalExtensions = ["admin","logs","permissions","events"]
startInternalExtensions = ["core","dev"]
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
	
async def userCheck(user):
	embed = (await utils.embedGen(f"{user.name}#{user.discriminator}",f"{user.mention} - {user.id}")).set_thumbnail(url=user.avatar_url)
	embed.add_field(name="Status",value=user.status,inline=True)
	embed.add_field(name="Server join date",value=f"{str(user.joined_at).split('.')[0]} - `{str(datetime.utcnow()-user.joined_at).split('.')[0]} ago`",inline=True)
	embed.add_field(name="Account age",value=f"{str(user.created_at).split('.')[0]} - `{str(datetime.utcnow()-user.created_at).split('.')[0]} ago`",inline=True)
	roles = "@everyone"
	for role in user.roles:
		if role.name != "@everyone":
			roles = roles + f", {role.name}"
	if roles == "@everyone":
		embed.add_field(name="Roles",value="No significant roles",inline=False)
	else:
		embed.add_field(name="Roles",value=roles,inline=False)
	return embed

# # # ## # # #
# CORE CLASS #
# # # ## # # #

class core(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	bot.remove_command("help")
	@commands.command(name="help",description="[module] | Returns a list of all commands with their usage")
	async def custom_help(self,ctx,module=""):
		msg = (await utils.embedGen("Help",None))
		modules = dict()
		modules["misc"] = []
		for command in bot.commands:
			if type(command) is discord.ext.commands.core.Group:
				modules[command.name.lower()] = command
			else:
				modules["misc"].append(command)
		if module == "":
			msg.description = "Please specify the modules you wish to look up"
			for key in sorted(modules.keys()):
				if key == "misc":
					msg.add_field(name=f"💿 - Misc ({await utils.getPrefix(bot,ctx)}help misc)",value="List of all non-groupped commands",inline=False)
				if key == "admin":
					msg.add_field(name=f"🔨 - Admin ({await utils.getPrefix(bot,ctx)}help admin)",value="Administrative commands",inline=False)
				if key == "logs":
					msg.add_field(name=f"🔍 - Logs ({await utils.getPrefix(bot,ctx)}help logs)",value="Logging of commands",inline=False)
				if key == "perms":
					msg.add_field(name=f"🔧 - Perms ({await utils.getPrefix(bot,ctx)}help perms)",value="Assigning and removing permissions",inline=False)
			return await ctx.send(embed=msg)
		elif module != "":
			if module.lower() in modules.keys():
				modules = {module.lower(): modules[module.lower()]}
			else:
				msg.description = f"We could not find module {module}"
				return await ctx.send(embed=msg)
		for cog,cog_obj in modules.items():
			prefix = (await utils.getPrefix(bot,ctx))
			if cog.lower() in ["misc"]:
				for command in sorted(cog_obj, key=lambda o: f"{o.full_parent_name} {o.name}"):
					split = command.description.split("|")
					if len(split) >= 2 and not command.hidden:
						msg.add_field(name=f"{prefix}{command.name} {split[0]}",value=split[1],inline=False)
					elif len(split) < 2 and not command.hidden:
						msg.add_field(name=f"{prefix}{command.name}",value=command.description)
			else:
				for command in sorted(cog_obj.commands, key=lambda o: f"{o.full_parent_name} {o.name}"):
					split = command.description.split("|")
					if len(split) >= 2 and not command.hidden:
						msg.add_field(name=f"{prefix}{command.full_parent_name} {command.name} {split[0]}",value=split[1],inline=False)
					elif len(split) < 2 and not command.hidden:
						msg.add_field(name=f"{prefix}{command.full_parent_name} {command.name}",value=command.description)
		await ctx.send(embed=msg)

	@commands.command(name="invite",description="| Receive an invite to your server")
	async def invite(self,ctx):
		await ctx.author.send(embed=(await utils.embedGen("Invite PXB to your server",f"[Click here](https://discordapp.com/oauth2/authorize?client_id=553602353962549249&scope=bot&permissions=8) to invite {bot.user.name} to your server")))

	@commands.command(name="userinfo",description="[user] | Returns information about a specific user")
	async def userinfo(self,ctx,user:discord.Member=None):
		if user is None:
			await ctx.send(embed=(await userCheck(ctx.author)))
		else:
			await ctx.send(embed=(await userCheck(user)))

	@commands.command(name="botinfo",description="| Returns information about the bot")
	async def botinfo(self,ctx):
		guildCount = 0
		userCount = 0
		version = open("version.txt").read()
		for guild in bot.guilds:
			guildCount += 1
			for user in guild.members:
				userCount += 1
		await ctx.send(embed=(await utils.embedGen("Bot information",f"Guilds: **{guildCount}**\nUsers: **{userCount}**\nDiscord.py Version: {discord.__version__}\n{bot.user.name} version: {version}")))

	@commands.command(name="setprefix",description="<prefix> | Sets a local prefix for the bot")
	async def setPrefix(self,ctx,prefix=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			(await db.dbUpdate("guilds",{"id": ctx.guild.id},{"prefix": prefix}))
			await ctx.send(embed=(await utils.embedGen("Prefix changed!",f"`{prefix}` is now the prefix for this guild")))
		else:
			(await utils.error(ctx,"You are missing 'GD_ADMINISTRATOR' permission to run this command."))

# # # # # # # # # #
# DEVELOPER CLASS #
# # # # # # # # # #

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
for module in startInternalExtensions:
	bot.add_cog(module)

bot.run(utils.getToken())