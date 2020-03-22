# GroundDug Permissions Cog

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.misc as misc
import cogs.utils.embed as embed
import cogs.utils.db as db

async def changePermission(bot,ctx,user,permChangeTo,permission=None):
    # Get the current user permissions
    userPermissions = await db.getUser(ctx.guild.id,ctx.author.id)
    userPermissions = userPermissions["permissions"]
    # If the permission to change is none
    # Check what permissions can be changed to permChangeTo and send a message
    if permission == None:
        prefix = await misc.getPrefix(bot,ctx)
        msg = await embed.generate("Permissions",f"{user.name}'s permissions that can be changed")
        for permission in userPermissions:
            permissionName = permission.split("_")
            # Check whether database permission name split is greater than 2 to capitalise text
            if len(permissionName) >= 2:
                permissionName = f"{permissionName[0].lower().capitalize()} {permissionName[1].lower().capitalize()}"
            else:
                permissionName.lower().capitalize()
            # Check whether the permission is the opposite, hence changable and add a field describing how to change the permission
            if userPermissions[permission] is not permChangeTo:
                # In future, change this so permission does not need to include the underscore
                msg = await embed.add_field(msg,permissionName,f"Change this permission by running `{prefix}perms <add/remove> @{user.name}#{user.discriminator} {permission.lower()}`")
        # If no permissions were listed, all permissions are set to permChangeTo
        if msg.fields == []:
            msg.title = "All permissions are already set to this"
            msg.description = f"{user.mention} already has all their permissions set to {permChangeTo}"
        await ctx.send(embed=msg)
    else:
        # Make the given permission upper case, if it wasn't already
        permission = permission.upper()
        if permission == "ADMINISTRATOR":
            # Change all permissions to permChangeTo if the permission is administrator
            for perm in permissions.copy():
                userPermissions[perm] = permChangeTo
            await db.update("users",{"guild": ctx.guild.id, "user": user.id},{"permissions": userPermissions})
        else:
            # Try to change the permission, if the key doesn't exist, raise an error
            try:
                userPermissions[permission] = change
            except Exception:
                return await embed.error(ctx,f"Permission {permission} cannot be found")
            else:
                # Update the permissions if the key was changed
                await db.update("users",{"guild": ctx.guild.id,"user": user.id},{"permissions": userPermissions})
        # Send a message letting the user know the permission change was successful
        await ctx.send(embed=(await embed.generate("Permission changed successfully!",f"Permission `{permission}` to {user.mention} was successfully changed, it is now set to `{permChangeTo}`")))

class Perms(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.group(name="perms",description="Custom permissions")
    async def perms(self,ctx):
        # Send a help perms command if no subcommand invoked
        if ctx.invoked_subcommand is None:
            pass
            # await ctx.invoke(self.bot.get_command("help"),"perms")
        else:
            # Check whether logging for perms is enabled
            guild = await db.find("guilds",{"id": ctx.guild.id})
            if guild["logs"]["perms"]:
                # Get the logging channel for the guild
                channel = self.bot.get_command(guild["channel"])
                try:
                    await channel.send(embed=(await embed.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in #{ctx.channel.name}")))
                except:
                    pass

    @perms.command(name="give",description="<user> [permission] | Give a user a GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def add(self,ctx,user:discord.Member,permission=None):
        await changePermission(self.bot,ctx,user,True,permission)

    @perms.command(name="remove",description="<user> [permission] | Remove a users GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def remove(self,ctx,user:discord.Member,permission=None):
        await changePermission(self.bot,ctx,user,False,permission)

    @perms.command(name="massadd",description="<role> <permission> | Give multiple users within a role a GroundDug (`GD`) permission")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def massAdd(self,ctx,role:discord.Role,permission):
        for user in role.members:
            await changePermission(self.bot,ctx,user,True,permission)

    @perms.command(name="massremove",description="<role> <permission> | Remove a GroundDug (`GD`) permission from users within a role")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def massRemove(self,ctx,role:discord.Role,permission):
        for user in role.members:
            await changePermission(self.bot,ctx,user,False,permission)

    @perms.command(name="list",description="[user] | Shows the current GroundDug (`GD`) permissions currently assigned to a user")
    @commands.guild_only()
    async def permsList(self,ctx,user:discord.Member=None):
        if user is None:
            user = ctx.author
        msg = await embed.generate("Permissions",f"{user.name}'s GroundDug permissions")
        # Get the current user permissions
        userPermissions = await db.getUser(ctx.guild.id,user.id)
        userPermissions = userPermissions["permissions"]
        # For every permission, capitalise the name and set it to permissionName
        for permission in userPermissions:
            permissionName = permission.split("_")
            if len(permissionName) >= 2:
                permissionName = f"{permissionName[0].lower().capitalize()} {permissionName[1].lower().capitalize()}"
            else:
                permissionName = permission.lower().capitalize()
            # If the permission is set to True, add a field to the embed
            if userPermissions[permission]:
                msg = await embed.add_field(msg,permissionName,"<:check:679095420202516480>",True)
        await ctx.send(embed=msg)

def setup(bot):
    bot.add_cog(Perms(bot))