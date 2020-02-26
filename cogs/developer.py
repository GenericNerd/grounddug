#GroundDug Developer Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embeds as embeds
import cogs.utils.dbhandle as dbhandle
import cogs.utils.levels as levels
import cogs.utils.dbhandle as db

class dev(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.group(name="developer",aliases=["dev"],hidden=True)
    async def developer(self,ctx):
        if ctx.invoked_subcommand is None:
            await embeds.error(ctx,"NO INVOKED SUBCOMMAND")

    @developer.command(name="eval",hidden=True)
    @checks.has_required_level(5)
    async def eval(self,ctx,cmd:str):
        try:
            result = (await eval(cmd))
        except:
            result = (eval(cmd))
        await ctx.send(result)

    @developer.command(name="modulereload",aliases=["mreload"],hidden=True)
    @checks.has_required_level(3)
    async def reload(self,ctx,module):
        self.bot.unload_extension(f"cogs.{module}")
        self.bot.load_extension(f"cogs.{module}")
        await ctx.send(embed=(await embeds.generate(f"Module {module} reloaded",None)))
    
    @developer.command(name="moduleload",aliases=["mload"],hidden=True)
    @checks.has_required_level(3)
    async def load(self,ctx,module):
        self.bot.load_extension(f"cogs.{module}")
        await ctx.send(embed=(await embeds.generate(f"Module {module} loaded",None)))

    @developer.command(name="moduleunload",aliases=["munload"],hidden=True)
    @checks.has_required_level(3)
    async def unload(self,ctx,module):
        self.bot.unload_extension(f"cogs.{module}")
        await ctx.send(embed=(await embeds.generate(f"Module {module} loaded",None)))

    @developer.command(name="invite",hidden=True)
    @checks.has_required_level(3)
    async def guild_invite(self,ctx,gid: int):
        guild = discord.utils.get(self.bot.guilds, id=gid)
        for channel in guild.text_channels:
            try:
                invite = await channel.create_invite(reason="Developer request")
            except:
                continue
            finally:
                return await ctx.send(embed=(await embeds.generate(f"{guild.name} invite",invite.url)))

    @developer.command(name="dbupdate",hidden=True)
    @checks.has_required_level(5)
    async def dbupdate(self,ctx):
        for guild in self.bot.guilds:
            dbObject = await db.dbFind("guilds",{"id": guild.id})
            # DB UPDATES BELOW
            dbObject["automod"]["unshortenURL"] = False
            # SEND DB UPDATE
            await db.dbUpdate("guilds",{"id": guild.id},dbObject)

def setup(bot):
    bot.add_cog(dev(bot))