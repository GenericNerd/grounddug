#GroundDug Logs Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embeds as embeds
from cogs.utils.dbhandle import dbFind
from cogs.utils.dbhandle import dbInsert
from cogs.utils.dbhandle import dbUpdate
import cogs.utils.useful as useful

async def moduleLogChange(self,ctx,boolean,status,module=None):
	if module == None:
		prefix = await useful.getPrefix(self.bot,ctx)
		msg = await embeds.generate("Modules",None)
		for item,result in (await dbFind("guilds", {"id": ctx.guild.id})).items():
			if result == boolean and len(item.split("_log")) > 1:
				item = item.split("_log")[0]
				msg = embeds.add_field(msg,item,f"Run `{prefix}logs {status} {item}` to log")
		await ctx.send(embed=msg)
	else:
		for item,result in (await db.dbFind("guilds", {"id": ctx.guild.id})).items():
			valid = False
			if result == boolean and module==item.split("_log")[0]:
				valid = True
				break
		if valid == False:
			await embeds.error(ctx,"INVALID MODULE")
		else:
			await dbUpdate("guilds",{"id": ctx.guild.id},{f"{module}_log": not boolean})
			if boolean == False:
				await ctx.send(embed=(await embeds.generate("Updated logging settings",f"`{module}` events will now be logged")))
			else:
				await ctx.send(embed=(await embeds.generate("Updated logging settings",f"`{module}` events will now not be logged")))

class logs(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="logs",description="Logging commands")
    async def logs(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"logs")
        else:
            guild = await dbFind("guilds",{"id": ctx.guild.id})
            if guild["logs_log"]:
                channel = self.bot.get_channel(guild["channel"])
                await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))

    @logs.command(name="setup",hidden=True)
    @checks.has_required_level(5)
    async def setup(self,ctx):
        msg = await embeds.generate("The following guilds were added to the database",None)
        for guild in self.bot.guilds:
            data = {"id": guild.id,
                "prefix": "g!",
                "channel": 0,
                "misc_log": False,
                "logs_log": False,
                "admin_log": False,
                "perms_log": False,
                "advertising_log": False,
                "delete_log": False,
                "raid_mode": False}
            if (await dbFind("guilds",{"id": guild.id})) == None:
                result = await dbInsert("guilds",data)
                msg = embeds.add_field(msg,f"Created {guild.name}",f"`{guild.id}`")
        await ctx.send(embed=msg)
    
    @logs.command(name="setchannel",description="<channel> | Set the channel to which all command logs will be sent to on the guild")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def setchannel(self,ctx,channel:discord.TextChannel=None):
        if channel == None:
            prefix = await useful.getPrefix(self.bot,ctx)
            guild = await dbFind("guilds",{"id": ctx.guild.id})
            if guild["channel"] == 0:
                await ctx.send(embed=(await embeds.generate("Logging channel",f"No current logging channel, set one by using `{prefix}logs setchannel <channel>`")))
            else:
                await ctx.send(embed=(await embeds.generate("Logging channel",f"<#{channel}> is the current logging channel")))
        else:
            await dbUpdate("guilds",{"id": ctx.guild.id},{"channel": channel.id})
            await ctx.send(embed=(await embeds.generate("Logging channel changed",f"{channel.mention} will now have logs posted to it")))
    
    @logs.command(name="enable",description="[module] | Enables logging of a specific module within the guild")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def enable(self,ctx,module):
        await moduleLogChange(self,ctx,False,"enable",module)

    @logs.command(name="disable",description="[module] | Disables logging of a specific module within the guild")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def disable(self,ctx,module):
        await moduleLogChange(self,ctx,True,"disable",module)

def setup(bot):
    bot.add_cog(logs(bot))