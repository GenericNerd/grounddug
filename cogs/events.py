#GroundDug Event Handler Module

import discord
from discord.ext import commands
import asyncio
from profanity_filter import ProfanityFilter
import httpx
from datetime import datetime
import cogs.utils.embeds as embeds
from cogs.utils.useful import getPrefix
import cogs.utils.dbhandle as db
import cogs.utils.useful as useful
import re

pf = ProfanityFilter()
httpxClient = httpx.AsyncClient()

class events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.bot.user.name}\nOnline\nFrom {str(datetime.utcnow()).split('.')[0]} UTC")
        await self.bot.change_presence(status=discord.Status.dnd,activity=discord.Game("Booting up!"))
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate("I'm online",f"As of {str(datetime.utcnow()).split('.')[0]} UTC, I am performing my member checks now!")))
        for guild in self.bot.guilds:
            for member in guild.members:
                if (await db.itemExist("users", {"guild": guild.id, "user": member.id})):
                    await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False,"WARN_MEMBERS": False,"MUTE_MEMBERS": False,"KICK_MEMBERS": False,"BAN_MEMBERS": False,"ADMINISTRATOR": False}, "strikes": {}})
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate("Checks completed!",f"I am now fully online as of {str(datetime.utcnow()).split('.')[0]} UTC")))
        await self.bot.change_presence(status=discord.Status.online,activity=discord.Game("g!help to get started"))

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        data = {
            "id": guild.id,
            "prefix": "g!",
            "channel": 0,
            "logs": {
                "misc": False,
                "logs": False,
                "mod": False,
                "perms": False,
                "automod": False,
            },
            "raid_mode": False,
            "cases": 0,
            "automod": {
                "caps": 0,
                "antiInvite": False,
                "antiURL": False,
                "profanity": False,
                "massMentions": 0
            }}
        await db.dbInsert("guilds",data)
        for member in guild.members:
            if member.guild_permissions.administrator:
                await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True, "WARN_MEMBERS": True, "MUTE_MEMBERS": True, "KICK_MEMBERS": True, "BAN_MEMBERS": True, "ADMINISTRATOR": True}, "strikes": {}})
            else:
                await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}})
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate(f"I have joined {guild.name}",f"{guild.name} has {guild.member_count} members")))

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        await db.dbRemoveMany("users",{"guild": guild.id})
        await db.dbRemove("guilds",{"id": guild.id})
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate(f"I have left {guild.name}",f"{guild.name} had {guild.member_count} members :(")))

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
            channel = self.bot.get_channel(guild["channel"])
            removed = False
            async def RuleViolator(msg,text,channel):
                global removed,guild
                await msg.delete()
                await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator} {text} in #{ctx.channel.name}",f"`{ctx.content}`")))
                # userDB = await db.dbFind("users",{"guild": ctx.guild.id, "user": user.id})
                # userDB["strikes"][str(guildDB["cases"])] = {"moderator": ctx.author.id, "reason": text.capitalize()}
                # await db.dbUpdate("users",{"_id": userDB["_id"]},{"strikes": userDB["strikes"]})
                # await db.dbUpdate("guilds",{"_id": guildDB["_id"]},{"cases": guildDB["cases"] + 1})
                removed = True
            if not removed and guild["automod"]["antiInvite"] and re.search("(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+[a-z]",ctx.content):
                await RuleViolator(ctx,"tried to advertise",channel)
            if not removed and guild["automod"]["antiURL"] and re.search(r"(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?",ctx.content):
                await RuleViolator(ctx,"tried to post a link",channel)
            if not removed and guild["automod"]["unshortenURL"] and re.search(r"(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?",ctx.content):
                async def findURLs(string):
                    url = re.findall(r"(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?",string)
                    return url
                shortenedURLs = []
                for url in await findURLs(ctx.content):
                    shortenedURL = await httpxClient.head(url,allow_redirects=True).url
                    if shortenedURL != url:
                        shortenedURLs.append(shortenedURL)
                await RuleViolator(ctx,f"tried to shorten links ({shortenedURLs})",channel)
            if not removed and guild["automod"]["profanity"] and pf.is_profane(ctx.content):
                await RuleViolator(ctx,"tried to swear",channel)
            if not removed and guild["automod"]["caps"] > 0 and len(ctx.content) > 0 and guild["automod"]["caps"] < (sum(1 for x in ctx.content if str.isupper(x))/len(ctx.content))*100:
                await RuleViolator(ctx,"used too many CAPS",channel)
            if not removed and guild["automod"]["massMentions"] > 0 and len(ctx.raw_mentions) > guild["automod"]["massMentions"]:
                await RuleViolator(ctx,"pinged too many people",channel)

    @commands.Cog.listener()
    async def on_command(self,ctx):
        if ctx.guild != None:
            guild = await db.dbFind("guilds",{"id": ctx.guild.id})
            channel = self.bot.get_channel(guild["channel"])
            command_base = (ctx.message.content).split((await getPrefix(self.bot,ctx)))[1].split(" ")[0]
            command_list = ["admin","logs","perms","developer","dev","automod","admin"]
            if not command_base in command_list and guild["logs"]["misc"]:
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