# GroundDug Moderator Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.cases as cases

async def log(ctx,bot):
    guild = await db.find("guilds",{"id": ctx.guild.id})
    if guild["logs"]["mod"]:
        # Get the logging channel for the guild
        channel = self.bot.get_command(guild["channel"])
        try:
            await channel.send(embed=(await embed.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in #{ctx.channel.name}")))
        except:
            pass

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
            await log(ctx,self.bot)

    @mod.command(name="ban",description="<member> [reason] | Bans a member from the guild")
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def ban(self,ctx,member:discord.Member,reason=None):
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
            await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
            await ctx.send(embed=(await embed.generate(f"{member.name} has been banned",f"{member.name}#{member.discriminator} has been banned by {ctx.author.mention} for `{reason}`",0xff5555)))

    @mod.command(name="hackban",description="<ID> [reason] | Bans a user by their ID from the guild without them needing them to be in the guild")
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def hackban(self,ctx,id:int,reason=None):
        # Get the discord object from the ID, and ban them from the guild
        try:
            await ctx.guild.ban(discord.Object(id=id),reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
        except:
            return await embed.error(ctx,"Invalid user ID")
        # Send a message confirming the ban
        await ctx.send(embed=(await embed.generate(f"{id} has been banned",f"{ctx.author.mention} has banned this ID for `{reason}`",0xff5555)))

    @mod.command(name="softban",description="<member> [reason] | Bans a member and immediately unbans them from the guild, removing their messages")
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def softban(self,ctx,member:discord.Member,reason=None):
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
            await member.ban(reason=f"Soft-banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
            await member.unban()
            await ctx.send(embed=(await embed.generate(f"{member.name} has been soft-banned",f"{member.name}#{member.discriminator} has been soft-banned by {ctx.author.mention} for `{reason}`",0xff5555)))

    @mod.command(name="kick",description="<member> [reason] | Kicks a member from the guild")
    @commands.guild_only()
    @checks.hasGDPermission("KICK_MEMBERS")
    async def kick(self,ctx,member:discord.Member,reason=None):
        await cases.createCase(ctx.guild,member,ctx.author,"kicked",reason)
        try:
            # Attempt to notify the member they have been kicked
            await member.send(embed=(await embed.generate(f"You have been kicked from {ctx.guild.name}",f"You were kicked by {ctx.author.name}#{ctx.author.discriminator} for: `{reason}`",0xff5555)))
        except:
            # Alert moderator that they do not know of their kick
            await embed.error(ctx,f"{member.name} could not be notified")
        finally:
            await ctx.send(embed=(await embed.generate(f"{member.name} has been kicked",f"{member.name}#{member.discriminator} has been kicked by {ctx.author}",0xff5555)))
            await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")

    @mod.command(name="gag",aliases=["vmute"],description="<member> [reason] | Stops a user from talking in all voice channels")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def gag(self,ctx,member:discord.Member,reason=None):
        # Create a case for the gagged user
        await cases.createCase(ctx.guild,member,ctx.author,"gagged",reason)
        # For each channel, set speak permissions to False for the member
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,speak=False)
        # Send a message in the channel notifying of successful gag
        await ctx.send(embed=(await embed.generate(f"{member.name} has been gagged",f"{ctx.author.mention} gagged them for `{reason}`")))

    @mod.command(name="ungag",aliases=["vunmute"],description="<member> [reason] | Allows a user to talk in all voice channels")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def ungag(self,ctx,member:discord.Member,reason=None):
        # For each channel, set speak permissions to True for the member
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,speak=True)
        # Send a message in the channel notifying of successful ungag
        await ctx.send(embed=(await embed.generate(f"{member.name} has been ungagged",f"{ctx.author.mention} ungagged them for `{reason}`")))

    @mod.command(name="mute",description="<member> [reason] | Stop a user from typing in all text channels")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def mute(self,ctx,member:discord.Member,reason=None):
        # Create a case for the muted user
        await cases.createCase(ctx.guild,member,ctx.author,"muted",reason)
        # For each text channel, set typing permissions to False for the member
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,send_messages=False)
        # Send a message in the channel notifying of successful mute
        await ctx.send(embed=(await embed.generate(f"{member.name} has been muted",f"{ctx.author.mention} muted this user for: `{reason}`")))

    @mod.command(name="unmute",description="<member> [reason] | Allow a user to typing in all text channels again")
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def unmute(self,ctx,member:discord.Member,reason=None):
        # For each channel, set typing permissions to True for each member
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,send_messages=True)
        # Send a message in the channel notifying of successful unmute
        await ctx.send(embed=(await embed.generate(f"{member.name} has been unmutted",f"{ctx.author.mention} unmutted this user for: `{reason}`")))

    @mod.command(name="purge",description="[member/bot/all] [amount (100 default)] | Deletes multiple messages at once from the text channel the command was ran in, depending on check")
    @commands.guild_only()
    @checks.hasGDPermission("MANAGE_MESSAGES")
    async def purge(self,ctx,check="",amount=100):
        # Create checks for purge invoke later on
        def member_check(ctx):
            return not ctx.author.bot
        def bot_check(ctx):
            return ctx.author.bot
        # Check what check is called, the purge based on that check
        if check.lower() == "member":
            await ctx.channel.purge(limit=amount,check=member_check)
        elif check.lower() == "bot":
            await ctx.channel.purge(limit=amount,check=bot_check)
        elif check.lower() == "all" or check == "":
            await ctx.channel.purge(limit=amount)
        else:
            await embed.error(ctx,"Invalid purge check, view command usage")

    @mod.command(name="strike",description="<user> [reason] | Warn a user for their behaviour")
    @commands.guild_only()
    @checks.hasGDPermission("WARN_MEMBERS")
    async def strike(self,ctx,user:discord.Member,*,reason=None):
        # Get the current guild case, before creating a case
        guildCase = await db.find("guilds",{"id": ctx.guild.id})
        await cases.createCase(ctx.guild,user,ctx.author,"warned",reason)
        # Send a message with the case number in footer
        await ctx.send(embed=(await embed.generate(f"{user.name}#{user.discriminator} was warned!",f"{ctx.author.mention} striked {user.mention} for `{reason}`",0xff5555)).set_footer(text=f"Case number #{guildCase['cases']}"))

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
            # Add forgiven to end of strike
            userDB["strikes"][str(strike)]["reason"] += " (Forgiven)"
            # Send a message and update DB to reflect
            await ctx.send(embed=(await embed.generate(f"Case number #{strike} has been forgiven by {ctx.author.name}#{ctx.author.discriminator}",None)))
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
    async def _ban(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod ban"),member,reason)

    @commands.command(name="hackban",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def _hackban(self,ctx,id:int,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod hackban"),id,reason)

    @commands.command(name="softban",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("BAN_MEMBERS")
    async def _softban(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod softban"),member,reason)

    @commands.command(name="kick",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("KICK_MEMBERS")
    async def _kick(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod kick"),member,reason)

    @commands.command(name="gag",aliases=["vmute"],hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _gag(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod gag"),member,reason)

    @commands.command(name="ungag",aliases=["vunmute"],hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _ungag(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod ungag"),member,reason)

    @commands.command(name="mute",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _mute(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod mute"),member,reason)

    @commands.command(name="unmute",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MUTE_MEMBERS")
    async def _unmute(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod unmute"),member,reason)

    @commands.command(name="purge",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("MANAGE_MESSAGES")
    async def _purge(self,ctx,check="",amount=100):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod purge"),check,amount)

    @commands.command(name="strike",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("WARN_MEMBERS")
    async def _strike(self,ctx,user:discord.Member,*,r=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod strike"),user,reason=r)

    @commands.command(name="forgive",hidden=True)
    @commands.guild_only()
    @checks.hasGDPermission("WARN_MEMBERS")
    async def _forgive(self,ctx,user:discord.Member,strike:int):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod forgive"),user,strike)

    @commands.command(name="history",hidden=True)
    @commands.guild_only()
    async def _history(self,ctx,user:discord.Member=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod history"),user)

    @commands.command(name="case",hidden=True)
    @commands.guild_only()
    async def _case(self,ctx,case:int):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod case"),case)

def setup(bot):
    bot.add_cog(Mod(bot))
    bot.add_cog(ModMisc(bot))