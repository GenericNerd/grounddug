# GroundDug Developer Cog

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
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

    @developer.command(name="dbupdate",hidden=True)
    @checks.hasRequiredLevel(5)
    async def dbupdate(self,ctx):
        for guild in self.bot.guilds:
            guildObject = await db.find("guilds",{"id": guild.id})
            # Update database here
            guildObject["premium"] = {"isPremium": True, "expires": 1596758400}
            guildObject["automod"]["zalgo"] = 0
            guildObject["logging"] = {"commands": [], "events": []}
            if guildObject["channel"] != 0:
                await self.bot.get_channel(guildObject["channel"]).send(embed=(await embed.generate("You now have GroundDug Premium!",f"Your GroundDug Premium will expire on {datetime.utcfromtimestamp(guildObject['premium']['expires']).strftime('%A the %d of %B %Y at %H:%M:%S UTC')}",0x0b9e00)))
            # for user in guild.members:
            #     userObject = await db.find("users",{"guild": guild.id, "user": user.id})
            #     if userObject is None:
            #         continue
            #     if userObject["permissions"]["ADMINISTRATOR"]:
            #         userObject["permissions"]["BYPASS_AUTOMOD"] = True
            #     else:
            #         userObject["permissions"]["BYPASS_AUTOMOD"] = False
            #     # Send database update
            #     await db.update("users",{"_id": userObject["_id"]},userObject)
            await db.update("guilds",{"_id": guildObject["_id"]},guildObject)
        mainDB = await db.find("settings",{})
        mainDB["levels"] = {"1": [149252578125938690, 485472170760339477], "2": [], "3": [280584515045425152], "4": [], "5": [179292162037514241, 96269247411400704, 206309860038410240]}
        await db.update("settings",{"_id": mainDB["_id"]}, mainDB)
        await ctx.send("Done")

    @developer.command(name="test",hidden=True)
    @checks.hasRequiredLevel(5)
    async def test(self,ctx):
        await ctx.send(ctx.channel.history(limit=1).flatten())

def setup(bot):
    bot.add_cog(Developer(bot))
