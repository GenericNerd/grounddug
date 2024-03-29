# GroundDug Moderator Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.cases as cases
import cogs.utils.logger as logger
# import cogs.utils.templates as templates
# import os

async def modLog(self,ctx,title,desc):
    guildDB = await db.find("guilds",{"id": ctx.guild.id})
    if "mod" in guildDB["logging"]["commands"]:
        msg = await embed.generate(title,desc,0xd90000)
        msg.set_footer(text=f"{ctx.author.name}#{ctx.author.discriminator} (ID: {ctx.author.id})",icon_url=ctx.author.avatar_url)
        if guildDB["channel"] != 0:
            await self.bot.get_channel(guildDB["channel"]).send(embed=msg)
    else:
        return

class Mod(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="mod",description="Guild moderation commands")
    @commands.guild_only()
    async def mod(self,ctx):
        # Send a help perms command if no subcommand invoked
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"mod")
        else:
            # Check whether logging for perms is enabled
            # await log(ctx,self.bot)
            pass

    @mod.command(name="ban",description="<member> [reason] | Bans a member from the guild")
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def ban(self,ctx,member:discord.Member,*,reason=None):
        # Create a case for the banned user before banning them, increasing case #
        await cases.createCase(ctx.guild,member,ctx.author,"banned",reason)
        try:
            # Attempt to notify the member they have been banned
            await member.send(embed=(await embed.generate(f"You have been banned from {ctx.guild.name}",f"You were banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`",0xff5555)))
        except:
            # Alert moderator that they do not know of their ban
            await embed.error(ctx,f"{member.name} could not be notified")
        finally:
            # Ban the user and send a message confirming the ban
            await modLog(self,ctx,f"{member.name} was banned",f"Banned for: `{reason}`")
            await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")

    @mod.command(name="hackban",description="<ID> [reason] | Bans a user by their ID from the guild without them needing them to be in the guild")
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def hackban(self,ctx,id:int,*,reason=None):
        # Get the discord object from the ID, and ban them from the guild
        try:
            await ctx.guild.ban(discord.Object(id=id),reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
        except:
            return await embed.error(ctx,"Invalid user ID")
        # Send a message confirming the ban
        await modLog(self,ctx,f"{id} was banned",f"Banned for: `{reason}`")

    @mod.command(name="softban",description="<member> [reason] | Bans a member and immediately unbans them from the guild, removing their messages")
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def softban(self,ctx,member:discord.Member,*,reason=None):
        # Create a case before soft-banning, increase case #
        await cases.createCase(ctx.guild,member,ctx.author,"soft-banned",reason)
        try:
            # Attempt to notify the member they have been soft-banned
            await member.send(embed=(await embed.generate(f"You have been soft-banned from {ctx.guild.name}",f"You were soft-banned by {ctx.author.name}#{ctx.author.discriminator}",0xff5555)))
        except:
            # Alert moderator that they do not know of their softban
            await embed.error(ctx,f"{member.name} could not be notified")
        finally:
            # Ban the member and immediately unban them
            await modLog(self,ctx,f"{member.name} was soft-banned",f"Banned for: `{reason}`")
            await member.ban(reason=f"Soft-banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
            await member.unban()

    @mod.command(name="kick",description="<member> [reason] | Kicks a member from the guild")
    @commands.guild_only()
    @checks.hasGDPermission("KICK_MEMBERS")
    async def kick(self,ctx,member:discord.Member,*,reason=None):
        await cases.createCase(ctx.guild,member,ctx.author,"kicked",reason)
        try:
            # Attempt to notify the member they have been kicked
            await member.send(embed=(await embed.generate(f"You have been kicked from {ctx.guild.name}",f"You were kicked by {ctx.author.name}#{ctx.author.discriminator} for: `{reason}`",0xff5555)))
        except:
            # Alert moderator that they do not know of their kick
            await embed.error(ctx,f"{member.name} could not be notified")
        finally:
            await modLog(self,ctx,f"{member.name} was kicked!",f"Kicked for: `{reason}`")
            await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")

    @mod.command(name="gag",aliases=["vmute"],description="<member> [reason] | Stops a user from talking in all voice channels")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def gag(self,ctx,member:discord.Member,*,reason=None):
        # Create a case for the gagged user
        await cases.createCase(ctx.guild,member,ctx.author,"gagged",reason)
        # For each channel, set speak permissions to False for the member
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,speak=False)
        # Send a message in the channel notifying of successful gag
        await modLog(self,ctx,f"{member.name} was gagged!",f"Gagged for: `{reason}`")

    @mod.command(name="ungag",aliases=["vunmute"],description="<member> [reason] | Allows a user to talk in all voice channels")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def ungag(self,ctx,member:discord.Member,*,reason=None):
        # For each channel, set speak permissions to True for the member
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,overwrite=None)
        # Send a message in the channel notifying of successful ungag
        await modLog(self,ctx,f"{member.name} was ungagged",None)

    @mod.command(name="mute",description="<member> [reason] | Stop a user from typing in all text channels")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def mute(self,ctx,member:discord.Member,*,reason=None):
        # Create a case for the muted user
        await cases.createCase(ctx.guild,member,ctx.author,"muted",reason)
        # For each text channel, set typing permissions to False for the member
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,send_messages=False)
        # Send a message in the channel notifying of successful mute
        await modLog(self,ctx,f"{member.name} was muted!",f"Muted for `{reason}`")

    @mod.command(name="unmute",description="<member> [reason] | Allow a user to typing in all text channels again")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def unmute(self,ctx,member:discord.Member,*,reason=None):
        # For each channel, set typing permissions to True for each member
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,overwrite=None)
        # Send a message in the channel notifying of successful unmute
        await modLog(self,ctx,f"{member.name} was unmuted",None)

    @mod.command(name="purge",description="[member/bot/all] [amount (100 default)] | Deletes multiple messages at once from the text channel the command was ran in, depending on check")
    @commands.guild_only()
    @checks.hasGDPermission("MANAGE_MESSAGES")
    async def purge(self,ctx,check="",amount=100):
        # Create checks for purge invoke later on
        def member_check(ctx):
            return not ctx.author.bot
        def bot_check(ctx):
            return ctx.author.bot
        # messages = []
        # async for message in ctx.channel.history(limit=amount):
        #     messages.append(message)
        # log = await templates.purgeTemplate("Purge Test",messages)
        # await ctx.send("Here",file=log)
        # Check what check is called, the purge based on that check
        if check.lower() == "member":
            await ctx.channel.purge(limit=amount,check=member_check)
        elif check.lower() == "bot":
            await ctx.channel.purge(limit=amount,check=bot_check)
        elif check.lower() == "all" or check == "":
            await ctx.channel.purge(limit=amount)
        else:
            await embed.error(ctx,"Invalid purge check, view command usage")
        await modLog(self,ctx,f"#{ctx.channel.name} was purged!",f"{check.title()} {amount} were purged!")

    @mod.command(name="strike",description="<user> [reason] | Warn a user for their behaviour")
    @commands.guild_only()
    @checks.hasGDPermission("WARN_MEMBERS")
    async def strike(self,ctx,user:discord.Member,*,reason=None):
        # Get the current guild case, before creating a case
        guildCase = await db.find("guilds",{"id": ctx.guild.id})
        await cases.createCase(ctx.guild,user,ctx.author,"warned",reason)
        # Send a message with the case number in footer
        await modLog(self,ctx,f"{user.name} was warned!",f"Warned for: `{reason}`")

    @mod.command(name="forgive",description="<user> <case #> | Forgives a users specific strike from their history")
    @commands.guild_only()
    @checks.hasGDPermission("WARN_MEMBERS")
    async def forgive(self,ctx,user:discord.Member,strike:int):
        userDB = await db.find("users",{"guild": ctx.guild.id, "user": user.id})
        try:
            # Try to get the strike from the user, if it exists
            userDB["strikes"][str(strike)]
        except:
            await embed.error(ctx,f"Strike number {strike} not found in {user.name}")
        else:
            # Check if strike is already forgiven
            if str(userDB["strikes"][str(strike)]["reason"])[-10:] == "(Forgiven)":
                return await embed.error(ctx,"This strike has already been forgiven")
            # Add forgiven to end of strike
            userDB["strikes"][str(strike)]["reason"] += " (Forgiven)"
            # Send a message and update DB to reflect
            await modLog(self,ctx,f"{user.name} was forgiven!",f"Strike {strike} was forgiven off record")
            await db.update("users",{"_id": userDB["_id"]},{"strikes": userDB["strikes"]})

    @mod.command(name="history",description="[user] | Returns user history")
    @commands.guild_only()
    async def history(self,ctx,user:discord.Member=None):
        if user is None:
            user = ctx.author
        msg = await embed.generate("User history",user.mention,0xff5555)
        # Find the user
        history = await db.find("users",{"guild": ctx.guild.id, "user": user.id})
        # For every strike, add a field to the embed
        for key in history["strikes"]:
            msg = await embed.add_field(msg,f"Case number #{key}",history["strikes"][key]["reason"])
        await ctx.send(embed=msg)

    @mod.command(name="case",description="<case #> | Returns the information for a specific case on the server")
    @commands.guild_only()
    async def case(self,ctx,case:int):
        msg = await embed.generate("Case history",None)
        # Get every user in the guild
        users = await db.findAll("users",{"guild": ctx.guild.id})
        # For field in each user
        async for field in users:
            # If the user has the strike number
            try:
                field["strikes"][str(case)]
            except:
                continue
            msg = await embed.add_field(msg,f"Here are the details for case number #{case}",field["strikes"][str(case)]["reason"])
        # If there are no embed fields, the case could not be found
        if msg.fields is []:
            msg.description = f"There is no case information for case number #{case}"
        await ctx.send(embed=msg)

