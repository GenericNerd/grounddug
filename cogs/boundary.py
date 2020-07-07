# GroundDug Boundary Cog

import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import uuid
import cogs.utils.db as db
import cogs.utils.checks as checks
import cogs.utils.embed as embed

# Create function to enable and disable Boundary db state
async def updateBoundary(ctx,state,langState):
    # Find the current guild in the database
    # Set the parsed state (boolean)
    # Update the database and return an embed with the contents
    guildDB = await db.find("guilds",{"id": ctx.guild.id})
    if state == guildDB["boundary"]["enabled"]:
        return
    guildDB["boundary"]["enabled"] = state
    await db.update("guilds",{"_id": guildDB["_id"]},{"boundary": guildDB["boundary"]})
    return await embed.generate(f"Boundary is now {langState}!",None,0xffcc4d)

# Boundary Class

class Boundary(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.boundary_check.start()
    
    @commands.group(name="boundary",description="Improve protection on your server")
    async def boundary(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"boundary")

    @boundary.command(name="enable",description="| Enable Boundary with current settings")
    @checks.hasGDPermission("ADMINISTRATOR")
    async def enable(self,ctx):
        # Update Boundary to state of True
        try:
            await ctx.send(embed=(await updateBoundary(ctx,True,"enabled")))
        except:
            pass

    @boundary.command(name="disable",description="| Disable Boundary")
    @checks.hasGDPermission("ADMINISTRATOR")
    async def disable(self,ctx):
        # Update Boundary to state of False
        try:
            await ctx.send(embed=(await updateBoundary(ctx,False,"disabled")))
        except:
            pass

    @boundary.command(name="setrole",description="[role] | Set the role given to users who have verified")
    @checks.hasGDPermission("ADMINISTRATOR")
    async def setrole(self,ctx,role:discord.Role=None):
        # If role is not given, return the current role,
        # otherwise, set the given role to Boundary role
        guildDB = await db.find("guilds",{"id": ctx.guild.id})
        if role == None:
            await ctx.send(embed=(await embed.generate("Boundary role",f"The current Boundary role is set to: <@&{guildDB['boundary']['role']}>",0xffcc4d)))
        elif guildDB["boundary"]["role"] == role.id:
            return
        else:  
            guildDB["boundary"]["role"] = role.id
            await db.update("guilds",{"_id": guildDB["_id"]},{"boundary": guildDB["boundary"]})
            await ctx.send(embed=(await embed.generate("Boundary role updated!",f"The new Boundary role has been set to <@&{role.id}>",0xffcc4d)))

    @boundary.command(name="create",description="This is a testing command",hidden=True)
    @checks.hasRequiredLevel(5)
    async def test(self,ctx):
        bid = uuid.uuid4()
        await db.insert("boundary",{"uuid": str(bid), "guild": ctx.guild.id, "user": ctx.author.id, "verified": False})
        await ctx.send(await db.find("boundary",{"uuid": str(bid), "guild": ctx.guild.id, "user": ctx.author.id}))

    @tasks.loop(seconds=60)
    async def boundary_check(self):
        # Wait until the bot is ready (mainly to avoid errors on_ready)
        await self.bot.wait_until_ready()
        # Find and iterate through each verified user
        documents = await db.findAll("boundary",{"verified": True})
        async for document in documents:
            # Find their member and guild objects (Discord and DB objects)
            guild = self.bot.get_guild(document["guild"])
            user = guild.get_member(document["user"])
            guildDB = await db.find("guilds",{"id": document["guild"]})
            # If the role is not set, but the logs channel is set, send a message alerting mods/admins that Boundary role is not set
            if guildDB["boundary"]["role"] == None and guildDB["channel"] != 0:
                await guild.get_channel(guildDB["channel"]).send(embed=(await embed.generate("Boundary role is not set!",f"You forgot to set a Boundary role! As users verify, the role is not given.\n\n**User**: {user.mention}",0xffcc4d)))
            else:
                # Add the Boundary role to the user and send them a message to let them know they have verified
                await user.add_roles(guild.get_role(guildDB["boundary"]["role"]))
                try:
                    await user.send(embed=(await embed.generate("You have been verified!",f"You are now a verified member in {guild.name}!",0xffcc4d)))
                except:
                    pass
            # Remove the verification document from the database
            await db.remove("boundary",{"_id": document["_id"]})

def setup(bot):
    bot.add_cog(Boundary(bot))
