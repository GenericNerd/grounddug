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
# FUNCTIONS #
# # # # # # #

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

	@commands.command(name="help",description="[module] | Returns a list of all commands with their usage")
	async def custom_help(self,ctx,module=""):
		prefix = await utils.getPrefix(self.bot,ctx)
		msg = (await utils.embedGen("Help",None))
		modules = dict()
		modules["misc"] = []
		for command in self.bot.commands:
			if type(command) is discord.ext.commands.core.Group:
				modules[command.name.lower()] = command
			else:
				modules["misc"].append(command)
		if module == "":
			msg.description = "Please specify the modules you wish to look up"
			for key in sorted(modules.keys()):
				if key == "misc":
					msg.add_field(name=f"💿 - Misc ({prefix}help misc)",value="List of all non-groupped commands",inline=False)
				if key == "admin":
					msg.add_field(name=f"🔨 - Admin ({prefix}help admin)",value="Administrative commands",inline=False)
				if key == "logs":
					msg.add_field(name=f"🔍 - Logs ({prefix}help logs)",value="Logging of commands",inline=False)
				if key == "perms":
					msg.add_field(name=f"🔧 - Perms ({prefix}help perms)",value="Assigning and removing permissions",inline=False)
			return await ctx.send(embed=msg)
		elif module != "":
			if module.lower() in modules.keys():
				modules = {module.lower(): modules[module.lower()]}
			else:
				msg.description = f"We could not find module {module}"
				return await ctx.send(embed=msg)
		for cog,cog_obj in modules.items():
			prefix = (await utils.getPrefix(self.bot,ctx))
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
		for guild in self.bot.guilds:
			guildCount += 1
			for user in guild.members:
				userCount += 1
		msg = (await utils.embedGen("Bot information",f"Guilds: **{guildCount}**\nUsers: **{userCount}**\nDiscord.py Version: {discord.__version__}\n{self.bot.user.name} version: {version}"))
		latency = round(self.bot.latency*100)
		if latency < 100:
			msg.add_field(name="Status",value=f"<:status_online:664530427012317194> Latency: **{latency}**ms")
		else:
			msg.add_field(name="Status",value=f"<:status_dnd:664530426949271556> Latency: **{latency}**ms")
		await ctx.send(embed=msg)

	@commands.command(name="setprefix",description="<prefix> | Sets a local prefix for the bot")
	async def setPrefix(self,ctx,prefix=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			(await db.dbUpdate("guilds",{"id": ctx.guild.id},{"prefix": prefix}))
			await ctx.send(embed=(await utils.embedGen("Prefix changed!",f"`{prefix}` is now the prefix for this guild")))
		else:
			(await utils.error(ctx,"You are missing 'GD_ADMINISTRATOR' permission to run this command."))

def setup(bot):
	bot.add_cog(core(bot))