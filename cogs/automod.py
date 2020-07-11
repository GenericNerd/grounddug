# GroundDug AutoMod Module

import discord
from discord.ext import commands
import asyncio
import cogs.utils.embed as embed
import cogs.utils.db as db
import cogs.utils.cases as cases
import cogs.utils.checks as checks
from cogs.utils.misc import zalgoDetect
from cogs.utils.misc import zalgoClean
import cogs.utils.logger as logger

import re
import aiohttp
from profanity_filter import ProfanityFilter

# Variables required for automod to work in future
pf = ProfanityFilter()

class AutoModListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self,ctx):
        # If message is not in a guild
        if ctx.guild is not None and self.bot.get_user(ctx.author.id).bot is False:
            # Check whether the user has got bypass automod
            user = await db.find("users",{"guild": ctx.guild.id, "user": ctx.author.id})
            try:
                bypass = user["permissions"]["BYPASS_AUTOMOD"]
            except:
                bypass = False
            if not bypass:
                # Get current guild, logging channel and set removed to False
                guild = await db.find("guilds",{"id": ctx.guild.id})
                logChannel = self.bot.get_channel(guild["channel"])
                removed = False
                async def RuleViolator(msg,text,delete):
                    if delete:
                        # Delete the message and set removed to True
                        await msg.delete()
                        removed = True
                        if guild["automod"]["warnOnRemove"]:
                            # Create a case for automod violation if the guild decides to warn on remove
                            await cases.createCase(ctx.guild,ctx.author,ctx.guild.me,"deleted message",text.capitalize())
                        # Return an embed with the text variable
                    return await embed.generate(f"{ctx.author.name}#{ctx.author.discriminator} {text} in #{ctx.channel.name}",f"`{ctx.content}`")
                async def attemptSend(channel, embed):
                    try:
                        await channel.send(embed=embed)
                    except:
                        pass
                if not removed:
                    # This is the regex that will be used to check against messages for URLs
                    url_Regex = r"(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))?"
                    # If anti-invite is on and message contains an invite, invoke RuleViolator
                    if guild["automod"]["antiInvite"] and re.search("(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+",ctx.content):
                        await attemptSend(logChannel,await RuleViolator(ctx,"tried to advertise",True))
                    # If anti-URL is on and the message contains a URL, invoke RuleViolator
                    elif guild["automod"]["antiURL"] and re.search(url_Regex,ctx.content):
                        await attemptSend(logChannel,await RuleViolator(ctx,"tried to post a link",True))
                    # If short-URL is on and the message contains a URL, check if it is shortened
                    elif guild["automod"]["shortURL"] and re.search(url_Regex,ctx.content):
                        shortened_URLs = []
                        # Find every URL in message
                        for url in re.findall(url_Regex,ctx.content):
                            # Emulate a browser to allow redirects
                            async with aiohttp.ClientSession() as session:
                                async with session.get(url, allow_redirects=True) as response:
                                    redirect = str(response).split("Location': \'")[1].split("\'")[0]
                            # If the browser URL after redirects is not the URL it was given, append it to shortenedURLs
                            if redirect != url:
                                shortened_URLs.append(redirect)
                        if shortened_URLs is not []:
                            # Embed description
                            description = ""
                            for url in shortened_URLs:
                                description += f"{url}, "
                            await ctx.channel.send(embed=(await embed.generate("Shortened URLs detected!",f"{ctx.author.mention} posted a shortened link(s) leading to {description}")))
                    # If the message contains swearing, invoke RuleViolator
                    elif guild["automod"]["profanity"] and pf.is_profane(ctx.content):
                        await attemptSend(logChannel,await RuleViolator(ctx,"tried to swear",True))
                    # If caps is not disabled, the message is longer than 8 characters and the percentage of caps is above the threshold, invoke RuleViolator
                    elif guild["automod"]["caps"] > 0 and len(ctx.content) > 8 and guild["automod"]["caps"] < (sum(1 for x in ctx.content if str.isupper(x))/len(ctx.content))*100:
                        await attemptSend(logChannel,await RuleViolator(ctx,"used too many caps",True))
                    # If mass mentions are not disabled, and more than mass mentions were mentioned, invoke RuleViolator
                    elif guild["automod"]["massMentions"] > 0 and len(ctx.raw_mentions) >= guild["automod"]["massMentions"]:
                        await attemptSend(logChannel,await RuleViolator(ctx,"pinged too many people",True))
                    # If Zalgo text detection is not disabled, and Zalgo is detected above the specified amount, invoke RuleViolator4
                    elif guild["automod"]["zalgo"] > 0 and ((await zalgoDetect(ctx.content)*100)>guild["automod"]["zalgo"]):
                        await ctx.channel.send(embed=(await embed.generate(f"{ctx.author.name} used Zalgo text!",f"Here is what they actually meant to say:\n\n{await zalgoClean(ctx.content)}")))
                        await attemptSend(logChannel,await RuleViolator(ctx,"used Zalgo text",False))

class AutoModSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="automod",description="AutoMod commands")
    @commands.guild_only()
    async def automod(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"automod")

    @automod.command(name="setup",description="| AutoMod Setup Wizard")
    @commands.guild_only()
    @checks.hasGDPermission("ADMINISTRATOR")
    async def setup(self, ctx):
        await ctx.send(embed=(await embed.generate("Auto-Mod setup just got easier!","You can review your automod settings and change them easier through the dashboard, you can find it [here](https://grounddug.xyz/dashboard)")))
        e = await embed.generate("AutoMod Setup","**Welcome to the AutoMod Setup Wizard.**\n\nThe Setup Wizard will configure AutoMod on your Discord server. Click :one: to continue, :two: to review settings already in place, or :x: to exit the Setup Wizard.")
        msg = await ctx.send(embed=e)

        cancel = "❌"
        one = "1\N{combining enclosing keycap}"
        two = "2\N{combining enclosing keycap}"
        three = "3\N{combining enclosing keycap}"
        four = "4\N{combining enclosing keycap}"
        five = "5\N{combining enclosing keycap}"
        tick = "<:check:679095420202516480>"
        cross = "<:cross:679095420319694898>"

        await msg.add_reaction(cancel)
        await msg.add_reaction(one)
        await msg.add_reaction(two)

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == one or str(reaction.emoji) == two or str(reaction.emoji) == cancel)

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
            return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

        if str(reaction) == cancel:
            return await msg.delete()
        elif str(reaction) == one:
            guildSettings = {
                "automod": {
                    "caps": 0,
                    "massMentions": 0,
                    "zalgo": 0,
                    "antiInvite": False,
                    "antiURL": False,
                    "profanity": False,
                    "shortURL": False,
                    "warnOnRemove": False,
                }
            }

            # CAPS LOCK SPAM DETECTION
            await msg.clear_reactions()
            e = await embed.generate("AutoMod Setup", "Would you like to enable caps lock spam detection?")
            await msg.edit(embed=e)

            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.remove_reaction(reaction, user)

            if str(reaction) == tick:
                await msg.clear_reactions()

                e = await embed.generate("AutoMod Setup", "What percentage of the message must be in full caps to trigger the detection? (Any number between 1-100)")

                await msg.edit(embed=e)

                def check(message):
                    try:
                        int(message.content)
                    except Exception:
                        pass
                    else:
                        return message.author == ctx.author

                try:
                    message = await self.bot.wait_for("message", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                if int(message.content) > 100:
                    guildSettings["automod"]["caps"] = 100
                elif int(message.content) < 0:
                    guildSettings["automod"]["caps"] = 0
                else:
                    guildSettings["automod"]["caps"] = int(message.content)

                await message.delete()

            # MASS-MENTION PROTECTION
            e = await embed.generate("AutoMod Setup", "Would you like to enable mass-mention protection?")
            await msg.edit(embed=e)

            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.remove_reaction(reaction, user)

            if str(reaction) == tick:
                await msg.clear_reactions()

                e = await embed.generate("AutoMod Setup", "How many mentions should mass-mention protection activate? (Any number)")

                await msg.edit(embed=e)

                def check(message):
                    try:
                        int(message.content)
                    except Exception:
                        pass
                    else:
                        return message.author == ctx.author

                try:
                    message = await self.bot.wait_for("message", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                if int(message.content) < 0:
                    guildSettings["automod"]["massMentions"] = 0
                else:
                    guildSettings["automod"]["massMentions"] = int(message.content)

                await message.delete()

            # ANTI INVITE
            e = await embed.generate("AutoMod Setup", "Would you like to enable Anti-Invite?")
            await msg.edit(embed=e)

            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.remove_reaction(reaction, user)

            if str(reaction) == tick:
                guildSettings["automod"]["antiInvite"] = True

            # ANTI URL
            e = await embed.generate("AutoMod Setup", "Would you like to enable Anti-URL?")
            await msg.edit(embed=e)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.remove_reaction(reaction, user)

            if str(reaction) == tick:
                guildSettings["automod"]["antiURL"] = True

            # PROFANITY
            e = await embed.generate("AutoMod Setup", "Would you like to enable the profanity filter?")
            await msg.edit(embed=e)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.remove_reaction(reaction, user)

            if str(reaction) == tick:
                guildSettings["automod"]["profanity"] = True

            # SHORT URLS
            e = await embed.generate("AutoMod Setup", "Would you like to enable short URL detection?")
            await msg.edit(embed=e)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.remove_reaction(reaction, user)

            if str(reaction) == tick:
                guildSettings["automod"]["shortURL"] = True

            # WARN ON REMOVE
            e = await embed.generate("AutoMod Setup", "Should AutoMod warn a user when they trip a detection mechanism?")
            await msg.edit(embed=e)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return await msg.edit(embed=(await embed.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.remove_reaction(reaction, user)

            if str(reaction) == tick:
                guildSettings["automod"]["warnOnRemove"] = True

            # FINISH
            await db.update("guilds",{"id": ctx.guild.id},{"automod": guildSettings["automod"]})

            await msg.clear_reactions()
            e = await embed.generate("AutoMod Setup", "AutoMod has been configured successfully. The Setup Wizard has now ended.")
            await msg.edit(embed=e)

        elif str(reaction) == two:
            await msg.clear_reactions()

            def emoteReturn(setting):
                if setting == True:
                    return tick
                else:
                    return cross

            guildSettings = await db.find("guilds", {"id": ctx.guild.id})

            e = await embed.generate("AutoMod Setup", "Here are the current settings you have:")

            if guildSettings["automod"]["caps"] == 0:
                e = await embed.add_field(e, "Caps Lock Spam Protection", cross)
            else:
                e = await embed.add_field(e, "Caps Lock Spam Protection", f"{tick} - Activated when message has {guildSettings['automod']['caps']}% of text in caps.")

            if guildSettings["automod"]["massMentions"] == 0:
                e = await embed.add_field(e, "Mass-Mention Protection", cross)
            else:
                e = await embed.add_field(e, "Mass-Mention Protection", f"{tick} - Activated at {guildSettings['automod']['massMentions']} mentions.")

            if guildSettings["automod"]["zalgo"] == 0:
                e = await embed.add_field(e, "Zalgo Text Detection", cross)
            else:
                e = await embed.add_field(e, "Zalgo Text Detection", f"{tick} - Activated at {guildSettings['automod']['massMentions']}% suspicion")

            e = await embed.add_field(e, "Anti-Invite", emoteReturn(guildSettings["automod"]["antiInvite"]))
            e = await embed.add_field(e, "Anti-URL", emoteReturn(guildSettings["automod"]["antiURL"]))
            e = await embed.add_field(e, "Profanity Filter", emoteReturn(guildSettings["automod"]["profanity"]))
            e = await embed.add_field(e, "Short URL Detection", emoteReturn(guildSettings["automod"]["shortURL"]))
            e = await embed.add_field(e, "Warn on Remove", emoteReturn(guildSettings["automod"]["warnOnRemove"]))

            await msg.edit(embed=e)

def setup(bot):
    bot.add_cog(AutoModListener(bot))
    bot.add_cog(AutoModSetup(bot))
