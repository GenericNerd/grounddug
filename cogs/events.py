# GroundDug Event Handler Cog

import discord
from discord.ext import commands
import asyncio
from profanity_filter import ProfanityFilter
import httpx
import re
from datetime import datetime
import cogs.utils.embed as embed
import cogs.utils.misc as misc
import cogs.utils.db as db
import cogs.utils.logger as logger
import cogs.utils.checks as checks
import cogs.utils.cases as cases
from sentry_sdk import capture_exception

# Variables required for automod to work in future
pf = ProfanityFilter()
httpxClient = httpx.AsyncClient()
# Channel to send logs to
coreChannel = 664541295448031295

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # on_ready performs checks and sends logs to GD Discord
    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Online")
        prefix = await misc.getPrefix(self.bot,None)
        # Change bot status to online when bot is ready
        await self.bot.change_presence(status=discord.Status.online,activity=discord.Game(f"{prefix}help to get started"))
        # Send a message to the core channel
        await self.bot.get_channel(coreChannel).send(embed=(await embed.generate("I'm online",None)))

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
                "warnOnRemove": False,
            },
	        "blacklistChannels": []}
        await db.insert("guilds",data)
        userObject = {"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}}
        # Run through every member, if they are an admin, change all perms to be True
        for member in guild.members:
            if member.guild_permissions.administrator:
                for item, key in userObject["permissions"].items():
                    userObject["permissions"][item] = True
        # Insert this to the database and send a message saying the bot joined
        await db.insert("users",userObject)
        await self.bot.get_channel(coreChannel).send(embed=(await embed.generate(f"I have joined {guild.name}",f"{guild.name} has {guild.member_count} members")))

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        # Remove all users in the guild and the guild information from both databases
        await db.removeMany("users",{"guild": guild.id})
        await db.remove("guilds",{"id": guild.id})
        # Send a message to the core channel saying the bot left
        await self.bot.channel(coreChannel).send(embed=(await embed.generate(f"I have left {guild.name}",f"{guild.name} had {guild.member_count} members :c")))

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
    async def on_command(self,ctx):
        # Misc command logging here, if we chose to keep it
        if ctx.guild is not None:
            pass

    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        logger.info(f"{after.channel.id}, {after.channel.id==665690058288005122}")
        if before.channel == None and after.channel.id == 665690058288005122:
            logger.info(member)

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
        # Is there a bad argument that was called?
        elif isinstance(error,commands.BadArgument):
            await embed.error(ctx,"Bad argument! Make sure you are calling something valid!")
        # Is the command not able to be ran in private messages?
        elif isinstance(error,commands.NoPrivateMessage):
            await embed.error(ctx,"This command cannot be ran in private messages.")
        else:
            await embed.error(ctx,f"{error} - Report sent to developer")
            await self.bot.get_channel(coreChannel).send(embed=(await embed.generate(f"Error raised! Sentry issue created",None,0xff0000)))
            capture_exception(error)

def setup(bot):
    bot.add_cog(Events(bot))