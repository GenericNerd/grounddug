# GroundDug Logs Cog

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.misc as misc

async def sendLog(self,ctx,module):
    guild = await db.find("guilds",{"id": ctx.guild.id})
    if guild["logs"][module]:
        # Get the current log channel and send a message
        channel = self.bot.get_channel(guild["channel"])
        try:
            await channel.send(embed=(await embed.generate(f"{ctx.author.name} - #{ctx.channel.name}",f"Ran command `{ctx.message.content}`",0x002fff)))
        except:
            pass

# async def sendHumanLog(self,ctx,)

async def logModuleChange(self,ctx,changeTo,module=None):
    # Check whether log module is to enable or disable
    if changeTo is True:
        stateChange = "enable"
    else:
        stateChange = "disable"
    if module is not None:
        module = module.lower()
    # Get the current guild settings
    guild = await db.find("guilds", {"id": ctx.guild.id})
    # If no module was passed, step through all the modules that can be changed
    # to the state changeTo and list them in an embed field
    if module is None:
        prefix = await misc.getPrefix(self.bot,ctx)
        msg = await embed.generate(f"Modules to {stateChange}",None)
        # Check every item in logs, if the key is not changeTo, add an embed field
        for item,key in guild["logs"].items():
            if key is not changeTo:
                msg = await embed.add_field(msg,item.capitalize(),f"Run `{prefix}logs {stateChange} {item}` to change")
        await ctx.send(embed=msg)
    else:
        # If a module is passed, check if the module is actually valid, whether
        # it can be changed and change it. Raise an error either is not true
        if module in guild["logs"] and guild["logs"][module] is not changeTo:
            guild["logs"][module] = changeTo
            # Update the database and send a message confirming change
            await db.update("guilds",{"_id": guild["_id"]},guild)
            await ctx.send(embed=(await embed.generate("Updated logging settings",f"`{module.capitalize()}` event logging is now {stateChange}d")))
        else:
            await embed.error(ctx,f"Module invalid, or already {stateChange}d")

class Logs(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="logs",description="Logging commands")
    @commands.guild_only()
    async def logs(self,ctx):
        # Send a help perms command if no subcommand invoked
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"logs")
        else:
            await sendLog(self,ctx,"logs")

    @logs.command(name="setchannel",description="[channel] | Set the channel to which all command logs will be sent to on the guild")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def setchannel(self,ctx,channel:discord.TextChannel=None):
        # Get the current guild object
        guild = await db.find("guilds",{"id": ctx.guild.id})
        # If no channel was parsed, send the current channel, if no channel is set,
        # tell the user how to change the logs channel
        if channel is None:
            prefix = await misc.getPrefix(self.bot,ctx)
            if guild["channel"] == 0:
                await ctx.send(embed=(await embed.generate("Logging channel",f"No current logging channel, set one by using `{prefix}logs setchannel <channel>`")))
            else:
                await ctx.send(embed=(await embed.generate("Logging channel",f"<#{guild['channel']}> is the current logging channel")))
        else:
            # Update the database and alert the user the change was successful
            await db.update("guilds",{"_id": guild["_id"]},{"channel": channel.id})
            await ctx.send(embed=(await embed.generate("Logging channel changed",f"{channel.mention} is now the new guild logging channel.")))

class Logging(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    # {"logging": {"commands": ["perms", "boundary", "automod", "admin", "mod"], "events": ["message", "role", "channel", "user"]}}
    @commands.Cog.listener()
    async def on_command(self,ctx):
        guildDB = await db.find("guilds",{"id": ctx.guild.id})
        print(guildDB["logging"]["commands"])
        if ctx.command.parent in guildDB["logging"]["commands"]:
            await ctx.send("lol")

def setup(bot):
    bot.add_cog(Logs(bot))
    bot.add_cog(Logging(bot))