# GroundDug Event Handler Cog

import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
from datetime import datetime
from bson.objectid import ObjectId
import cogs.utils.embed as embed
import cogs.utils.misc as misc
import cogs.utils.db as db
import cogs.utils.logger as logger
import cogs.utils.checks as checks
import cogs.utils.cases as cases
import uuid
import os
import glob
from sentry_sdk import capture_exception

# Channel to send logs to
coreChannel = 664541295448031295

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.clearStorage.start()

    # on_ready performs checks and sends logs to GD Discord
    @commands.Cog.listener()
    async def on_ready(self):
        logger.success("Online")
        prefix = await misc.getPrefix(self.bot,None)
        # Change bot status to online when bot is ready
        await self.bot.change_presence(status=discord.Status.online,activity=discord.Game(f"{prefix}help to get started"))
        # Send a message to the core channel
        await self.bot.get_channel(coreChannel).send(embed=(await embed.generate("I'm online",None)))
        # Get the current users the bot has and update the DB
        users = 0
        for guild in self.bot.guilds:
            users += guild.member_count
        await db.update("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")},{"userCount": users})

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        # Create data variable with what will be inserted in DB and insert it
        data = {
            "id": guild.id,
            "prefix": "g!",
            "channel": 0,
            "logging": {
                "commands": [],
                "events": []
                },
            "raid_mode": False,
            "cases": 0,
            "automod": {
                "caps": 0,
                "zalgo": 0,
                "massMentions": 0,
                "antiInvite": False,
                "antiURL": False,
                "profanity": False,
                "shortURL": False,
                "warnOnRemove": False,
            },
            "blacklistChannels": [],
            "boundary":{
                "enabled": False,
                "role": None
            },
            "premium": {"isPremium": False}}
        await db.insert("guilds",data)
        # Get the current user count and update the DB
        currentUsers = await db.find("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})
        currentUsers["userCount"] = int(currentUsers["userCount"])+len(guild.members)
        await db.update("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")},{"userCount": currentUsers["userCount"]})
        # Run through every member, if they are an admin, change all perms to be True
        for member in guild.members:
            userObject = {"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "BYPASS_AUTOMOD": False, "ADMINISTRATOR": False}, "strikes": {}}
            if member.guild_permissions.administrator:
                for item, key in userObject["permissions"].items():
                    userObject["permissions"][item] = True
            await db.insert("users",userObject)
        # Insert this to the database and send a message saying the bot joined
        await self.bot.get_channel(coreChannel).send(embed=(await embed.generate(f"I have joined {guild.name}",f"{guild.name} has {guild.member_count} members [{guild.id}]")))

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        # Remove all users in the guild and the guild information from both databases
        await db.removeMany("users",{"guild": guild.id})
        await db.remove("guilds",{"id": guild.id})
        # Send a message to the core channel saying the bot left
        await self.bot.get_channel(coreChannel).send(embed=(await embed.generate(f"I have left {guild.name}",f"{guild.name} had {guild.member_count} members :c")))
        # Get the current user count and update the DB
        currentUsers = await db.find("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})
        currentUsers["userCount"] = int(currentUsers["userCount"])-len(guild.members)
        await db.update("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")},{"userCount": currentUsers["userCount"]})

    @commands.Cog.listener()
    async def on_member_join(self,member):
        # Check if raid mode is enabled
        guildDB = await db.find("guilds",{"id": member.guild.id})
        if not guildDB["raid_mode"]:
            # Insert database object
            await db.insert("users",{"guild": member.guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "BYPASS_AUTOMOD": False,"ADMINISTRATOR": False}, "strikes": {}})
            # Check if Boundary is enabled, if so, message user with a link to verify
            if guildDB["boundary"]["enabled"]:
                boundaryID = uuid.uuid4()
                await db.insert("boundary",{"uuid": str(boundaryID), "guild": member.guild.id, "user": member.id, "verified": False})
                try:
                    await member.send(embed=(await embed.generate("Verification needed!",f"Verify here: https://grounddug.xyz/boundary/{str(boundaryID)}",0xffcc4d)))
                except:
                    if guildDB["channel"] != 0:
                        await self.bot.get_channel(guildDB["channel"]).send(embed=(await embed.generate(f"{member.name} was not sent a link!",f"Some manual verification may be required, but here is the link for them to verify:\nhttps://grounddug.xyz/boundary/{str(boundaryID)}")))
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
        # Get the current user count and update the DB
        currentUsers = await db.find("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})
        currentUsers["userCount"] = int(currentUsers["userCount"])+1
        await db.update("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")},{"userCount": currentUsers["userCount"]})

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        # Try needed because if guild is in raid mode, a object is never inserted
        try:
            await db.remove("users",{"guild": member.guild.id, "user": member.id})
        except Exception as e:
            logger.error(e)
        # Get the current user count and update the DB
        currentUsers = await db.find("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})
        currentUsers["userCount"] = int(currentUsers["userCount"])-1
        await db.update("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")},{"userCount": currentUsers["userCount"]})

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        prefix = await misc.getPrefix(self.bot,ctx)
        # Is the error a required argument?
        if isinstance(error,commands.MissingRequiredArgument):
            await embed.error(ctx,f"{error} - Use {prefix}help to find the required arguments")
        # Is the action the bot is trying forbidden?
        elif isinstance(error,discord.Forbidden):
            pass
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

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        # If the roles are not the same, check whether a role has been added or removed
        if before.roles != after.roles:
            roles = set(after.roles) - set(before.roles)
            removed = False
            if roles == set():
                removed = True
                roles = set(before.roles) - set(after.roles)
            # If the removed role has the administrator permissions, check whether the user is still an admin
            if removed and after.guild_permissions.administrator:
                return
            for role in roles:
                if role.permissions.administrator:
                    userObject = await db.find("users", {"guild": before.guild.id, "user": before.id})
                    for permission in userObject["permissions"]:
                        # If the new role is given, and has administrator, give GD_ADMINISTRATOR to user
                        if not removed:
                            userObject["permissions"][permission] = True
                        # If the user is no longer an admin, remove all permissions
                        else:
                            userObject["permissions"][permission] = False
                    # Update the database
                    await db.update("users",{"_id": userObject["_id"]},{"permissions": userObject["permissions"]})

    # @tasks.loop(seconds=10)
    # async def clearStorage(self):
    #     try:
    #         files = glob.glob("storage/")
    #         for f in files:
    #             os.remove(f)
    #     except:
    #         return

def setup(bot):
    bot.add_cog(Events(bot))
