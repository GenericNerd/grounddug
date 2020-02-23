#GroundDug Admin Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embeds as embeds
from cogs.utils.dbhandle import dbFind
from cogs.utils.dbhandle import dbUpdate
from cogs.utils.dbhandle import dbFindAll

async def log(ctx,bot):
    guild = await dbFind("guilds",{"id": ctx.guild.id})
    if guild["logs"]["mod"]:
        channel = bot.get_channel(guild["channel"])
        try:
            await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
        except:
            pass

class mod(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="mod",description="Guild moderation commands")
    async def mod(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"mod")
        else:
            guild = await dbFind("guilds",{"id": ctx.guild.id})
            if guild["logs"]["mod"]:
                channel = self.bot.get_channel(guild["channel"])
                try:
                    await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
                except:
                    pass

    @mod.command(name="ban",description="<member> [reason] | Bans a member from the guild")
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def ban(self,ctx,member:discord.Member,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been banned",f"{member.name}#{member.discriminator} has been banned by {ctx.author} for `{reason}`",0xff5555)))
        try:
            await member.send(embed=(await embeds.generate(f"You have been banned from {ctx.guild.name}",f"You were banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`",0xff5555)))
        except Exception:
            await embeds.error(ctx,f"{member.name} could not be notified")
        finally:
            await member.ban(reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
    
    @mod.command(name="hackban",description="<ID> [reason] | Bans a user by their ID from the guild without them needing to be in the guild")
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def hackban(self,ctx,id:int,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{id} has been banned by {ctx.author.name}#{ctx.author.discriminator} for `{reason}`",None,0xff5555)))
        await ctx.guild.ban(discord.Object(id=id),reason=f"Banned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")

    @mod.command(name="softban",description="<member> [reason] | Bans a member and immediately unbans them from the guild, removing their messages")
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def softban(self,ctx,member:discord.Member,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been soft-banned",f"{member.name}#{member.discriminator} has been soft-banned by {ctx.author}",0xff5555)))
        try:
            await member.send(embed=(await embeds.generate(f"You have been soft-banned from {ctx.guild.name}",f"You were soft-banned by {ctx.author.name}#{ctx.author.discriminator}",0xff5555)))
        except Exception:
            await embeds.error(ctx,f"{member.name} could not be notified")
        finally:
            await member.ban(reason=f"Softbanned by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")
            await member.unban()
    
    @mod.command(name="kick",description="<member> [reason] | Kicks a member from the guild")
    @commands.guild_only()
    @checks.has_GD_permission("KICK_MEMBERS")
    async def kick(self,ctx,member:discord.Member,reason=None):
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been kicked",f"{member.name}#{member.discriminator} has been kicked by {ctx.author}",0xff5555)))
        try:
            await member.send(embed=(await embeds.generate(f"You have been kicked from {ctx.guild.name}",f"You were kicked by {ctx.author.name}#{ctx.author.discriminator}",0xff5555)))
        except Exception as e:
            await embeds.error(ctx,f"{member.name} could not be notified")
        finally:
            await member.kick(reason=f"Kicked by {ctx.author.name}#{ctx.author.discriminator} for: {reason}")

    @mod.command(name="gag",description="<member> | Stops a user from talking in all voice channels")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def gag(self,ctx,member:discord.Member):
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,speak=False)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been gagged by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @mod.command(name="ungag",description="<member> | Allows a user from talking again in all voice channels")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def ungag(self,ctx,member:discord.Member):
        for channel in ctx.guild.voice_channels:
            await channel.set_permissions(member,speak=True)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been ungagged by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @mod.command(name="mute",description="<member> | Stops a user from typing in all text channels")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def mute(self,ctx,member:discord.Member):
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,send_messages=False)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been muted by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @mod.command(name="unmute",description="<member> | Allows a user to typing in all text channels again")
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def unmute(self,ctx,member:discord.Member):
        for channel in ctx.guild.text_channels:
            await channel.set_permissions(member,send_messages=True)
        await ctx.send(embed=(await embeds.generate(f"{member.name} has been unmuted by {ctx.author.name}#{ctx.author.discriminator}",None)))

    @mod.command(name="purge",description="[amount (100 by default)] [member/bot/all] | Deletes multiple messages at once from the text channel the command was ran in")
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

    @mod.command(name="strike",description="<user> [reason] | Warn a user for their behaviour")
    @commands.guild_only()
    @checks.has_GD_permission("WARN_MEMBERS")
    async def strike(self,ctx,user:discord.Member,*,reason=None):
        guildDB = await dbFind("guilds",{"id": ctx.guild.id})
        userDB = await dbFind("users",{"guild": ctx.guild.id, "user": user.id})
        userDB["strikes"][str(guildDB["cases"])] = {"moderator": ctx.author.id, "reason": reason}
        await dbUpdate("users",{"_id": userDB["_id"]},{"strikes": userDB["strikes"]})
        await dbUpdate("guilds",{"_id": guildDB["_id"]},{"cases": guildDB["cases"] + 1})
        await ctx.send(embed=(await embeds.generate(f"{user.name}#{user.discriminator} has been striked!",f"{ctx.author.mention} striked {user.mention} for `{reason}`",0xff5555)).set_footer(text=f"Case number #{guildDB['cases']}"))

    @mod.command(name="forgive",description="<user> <case #> | Removes a users specific strike from their history")
    @commands.guild_only()
    @checks.has_GD_permission("WARN_MEMBERS")
    async def forgive(self,ctx,user:discord.Member,strike:int):
        userDB = await dbFind("users",{"guild": ctx.guild.id, "user": user.id})
        try:
            del userDB["strikes"][str(strike)]
        except:
            return await ctx.send(embed=(await embeds.generate(f"Could not find case number #{strike} for {user.name}",None)))
        await ctx.send(embed=(await embeds.generate(f"Case number #{strike} has been forgiven",None)))
        await dbUpdate("users",{"_id": userDB["_id"]},{"strikes": userDB["strikes"]})

    @mod.command(name="history",description="[user] | Returns strike history for a user")
    @commands.guild_only()
    async def history(self,ctx,user:discord.Member=None):
        if user == None:
            user = ctx.author
        msg = await embeds.generate("Strike history",user.mention,0xff5555)
        history = await dbFind("users",{"guild": ctx.guild.id, "user": user.id})
        for key in history["strikes"]:
            msg = await embeds.add_field(msg,f"Case #{key}: Warning from {self.bot.get_user(history['strikes'][key]['moderator']).name}",f"Warned for {history['strikes'][key]['reason']}")
        await ctx.send(embed=msg)

    @mod.command(name="case",description="<case number> | Returns the information for a specific case on the server")
    @commands.guild_only()
    async def case(self,ctx,case:int):
        msg = await embeds.generate("Case history",None)
        guildDB = await dbFindAll("users",{"guild": ctx.guild.id})
        async for field in guildDB:
            if field["strikes"]:
                try:
                    msg = await embeds.add_field(msg,f"Here are the details for case number #{case}",f"<@{field['strikes'][str(case)]['moderator']}> warned <@{field['user']}> for: `{field['strikes'][str(case)]['reason']}`")
                except:
                    pass
        if msg.fields == []:
            msg.description = f"There is no case information for case number #{case}"
        await ctx.send(embed=msg)

    # MISC COMMAND INVOKE

    @commands.command(name="ban",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def _ban(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod ban"),member,reason)

    @commands.command(name="hackban",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def _hackban(self,ctx,id:int,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod hackban"),id,reason)

    @commands.command(name="softban",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("BAN_MEMBERS")
    async def _softban(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod softban"),member,reason)

    @commands.command(name="kick",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("KICK_MEMBERS")
    async def _kick(self,ctx,member:discord.Member,reason=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod kick"),member,reason)

    @commands.command(name="gag",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def _gag(self,ctx,member:discord.Member):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod gag"),member)

    @commands.command(name="ungag",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def _ungag(self,ctx,member:discord.Member):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod ungag"),member)

    @commands.command(name="mute",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def _mute(self,ctx,member:discord.Member):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod mute"),member)

    @commands.command(name="unmute",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("MUTE_MEMBERS")
    async def _unmute(self,ctx,member:discord.Member):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod unmute"),member)

    @commands.command(name="purge",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("MANAGE_MESSAGES")
    async def _purge(self,ctx,amount=100,check=""):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod purge"),amount,check)

    @commands.command(name="strike",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("WARN_MEMBERS")
    async def _strike(self,ctx,user:discord.Member,*,r=None):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod strike"),user,reason=r)
    
    @commands.command(name="forgive",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("WARN_MEMBERS")
    async def _forgive(self,ctx,user:discord.Member,strike:int):
        await log(ctx,self.bot)
        await ctx.invoke(self.bot.get_command("mod forgive"),user,strike)

    @commands.command(name="history",hidden=True)
    @commands.guild_only()
    async def _history(self,ctx,user:discord.Member=None):
        await ctx.invoke(self.bot.get_command("mod history"),user)

    @commands.command(name="case",hidden=True)
    @commands.guild_only()
    async def _case(self,ctx,case:int):
        await ctx.invoke(self.bot.get_command("mod case"),case)

def setup(bot):
    bot.add_cog(mod(bot))