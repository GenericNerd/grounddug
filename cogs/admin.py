#GroundDug Admin Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embeds as embeds
from cogs.utils.dbhandle import dbFind
from cogs.utils.dbhandle import dbUpdate

class admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="admin",description="Administrative commands")
    async def admin(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"admin")
        else:
            guild = await dbFind("guilds",{"id": ctx.guild.id})
            if guild["admin_log"]:
                channel = self.bot.get_channel(guild["channel"])
                await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))

    @admin.command(name="ban",description="<member> [reason] | Bans a member from the guild")
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def ban(self,ctx,member:discord.Member,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been banned",f"{member.name}#{member.discriminator} has been banned by {ctx.author} for `{reason}`",0xff5555)))
        try:
            await member.send(embed=(await embeds.generate(f"You have been banned from {ctx.guild.name}",f"You were banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`")))
        except Exception:
            await embeds.error(ctx,f"{member.name} could not be notified")
        finally:
            await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
    
    @admin.command(name="hackban",description="<ID> [reason] | Bans a user by their ID from the guild without them needing to be in the guild")
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def hackban(self,ctx,id:int,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{id} has been banned by {ctx.author.name}#{ctx.user.discriminator} for `{reason}`",None,0xff5555)))
        await ctx.guild.ban(discord.Object(id=id),reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")

    @admin.command(name="softban",description="<member> [reason] | Bans a member and immediately unbans them from the guild, removing their messages")
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def softban(self,ctx,member:discord.Member,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been soft-banned",f"{member.name}#{member.discriminator} has been soft-banned by {ctx.author}",0xff5555)))
        try:
            await member.send(embed=(await embeds.generate(f"You have been soft-banned from {ctx.guild.name}",f"You were soft-banned by {ctx.author.name}#{ctx.author.discriminator}")))
        except Exception:
            await embeds.error(ctx,f"{member.name} could not be notified")
        finally:
            await member.ban(reason=f"Softbanned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
            await member.unban()
    
    @admin.command(name="kick",description="<member> [reason] | Kicks a member from the guild")
    @commands.guild_only()
    @checks.has_GD_permission("KICK_MEMBERS")
    async def kick(self,ctx,member:discord.Member,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been kicked",f"{member.name}#{member.discriminator} has been kicked by {ctx.author}",0xff5555)))
        try:
            await member.send(embed=(await embeds.generate(f"You have been kicked from {ctx.guild.name}",f"You were kicked by {ctx.author.name}#{ctx.author.discriminator}")))
        except Exception as e:
            await embeds.error(ctx,f"{member.name} could not be notified")
        finally:
            await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")

    @admin.command(name="gag",description="<member> | Stops a user from talking in all voice channels")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def gag(self,ctx,member:discord.Member):
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,speak=False)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been gagged by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @admin.command(name="ungag",description="<member> | Allows a user from talking again in all voice channels")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def ungag(self,ctx,member:discord.Member):
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,speak=False)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been ungagged by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @admin.command(name="mute",description="<member> | Stops a user from typing in all text channels")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def mute(self,ctx,member:discord.Member):
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,send_messages=False)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been muted by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @admin.command(name="unmute",description="<member> | Allows a user to typing in all text channels again")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def unmute(self,ctx,member:discord.Member):
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,send_messages=True)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been unmuted by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @admin.command(name="purge",description="[amount (100 by default)] [member/bot/all] | Deletes multiple messages at once from the text channel the command was ran in")
    @commands.guild_only()
    @checks.has_GD_permission("MANAGE_MESSAGES")
    async def purge(self,ctx,amount=100,check=""):
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
            await embeds.error(ctx,"INVALID CHECK (Must be member, bot, all or empty)")

    @admin.command(name="raid",description="<state> | Enables or disables raid mode")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def raid(self,ctx,state=None):
        guild = await dbFind("guilds",{"id": ctx.guild.id})
        if state == None:
            await ctx.send(embed=(await embeds.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode is currently set to `{guild['raid_mode']}`")))
        elif state.lower() == "true":
            await dbUpdate("guilds",{"id": ctx.guild.id},{"raid_mode": True})
            await ctx.send(embed=(await embeds.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `enabled` by {ctx.author.mention}")))
        elif state.lower() == "false":
            await dbUpdate("guilds",{"id": ctx.guild.id},{"raid_mode": False})
            await ctx.send(embed=(await embeds.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `disabled` by {ctx.author.mention}")))
        else:
            await embeds.error(ctx,"Raid Mode state needs to be either `True` or `False`")

def setup(bot):
    bot.add_cog(admin(bot))