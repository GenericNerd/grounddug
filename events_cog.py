#GroundDug Event Handling

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import utils
import re
import db_handle as db 

# # # # # # # #
# EVENT CLASS #
# # # # # # # #

class Events(commands.Cog):
	def __init__(self,bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_guild_join(self,guild):
		data = {
			"id": guild.id,
			"prefix": "g!",
			"channel": 0,
			"misc_log": False,
			"logs_log": False,
			"admin_log": False,
			"advertising_log": False,
			"delete_log": False}
		(await db.dbInsert("guilds",data))
		for member in guild.members:
			if member.id == guild.owner_id:
				(await db.dbInsert("permissions",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True, "MUTE_MEMBERS": True, "KICK_MEMBERS": True, "BAN_MEMBERS": True, "ADMINISTRATOR": True}}))
			else:
				(await db.dbInsert("permissions",{"guild": guild.id, "user": member.id, "permissions": {
					"MANAGE_MESSAGES": False,
					"MUTE_MEMBERS": False,
					"KICK_MEMBERS": False,
					"BAN_MEMBERS": False,
					"ADMINISTRATOR": False}}))
	
	@commands.Cog.listener()
	async def on_guild_remove(self,guild):
		(await db.dbRemoveMany("permissions",{"guild": guild.id}))
		(await db.dbRemove("guilds",{"id": guild.id}))

	@commands.Cog.listener()
	async def on_member_join(self,member):
		(await db.dbInsert("permissions",{"guild": member.guild.id, "user": member.id, "permissions": {
			"MANAGE_MESSAGES": False,
			"MUTE_MEMBERS": False,
			"KICK_MEMBERS": False,
			"BAN_MEMBERS": False,
			"ADMINISTRATOR": False}}))

	@commands.Cog.listener()
	async def on_member_remove(self,member):
		(await db.dbRemove("permissions",{"guild": member.guild.id,"user":member.id}))

	@commands.Cog.listener()
	async def on_message(self,ctx):
		guild = (await db.dbFind("guilds",{"id": ctx.guild.id}))
		if re.search("discord.gg/......",ctx.content) and guild["advertising_log"]:
			await ctx.delete()
			channel = self.bot.get_channel(guild["channel"])
			await channel.send(embed=(await utils.embedGen(f"{ctx.author.name}#{ctx.author.discriminator} tried to advertise in {channel.mention}",None)))

	@commands.Cog.listener()
	async def on_command(self,ctx):
		if ctx.guild != None:
			guild = (await db.dbFind("guilds",{"id": ctx.guild.id}))
			channel = self.bot.get_channel(guild["channel"])
			command_base = (ctx.message.content).split((await utils.getPrefix(self.bot,ctx)))[1].split(" ")[0]
			if command_base == "admin" and guild["admin_log"]:
				(await channel.send(embed=(await utils.embedGen(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>"))))
			elif command_base == "logs" and guild["logs_log"]:
				(await channel.send(embed=(await utils.embedGen(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>"))))
			elif command_base == "developer" or command_base == "modules":
				pass
			elif command_base != "admin" and command_base != "logs" and guild["misc_log"]:
				(await channel.send(embed=(await utils.embedGen(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>"))))

	@commands.Cog.listener()
	async def on_message_delete(self,message):
		if message.guild != None and not "discord.gg/" in message.content:
			guild = (await db.dbFind("guilds",{"id": message.guild.id}))
			if guild["delete_log"]:
				msg = (await utils.embedGen("Message delete",None,0xff5555))
				msg.set_author(name=message.author.name,icon_url=message.author.avatar_url)
				msg.add_field(name="Content",value=message.content,inline=False)
				await message.channel.send(embed=msg)

def setup(bot):
	bot.add_cog(Events(bot))