class ModMisc(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="ban",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def _ban(self,ctx,member:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod ban"),member=member,reason=reason)

    @commands.command(name="hackban",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def _hackban(self,ctx,id:int,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod hackban"),id=id,reason=reason)

    @commands.command(name="softban",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def _softban(self,ctx,member:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod softban"),member=member,reason=reason)

    @commands.command(name="kick",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("KICK_MEMBERS")
    async def _kick(self,ctx,member:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod kick"),member=member,reason=reason)

    @commands.command(name="gag",aliases=["vmute"],hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _gag(self,ctx,member:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod gag"),member=member,reason=reason)

    @commands.command(name="ungag",aliases=["vunmute"],hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _ungag(self,ctx,member:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod ungag"),member=member,reason=reason)

    @commands.command(name="mute",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _mute(self,ctx,member:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod mute"),member=member,reason=reason)

    @commands.command(name="unmute",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _unmute(self,ctx,member:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod unmute"),member=member,reason=reason)

    @commands.command(name="purge",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MANAGE_MESSAGES")
    async def _purge(self,ctx,check="",amount=100):
        await ctx.invoke(self.bot.get_command("mod purge"),check=check,amount=amount)

    @commands.command(name="strike",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("WARN_MEMBERS")
    async def _strike(self,ctx,user:discord.Member,*,reason=None):
        await ctx.invoke(self.bot.get_command("mod strike"),user=user,reason=reason)

    @commands.command(name="forgive",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("WARN_MEMBERS")
    async def _forgive(self,ctx,user:discord.Member,strike:int):
        await ctx.invoke(self.bot.get_command("mod forgive"),user=user,strike=strike)

    @commands.command(name="history",hidden=True)
    @commands.guild_only()
    async def _history(self,ctx,user:discord.Member=None):
        await ctx.invoke(self.bot.get_command("mod history"),user=user)

    @commands.command(name="case",hidden=True)
    @commands.guild_only()
    async def _case(self,ctx,case:int):
        await ctx.invoke(self.bot.get_command("mod case"),case=case)

def setup(bot):
    bot.add_cog(Mod(bot))
    bot.add_cog(ModMisc(bot))