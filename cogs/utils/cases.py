# GroundDug Case Handler

import discord
from discord.ext import commands
import asyncio
import cogs.utils.db as db

async def createCase(guild:discord.Guild,user:discord.Member,moderator:discord.Member,action,reason=None):
    """
    Action must be in verb form
    """
    # Find the guild and user database object
    guildDB = await db.find("guilds",{"id": guild.id})
    userDB = await db.find("users",{"guild": guild.id, "user": user.id})
    # Add a strike with the current case number, giving moderator and reason
    # Reason includes the action that was performed 
    userDB["strikes"][str(guildDB["cases"])] = {"moderator": moderator.id, "reason": f"{action.capitalize()} by {moderator.name} for {reason}"}
    # Update database with an increased case numbed and the new user strike
    await db.update("guilds",{"_id": guildDB["_id"]},{"cases": guildDB["cases"]+1})
    await db.update("users",{"_id": userDB["_id"]},{"strikes": userDB["strikes"]})
