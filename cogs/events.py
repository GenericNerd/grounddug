# GroundDug Event Handler Cog

import discord
from discord.ext import commands
import asyncio
from profanity_filter import ProfanityFilter
import httpx
import re
from datetime import datetime
from colorama import Fore
import cogs.utils.embed as embed
import cogs.utils.misc as misc
import cogs.utils.db as db
import cogs.utils.logger as logger
import cogs.utils.checks as checks

# Variables required for automod to work in future
pf = ProfanityFilter()
httpx_Client = httpx.AsyncClient()
# Channel to send logs to
core_Channel = 664541295448031295

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # on_ready performs checks and sends logs to GD Discord
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Online")
        # Change bot status to DND while checks are being performed
        await self.bot.change_presence(status=discord.Status.dnd,activity=discord.Game("Starting up!"))
        # Send a message to the core channel
        await self.bot.get_channel(core_Channel).send(embed=(await embed.generate("I'm online","Starting member checks")))
        logger.work("Starting checks")
        database = []
        # # For every document on the database, append it to the database array
        for document in db.nsyncFindAll("users",{}):
            pass
            # if document["user"] not in database:
            #     database.append(document["user"])
        # Step through every user, if the user is not in the database, add it
        # for guild in self.bot.guilds:
        #     for user in guild.members:
        #         if user.id not in database:
        #             await db.insert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False,"WARN_MEMBERS": False,"MUTE_MEMBERS": False,"KICK_MEMBERS": False,"BAN_MEMBERS": False,"ADMINISTRATOR": False}, "strikes": {}})
        logger.work("Checks completed")
        # Send message to core channel saying checks are complete and make bot show as online
        await self.bot.get_channel(core_Channel).send(embed=(await embed.generate("Checks complete","Showing as online")))
        await self.bot.change_presence(status=discord.Status.online,activity=discord.Game("g!help to get started"))

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        # Create data variable with what will be inserted in DB and insert it
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
		        "admin": False,
            },
            "raid_mode": False,
            "cases": 0,
            "automod": {
                "caps": 0,
                "antiInvite": False,
                "antiURL": False,
                "profanity": False,
                "massMentions": 0,
		        "shortURL": False,
            },
	        "blacklistChannels": []}
        await db.insert("guilds",data)
        user_Object = {"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}}
        # Run through every member, if they are an admin, change all perms to be True
        for member in guild.members:
            if member.guild_permissions.administrator:
                for item, key in user_Object["permissions"].items():
                    user_Object["permissions"][item] = True
        # Insert this to the database and send a message saying the bot joined
        await db.insert("users",user_Object)
        await self.bot.get_channel(core_Channel).send(embed=(await embed.generate(f"I have joined {guild.name}",f"{guild.name} has {guild.member_count} members")))

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        # Remove all users in the guild and the guild information from both databases
        await db.removeMany("users",{"guild": guild.id})
        await db.remove("guilds",{"id": guild.id})
        # Send a message to the core channel saying the bot left
        await self.bot.channel(core_Channel).send(embed=(await embed.generate(f"I have left {guild.name}",f"{guild.name} had {guild.member_count} members :c")))

    @commands.Cog.listener()
    async def on_member_join(self,member):
        # Check if raid mode is enabled
        if not (await db.find("guilds",{"id": member.guild.id}))["raid_mode"]:
            # Insert database object
            await db.insert("users",{"guild": member.guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}})
        else:
            # Create an invite to send to the user
            invite = await member.guild.create_invite(max_uses=1,reason="Raid mode activated - Providing link to user")
            # Try sending a message and alerting the user, kick them regardless of if they were notified
            try:
                await member.send(embed=(await embed.generate(f"{member.guild.name} is currently in raid mode", f"This means that no new users can join. Please try and join again in a couple of hours on this link: https://discord.gg/{invite.code}")))
            except:
                pass
            finally:
                await member.kick(reason="Guild is in raid mode")

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        # Try needed because if guild is in raid mode, a object is never inserted
        try:
            await db.remove("users",{"guild": member.guild.id, "user": member.id})
        except Exception as e:
            logger.error(e)

    @commands.Cog.listener()
    async def on_message(self,ctx):
        # If message is not in a guild
        if ctx.guild is not None:
            # Get current guild, logging channel and set removed to False
            guild = await db.find("guilds",{"id": ctx.guild.id})
            log_Channel = self.bot.get_channel(guild["channel"])
            removed = False
            async def RuleViolator(msg,text,delete):
                # Could possibly add a strike feature here
                if delete:
                    await msg.delete()
                    removed = True
                    # Return an embed with the text variable
                    return await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator} {text} in #{ctx.channel.name}",f"`{ctx.content}`")
            if not removed:
                # This is the regex that will be used to check against messages for URLs
                url_Regex = r"(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?"
                # If anti-invite is on and message contains an invite, invoke RuleViolator
                if guild["automod"]["antiInvite"] and re.search("(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+[a-z]",ctx.content):
                    await log_Channel.send(embed=await RuleViolator(ctx,"tried to advertise",True))
                # If anti-URL is on and the message contains a URL, invoke RuleViolator
                elif guild["automod"]["antiURL"] and re.search(url_Regex,ctx.content):
                    await log_Channel.send(embed=await RuleViolator(ctx,"tried to post a link",True))
                # If short-URL is on and the message contains a URL, check if it is shortened
                elif guild["automod"]["shortURL"] and re.search(url_Regex,ctx.content):
                    shortened_URLs = []
                    # Find every URL in message
                    for url in re.findall(url_Regex):
                        # Emulate a browser to allow redirects
                        browser = await httpx_Client.head(url,allow_redirects=True)
                        # If the browser URL after redirects is not the URL it was given, append it to shortenedURLs
                        if browser.url != url:
                            shortened_URLs.append(str(browser.url))
                    if shortened_URLs is not []:
                        await ctx.delete()
                        # Embed description
                        description = ""
                        for url in shortened_URLs:
                            desc += f"{item} "
                        await ctx.send(embed=(await embed.generate("Shortened URLs detected!",f"{ctx.author.mention} posted a shortened link(s) leading to {desc}")))
                # If the message contains swearing, invoke RuleViolator
                elif guild["automod"]["profanity"] and pf.is_profane(ctx.content):
                    await log_Channel.send(embed=await RuleViolator(ctx,"tried to swear",True))
                # If caps is not disabled, the message is longer than 8 characters and the percentage of caps is above the threshold, invoke RuleViolator
                elif guild["automod"]["caps"] > 0 and len(ctx.content) > 8 and guild["automod"]["caps"] < (sum(1 for x in ctx.content if str.isupper(x))/len(ctx.content))*100:
                    await log_Channel.send(embed=await RuleViolator(ctx,"used too many caps",True))
                # If mass mentions are not disabled, and more than mass mentions were mentioned, invoke RuleViolator
                elif guild["automod"]["massMentions"] > 0 and len(ctx.raw_mentions) >= guild["automod"]["massMentions"]:
                    await log_Channel.send(embed=await RuleViolator(ctx,"pinged too many people",True))

    @commands.Cog.listener()
    async def on_command(self,ctx):
        # Misc command logging here, if we chose to keep it
        if ctx.guild is not None:
            pass

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        prefix = await misc.getPrefix(self.bot,ctx)
        # Is the error a required argument?
        if isinstance(error,commands.MissingRequiredArgument):
            await embed.error(ctx,f"{error} - Use {prefix}help to find the required arguments")
        # Is the error that the command doesn't exist?
        elif isinstance(error,commands.CommandNotFound):
            pass
        # Is the user missing the GD permission?
        elif isinstance(error,checks.MissingGDPermissionError):
            await embed.error(ctx,"You do not have the required GD permission to run this command")
        # Is the user missing the required level?
        elif isinstance(error,checks.LevelPermissionsError):
            await embed.error(ctx,"You do not have the required level to run this command")
        else:
            await embed.error(ctx,f"{error} - Report sent to developer")
            logger.error(f"{error} -- Context: {ctx.content}")
            await self.bot.get_channel(core_Channel).send(embed=(await embed.generate(f"{ctx.content} raised an error",error)))

def setup(bot):
    bot.add_cog(Events(bot))