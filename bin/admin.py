#PXB Admin Module

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import json
from datetime import datetime

# # # # # # #
# VARIABLES #
# # # # # # #

developers = []

# # # # # # #
# FUNCTIONS #
# # # # # # #

async def error(ctx,error):
    msg = await ctx.send(embed=discord.Embed(title=f"The command you have entered is invalid",description=f"{ctx.message.content} `{error}`",color=0xff0000).set_footer(text=f"{str(datetime.utcnow())[:-7]} UTC"))
    await asyncio.sleep(5)
    await msg.delete()

# # #### # #
# GET DEVS #
# # #### # #

with open("settings.json","r",encoding="UTF-8") as file:
    settings = json.loads(file.read())
    for developer in settings["badges"]["developers"]:
        developers.append(developer)

# # # # # # # #
# ADMIN CLASS #
# # # # # # # #

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.group(name="admin",description="Administrative commands")
    async def admin(self,ctx):
        if ctx.invoked_subcommand is None:
            await error(ctx,"NO_INVOKED_SUBCOMMAND")

    @admin.command(name="ban",description="Ban a member from your server")
    async def _ban(self,ctx,member:discord.Member,reason):
        if ctx.author.guild_permissions.ban_members or ctx.author.id in developers:
            await ctx.send(embed=discord.Embed(title=f"{member.name} has been banned",description=f"Member {member.name}#{member.discriminator} was banned for {reason} by {ctx.author}",color=0xff0000).set_footer(text=str(datetime.utcnow())[:-7]))
            await member.send(embed=discord.Embed(title=f"You have been banned from {ctx.guild.name}",description=f"You were banned by {ctx.author.name} for {reason}",color=0xff0000).set_footer(text=str(datetime.utcnow())[:-7]))
            await member.ban(reason=reason)
        else:
            await error(ctx,"INSUFFICIENT_PERMISSIONS")
    @_ban.error
    async def _ban_handler(self,ctx,error):
    	if isinstance(error,commands.MissingRequiredArgument):
    		if error.param.name == "member":
    			await error(ctx,"NO_MEMBER_PROVIDED")
    		elif error.param.name == "reason":
    			await error(ctx,"NO_REASON_PROVIDED")
    
    @admin.command(name="banid",description="Ban a member from your server using their ID")
    async def _banid(self,ctx,mid:int,reason):
        if ctx.author.guild_permissions.ban_members or ctx.author.id in developers:
            await ctx.guild.ban(discord.Object(id=mid))
            await ctx.send(embed=discord.Embed(title=f"{mid} has been banned for '`{reason}`' by {ctx.author.name}",color=0xff0000).set_footer(text=str(datetime.utcnow())[:-7]))
    @_banid.error
    async def _banid_handler(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            if error.param.name == "id":
                await error(ctx,"NO_ID_PROVIDED")
            elif error.param.name == "reason":
                await error(ctx,"NO_REASON_PROVIDED")

    @admin.command(name="kick",description="Kick a member from your server")
    async def _kick(self,ctx,member:discord.Member):
        if ctx.author.guild_permissions.kick_members or ctx.author.id in developers:
            await ctx.send(embed=discord.Embed(title=f"{member.name} has been kicked",description=f"Member {member.name}#{member.discriminator} was kicked by {ctx.author}",color=0x770000).set_footer(text=str(datetime.utcnow())[:-7]))
            await member.send(embed=discord.Embed(title=f"You have been kicked from {ctx.guild.name} by {ctx.author.name}",color=0x770000).set_footer(text=str(datetime.utcnow())[:-7]))
            await member.kick()
        else:
            await error(ctx,"INSUFFICIENT_PERMISSIONS")
    @_kick.error
    async def _kick_handler(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            if error.param.name == "member":
                await error(ctx,"NO_MEMBER_PROVIDED")
    
    @admin.command(name="gag",description="Stops a user from being able to talk in voice channels")
    async def _gag(self,ctx,member:discord.Member):
        if ctx.author.guild_permissions.manage_roles or ctx.author.id in developers:
            for channel in ctx.guild.voice_channels:
                await channel.set_permissions(member,speak=False)
            await ctx.send(embed=discord.Embed(title=f"{ctx.author.name} gagged {member.name}").set_footer(text=str(datetime.utcnow())[:-7]))
    @_gag.error
    async def _gag_handler(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            if error.param.name == "member":
                await error(ctx,"NO_MEMBER_PROVIDED")

    @admin.command(name="ungag",description="Allows a user to be able to talk in voice channels again")
    async def _ungag(self,ctx,member:discord.Member):
        if ctx.author.guild_permissions.manage_roles or ctx.author.id in developers:
            for channel in ctx.guild.voice_channels:
                await channel.set_permissions(member,speak=True)
            await ctx.send(embed=discord.Embed(title=f"{ctx.author.name} ungagged {member.name}").set_footer(text=str(datetime.utcnow())[:-7]))
    async def _ungag_handler(self,ctx,error):
        if isinstance(error,commands.MissingRequiredArgument):
            if error.param.name == "member":
                await error(ctx,"NO_MEMBER_PROVIDED")

    @admin.command(name="purge",description="Delete multiple messages based on a specific parameter")
    async def _purge(self,ctx,check,amount:int):
        if ctx.author.guild_permissions.manage_messages or ctx.author.id in developers:
            if amount == None:
                amount = 100
            def bot_check(sender):
                return sender.author.bot
            def member_check(sender):
                if sender.author.bot:
                    return False
                else:
                    return True
            if check.lower() == "bot":
                await ctx.channel.purge(limit=amount,check=bot_check)
            elif check.lower() == "member":
                await ctx.channel.purge(limit=amount,check=member_check)
            elif check.lower() == "all":
                await ctx.channel.purge(limit=amount)
            else:
                await error(ctx,"INVALID_TYPE [bot, member or all]")
        else:
            await error(ctx,"INSUFFICIENT_PERMISSIONS")

def setup(bot):
	bot.add_cog(Admin(bot))