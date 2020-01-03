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

startUpExtensions = ["admin","logs","permissions","events"]
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
	embed.add_field(name="Account age",value=f"{str(user.created_at).split('.')[0]} - ``",inline=True)
	roles = "@everyone"
	for role in user.roles:
		if role.name != "@everyone":
			roles = roles + f", {role.name}"
	if roles == "@everyone":
		embed.add_field(name="Roles",value="No significant roles",inline=False)
	else:
		embed.add_field(name="Roles",value=roles,inline=False)
	return embed
	
# # ## # #
# EVENTS #
# # ## # #

@bot.event
async def on_ready():
	print(f"\n{bot.user.name}\nOnline\nFrom {str(datetime.utcnow()).split('.')[0]} UTC")
	(await bot.get_channel(528300655610167326).send(embed=(await utils.embedGen("I'm online",f"As of {str(datetime.utcnow()).split('.')[0]} UTC"))))
	await bot.change_presence(activity=discord.Game("g!help to get started"))

@bot.event
async def on_command_error(ctx,error):
	if isinstance(error,commands.MissingRequiredArgument):
		prefix = (await utils.getPrefix(bot,ctx))
		(await utils.error(ctx,f"{error} - Use {prefix}help {str(ctx.message.content).split(' ')[0].split(prefix)[1]}"))
	else:
		(await utils.error(ctx,f"error - Report to developers"))

# # # # # # # # #
# MISC COMMANDS #
# # # # # # # # #

@bot.command(name="invite",description="| Receive an invite to your server")
async def invite(ctx):
	await ctx.author.send(embed=(await utils.embedGen("Invite PXB to your server",f"[Click here](https://discordapp.com/oauth2/authorize?client_id=553602353962549249&scope=bot&permissions=8) to invite {bot.user.name} to your server")))

@bot.command(name="userinfo",description="[user] | Returns information about a specific user")
async def userinfo(ctx,user:discord.Member=None):
	if user is None:
		await ctx.send(embed=(await userCheck(ctx.author)))
	else:
		await ctx.send(embed=(await userCheck(user)))

@bot.command(name="botinfo",description="| Returns information about the bot")
async def botinfo(ctx):
	guildCount = 0
	userCount = 0
	version = open("version.txt").read()
	for guild in bot.guilds:
		guildCount += 1
		for user in guild.members:
			userCount += 1
	await ctx.send(embed=(await utils.embedGen("Bot information",f"Guilds: **{guildCount}**\nUsers: **{userCount}**\nDiscord.py Version: {discord.__version__}\n{bot.user.name} version: {version}")))

@bot.command(name="setprefix",description="<prefix> | Sets a local prefix for the bot")
async def setPrefix(ctx,prefix):
	if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
		(await db.dbUpdate("guilds",{"id": ctx.guild.id},{"prefix": prefix}))
		await ctx.send(embed=(await utils.embedGen("Prefix changed!",f"`{prefix}` is now the prefix for this guild")))
	else:
		(await utils.error(ctx,"You are missing 'Administrator' permission to run this command."))

# # # #### # # #
# HELP COMMAND #
# # # #### # # #

bot.remove_command("help")
@bot.command(name="help",description="[module] | Returns a list of all commands with their usage")
async def custom_help(ctx,module=""):
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
				msg.add_field(name="💿 - Misc",value="List of all non-groupped commands",inline=False)
			if key == "admin":
				msg.add_field(name="🔨 - Admin",value="Administrative commands",inline=False)
			if key == "logs":
				msg.add_field(name="🔍 - Logs",value="Logging of commands",inline=False)
			if key == "perms":
				msg.add_field(name="🔧 - Perms",value="Assigning and removing permissions",inline=False)
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

# # # ## # # #
# CMD GROUPS #
# # # ## # # #

@bot.group(name="developer",description="Developer only commands",hidden=True)
@commands.check(utils.checkDev)
async def developer(ctx):
	if ctx.invoked_subcommand is None:
		(await utils.error(ctx,"NO INVOKED SUBCOMMAND"))
		
@bot.group(name="modules",description="Module management",hidden=True)
@commands.check(utils.checkDev)
async def modules(ctx):
	if ctx.invoked_subcommand is None:
		(await utils.error(ctx,"NO INVOKED SUBCOMMAND"))

# # # # ## # # # #
# DEVELOPER CMDS #
# # # # ## # # # #

@developer.command(name="restart",description="Restart the bot",hidden=True)
async def _restart(ctx):
	await ctx.send(embed=(await utils.embedGen("Bot is restarting",None)))
	os._exit(100)

@developer.command(name="eval",description="<command> | Seriously no touchy",hidden=True)
async def _eval(ctx,cmd:str):
	try:
		result = (await eval(cmd))
	except:
		result = (eval(cmd))
	await ctx.send(result)
	
# # # # # # # #
# MODULE CMDS #
# # # # # # # #

@modules.command(name="reload",description="<module> | Reload one module",hidden=True)
async def _reload(ctx,module=None):
	if module is None:
		(await utils.error(ctx,"NO MODULE CALLED"))
	else:
		bot.unload_extension(f"{module}_cog")
		bot.load_extension(f"{module}_cog")
		await ctx.send(embed=(await utils.embedGen("Module reloaded",module)))

@modules.command(name="reloadall",aliases=["re"],description="Reloads all modules",hidden=True)
async def _reloadall(ctx):
	embed = await reloadAllModules()
	await ctx.send(embed=embed)

@modules.command(name="unload",description="<module> | Unload a specific module",hidden=True)
async def _unload(ctx,module=None):
	if module is None:
		(await utils.error(ctx,"NO MODULE CALLED"))
	else:
		bot.unload_extension(f"{module}_cog")
		await ctx.send(embed=(await utils.embedGen("Module unloaded",module)))

@modules.command(name="load",description="<module> | Load a specific module",hidden=True)
async def _load(ctx,module=None):
	if module is None:
		(await utils.error(ctx,"NO MODULE CALLED"))
	else:
		bot.load_extension(f"{module}_cog")
		await ctx.send(embed=(await utils.embedGen("Module loaded",module)))

for module in startUpExtensions:
	bot.load_extension(f"{module}_cog")

bot.run(utils.getToken())