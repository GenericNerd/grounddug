# GroundDug Boundary Cog

import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import uuid
import cogs.utils.db as db
import cogs.utils.checks as checks
import cogs.utils.embed as embed

# Boundary Class

class Boundary(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.boundary_check.start()
    
    @commands.group(name="boundary",description="Improve protection on your server")
    @checks.hasRequiredLevel(5)
    async def boundary(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"boundary")

    @commands.command(name="create",description="This is a testing command")
    async def test(self,ctx):
        bid = uuid.uuid4()
        await db.insert("boundary",{"uuid": str(bid), "guild": ctx.guild.id, "user": ctx.author.id, "verified": False})
        await ctx.send(await db.find("boundary",{"uuid": str(bid), "guild": ctx.guild.id, "user": ctx.author.id}))

    @tasks.loop(seconds=60)
    async def boundary_check(self):
        documents = await db.findAll("boundary",{"verified": True})
        async for document in documents:
            print(int(document["guild"]))
            guild = self.bot.get_guild(int(document["guild"]))
            print(guild)
            user = guild.get_member(int(document["user"]))
            guildDB = await db.find("guilds",{"id": int(document["guild"])})
            if guildDB["boundaryRole"] == None:
                print("No Boundary Role")
                try:
                    guildDB["logs"]
                except:
                    return
                else:
                    return await self.bot.get_channel(guildDB["logs"]).send(embed=embed.generate("Boundary role not set!",f"You forgot to set a Boundary role! As users verify, the role is not given.\n\n**User**: {user.mention}"))
            else:
                print("Boundary Role")
                await user.add_roles(id=guildDB["boundaryRole"])
                await user.send(embed=embed.generate("You have been verified!",f"You are now a verified in {guild.name}!"))
            await db.remove("boundary",{"_id": document["_id"]})

def setup(bot):
    bot.add_cog(Boundary(bot))
