# GroundDug Developer Cog

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.levels as levels
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.cases as cases
import cogs.utils.logger as logger
import cogs.utils.misc as misc

class Developer(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="developer",aliases=["dev"])
    async def developer(self,ctx):
        if ctx.invoked_subcommand is None:
            await embed.error(ctx,"No invoked subcommand")
    
    @developer.command(name="eval",hidden=True)
    @checks.hasRequiredLevel(5)
    async def eval(self,ctx,cmd:str):
        try:
            result = (await eval(cmd))
        except:
            result = (eval(cmd))
        await ctx.send(result)

    @developer.command(name="modulereload",aliases=["mreload"],hidden=True)
    @checks.hasRequiredLevel(5)
    async def reload(self,ctx,module):
        self.bot.unload_extension(f"cogs.{module}")
        self.bot.load_extension(f"cogs.{module}")
        await ctx.send(embed=(await embed.generate(f"Module {module} reloaded",None)))
    
    @developer.command(name="moduleload",aliases=["mload"],hidden=True)
    @checks.hasRequiredLevel(5)
    async def load(self,ctx,module):
        self.bot.load_extension(f"cogs.{module}")
        await ctx.send(embed=(await embed.generate(f"Module {module} loaded",None)))

    @developer.command(name="moduleunload",aliases=["munload"],hidden=True)
    @checks.hasRequiredLevel(5)
    async def unload(self,ctx,module):
        self.bot.unload_extension(f"cogs.{module}")
        await ctx.send(embed=(await embed.generate(f"Module {module} unloaded",None)))

    @developer.command(name="invite",hidden=True)
    @checks.hasRequiredLevel(3)
    async def guild_invite(self,ctx,gid: int):
        guild = discord.utils.get(self.bot.guilds, id=gid)
        for channel in guild.text_channels:
            try:
                invite = await channel.create_invite(reason="Developer request")
            except:
                continue
            finally:
                return await ctx.send(embed=(await embed.generate(f"{guild.name} invite",invite.url)))

def setup(bot):
    bot.add_cog(Developer(bot))