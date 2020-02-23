#GroundDug Administrator Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embeds as embeds
from cogs.utils.dbhandle import dbUpdate
from cogs.utils.dbhandle import dbFind
from bson.objectid import ObjectId

class admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="admin",description="Guild administrative commands")
    async def admin(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"admin")
        else:
            guild = await dbFind("guilds",{"id": ctx.guild.id})
            if guild["logs"]["admin"]:
                channel = self.bot.get_channel(guild["channel"])
                try:
                    await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
                except:
                    pass

    @admin.command(name="raid",description="<state> | Enables or disables raid mode")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def raid(self,ctx,state=None):
        guild = await dbFind("guilds",{"id": ctx.guild.id})
        if state == None:
            await ctx.send(embed=(await embeds.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode is currently set to `{guild['raid_mode']}`")))
        elif state.lower() == "true":
            await dbUpdate("guilds",{"id": ctx.guild.id},{"raid_mode": True})
            await ctx.send(embed=(await embeds.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `enabled` by {ctx.author.mention}")))
        elif state.lower() == "false":
            await dbUpdate("guilds",{"id": ctx.guild.id},{"raid_mode": False})
            await ctx.send(embed=(await embeds.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `disabled` by {ctx.author.mention}")))
        else:
            await embeds.error(ctx,"Raid Mode state needs to be either `True` or `False`")

    @admin.command(name="blacklistadd",description="<channel> | Add a channel where commands cannot be ran")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def blacklistAdd(self,ctx,channel:discord.TextChannel):
        dbObject = await dbFind("guilds",{"id": ctx.guild.id})
        dbObject["blacklistChannels"].append(channel.id)
        await ctx.send(embed=(await embeds.generate("Channel added",f"#{channel.mention} will now ignore commands sent to it")))
        await dbUpdate("guilds",{"id": ctx.guild.id},dbObject)

    @admin.command(name="blacklistremove",description="<channel> | Remove a channel where commands cannot be ran")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def blacklistRemove(self,ctx,channel:discord.TextChannel):
        dbObject = await dbFind("guilds",{"id": ctx.guild.id})
        dbObject["blacklistChannels"].remove(channel.id)
        await ctx.send(embed=(await embeds.generate("Channel added",f"{channel.mention} will no longer ignore commands sent to it")))
        await dbUpdate("guilds",{"id": ctx.guild.id},dbObject)

    @admin.command(name="setprefix",description="<prefix> | Set a custom prefix for your guild locally. The bot default is `g!`")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def setprefix(self,ctx,prefix):
        await dbUpdate("guilds",{"id": ctx.guild.id},{"prefix": prefix})
        await ctx.send(embed=(await embeds.generate("Prefix changed!",f"`{prefix}` is now the prefix for this guild")))

def setup(bot):
    bot.add_cog(admin(bot))