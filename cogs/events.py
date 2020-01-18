#GroundDug Event Handler Module

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import cogs.utils.embeds as embeds
from cogs.utils.useful import getPrefix
import cogs.utils.dbhandle as db 
import re

class events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.bot.user.name}\nOnline\nFrom {str(datetime.utcnow()).split('.')[0]} UTC")
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate("I'm online",f"As of {str(datetime.utcnow()).split('.')[0]} UTC")))
        await self.bot.change_presence(activity=discord.Game("g!help to get started"))

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        data = {
            "id": guild.id,
            "prefix": "g!",
            "channel": 0,
            "misc_log": False,
            "logs_log": False,
            "mod_log": False,
            "perms_log": False,
            "advertising_log": False,
            "delete_log": False,
            "raid_mode": False,
            "cases": 0}
        await db.dbInsert("guilds",data)
        for member in guild.members:
            if member.guild_permissions.administrator:
                await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True, "WARN_MEMBERS": True, "MUTE_MEMBERS": True, "KICK_MEMBERS": True, "BAN_MEMBERS": True, "ADMINISTRATOR": True}, "strikes": {}})
            else:
                await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}})
    
    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        await db.dbRemoveMany("users",{"guild": guild.id})
        await db.dbRemove("guilds",{"id": guild.id})

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if not (await db.dbFind("guilds",{"id": member.guild.id}))["raid_mode"]:
            await db.dbInsert("users",{"guild": member.guild.id, "user": member.id, "permissions": {
                "MANAGE_MESSAGES": False,
                "WARN_MEMBERS": False,
				"MUTE_MEMBERS": False,
				"KICK_MEMBERS": False,
				"BAN_MEMBERS": False,
				"ADMINISTRATOR": False}, "strikes": {}})
        else:
            try:
                await member.send(embed=(await embeds.generate(f"{member.guild.name} is currently on lockdown","Please try to join again in a couple of hours")))
            except Exception:
                pass
            finally:
                await member.kick(reason="Guild is on lockdown")

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        await db.dbRemove("users",{"guild": member.guild.id, "user": member.id})

    @commands.Cog.listener()
    async def on_message(self,ctx):
        if ctx.guild != None:
            guild = await db.dbFind("guilds",{"id": ctx.guild.id})
            if re.search("discord.gg/......",ctx.content) and guild["advertising_log"]:
                await ctx.delete()
                channel = self.bot.get_channel(guild["channel"])
                await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator} tried to advertise in {channel.mention}",None)))
    
    @commands.Cog.listener()
    async def on_message_delete(self,message):
        if message.guild != None and not "discord.gg/" in message.content:
            guild = await db.dbFind("guilds",{"id": message.guild.id})
            if guild["delete_log"]:
                channel = self.bot.get_channel(guild["channel"])
                msg = await embeds.generate("Message deleted",None,0xff5555)
                msg.set_author(name=message.author.name,icon_url=message.author.avatar_url)
                msg = await embeds.add_field(msg,message.content)
                await channel.send(embed=msg)

    @commands.Cog.listener()
    async def on_command(self,ctx):
        if ctx.guild != None:
            guild = await db.dbFind("guilds",{"id": ctx.guild.id})
            channel = self.bot.get_channel(guild["channel"])
            command_base = (ctx.message.content).split((await getPrefix(self.bot,ctx)))[1].split(" ")[0]
            command_list = ["admin","logs","perms","developer","dev"]
            if not command_base in command_list and guild["misc_log"]:
                try:
                    await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
                except:
                    pass

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        prefix = await getPrefix(self.bot,ctx)
        if isinstance(error,commands.MissingRequiredArgument):
            await embeds.error(ctx,f"{error} - Use {prefix}help to find the required arguments")
        elif isinstance(error,commands.CommandNotFound):
            pass
        elif isinstance(error,commands.CheckFailure):
            await embeds.error(ctx,f"You do not have the valid permissions to run this command")
        else:
            await embeds.error(ctx,f"{error} - Report to developers")

def setup(bot):
	bot.add_cog(events(bot))