#GroundDug Core Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
from cogs.utils.useful import getPrefix
import cogs.utils.embeds as embeds
from cogs.utils.dbhandle import dbUpdate
from cogs.utils.dbhandle import dbFind
from datetime import datetime
from bson.objectid import ObjectId

class core(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="help",description="[module] | Provides a list of commands and their usage")
    async def custom_help(self,ctx,module=""):
        prefix = await getPrefix(self.bot,ctx)
        msg = await embeds.generate("Help","Arguments in <> are required, [] are optional")
        modules = dict()
        modules["misc"] = []
        for command in self.bot.commands:
            if type(command) is discord.ext.commands.core.Group:
                modules[command.name.lower()] = command
            else:
                modules["misc"].append(command)
        if module == "":
            msg.description = "Please specify the modules you wish to look up"
            for key in sorted(modules.keys()):
                if key == "misc":
                    msg = await embeds.add_field(msg,f"💿 - Misc ({prefix}help misc)")
                elif key == "admin":
                    msg = await embeds.add_field(msg,f"🔨 - Admin ({prefix}help admin)")
                elif key == "logs":
                    msg = await embeds.add_field(msg,f"🔍 - Logs ({prefix}help logs)")
                elif key == "perms":
                    msg = await embeds.add_field(msg,f"🔧 - Perms ({prefix}help perms)")
            return await ctx.send(embed=msg)
        elif module != "":
            if module.lower() in modules.keys():
                modules = {module.lower(): modules[module.lower()]}
            else:
                msg.description = f"We could not find module {module}"
                return await ctx.send(embed=msg)
        for cog,cog_obj in modules.items():
            if cog.lower() in ["misc"]:
                for command in sorted(cog_obj, key=lambda o: f"{o.full_parent_name} {o.name}"):
                    split = command.description.split("|")
                    if len(split) >= 2 and not command.hidden:
                        msg = await embeds.add_field(msg,f"{prefix}{command.name} {split[0]}",split[1])
                    elif len(split) < 2 and not command.hidden:
                        msg = await embeds.add_field(msg,f"{prefix}{command.name}",command.description)
            else:
                for command in sorted(cog_obj.commands, key=lambda o: f"{o.full_parent_name} {o.name}"):
                    split = command.description.split("|")
                    if len(split) >= 2 and not command.hidden:
                        msg = await embeds.add_field(msg,f"{prefix}{command.full_parent_name} {command.name} {split[0]}",split[1])
                    elif len(split) < 2 and not command.hidden:
                        msg = await embeds.add_field(msg,f"{prefix}{command.full_parent_name} {command.name}",command.description)
        await ctx.send(embed=msg)

    @commands.command(name="invite",description="| Receive a private message with a link to invite GroundDug")
    async def invite(self,ctx):
        try:
            await ctx.author.send(embed=(await embeds.generate(f"Invite {self.bot.user.name}",f"[Click here](https://discordapp.com/oauth2/authorize?client_id=553602353962549249&scope=bot&permissions=8) to invite {self.bot.user.name} to your server")))
        except Exception as e:
            await ctx.send(embed=(await embeds.generate(f"Invite {self.bot.user.name}",f"[Click here](https://discordapp.com/oauth2/authorize?client_id=553602353962549249&scope=bot&permissions=8) to invite {self.bot.user.name} to your server")))

    @commands.command(name="userinfo",description="[user] | Obtain information about a user, such as the server join date, account age and server roles")
    async def userinfo(self,ctx,user:discord.Member=None):
        if user is None:
            user = ctx.author
        msg = await embeds.generate(f"{user.name}#{user.discriminator}",f"{user.mention} - {user.id}")
        msg = await embeds.add_field(msg,"Status",user.status,True)
        msg = await embeds.add_field(msg,"Server join date",f"{str(user.joined_at).split('.')[0]} - `{str(datetime.utcnow()-user.joined_at).split('.')[0]} ago`",True)
        msg = await embeds.add_field(msg,"Account age",f"{str(user.created_at).split('.')[0]} - `{str(datetime.utcnow()-user.created_at).split('.')[0]} ago`",True)
        msg.set_thumbnail(url=user.avatar_url)
        roles = "@everyone"
        for role in user.roles:
            if role.name != "@everyone":
                roles = roles + f", {role.name}"
        if roles == "@everyone":
            msg = await embeds.add_field(msg,"Roles","No significant roles")
        else:
            msg = await embeds.add_field(msg,"Roles",roles)
        await ctx.send(embed=msg)

    @commands.command(name="botinfo",description="| Returns information about the bot, including guilds, users and shard latency information")
    async def botinfo(self,ctx):
        guildCount = 0
        userCount = 0
        version = await dbFind("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})
        version = version["version"]
        for guild in self.bot.guilds:
            guildCount += 1
            for user in guild.members:
                userCount += 1
        msg = await embeds.generate("Bot information",f"Guilds: **{guildCount}**\nUsers: **{userCount}**\nDiscord.py Version: {discord.__version__}\n{self.bot.user.name} version: {version}")
        for shard in self.bot.latencies:
            if round(shard[1]*100) < 100:
                msg = await embeds.add_field(msg,f"Shard {shard[0]}",f"<:status_online:437236812382208000> Latency: **{round(shard[1]*100)}**ms")
            else:
                msg = await embeds.add_field(msg,f"Shard {shard[0]}",f"<:status_dnd:437236811664982016> Latency: **{round(shard[1]*100)}**ms")
        await ctx.send(embed=msg)

    @commands.command(name="setprefix",description="<prefix> | Set a custom prefix for your guild locally. The bot default is `g!`")
    @checks.has_GD_permission("ADMINISTRATOR")
    async def setprefix(self,ctx,prefix):
        await dbUpdate("guilds",{"id": ctx.guild.id},{"prefix": prefix})
        await ctx.send(embed=(await embeds.generate("Prefix changed!",f"`{prefix}` is now the prefix for this guild")))

def setup(bot):
    bot.add_cog(core(bot))