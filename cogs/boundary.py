# GroundDug Boundary Cog

import discord
from discord.ext import commands
import asyncio
import uuid
import cogs.utils.db as db
import cogs.utils.checks as checks

# Boundary Class

class Boundary(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(name="test",description="This is a testing command")
    @checks.hasRequiredLevel(5)
    async def test(self,ctx):
        bid = uuid.uuid4()
        await db.insert("boundary",{"uuid": bid, "guild": ctx.guild.id, "user": ctx.author.id})
        await ctx.send(await db.find("boundary",{"guild": ctx.guild.id, "user": ctx.author.id}))

def setup(bot):
    bot.add_cog(Boundary(bot))