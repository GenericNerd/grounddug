#PXB Custom Permissions System

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import utils
import db_handle as db

# # # # # # #
# FUNCTIONS #
# # # # # # #

async def template_data(guild,member):
	return {
		"guild": guild.id, "user": member.id, "permissions": {
			"MANAGE_MESSAGES": False,
			"MUTE_MEMBERS": False,
			"KICK_MEMBERS": False,
			"BAN_MEMBERS": False,
			"ADMINISTRATOR": False
		}
	}

async def getPermissions(guild,member):
	return (await db.dbFind("permissions",{"guild": guild,"user": member}))["permissions"]

async def changePermission(self,ctx,user,change,permission=None):
	if permission == None:
		msg = (await utils.embedGen("Permissions",f"{user.name}'s current permissions"))
		for permission in (await getPermissions(ctx.guild.id,user.id)):
			if len(permission.split("_")) >= 2:
				perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
			else:
				perm = permission.lower()
			if not (await getPermissions(ctx.guild.id,user.id))[permission]:
				msg.add_field(name=perm,value=f"Change by using `{(await utils.getPrefix(self.bot,ctx))}permissions <add/remove> @{user.name}#{user.discriminator} {permission.lower()}`")
		await ctx.send(embed=msg)
	else:
		permission = permission.upper()
		currentPermissions = (await getPermissions(ctx.guild.id,user.id))
		if permission == "ADMINISTRATOR":
			for perm,value in currentPermissions.items():
				value = change
			(await db.dbUpdate("permissions",{"guild": ctx.guild.id, "user": user.id},{"permissions": currentPermissions}))
		else:
			opchange = not change
			if (await getPermissions(ctx.guild.id,user.id))[permission] == opchange:
				currentPermissions[permission] = change
				(await db.dbUpdate("permissions",{"guild": ctx.guild.id, "user": user.id},{"permissions": currentPermissions}))
		await ctx.send(embed=(await utils.embedGen("Permission changed",f"Permission `{permission}` to {user.name}#{user.discriminator} was changed to `{change}`")))

# # # # # # # # # # #
# PERMISSIONS CLASS #
# # # # # # # # # # #

class Permissions(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.group(name="perms",aliases=["permissions"],description="Custom permission setting")
	async def perms(self,ctx):
		if ctx.invoked_subcommand is None:
			(await utils.error(ctx,"NO INVOKED SUBCOMMAND"))

	@perms.command(name="list",description="<user> | List a users' permissions")
	async def _list(self,ctx,user:discord.Member):
		msg = (await utils.embedGen("Permissions",f"{user.name}'s current permissions"))
		for permission in (await getPermissions(ctx.guild.id,user.id)):
			if len(permission.split("_")) >= 2:
				perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
			else:
				perm = permission.lower()
			if (await getPermissions(ctx.guild.id,user.id))[permission]:
				msg.add_field(name=f"{perm}",value=f"✅")
		await ctx.send(embed=msg)

	@perms.command(name="add",description="<user> <permission> | Add a permission to a user")
	async def _add(self,ctx,user:discord.Member,permission=None):
		if (await getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			(await changePermission(self,ctx,user,True,permission))
		else:
			(await utils.error(ctx,"You are missing 'Administrator' permission to run this command."))

	@perms.command(name="remove",description="<user> <permission> | Remove a permission to a user")
	async def _remove(self,ctx,user:discord.Member,permission=None):
		if (await getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			(await changePermission(self,ctx,user,False,permission))
		else:
			(await utils.error(ctx,"You are missing 'Administrator' permission to run this command."))

	@perms.command(name="setup",description="| Initial guild setup",hidden=True)
	@commands.check(utils.checkDev)
	async def _setup(self,ctx):
		msg = (await utils.embedGen("Initial guild setup for permissions","Following items created:"))
		for guild in self.bot.guilds:
			for member in guild.members:
				if member.id == guild.owner_id:
					result = (await db.dbInsert("permissions",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True,"MUTE_MEMBERS": True,"KICK_MEMBERS": True,"BAN_MEMBERS": True,"ADMINISTRATOR": True}}))
				else:
					result = (await db.dbInsert("permissions",(await template_data(guild,member))))
				msg.add_field(name=f"Inserted object",value=f"{guild.name} `{guild.id}` {member.name} `{member.id}`",inline=False)
		(await ctx.send(embed=msg))

	@commands.command(name="test",description="Testing",hidden=True)
	@commands.check(utils.checkDev)
	async def test(self,ctx):
		test = {
			"guild": ctx.guild.id, "user": ctx.author.id, "permissions": {
				"MANAGE_MESSAGES": False,
				"MUTE_MEMBERS": False,
				"KICK_MEMBERS": False,
				"BAN_MEMBERS": False,
				"ADMINISTRATOR": False
			}
		}
		await db.dbInsert("permissions",test)

	@commands.command(name="test2",description="Further testing tf do you think",hidden=True)
	@commands.check(utils.checkDev)
	async def test2(self,ctx):
		await ctx.send(await db.dbFind("permissions",{"guild": ctx.guild.id, "user": ctx.author.id}))

def setup(bot):
	bot.add_cog(Permissions(bot))