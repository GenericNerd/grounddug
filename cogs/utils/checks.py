#GroundDug Custom Checks

import discord
from discord.ext import commands
import asyncio
from cogs.utils.levels import get_level
import cogs.utils.dbhandle as dbhandle

class LevelPermissionsError(commands.CheckFailure):
    def __init__(self,required,current):
        self.required = required
        self.current = current

class MissingGDPermission(commands.CheckFailure):
    def __init__(self,required):
        self.required = required

def has_required_level(required: int = 0):
    async def levelCalculate(ctx):
        level = await get_level(ctx.message.author)
        if level >= required:
            return True
        else:
            raise LevelPermissionsError(required=required, current=level)
    return commands.check(levelCalculate)

def has_GD_permission(permission):
    async def permissionCalculate(ctx):
        dbObject = await dbhandle.dbFind("permissions",{"guild": ctx.guild.id, "user": ctx.author.id})
        if dbObject["permissions"][permission]:
            return True
        else:
            raise MissingGDPermission(required=permission)
    return commands.check(permissionCalculate)