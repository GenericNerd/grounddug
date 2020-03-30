# GroundDug AutoMod Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.cases as cases

class AutoModListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,ctx):
        # If message is not in a guild
        if ctx.guild is not None:
            # Get current guild, logging channel and set removed to False
            guild = await db.find("guilds",{"id": ctx.guild.id})
            logChannel = self.bot.get_channel(guild["channel"])
            removed = False
            async def RuleViolator(msg,text,delete):
                global removed
                # Could possibly add a strike feature here
                if delete:
                    # Delete the message and set removed to True
                    await msg.delete()
                    removed = True
                    if guild["automod"]["warnOnRemove"]:
                        # Create a case for automod violation if the guild decides to warn on remove
                        await cases.createCase(ctx.guild,ctx.author,ctx.guild.me,"message deleted",text.capitalize())
                    # Return an embed with the text variable
                    return await embed.generate(f"{ctx.author.name}#{ctx.author.discriminator} {text} in #{ctx.channel.name}",f"`{ctx.content}`")
            if not removed:
                # This is the regex that will be used to check against messages for URLs
                url_Regex = r"(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?"
                # If anti-invite is on and message contains an invite, invoke RuleViolator
                if guild["automod"]["antiInvite"] and re.search("(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+[a-z]",ctx.content):
                    await logChannel.send(embed=(await RuleViolator(ctx,"tried to advertise",True)))
                # If anti-URL is on and the message contains a URL, invoke RuleViolator
                elif guild["automod"]["antiURL"] and re.search(url_Regex,ctx.content):
                    await logChannel.send(embed=(await RuleViolator(ctx,"tried to post a link",True)))
                # If short-URL is on and the message contains a URL, check if it is shortened
                elif guild["automod"]["shortURL"] and re.search(url_Regex,ctx.content):
                    shortened_URLs = []
                    # Find every URL in message
                    for url in re.findall(url_Regex):
                        # Emulate a browser to allow redirects
                        browser = await httpxClient.head(url,allow_redirects=True)
                        # If the browser URL after redirects is not the URL it was given, append it to shortenedURLs
                        if browser.url != url:
                            shortened_URLs.append(str(browser.url))
                    if shortened_URLs is not []:
                        await ctx.delete()
                        # Embed description
                        description = ""
                        for url in shortened_URLs:
                            desc += f"{item} "
                        await ctx.send(embed=(await embed.generate("Shortened URLs detected!",f"{ctx.author.mention} posted a shortened link(s) leading to {desc}")))
                # If the message contains swearing, invoke RuleViolator
                elif guild["automod"]["profanity"] and pf.is_profane(ctx.content):
                    await logChannel.send(embed=(await RuleViolator(ctx,"tried to swear",True)))
                # If caps is not disabled, the message is longer than 8 characters and the percentage of caps is above the threshold, invoke RuleViolator
                elif guild["automod"]["caps"] > 0 and len(ctx.content) > 8 and guild["automod"]["caps"] < (sum(1 for x in ctx.content if str.isupper(x))/len(ctx.content))*100:
                    await logChannel.send(embed=(await RuleViolator(ctx,"used too many caps",True)))
                # If mass mentions are not disabled, and more than mass mentions were mentioned, invoke RuleViolator
                elif guild["automod"]["massMentions"] > 0 and len(ctx.raw_mentions) >= guild["automod"]["massMentions"]:
                    await logChannel.send(embed=(await RuleViolator(ctx,"pinged too many people",True)))


class AutoModSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="automod",description="AutoMod commands")
    async def automod(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"automod")

    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def setup(self, ctx):
        guild = await db.find("guilds", {"id": ctx.guild.id})

        for _, key in guild["automod"].items():
            pass

def setup():
    bot.add_cog(AutoModListener(bot))
    bot.add_cog(AutoModSetup(bot))