# GroundDug Administrator Cog

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embed as embed
import cogs.utils.db as db

class Admin(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.group(name="admin",description="Guild administrative commands")
    @commands.guild_only()
    async def admin(self,ctx):
        # Send a help perms command if no subcommand invoked
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"admin")
        else:
            # Check whether logging for admin is enabled
            guild = await db.find("guilds",{"id": ctx.guild.id})
            if guild["logs"]["admin"]:
                # Get the logging channel for the guild
                channel = self.bot.get_channel(guild["channel"])
                try:
                    await channel.send(embed=(await embed.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
                except:
                    pass
        
    @admin.command(name="raid",description="<true/false> | Enables or disables raid mode")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def raid(self,ctx,state):
        # Get the guild database object
        guild = await db.find("guilds",{"id": ctx.guild.id})
        if state.lower() == "true":
            # Update raid mode to true and send a message
            await db.update("guilds",{"id": ctx.guild.id},{"raid_mode": True})
            await ctx.send(embed=(await embed.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `enabled` by {ctx.author.mention}")))
        elif state.lower() == "false":
            # Update raid mode to false and send a message
            await db.update("guilds",{"id": ctx.guild.id},{"raid_mode": False})
            await ctx.send(embed=(await embed.generate(f"{ctx.guild.name} Raid Mode",f"Raid Mode has been `disabled` by {ctx.author.mention}")))
        else:
            # Say that state must be true or false
            await embed.error(ctx,"Raid Mode state needs to be either 'True' or 'False'")

    @admin.command(name="setprefix",description="<prefix> | Set a custom prefix for your guild. Bot default is `g!`")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def setprefix(self,ctx,prefix):
        # Update the db object and send a message alerting of the change
        await db.update("guilds",{"id": ctx.guild.id},{"prefix": prefix})
        await ctx.send(embed=(await embed.generate("Prefix changed!",f"`{prefix}` is now the prefix for this guild")))
    
    @admin.command(name="blacklistadd",description="<channel> | Add a channel where commands will be ignored")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def blacklistAdd(self,ctx,channel:discord.TextChannel):
        # Get guild database object
        guild = await db.find("guilds",{"id": ctx.guild.id})
        # If the channel is not blacklisted, add it to the blacklist
        if channel.id not in guild["blacklistChannels"]:
            guild["blacklistChannels"].append(channel.id)
            # Update the database object and send a message saying channel is blacklisted
            await db.update("guilds",{"_id": guild["_id"]},guild)
            await ctx.send(embed=(await embed.generate("Channel added",f"{channel.mention} will now ignore commands sent to it")))
        else:
            # Say the channel is already in blacklist, and cannot be added again
            await ctx.send(embed=(await embed.generate("Channel already in blacklist",None)))
    
    @admin.command(name="blacklistremove",description="<channel> | Remove a channel where commands will be ignored")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def blacklistRemove(self,ctx,channel:discord.TextChannel):
        # Get guild database object
        guild = await db.find("guilds",{"id": ctx.guild.id})
        try:
            # Try to remove the channel
            guild["blacklistChannels"].remove(channel.id)
        except:
            # If the channel cannot be removed, it was never blacklisted, send a message alerting of this
            await ctx.send(embed=(await embed.generate("Channel is not in blacklist",None)))
        else:
            # Update the database object and send a message saying the channel is no longer blacklisted
            await db.update("guilds",{"_id": guild["_id"]},guild)
            await ctx.send(embed=(await embed.generate("Channel removed",f"{channel.mention} will no longer ignore commands sent to it")))

def setup(bot):
    bot.add_cog(Admin(bot))