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
    # {"logging": {"commands": ["perms", "boundary", "automod", "admin", "mod"], "events": ["message", "role", "nicknames", "channel"]}}

    @commands.Cog.listener()
    async def on_command(self,ctx):
        guildDB = await db.find("guilds",{"id": ctx.guild.id})
        if str(ctx.command.parent) in guildDB["logging"]["commands"]:
            if str(ctx.command.parent) == "mod":
                return await self.bot.get_channel(guildDB["channel"]).send(f"🔨 - {ctx.author.name}: #{ctx.channel.name}",f"Ran moderator command `{ctx.message.content}`",0xff8400)
            await self.bot.get_channel(guildDB["channel"]).send(embed=(await embed.generate(f"{ctx.author.name}: #{ctx.channel.name}",f"Ran command `{ctx.message.content}`")))

    # Message specific events

    @commands.Cog.listener()
    async def on_message_edit(self,before,after):
        if before.content == after.content:
            return
        guildDB = await db.find("guilds",{"id": before.guild.id})
        if "message" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"{before.author.name} edited a message!",None,0xff9900)
            msg = await embed.add_field(msg,"Channel",f"{before.channel.mention}\n[Jump to message]({before.jump_url})")
            msg = await embed.add_field(msg,"Previous message",before.content)
            msg = await embed.add_field(msg,"Message now",after.content)
            await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        guildDB = await db.find("guilds",{"id": message.guild.id})
        if "message" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"{message.author.name} deleted a message",f"Message was deleted from {message.channel.mention}",0xf00000)
            msg = await embed.add_field(msg,"Content",message.content)
            try:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)
            except:
                pass

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        guildDB = await db.find("guilds",{"id": before.guild.id})
        if before.roles != after.roles and "role" in guildDB["logging"]["events"]:
            if list(set(after.roles)-set(before.roles)) == []:
                roleDif = list(set(before.roles)-set(after.roles))
                roleDif.append("removed")
            else:
                roleDif = list(set(after.roles)-set(before.roles))
                roleDif.append("added")
            msg = await embed.generate(f"{before.name} was {roleDif[1]} a role!",None,0x9e0000 if roleDif[1] == "removed" else 0x0b9e00)
            msg = await embed.add_field(msg,f"Role {roleDif[1]}",roleDif[0].mention)
            await self.bot.get_channel(guildDB["channel"]).send(embed=msg)
        elif before.display_name != after.display_name and "nicknames" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"{before.name} changed their name!",None,0x10009e)
            msg = await embed.add_field(msg,"Name before",before.display_name)
            msg = await embed.add_field(msg,"Name now",after.display_name)
            await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    # Role specific events

    @commands.Cog.listener()
    async def on_guild_role_create(self,role):
        guildDB = await db.find("guilds",{"id": role.guild.id})
        if "role" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"Role {role.name} was created!",None,0x0b9e00)
            permissions = dict()
            permsString = ""
            for permission in role.permissions:
                if permission[1]:
                    permissions[permission[0]] = permission[1]
            for permission, key in permissions.items():
                permsString += " " + str(permission).replace('_',' ').title() + " - <:check:679095420202516480>\n"
            permsString = permsString[:-1]
            msg = await embed.add_field(msg, "Role permissions",permsString)
            await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    @commands.Cog.listener()
    async def on_guild_role_delete(self,role):
        guildDB = await db.find("guilds",{"id": role.guild.id})
        if "role" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"Role {role.name} was deleted!",None,0x9e0000)
            await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    @commands.Cog.listener()
    async def on_guild_role_update(self,before,after):
        guildDB = await db.find("guilds",{"id": before.guild.id})
        if "role" in guildDB["logging"]["events"]:
            if list(set(after)-set(before)) == []:
                roleDif = list(set(before)-set(after))
                roleDif.append("removed")
            else:
                roleDif = list(set(after)-set(before))
                roleDif.append("added")
            print(f"{roleDif=}")

    # Channel specific events

    @commands.Cog.listener()
    async def on_guild_channel_create(self,channel):
        guildDB = await db.find("guilds",{"id": channel.guild.id})
        if "channel" in guildDB["logging"]["events"]:
            # Pass the channel
            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self,channel):
        guildDB = await db.find("guilds",{"id": channel.guild.id})
        if "channel" in guildDB["logging"]["events"]:
            # Pass the channel
            pass

    @commands.Cog.listener()
    async def on_guild_channel_update(self,before,after):
        guildDB = await db.find("guilds",{"id": before.guild.id})
        if "channel" in guildDB["logging"]["events"]:
            # Pass the before and after channels
            pass

def setup(bot):
    bot.add_cog(Logs(bot))
    bot.add_cog(Logging(bot))