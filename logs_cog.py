#PXB Logs

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import utils
import db_handle as db
import permissions_cog as perms

# # # # # # #
# FUNCTIONS #
# # # # # # #

async def template_data(gid):
	return {
		"id": gid,
		"prefix": "p!",
		"channel": 0,
		"misc_log": False,
		"logs_log": False,
		"admin_log": False,
		"advertising_log": False,
		"delete_log": False
	}

async def moduleLogChange(self,ctx,boolean,status,module=None):
	if module == None:
		prefix = (await utils.getPrefix(self.bot,ctx))
		msg = (await utils.embedGen("Modules",None))
		for item,result in (await db.dbFind("guilds", {"id": ctx.guild.id})).items():
			if result == boolean and len(item.split("_log")) > 1:
				item = item.split("_log")[0]
				msg.add_field(name=item,value=f"Run `{prefix}logs {status} {item}` to log",inline=False)
		await ctx.send(embed=msg)
	else:
		for item,result in (await db.dbFind("guilds", {"id": ctx.guild.id})).items():
			valid = False
			if result == boolean and module==item.split("_log")[0]:
				valid = True
				break
		if valid == False:
			(await utils.error(ctx,"INVALID MODULE"))
		else:
			(await db.dbUpdate("guilds",{"id": ctx.guild.id},{f"{module}_log": not boolean}))
			if boolean == False:
				await ctx.send(embed=(await utils.embedGen("Updated logging settings",f"`{module}` events will now be logged")))
			else:
				await ctx.send(embed=(await utils.embedGen("Updated logging settings",f"`{module}` events will now not be logged")))

async def logGen(ctx):
	return (await utils.embedGen(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>"))

# # # ## # # #
# LOGS CLASS #
# # # ## # # #

class Logs(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
	@commands.group(name="logs",description="Logging commands")
	async def logs(self,ctx):
		if ctx.invoked_subcommand is None:
			(await ctx.invoke(self.bot.get_command("help"),"logs"))

	@logs.command(name="setup",description="| Initial guild setup (developer only)",hidden=True)
	@commands.check(utils.checkDev)
	async def _setup(self,ctx):
		msg = (await utils.embedGen("The following guilds were added to the database",None))
		for guild in self.bot.guilds:
			data = (await template_data(guild.id))
			if (await db.dbFind("guilds",{"id": guild.id})) == None:
				result = (await db.dbInsert("guilds",data))
				msg.add_field(name=f"Created {guild.name} ({guild.id})",value=f"Object ID {result.inserted_id}",inline=False)
		await ctx.send(embed=msg)

	@logs.command(name="setchannel", description="<channel> | Set the channel for logs to be posted")
	async def _setchannel(self,ctx,channel:discord.TextChannel=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			if channel == None:
				prefix = (await utils.getPrefix(self.bot,ctx))
				guild = (await db.dbFind("guilds",{"id": ctx.guild.id}))
				channel = guild["channel"]
				if channel == 0:
					await ctx.send(embed=(await utils.embedGen("Logging channel",f"No current logging channel, set one by using `{prefix}logs setchannel <channel>`")))
				else:
					await ctx.send(embed=(await utils.embedGen("Logging channel",f"<#{channel}> is the current logging channel")))
			else:
				(await db.dbUpdate("guilds",{"id": ctx.guild.id},{"channel":channel.id}))
				await ctx.send(embed=(await utils.embedGen("Logging channel changed",f"{channel.mention} will now have logs posted to it")))
		else:
			(await utils.error(ctx,"You are missing 'Administrator' permission to run this command."))

	@logs.command(name="enable",description="<module> | Enable logging for a module")
	async def _enable(self,ctx,module=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			await moduleLogChange(self,ctx,False,"enable",module)
		else:
			(await utils.error(ctx,"You are missing 'Administrator' permission to run this command."))

	@logs.command(name="disable",description="<module> | Disable logging for a module")
	async def _disable(self,ctx,module=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			await moduleLogChange(self,ctx,True,"disable",module)
		else:
			(await utils.error(ctx,"You are missing 'Administrator' permission to run this command."))

def setup(bot):
	bot.add_cog(Logs(bot))