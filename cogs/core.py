# GroundDug Core Cog

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.misc as misc
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.levels as levels
from datetime import datetime
from bson.objectid import ObjectId

class Core(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(name="help",description="[module] | Provides a list of commands and how to use them")
    async def custom_help(self,ctx,module=""):
        # Get the current guild prefix
        prefix = await misc.getPrefix(self.bot,ctx)
        msg = await embed.generate("Help","Arguments in <> are required, arguments in [] are optional")
        # Create a modules dictionary and add a misc key, for commands not in a cog
        modules = {}
        modules["misc"] = []
        # For each command, check whether it is in a group and add it to the dictionary key
        # Else, append it to the misc array in the modules dictionary
        for command in self.bot.commands:
            if type(command) is discord.ext.commands.core.Group:
                modules[command.name.lower()] = command
            else:
                modules["misc"].append(command)
        # If the module requested was none, provide the cogs
        if module == "":
            # Change embed description, add a field with each cog, return a message
            msg.description = "Please specify the modules you wish to look up"
            msg = await embed.add_field(msg,f"💿 - Misc ({prefix}help misc)\n🔨 - Mod ({prefix}help mod)\n⚙ - Admin ({prefix}help admin)\n🔍 - Logs ({prefix}help logs)\n🔧 - Perms ({prefix}help perms)\n🤖 - Auto-Mod - ({prefix}help automod)\n🚧 - Boundary ({prefix}help boundary)")
            return await ctx.send(embed=msg)
        elif module != "":
            # If the module is in fact a cog
            if module.lower() in modules.keys():
                # Variable modules is a dictionary with the key of module with
                # the value of the previous modules dictionary, with all commands
                # specified
                modules = {module.lower(): modules[module.lower()]}
            else:
                msg.description = f"Module {module} was not found"
                return await ctx.send(embed=msg)
        for cog, cogObject in modules.items():
            # Split command descriptions by |, left of this is usage, right is description
            if cog.lower() in ["misc"]:
                # Step through each command, iterating through the full name of the command object
                for command in sorted(cogObject, key=lambda obj: f"{obj.full_parent_name} {obj.name}"):
                    commandDesc = command.description.split("|")
                    # If the command is not hidden, create an embed field, based on how command description was split
                    if len(commandDesc) >= 2 and not command.hidden:
                        msg = await embed.add_field(msg,f"{prefix}{command.name} {commandDesc[0]}",commandDesc[1])
                    elif len(commandDesc) < 2 and not command.hidden:
                        msg = await embed.add_field(msg,f"{prefix}{command.name}",command.description)
            else:
                # Repeat the same from above, but with full command name instead
                # Possible future optimisations here?
                for command in sorted(cogObject.commands, key=lambda obj: f"{obj.full_parent_name} {obj.name}"):
                    commandDesc = command.description.split("|")
                    if command.full_parent_name == "mod":
                        if len(commandDesc) >= 2 and not command.hidden:
                            msg = await embed.add_field(msg,f"{prefix}{command.name} {commandDesc[0]}",commandDesc[1])
                        elif len(commandDesc) < 2 and not command.hidden:
                            msg = await embed.add_field(msg,f"{prefix}{command.name}",command.description)
                    else:
                        if len(commandDesc) >= 2 and not command.hidden:
                            msg = await embed.add_field(msg,f"{prefix}{command.full_parent_name} {command.name} {commandDesc[0]}",commandDesc[1])
                        elif len(commandDesc) < 2 and not command.hidden:
                            msg = await embed.add_field(msg,f"{prefix}{command.full_parent_name} {command.name}",command.description)
        await ctx.send(embed=msg)

    @commands.command(name="invite",description="| Receive a message with an invite link for GroundDug")
    async def invite(self,ctx):
        # If member has DMs enabled, send them a message, else, send a message in the channel
        try:
            await ctx.author.send(embed=(await embed.generate(f"Invite {self.bot.user.name}",f"[Click here](https://discordapp.com/oauth2/authorize?client_id=553602353962549249&scope=bot&permissions=8) to invite {self.bot.user.name} to your server")))
        except:
            await ctx.send(embed=(await embed.generate(f"Invite {self.bot.user.name}",f"[Click here](https://discordapp.com/oauth2/authorize?client_id=553602353962549249&scope=bot&permissions=8) to invite {self.bot.user.name} to your server")))

    @commands.command(name="userinfo",description="[user] | Get information on a user, such as server join date, account age etc.")
    async def userinfo(self,ctx,user:discord.Member=None):
        # If no user passed, use the author
        if user is None:
            user = ctx.author
        if ctx.guild is None:
            for guild in self.bot.guilds:
                try:
                    user = guild.get_member(user.id)
                except:
                    pass
        msg = await embed.generate(f"{user.name}#{user.discriminator}",f"{user.mention} - `{user.id}`")
        # Check the status, add an emoji representing icon
        # Possible future optimisations here?
        # In DM's, returning a User instead of Member object
        if str(user.status) == "online":
            msg = await embed.add_field(msg,"Status","<:status_online:679095420605038617>",True)
        elif str(user.status) == "idle":
            msg = await embed.add_field(msg,"Status","<:status_idle:679095420819079188>",True)
        elif str(user.status) == "dnd":
            msg = await embed.add_field(msg,"Status","<:status_dnd:679095420626141214>",True)
        elif str(user.status) == "streaming":
            msg = await embed.add_field(msg,"Status","<:status_streaming:679095420944777227>",True)
        else:
            msg = await embed.add_field(msg,"Status","<:status_offline:679095420684730368>",True)
        # Try to get the server join date, may fail if command is ran in DMs
        if ctx.guild is not None:
            try:
                msg = await embed.add_field(msg,"Server join date",f"{str(user.joined_at).split('.')[0]} - `{str(datetime.utcnow()-user.joined_at).split('.')[0]} ago`",True)
            except:
                pass
        msg = await embed.add_field(msg,"Account age",f"{str(user.created_at).split('.')[0]} - `{str(datetime.utcnow()-user.created_at).split('.')[0]} ago`",True)
        msg.set_thumbnail(url=user.avatar_url)
        # Iterate through user roles, if not @everyone, add it to the roles variable
        if ctx.guild is not None:
            roles = ""
            for role in user.roles:
                roles += f"- {role.name}"
            # If roles is @everyone, user has no special roles, otherwise, send the roles
            if roles == "- @everyone":
                msg = await embed.add_field(msg,"Roles","No significant roles")
            else:
                msg = await embed.add_field(msg,"Roles",roles)
        await ctx.send(embed=msg)

    @commands.command(name="botinfo",description="| Returns information about the bot, including guilds, users and shard latency information")
    async def botinfo(self,ctx):
        guildCount = 0
        userCount = 0
        # Find the settings for GD, get the current version
        version = await db.find("settings",{"_id": ObjectId("5e18fd4d123a50ef10d8332e")})
        version = version["version"]
        for guild in self.bot.guilds:
            guildCount += 1
            userCount += len(guild.members)
        # User text file write would go here, better way of doing this?
        msg = await embed.generate("Bot information",f"Guilds: **{guildCount}**\nUsers: **{userCount}**\nDiscord.py Version: {discord.__version__}\n{self.bot.user.name} version: {version}")
        for shard in self.bot.latencies:
            # If the latency is less than 100ms
            if round(shard[1]*100) < 100:
                msg = await embed.add_field(msg,f"Shard {shard[0]}",f"<:status_online:679095420605038617> Latency: **{round(shard[1]*100)}**ms")
            else:
                msg = await embed.add_field(msg,f"Shard {shard[0]}",f"<:status_dnd:679095420626141214> Latency: **{round(shard[1]*100)}**ms")
        await ctx.send(embed=msg)

    @commands.command(name="badges",description="[user] | Returns a list of the badges a user has in relation to the bot")
    async def badges(self,ctx,user:discord.Member=None):
        # If no user given, use the author
        if user == None:
            user = ctx.author
        # Get the current user level
        level = await levels.getLevel(user)
        msg = await embed.generate(f"@{user.name}#{user.discriminator} - {self.bot.user.name} Badges",None)
        # Add a field best related to the level
        # Possible improvements here?
        if level == 5:
            msg = await embed.add_field(msg,"⚙️ - Level 5","`These users are the creators and developers of the bot`")
        elif level == 4:
            pass
        elif level == 3:
            msg = await embed.add_field(msg,"🔨 - Level 3","`These users are moderators to the bot. They are trusted to handle bot issues`")
        elif level == 2:
            pass
        elif level == 1:
            msg = await embed.add_field(msg,"🔖 - Level 1","`These users help find and report bugs to the developers in unstable releases`")
        else:
            msg = await embed.add_field(msg,"No badges")
        await ctx.send(embed=msg)

def setup(bot):
    bot.add_cog(Core(bot))
