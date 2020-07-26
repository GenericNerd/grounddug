# GroundDug Votes Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.misc as misc
from datetime import datetime, timedelta

class Vote(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.group(name="vote",description="Vote to receive GroundDug Premium")
    async def vote(self,ctx):
        if ctx.invoked_subcommand is None:
            votes = await db.getVoteUser(ctx.author.id)
            print(votes)
            msg = await embed.generate("Vote for GroundDug Premium","Here is how you can vote for GroundDug and your current information")
            msg = await embed.add_field(msg,"Voting","You can vote for GroundDug here:\n[Top.gg](https://top.gg/bot/553602353962549249/vote)")
            msg = await embed.add_field(msg,"Current information",f"**Current votes:** {votes['votes']}\n**Linked user:** {votes['linkedTo']}")
        
    @vote.command(name="redeem",description="| Redeem your current votes and turn them into Premium")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def redeem(self,ctx):
        votes = await db.getVoteUser(ctx.author.id)
        guild = await db.find("guilds",{"id": ctx.guild.id})
        if not guild["premium"]["isPremium"] and votes["votes"] > 0:
            hours = 24 * votes["votes"]
            timestamp = datetime.utcnow() + timedelta(hours=hours)
            guild["premium"]["isPremium"] = True
            guild["premium"]["expires"] = (timestamp-datetime(1970,1,1)).total_seconds()
            await db.update("guilds",{"_id": guild["_id"]},{"premium": guild["premium"]})
        elif guild["premium"]["isPremium"] and votes["votes"] > 0:
            hours = 24 * votes["votes"]
            timestamp = guild["premium"]["expires"] + datetime.utcnow()+timedelta(hours=hours)
            await db.update("guilds",{"_id": guild["_id"]},{"premium": guild["premium"]})
        else:
            await ctx.invoke(self.bot.get_command("vote"))
    
    @vote.command(name="link",description="<user> | Link your votes to another user")
    @commands.guild_only()
    async def link(self,ctx,user:discord.Member):
        if user.id != ctx.author.id:
            votes = await db.getVoteUser(ctx.author.id)
            await db.update("voteUsers",{"user": ctx.author.id},{"linkedTo": user.id})
            prefix = await misc.getPrefix(self.bot,ctx)
            await ctx.send(embed=(await embed.generate(f"You have linked your votes to {user.name}",f"To unlink your votes, you can do {prefix}vote unlink")))
        else:
            await embed.error(ctx,"You cannot link votes to yourself!")
    
    @vote.command(name="unlink",description="Unlink your votes from another user")
    async def unlink(self,ctx):
        votes = await db.getVoteUser(ctx.author.id)
        if votes["linkedTo"] != None:
            await db.update("voteUsers",{"user": ctx.author.id},{"linkedTo": None})
            await ctx.send(embed=(await embed.generate("You have unlinked your votes")))
        else:
            await embed.error(ctx,"You do not have your votes linked to anyone!")

def setup(bot):
    bot.add_cog(Vote(bot))