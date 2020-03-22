# GroundDug Custom Checks

import discord
from discord.ext import commands
import asyncio
import cogs.utils.levels as levels
import cogs.utils.db as db

# Permissions failure class if level is not sufficient
class LevelPermissionsError(commands.CheckFailure):
    def __init__(self,required,current):
        self.required = required
        self.current = current

# Permissions failure class if GD permission is missing
class MissingGDPermissionError(commands.CheckFailure):
    def __init__(self,required):
        self.required = required

# Checks if user has required level
def hasRequiredLevel(required: int=0):
    # Async check function
    async def calculateIfLevelSufficent(ctx):
        level = await levels.getLevel(ctx.message.author)
        if level >= required:
            return True
        else:
            # Raise custom error showing current and required levels
            raise LevelPermissionsError(required=required,current=level)
    # Check level using async function
    return commands.check(calculateIfLevelSufficent)

# Checks if user had the GD permission permission
def hasGDPermission(permission):
    # Async check function
    async def permissionCheck(ctx):
        userObject = await db.getUser(ctx.guild.id,ctx.author.id)
        if userObject["permissions"][permission]:
            return True
        else:
            # Raise custom error showing the required permission
            raise MissingGDPermissionError(required=permission)
    # Check level using async function
    return commands.check(permissionCheck)