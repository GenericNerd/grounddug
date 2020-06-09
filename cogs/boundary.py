# GroundDug Boundary Cog

import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import uuid
import cogs.utils.db as db
import cogs.utils.checks as checks

# Boundary Class

class Boundary(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.boundary_check.start()
    
    @commands.command(name="test",description="This is a testing command")
    @checks.hasRequiredLevel(5)
    async def test(self,ctx):
        bid = uuid.uuid4()
        await db.insert("boundary",{"uuid": str(bid), "guild": ctx.guild.id, "user": ctx.author.id, "verified": False})
        await ctx.send(await db.find("boundary",{"guild": ctx.guild.id, "user": ctx.author.id}))

    @tasks.loop(seconds=60)
    async def boundary_check(self):
        cursor = await db.returnCursor()
        async for document in cursor.find({}):
            print(document)

def setup(bot):
    bot.add_cog(Boundary(bot))
