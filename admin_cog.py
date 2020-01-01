#PXB Admin Module

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import utils
import permissions_cog as perms
	
# # # # # # # #
# ADMIN CLASS #
# # # # # # # #

class Admin(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
	@commands.group(name="admin",description="Administrative commands")
	async def admin(self,ctx):
		if ctx.invoked_subcommand is None:
			await utils.error(ctx,"NO INVOKED SUBCOMMAND")

	@commands.Cog.listener("on_message")
	async def on_msg_log(self,ctx):
		if "discord.gg/" in ctx.message.content:
			await ctx.delete()
		await self.bot.process_commands(ctx)

	@admin.command(name="ban",description="<member> [reason] | Ban a member from your server")
	async def _ban(self,ctx,member:discord.Member,reason=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["BAN_MEMBERS"]:
			if reason is None:
				await ctx.send(embed=(await utils.embedGen(f"{member.name} has been banned",f"{member.name}#{member.discriminator} has been banned by {ctx.author}",0xff5555)))
				await member.send(embed=(await utils.embedGen(f"You have been banned from {ctx.guild.name}",f"You were banned by {ctx.author.name}#{ctx.author.discriminator}")))
				await member.ban()
			else:
				await ctx.send(embed=(await utils.embedGen(f"{member.name} has been banned",f"{member.name}#{member.discriminator} has been banned by {ctx.author} for `{reason}`",0xff5555)))
				await member.send(embed=(await utils.embedGen(f"You have been banned from {ctx.guild.name}",f"You were banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`")))
				await member.ban(reason=reason)
		else:
			(await utils.error(ctx,"You are missing 'Ban Members' permission to run this command."))

	@admin.command(name="banid",description="<ID> [reason] | Ban a member from your server using their ID")
	async def _banid(self,ctx,id:int,reason=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["BAN_MEMBERS"]:
			if reason is None:
				await ctx.send(embed=(await utils.embedGen(f"{id} has been banned by {ctx.author.name}#{ctx.author.discriminator}",0xff5555)))
				await ctx.guild.ban(discord.Object(id=id))
			else:
				await ctx.send(embed=(await utils.embedGen(f"{id} has been banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`",0xff5555)))
				await ctx.guild.ban(discord.Object(id=id))
		else:
			(await utils.error(ctx,"You are missing 'Ban Members' permission to run this command."))

	@admin.command(name="softban",description="<member> [reason] | Ban and immediately unban a member, deleting their messages")
	async def _softban(self,ctx,member:discord.Member,reason=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["BAN_MEMBERS"]:
			if reason is None:
				await ctx.send(embed=(await utils.embedGen(f"{member.name} has been soft-banned",f"{member.name}#{member.discriminator} has been soft-banned by {ctx.author}",0xff5555)))
				await member.send(embed=(await utils.embedGen(f"You have been soft-banned from {ctx.guild.name}",f"You were soft-banned by {ctx.author.name}#{ctx.author.discriminator}")))
				await member.ban()
				await member.unban()
			else:
				await ctx.send(embed=(await utils.embedGen(f"{member.name} has been soft-banned",f"{member.name}#{member.discriminator} has been soft-banned by {ctx.author} for `{reason}`",0xff5555)))
				await member.send(embed=(await utils.embedGen(f"You have been soft-banned from {ctx.guild.name}",f"You were soft-banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`")))
				await member.ban(reason=reason)
				await member.unban()
		else:
			(await utils.error(ctx,"You are missing 'Ban Members' permission to run this command."))

	@admin.command(name="softbanid",description="<ID> [reason] | Ban and immediately unban a member via their ID, deleting their messages")
	async def _softbanid(self,ctx,id:int,reason=None):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["BAN_MEMBERS"]:
			if reason is None:
				await ctx.send(embed=(await utils.embedGen(f"{id} has been soft-banned by {ctx.author.name}#{ctx.author.discriminator}",0xff5555)))
				await ctx.guild.ban(discord.Object(id=id))
				await ctx.guild.unban(discord.Object(id=id))
			else:
				await ctx.send(embed=(await utils.embedGen(f"{id} has been soft-banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`",0xff5555)))
				await ctx.guild.ban(discord.Object(id=id))
				await ctx.guild.unban(discord.Object(id=id))
		else:
			(await utils.error(ctx,"You are missing 'Ban Members' permission to run this command."))
	
	@admin.command(name="gag",description="<member> | Stop a user from being able to speak in a voice channel")
	async def _gag(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.voice_channels:
				await channel.set_permissions(member,speak=False)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been gagged by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'Mute Members' permission to run this command."))

	@admin.command(name="ungag",description="<member> | Allows a user to talk in voice channels again")
	async def _ungag(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.voice_channels:
				await channel.set_permissions(member,speak=True)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been ungagged by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'Mute Members' permission to run this command."))

	@admin.command(name="mute",description="<member> | Stops a user from being able to type in a text channel")
	async def _mute(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.text_channels:
				await channel.set_permissions(member,send_messages=False)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been muted by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'Mute Members' permission to run this command."))

	@admin.command(name="unmute",description="<member> | Allows a user to type in a text channel again")
	async def _unmute(self,ctx,member:discord.Member):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MUTE_MEMBERS"]:
			for channel in ctx.guild.text_channels:
				await channel.set_permissions(member,send_messages=True)
			await ctx.send(embed=(await utils.embedGen(f"{member.name} has been unmuted by {ctx.author.name}#{ctx.author.discriminator}",None)))
		else:
			(await utils.error(ctx,"You are missing 'Mute Members' permission to run this command."))

	@admin.command(name="purge",description="<member/bot/all> [amount (100 by default)] | Delete multiple messages at once")
	async def _purge(self,ctx,check,amount=100):
		if (await perms.getPermissions(ctx.guild.id,ctx.author.id))["MANAGE_MESSAGES"]:
			def member_check(ctx):
				return not ctx.author.bot
			def bot_check(ctx):
				return ctx.author.bot
			if check.lower() == "member":
				await ctx.channel.purge(limit=amount,check=member_check)
			elif check.lower() == "bot":
				await ctx.channel.purge(limit=amount,check=bot_check)
			else:
				await ctx.channel.purge(limit=amount)
		else:
			(await utils.error(ctx,"You are missing 'Manage Messages' permission to run this command."))

def setup(bot):
	bot.add_cog(Admin(bot))