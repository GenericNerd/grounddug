#GroundDug Permissions Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
from cogs.utils.useful import getPrefix
from cogs.utils.useful import getPermissions
import cogs.utils.embeds as embeds
from cogs.utils.dbhandle import dbUpdate
from cogs.utils.dbhandle import dbFind
from cogs.utils.dbhandle import dbInsert
from cogs.utils.levels import get_level

async def changePermission(self,ctx,user,change,permission=None):
    if permission == None:
        prefix = await getPrefix(self.bot,ctx)
        msg = await embeds.generate("Permissions",f"{user.name}'s current permissions")
        for permission in (await getPermissions(ctx.guild,user)):
            if len(permission.split("_")) >= 2:
                perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
            else:
                perm = permission.lower()
            if not (await getPermissions(ctx.guild,user))[permission]:
                msg = embeds.add_field(msg,perm,f"Change by using `{prefix}permissions <add/remove> @{user.name}#{user.discriminator} {permission.lower()}`")
        if msg.fields == []:
            msg = embeds.add_field(msg,"All permissions",f"`{change}` - `{prefix}permissions list {user.name}#{user.discriminator}` to check them")
        await ctx.send(embed=msg)
    else:
        permission = permission.upper()
        currentPermissions = await getPermissions(ctx.guild,user)
        if permission == "ADMINISTRATOR":
            for perm in currentPermissions.copy():
                currentPermissions[perm] = change
            await dbUpdate("permissions",{"guild": ctx.guild.id, "user": user.id},{"permissions": currentPermissions})
        else:
            notChange = not change
            if (await getPermissions(ctx.guild,user))[permission] == notChange:
                currentPermissions[permission] = change
                dbUpdate("permissions",{"guild": ctx.guild.id, "user": user.id},{"permissions": currentPermissions})
        await ctx.send(embed=(await embeds.generate("Permission changed",f"Permission `{permission}` to {user.name}#{user.discriminator} was changed to `{change}`")))

class perms(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.group(name="perms",description="Custom permissions settings")
    async def perms(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"perms")
        else:
            guild = await dbFind("guilds",{"id": ctx.guild.id})
            if guild["perms_log"]:
                channel = self.bot.get_channel(guild["channel"])
                await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
    
    @perms.command(name="setup",hidden=True)
    @checks.has_required_level(5)
    async def setup(self,ctx):
        for guild in self.bot.guilds:
            for member in guild.members:
                if (await dbFind("permissions", {"guild": guild.id, "user": member.id})) == None:
                    if member.id == guild.owner_id:
                        await dbInsert("permissions",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True,"MUTE_MEMBERS": True,"KICK_MEMBERS": True,"BAN_MEMBERS": True,"ADMINISTRATOR": True}})
                    else:
                        await dbInsert("permissions",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False,"MUTE_MEMBERS": False,"KICK_MEMBERS": False,"BAN_MEMBERS": False,"ADMINISTRATOR": False}})

    @perms.command(name="add",description="<user> [permission] | Assigns a users' GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def add(self,ctx,user:discord.Member,permission=None):
        await changePermission(self,ctx,user,True,permission)

    @perms.command(name="remove",description="<user> [permission] | Removes a users' GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def remove(self,ctx,user:discord.Member,permission=None):
        await changePermission(self,ctx,user,False,permission)
    
    @perms.command(name="list",description="[user] | Shows the current GroundDug (`GD`) permissions currently assigned to a user")
    @commands.guild_only()
    async def permsList(self,ctx,user:discord.Member=None):
        if user == None:
            user = ctx.author
        msg = await embeds.generate("Permissions",f"{user.name}'s current permissions")
        for permission in (await getPermissions(ctx.guild,user)):
            if len(permission.split("_")) >= 2:
                perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
            else:
                perm = permission.lower()
            if (await getPermissions(ctx.guild,user))[permission]:
                msg = embeds.add_field(msg,perm,"<:check:437236812189270018>")
        await ctx.send(embed=msg)

def setup(bot):
    bot.add_cog(perms(bot))