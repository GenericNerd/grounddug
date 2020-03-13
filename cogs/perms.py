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
    permissions = await getPermissions(ctx.guild,user)
    if permission == None:
        prefix = await getPrefix(self.bot,ctx)
        msg = await embeds.generate("Permissions",f"{user.name}'s permissions to change")
        for permission in permissions:
            if len(permission.split("_")) >= 2:
                perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
            else:
                perm = permission.lower()
            if permissions[permission] != change:
                msg = await embeds.add_field(msg,perm,f"Change by using `{prefix}perms <add/remove> @{user.name}#{user.discriminator} {permission.lower()}`")
        if msg.fields == []:
            msg = await embeds.add_field(msg,"All permissions",f"`{change}` - `{prefix}perms list {user.name}#{user.discriminator}` to check them")
        await ctx.send(embed=msg)
    else:
        permission = permission.upper()
        if permission == "ADMINISTRATOR":
            for perm in permissions.copy():
                permissions[perm] = change
            await dbUpdate("users",{"guild": ctx.guild.id, "user": user.id},{"permissions": permissions})
        else:
            permissions[permission] = change
            await dbUpdate("users",{"guild": ctx.guild.id, "user": user.id},{"permissions": permissions})
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
            if guild["logs"]["perms"]:
                channel = self.bot.get_channel(guild["channel"])
                try:
                    await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
                except:
                    pass

    @perms.command(name="add",description="<user> [permission] | Assigns a users GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def add(self,ctx,user:discord.Member,permission=None):
        await changePermission(self,ctx,user,True,permission)

    @perms.command(name="remove",description="<user> [permission] | Removes a users GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def remove(self,ctx,user:discord.Member,permission=None):
        await changePermission(self,ctx,user,False,permission)
    
    @perms.command(name="massadd",description="<role> <permission> | Assigns users within the pinged role a GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def massAdd(self,ctx,role:discord.Role,permission):
        for user in role.members:
            await changePermission(self,ctx,user,True,permission)

    @perms.command(name="massremove",description="<role> <permission> | Removes users within the pinged role a GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def massRemove(self,ctx,role:discord.Role,permission):
        for user in role.members:
            await changePermission(self,ctx,user,False,permission)

    @perms.command(name="list",description="[user] | Shows the current GroundDug (`GD`) permissions currently assigned to a user")
    @commands.guild_only()
    async def permsList(self,ctx,user:discord.Member=None):
        if user == None:
            user = ctx.author
        msg = await embeds.generate("Permissions",f"{user.name}'s current permissions")
        permissions = await getPermissions(ctx.guild,user)
        for permission in permissions:
            if len(permission.split("_")) >= 2:
                perm = f"{permission.split('_')[0].lower()} {permission.split('_')[1].lower()}"
            else:
                perm = permission.lower()
            if permissions[permission]:
                msg = await embeds.add_field(msg,perm,"<:check:679095420202516480>",True)
        await ctx.send(embed=msg)

def setup(bot):
    bot.add_cog(perms(bot))