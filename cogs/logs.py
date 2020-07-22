# GroundDug Logs Cog

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.misc as misc
import numpy as np

loggingModules = {"commands": ["perms", "boundary", "automod", "admin", "mod"], "events": ["message", "role", "channel", "member", "nicknames"]}

async def sendLog(self,ctx,module):
    guild = await db.find("guilds",{"id": ctx.guild.id})
    if guild["logs"][module]:
        # Get the current log channel and send a message
        channel = self.bot.get_channel(guild["channel"])
        try:
            await channel.send(embed=(await embed.generate(f"{ctx.author.name} - #{ctx.channel.name}",f"Ran command `{ctx.message.content}`",0x002fff)))
        except:
            pass

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

    @logs.command(name="enable",description="[module] | Enable logging features to be enabled")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def enable(self,ctx,module=None):
        if module == None:
            guildDB = await db.find("guilds",{"id": ctx.guild.id})
            prefix = await misc.getPrefix(self.bot,ctx)
            msg = await embed.generate("Disabled Logging Modules","Here are the logging modules that you can current disabled")
            for modules in loggingModules["commands"]:
                if modules not in guildDB["logging"]["commands"]:
                    msg = await embed.add_field(msg,f"Command module - {modules}",f"Enable with `{prefix}logs enable {modules}`")
            for modules in loggingModules["events"]:
                if modules not in guildDB["logging"]["events"]:
                    msg = await embed.add_field(msg,f"Event module - {modules}",f"Enable with `{prefix}logs enable {modules}`")
            return await ctx.send(embed=msg)
        elif module not in loggingModules["commands"] and module not in loggingModules["events"]:
            return await ctx.invoke(self.bot.get_command("logs"),"enable")
        else:
            guildDB = await db.find("guilds",{"id": ctx.guild.id})
            if module in loggingModules["commands"] and module not in loggingModules["events"] and module not in guildDB["logging"]["commands"]:
                guildDB["logging"]["commands"].append(module)
                await db.update("guilds",{"id": ctx.guild.id},guildDB["logging"])
                return await ctx.send(embed=(await embed.generate(f"Logging module \"{module}\" enabled",None)))
            elif module in loggingModules["events"] and module not in loggingModules["commands"] and module not in guildDB["logging"]["events"]:
                guildDB["logging"]["events"].append(module)
                await db.update("guilds",{"id": ctx.guild.id},guildDB["logging"])
                return await ctx.send(embed=(await embed.generate(f"Logging module \"{module}\" enabled",None)))
            else:
                return await ctx.send(embed=(await embed.generate(f"Logging module \"{module}\" is already enabled!",None)))

    @logs.command(name="disable",description="[module] | Disable logging features to be enabled")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def disable(self,ctx,module=None):
        if module == None:
            guildDB = await db.find("guilds",{"id": ctx.guild.id})
            prefix = await misc.getPrefix(self.bot,ctx)
            msg = await embed.generate("Enabled Logging Modules","Here are the logging modules that you can current enabled")
            for modules in loggingModules["commands"]:
                if modules in guildDB["logging"]["commands"]:
                    msg = await embed.add_field(msg,f"Command module - {modules}",f"Disable with `{prefix}logs disable {modules}`")
            for modules in loggingModules["events"]:
                if modules in guildDB["logging"]["events"]:
                    msg = await embed.add_field(msg,f"Event module - {modules}",f"Disable with `{prefix}logs disable {modules}`")
            return await ctx.send(embed=msg)
        elif module not in loggingModules["commands"] and module not in loggingModules["events"]:
            return await ctx.invoke(self.bot.get_command("logs"),"disable")
        else:
            guildDB = await db.find("guilds",{"id": ctx.guild.id})
            if module in loggingModules["commands"] and module not in loggingModules["events"] and module in guildDB["logging"]["commands"]:
                index = 0
                for modules in guildDB["logging"]["commands"]:
                    index += 1
                    if modules == module:
                        continue
                del guildDB["logging"]["commands"][index]
                await db.update("guilds",{"id": ctx.guild.id},guildDB["logging"])
                return await ctx.send(embed=(await embed.generate(f"Logging module \"{module}\" disabled",None)))
            elif module in loggingModules["events"] and module not in loggingModules["commands"] and module in guildDB["logging"]["events"]:
                index = 0
                for modules in guildDB["logging"]["commands"]:
                    index += 1
                    if modules == module:
                        continue
                del guildDB["logging"]["events"][index]
                await db.update("guilds",{"id": ctx.guild.id},guildDB["logging"])
                return await ctx.send(embed=(await embed.generate(f"Logging module \"{module}\" disabled",None)))
            else:
                return await ctx.send(embed=(await embed.generate(f"Logging module \"{module}\" is already disabled!",None)))

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
            if guildDB["channel"] != 0:
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

    # Member specific events

    @commands.Cog.listener()
    async def on_member_update(self,before,after):
        guildDB = await db.find("guilds",{"id": before.guild.id})
        if before.roles != after.roles and "role" in guildDB["logging"]["events"]:
            async for entry in before.guild.audit_logs(limit=1,action=discord.AuditLogAction.member_role_update):
                auditLogEntry = entry
            if list(set(after.roles)-set(before.roles)) == []:
                roleDif = list(set(before.roles)-set(after.roles))
                roleDif.append("removed")
            else:
                roleDif = list(set(after.roles)-set(before.roles))
                roleDif.append("added")
            msg = await embed.generate(f"{before.name} was {roleDif[1]} a role!",None,0x9e0000 if roleDif[1] == "removed" else 0x0b9e00)
            msg = await embed.add_field(msg,f"Role {roleDif[1]}",roleDif[0].mention)
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)
        elif before.display_name != after.display_name and "nicknames" in guildDB["logging"]["events"]:
            async for entry in before.guild.audit_logs(limit=1):
                auditLogEntry = entry
            msg = await embed.generate(f"{before.name} changed their name!",None,0x10009e)
            msg = await embed.add_field(msg,"Name before",before.display_name)
            msg = await embed.add_field(msg,"Name now",after.display_name)
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    # Role specific events

    @commands.Cog.listener()
    async def on_guild_role_create(self,role):
        guildDB = await db.find("guilds",{"id": role.guild.id})
        if "role" in guildDB["logging"]["events"]:
            async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
                auditLogEntry = entry
            msg = await embed.generate(f"Role {role.name} was created!",None,0x0b9e00)
            permissions = dict()
            permsString = str()
            for permission in role.permissions:
                if permission[1]:
                    permissions[permission[0]] = permission[1]
            for permission, key in permissions.items():
                permsString += str(permission).replace('_',' ').title() + " - <:check:679095420202516480>\n"
            permsString = permsString[:-1]
            msg = await embed.add_field(msg, "Role permissions",permsString)
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    @commands.Cog.listener()
    async def on_guild_role_delete(self,role):
        guildDB = await db.find("guilds",{"id": role.guild.id})
        if "role" in guildDB["logging"]["events"]:
            async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
                auditLogEntry = entry
            msg = await embed.generate(f"Role {role.name} was deleted!",None,0x9e0000)
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    @commands.Cog.listener()
    async def on_guild_role_update(self,before,after):
        guildDB = await db.find("guilds",{"id": before.guild.id})
        if "role" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"Role {before.name} was updated!",None,0xff9900)
            if before.name != after.name:
                msg = await embed.add_field(msg,"Name changed",f"**Was:** {before.name}\n**Now:** {after.name}")
            if before.permissions != after.permissions:
                changes = {}
                for permission in list(set(before.permissions)-set(after.permissions)):
                    changes[permission[0]] = permission[1]
                permsString = str()
                for permission, key in changes.items():
                    if not key:
                        permsString += str(permission).replace('_',' ').title() + " - <:check:679095420202516480>\n"
                    else:
                        permsString += str(permission).replace('_',' ').title() + " - <:cross:679095420319694898>\n"
                msg = await embed.add_field(msg,f"Permissions changed",permsString)
            if before.hoist != after.hoist or before.color != after.color:
                msg = await embed.add_field(msg,"Special Attributes",f"**Hoisted**\nBefore: {'<:check:679095420202516480>' if before.hoist else '<:cross:679095420319694898>'}\nNow: {'<:check:679095420202516480>' if after.hoist else '<:cross:679095420319694898>'}\n\n**Color**\nBefore: {before.color}\nNow: {after.color}")
            async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
                auditLogEntry = entry
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    # Channel specific events

    @commands.Cog.listener()
    async def on_guild_channel_create(self,channel):
        guildDB = await db.find("guilds",{"id": channel.guild.id})
        if "channel" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"{str(channel.type).title()} channel #{channel.name} was created!",None,0x0b9e00)
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
                auditLogEntry = entry
            msg = await embed.add_field(msg,"Under category",channel.category if channel.category != None else "No category")
            for role, value in channel.overwrites.items():
                permissionPair = value.pair()
                overwriteString = ""
                # value[0] = Allowed Permissions
                # value[1] = Denied Permissions
                # When permissions value = 0, it is set to nothing
                for permission, val in iter(permissionPair[0]):
                    if val:
                        overwriteString += f"{permission.replace('_',' ').title()} - <:check:679095420202516480>\n"
                for permission, val in iter(permissionPair[1]):
                    if val:
                        overwriteString += f"{permission.replace('_',' ').title()} - <:cross:679095420319694898>\n"
                msg = await embed.add_field(msg,f"Permissions for {role.name}",overwriteString)
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self,channel):
        guildDB = await db.find("guilds",{"id": channel.guild.id})
        if "channel" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"{str(channel.type).title()} channel #{channel.name} was created!",None,0x9e0000)
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                auditLogEntry = entry
            msg = await embed.add_field(msg,"Under category",channel.category if channel.category != None else "No category")
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

    @commands.Cog.listener()
    async def on_guild_channel_update(self,before,after):
        guildDB = await db.find("guilds",{"id": before.guild.id})
        if "channel" in guildDB["logging"]["events"]:
            msg = await embed.generate(f"{str(before.type).title()} channel #{before.name} was updated!",None,0xff9900)
            async for entry in before.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
                auditLogEntry = entry
            if before.name != after.name:
                msg = await embed.add_field(msg,"Name changed",f"**Was:** {before.name}\n**Now:** {after.name}")
            if before.topic != after.topic:
                msg = await embed.add_field(msg,"Description changed",f"**Was:** {before.topic if before.topic != None else 'No description'}\n**Now:**: {after.topic if after.topic != None else 'No description'}")
            if before.type != after.type:
                msg = await embed.add_field(msg,"Type changed!",f"**Was:** {str(before.type).title()} channel\n**Now:**: {str(after.type).title()}")
            if before.overwrites != after.overwrites:
                overwriteString = ""
                for obj, value in before.overwrites.items():
                    beforeOverwriteString = ""
                    beforePair = value.pair()
                    for permission, val in iter(beforePair[0]):
                        if val:
                            beforeOverwriteString += f"{permission.replace('_',' ').title()} - <:check:679095420202516480>\n"
                    for permission, val in iter(beforePair[1]):
                        if val:
                            beforeOverwriteString += f"{permission.replace('_',' ').title()} - <:cross:679095420319694898>\n"
                    overwriteString += f"**{obj.mention}'s permissions before**\n{beforeOverwriteString}\n"
                overwriteString += "\n"
                for obj, value in after.overwrites.items():
                    afterPair = value.pair()
                    afterOverwriteString = ""
                    for permission, val in iter(afterPair[0]):
                        if val:
                            afterOverwriteString += f"{permission.replace('_',' ').title()} - <:check:679095420202516480>\n"
                    for permission, val in iter(afterPair[1]):
                        if val:
                            afterOverwriteString += f"{permission.replace('_',' ').title()} - <:cross:679095420319694898>\n"
                    overwriteString += f"**{obj.mention}'s permissions now**\n{afterOverwriteString}\n"
                msg = await embed.add_field(msg,"Permissions changed",overwriteString)
            msg.set_footer(text=f"{auditLogEntry.user.name}#{auditLogEntry.user.discriminator} (ID: {auditLogEntry.user.id})",icon_url=auditLogEntry.user.avatar_url)
            if guildDB["channel"] != 0:
                await self.bot.get_channel(guildDB["channel"]).send(embed=msg)

def setup(bot):
    bot.add_cog(Logs(bot))
    bot.add_cog(Logging(bot))