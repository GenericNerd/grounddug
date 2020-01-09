#GroundDug Custom Permissions System

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
		prefix = (await utils.getPrefix(self.bot,ctx))
		msg = (await utils.embedGen("Permissions",f"{user.name}'s current permissions"))
		for permission in (await getPermissions(ctx.guild.id,user.id)):
			if len(permission.split("_")) >= 2:
				perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
			else:
				perm = permission.lower()
			if not (await getPermissions(ctx.guild.id,user.id))[permission]:
				msg.add_field(name=perm,value=f"Change by using `{prefix}permissions <add/remove> @{user.name}#{user.discriminator} {permission.lower()}`")
		if msg.fields == []:
			msg.add_field(name="All permissions",value=f"`{change}` - `{prefix}permissions list {user.name}#{user.discriminator}` to check them")
		await ctx.send(embed=msg)
	else:
		permission = permission.upper()
		currentPermissions = (await getPermissions(ctx.guild.id,user.id))
		if permission == "ADMINISTRATOR":
			for perm in currentPermissions.copy():
				currentPermissions[perm] = change
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
			(await ctx.invoke(self.bot.get_command("help"),"perms"))

	@perms.command(name="setup",description="| Initial guild setup",hidden=True)
	@commands.check(utils.checkDev)
	async def _setup(self,ctx):
		for guild in self.bot.guilds:
			for member in guild.members:
				if (await db.dbFind("permissions", {"guild": guild.id, "user": member.id})) == None:
					if member.id == guild.owner_id:
						(await db.dbInsert("permissions",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True,"MUTE_MEMBERS": True,"KICK_MEMBERS": True,"BAN_MEMBERS": True,"ADMINISTRATOR": True}}))
					else:
						(await db.dbInsert("permissions",(await template_data(guild,member))))

	@perms.command(name="list",description="<user> | List a users' permissions")
	async def _list(self,ctx,user:discord.Member):
		msg = (await utils.embedGen("Permissions",f"{user.name}'s current permissions"))
		for permission in (await getPermissions(ctx.guild.id,user.id)):
			if len(permission.split("_")) >= 2:
				perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
			else:
				perm = permission.lower()
			if (await getPermissions(ctx.guild.id,user.id))[permission]:
				msg.add_field(name=f"{perm}",value=f"<:check:437236812189270018>")
		await ctx.send(embed=msg)

	@perms.command(name="add",description="<user> <permission> | Add a permission to a user")
	async def _add(self,ctx,user:discord.Member,permission=None):
		if (await getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			(await changePermission(self,ctx,user,True,permission))
		else:
			(await utils.error(ctx,"You are missing 'GD_ADMINISTRATOR' permission to run this command."))

	@perms.command(name="remove",description="<user> <permission> | Remove a permission to a user")
	async def _remove(self,ctx,user:discord.Member,permission=None):
		if (await getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			(await changePermission(self,ctx,user,False,permission))
		else:
			(await utils.error(ctx,"You are missing 'GD_ADMINISTRATOR' permission to run this command."))

def setup(bot):
	bot.add_cog(Permissions(bot))