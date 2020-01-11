#GroundDug Developer Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embeds as embeds

class dev(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.group(name="developer",aliases=["dev"],hidden=True)
    @checks.has_required_level(5)
    async def developer(self,ctx):
        if ctx.invoked_subcommand is None:
            await embeds.error(ctx,"NO INVOKED SUBCOMMAND")

    @developer.command(name="eval",hidden=True)
    async def eval(self,ctx,cmd:str):
        try:
            result = (await eval(cmd))
        except:
            result = (eval(cmd))
        await ctx.send(result)

    @developer.command(name="modulereload",aliases=["mreload"],hidden=True)
    async def reload(self,ctx,module):
        self.bot.unload_extension(f"cogs.{module}")
        self.bot.load_extension(f"cogs.{module}")
        await ctx.send(embed=(await embeds.generate(f"Module {module} reloaded",None)))
    
    @developer.command(name="moduleload",aliases=["mload"],hidden=True)
    async def load(self,ctx,module):
        self.bot.load_extension(f"cogs.{module}")
        await ctx.send(embed=(await embeds.generate(f"Module {module} loaded",None)))

    @developer.command(name="moduleunload",aliases=["munload"],hidden=True)
    async def unload(self,ctx,module):
        self.bot.unload_extension(f"cogs.{module}")
        await ctx.send(embed=(await embeds.generate(f"Module {module} loaded",None)))

def setup(bot):
    bot.add_cog(dev(bot))