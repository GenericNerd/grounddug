#GroundDug Admin Module

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import utils
import permissions_cog as perms
import db_handle as db
	
# # # # # # # #
# ADMIN CLASS #
# # # # # # # #

class Admin(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.group(name="admin",description="Administrative commands")
	async def admin(self,ctx):
		if ctx.invoked_subcommand is None:
			(await ctx.invoke(self.bot.get_command("help"),"admin"))

	@admin.command(name="ban",description="<member> [reason] | Ban a member from your server")
	async def _ban(self,ctx,member:discord.Member,reason=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["BAN_MEMBERS"]:
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been banned",f"{member.name}#{member.discriminator} has been banned by {ctx.author} for `{reason}`",0xff5555)))
			try:
				await member.send(embed=(await utils.embedGen(f"You have been banned from {ctx.guild.name}",f"You were banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`")))
			except Exception as e:
				(await utils.error(ctx,f"{member.name} could not be notified - {e}"))
			finally:
				await member.ban(reason=f"Banned by @{ctx.user.name}#{ctx.user.discriminator} for: {reason}")
		else:
			(await utils.error(ctx,"You are missing 'GD_BAN_MEMBERS' permission to run this command."))

	@admin.command(name="hackban",description="<ID> [reason] | Ban a member from your server using their ID")
	async def _banid(self,ctx,id:int,reason=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["BAN_MEMBERS"]:
			await ctx.send(embed=(await utils.embedGen(f"{id} has been banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`",None,0xff5555)))
			await ctx.guild.ban(discord.Object(id=id),reason=f"Banned by @{ctx.user.name}#{ctx.user.discriminator} for: {reason}")
		else:
			(await utils.error(ctx,"You are missing 'GD_BAN_MEMBERS' permission to run this command."))

	@admin.command(name="softban",description="<member> [reason] | Ban and immediately unban a member, deleting their messages")
	async def _softban(self,ctx,member:discord.Member,reason=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["BAN_MEMBERS"]:
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been soft-banned",f"{member.name}#{member.discriminator} has been soft-banned by {ctx.author}",0xff5555)))
			try:
				await member.send(embed=(await utils.embedGen(f"You have been soft-banned from {ctx.guild.name}",f"You were soft-banned by {ctx.author.name}#{ctx.author.discriminator}")))
			except Exception as e:
				(await utils.error(ctx,f"{member.name} could not be notified - {e}"))
			finally:
				await member.ban(reason=f"Softbanned by @{ctx.user.name}#{ctx.user.discriminator} for: {reason}")
				await member.unban()
		else:
			(await utils.error(ctx,"You are missing 'GD_BAN_MEMBERS' permission to run this command."))

	@admin.command(name="gag",description="<member> | Stop a user from being able to speak in a voice channel")
	async def _gag(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.voice_channels:
				await channel.set_permissions(member,speak=False)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been gagged by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'GD_MUTE_MEMBERS' permission to run this command."))

	@admin.command(name="ungag",description="<member> | Allows a user to talk in voice channels again")
	async def _ungag(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.voice_channels:
				await channel.set_permissions(member,speak=True)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been ungagged by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'GD_MUTE_MEMBERS' permission to run this command."))

	@admin.command(name="mute",description="<member> | Stops a user from being able to type in a text channel")
	async def _mute(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.text_channels:
				await channel.set_permissions(member,send_messages=False)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been muted by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'GD_MUTE_MEMBERS' permission to run this command."))

	@admin.command(name="unmute",description="<member> | Allows a user to type in a text channel again")
	async def _unmute(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.text_channels:
				await channel.set_permissions(member,send_messages=True)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been unmuted by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'GD_MUTE_MEMBERS' permission to run this command."))

	@admin.command(name="purge",description="[amount (100 by default)] [member/bot/all] | Delete multiple messages at once")
	async def _purge(self,ctx,amount=100,check=""):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MANAGE_MESSAGES"]:
			def member_check(ctx):
				return not ctx.author.bot
			def bot_check(ctx):
				return ctx.author.bot
			if check.lower() == "member":
				await ctx.channel.purge(limit=amount,check=member_check)
			elif check.lower() == "bot":
				await ctx.channel.purge(limit=amount,check=bot_check)
			elif check.lower() == "all" or check == "":
				await ctx.channel.purge(limit=amount)
		else:
			(await utils.error(ctx,"You are missing 'GD_MANAGE_MESSAGES' permission to run this command."))

	@admin.command(name="raid",description="<state> | Activates or deactivates raid mode, which kicks new members as soon as they join in case of a raid")
	async def _raid(self,ctx,state=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["ADMINISTRATOR"]:
			guild = (await db.dbFind("guilds",{"id": ctx.guild.id}))
			if state == None:
				await ctx.send(embed=(await utils.embedGen(f"{ctx.guild.name} Raid Mode",f"Raid Mode is currently set to `{guild['raid_mode']}`")))
			elif state.lower() == "true":
				(await db.dbUpdate("guilds",{"id": ctx.guild.id},{"raid_mode": True}))
				await ctx.send(embed=(await utils.embedGen(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `enabled` by {ctx.author.mention}")))
			elif state.lower() == "false":
				(await db.dbUpdate("guilds",{"id": ctx.guild.id},{"raid_mode": False}))
				await ctx.send(embed=(await utils.embedGen(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `disabled` by {ctx.author.mention}")))
			else:
				(await utils.error(ctx,"Raid mode state needs to be either 'true' or 'false'"))
		else:
			(await utils.error(ctx,"You are missing 'GD_ADMINISTRATOR' permission to run this command."))

def setup(bot):
	bot.add_cog(Admin(bot))