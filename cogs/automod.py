#GroundDug AutoMod Module .

import discord
from discord.ext import commands
import asyncio
import cogs.utils.checks as checks
import cogs.utils.embeds as embeds
from cogs.utils.dbhandle import dbFind
from cogs.utils.dbhandle import dbUpdate
from cogs.utils.levels import get_level
from datetime import datetime

class automod(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.group(name="automod",description="Auto-moderation commands")
    async def automod(self,ctx):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("help"),"automod")
        elif ctx.guild != None:
            guild = await dbFind("guilds",{"id": ctx.guild.id})
            if guild["logs"]["automod"]:
                channel = self.bot.get_channel(guild["channel"])
                try:
                    await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
                except:
                    pass

    @automod.command(name="setup",description="Set up your automod for the server",hidden=True)
    @commands.guild_only()
    @checks.has_GD_permission("ADMINISTRATOR")
    async def setup(self,ctx):
        msg = await embeds.generate("GroundDug Auto-Moderation","Thank you for using GroundDug, this will guide you through the setup of the auto-moderation module of the bot. Please read this carefully.")
        msg = await embeds.add_field(msg,"Set up Auto-Moderation","React with :zero: to start setting up Auto-Moderation")
        msg = await embeds.add_field(msg,"Review current Auto-Moderation settings","Reach with :one: to review your settings")
        msg = await embeds.add_field(msg,"Change a setting","React with :two: to change a Auto-Moderation setting")
        msg = await ctx.send(embed=msg)

        zero = "0\N{combining enclosing keycap}"
        one = "1\N{combining enclosing keycap}"
        two = "2\N{combining enclosing keycap}"
        three = "3\N{combining enclosing keycap}"
        four = "4\N{combining enclosing keycap}"
        tick = "<:check:679095420202516480>"
        cross = "<:cross:679095420319694898>"

        await msg.add_reaction(zero)
        await msg.add_reaction(one)
        await msg.add_reaction(two)

        def check(reaction, user):
            return user == ctx.author and (str(reaction.emoji) == zero or str(reaction.emoji) == one or str(reaction.emoji) == two)
        
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))
        
        await msg.delete()

        #SETUP
        if str(reaction) == zero:
            guildSettings = {"automod": {
                "caps": 0,
                "antiInvite": False,
                "antiURL": False,
                "profanity": False,
                "massMentions": 0
            }}

            # MASS CAPS PROTECTION
            msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
            msg = await embeds.add_field(msg,"Mass Caps Lock Spam","Would you like to enable this feature?")
            msg = await ctx.send(embed=msg)
            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))
            
            if str(reaction) == tick:
                await msg.delete()
                msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
                msg = await embeds.add_field(msg,"Mass Caps Lock Spam","What percentage of the message would you like Mass Caps Lock Spam to trigger? Say a number between 0-100 (%)")
                msg = await ctx.send(embed=msg)

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
                    await msg.delete()
                    return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                if int(message.content) > 100:
                    guildSettings["automod"]["caps"] = 100
                elif int(message.content) < 0:
                    guildSettings["automod"]["caps"] = 0
                else:
                    guildSettings["automod"]["caps"] = int(message.content)

            await msg.delete()

            # ANTI-INVITE
            msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
            msg = await embeds.add_field(msg,"Anti-Invite","Would you like to enable this feature?")
            msg = await ctx.send(embed=msg)
            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            if str(reaction) == tick:
                guildSettings["automod"]["antiInvite"] = True
            
            await msg.delete()

            # ANTI-URL
            msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
            msg = await embeds.add_field(msg,"Anti-URL","Would you like to enable this feature?")
            msg = await ctx.send(embed=msg)
            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            if str(reaction) == tick:
                guildSettings["automod"]["antiURL"] = True

            await msg.delete()

            # PROFANITY
            msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
            msg = await embeds.add_field(msg,"Profanity Filter","Would you like to enable this feature?")
            msg = await ctx.send(embed=msg)
            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            if str(reaction) == tick:
                guildSettings["automod"]["profanity"] = True

            await msg.delete()

            # MASS PING PROTECTION
            msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
            msg = await embeds.add_field(msg,"Mass Ping Spam","Would you like to enable this feature?")
            msg = await ctx.send(embed=msg)
            await msg.add_reaction(tick)
            await msg.add_reaction(cross)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))
            
            if str(reaction) == tick:
                await msg.delete()
                msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
                msg = await embeds.add_field(msg,"Mass Ping Spam","How many pings should Mass Ping Protection Activate with? Say a number of pings")
                msg = await ctx.send(embed=msg)

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
                    await msg.delete()
                    return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                if int(message.content) < 0:
                    guildSettings["automod"]["massMentions"] = 0
                else:
                    guildSettings["automod"]["massMentions"] = int(message.content)

            await msg.delete()

            #FINAL MESSAGE

            def emoteReturn(setting):
                if setting == True:
                    return tick
                else:
                    return cross
                
            msg = await embeds.generate("GroundDug Auto-Moderation","You are all setup! Here are the settings you just added:")
            if guildSettings["automod"]["caps"] == 0:
                msg = await embeds.add_field(msg,"Caps Lock Spam Protection",cross)
            else:
                msg = await embeds.add_field(msg,"Caps Lock Spam Protection",f"{tick} - Activated at {guildSettings['automod']['caps']}%")
            msg = await embeds.add_field(msg,"Anti-Invite",emoteReturn(guildSettings["automod"]["antiInvite"]))
            msg = await embeds.add_field(msg,"Anti-URL",emoteReturn(guildSettings["automod"]["antiURL"]))
            msg = await embeds.add_field(msg,"Profanity Filter",emoteReturn(guildSettings["automod"]["profanity"]))
            if guildSettings["automod"]["massMentions"] == 0:
                msg = await embeds.add_field(msg,"Mass Mention Protection",cross)
            else:
                msg = await embeds.add_field(msg,"Mass Mention Protection",f"{tick} - Activated at {guildSettings['automod']['massMentions']} mentions")
            
            await ctx.send(embed=msg)
            await dbUpdate("guilds",{"id": ctx.guild.id},{"automod": guildSettings["automod"]})

        #REVIEW
        elif str(reaction) == one:
            def emoteReturn(setting):
                if setting == True:
                    return tick
                else:
                    return cross
            
            guildSettings = await dbFind("guilds",{"id": ctx.guild.id})
            msg = await embeds.generate("GroundDug Auto-Moderation","Here are the settings you have for Auto-Moderation:")
            if guildSettings["automod"]["caps"] == 0:
                msg = await embeds.add_field(msg,"Caps Lock Spam Protection",cross)
            else:
                msg = await embeds.add_field(msg,"Caps Lock Spam Protection",f"{tick} - Activated at {guildSettings['automod']['caps']}%")
            msg = await embeds.add_field(msg,"Anti-Invite",emoteReturn(guildSettings["automod"]["antiInvite"]))
            msg = await embeds.add_field(msg,"Anti-URL",emoteReturn(guildSettings["automod"]["antiURL"]))
            msg = await embeds.add_field(msg,"Profanity Filter",emoteReturn(guildSettings["automod"]["profanity"]))
            if guildSettings["automod"]["massMentions"] == 0:
                msg = await embeds.add_field(msg,"Mass Mention Protection",cross)
            else:
                msg = await embeds.add_field(msg,"Mass Mention Protection",f"{tick} - Activated at {guildSettings['automod']['massMentions']} mentions")
            
            await ctx.send(embed=msg)

        #CHANGE SETUP
        elif str(reaction) == two:
            def emoteReturn(setting):
                if setting == True:
                    return tick
                else:
                    return cross

            guildSettings = await dbFind("guilds",{"id": ctx.guild.id})
            msg = await embeds.generate("GroundDug Auto-Moderation","Which setting would you like to change?")

            if guildSettings["automod"]["caps"] == 0:
                msg = await embeds.add_field(msg,f"{zero} - Caps Lock Spam Protection",cross)
            else:
                msg = await embeds.add_field(msg,f"{zero} - Caps Lock Spam Protection",f"{tick} - Activated at {guildSettings['automod']['caps']}%")
            msg = await embeds.add_field(msg,f"{one} - Anti-Invite",emoteReturn(guildSettings["automod"]["antiInvite"]))
            msg = await embeds.add_field(msg,f"{two} - Anti-URL",emoteReturn(guildSettings["automod"]["antiURL"]))
            msg = await embeds.add_field(msg,f"{three} - Profanity Filter",emoteReturn(guildSettings["automod"]["profanity"]))
            if guildSettings["automod"]["massMentions"] == 0:
                msg = await embeds.add_field(msg,f"{four} - Mass Mention Protection",cross)
            else:
                msg = await embeds.add_field(msg,f"{four} - Mass Mention Protection",f"{tick} - Activated at {guildSettings['automod']['massMentions']} mentions")

            msg = await ctx.send(embed=msg)
            await msg.add_reaction(zero)
            await msg.add_reaction(one)
            await msg.add_reaction(two)
            await msg.add_reaction(three)
            await msg.add_reaction(four)

            def check(reaction, user):
                return user == ctx.author and (str(reaction.emoji) == zero or str(reaction.emoji) == one or str(reaction.emoji) == two or str(reaction.emoji) == three or str(reaction.emoji) == four)
        
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.delete()
                return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

            await msg.delete()

            if str(reaction) == zero:
                msg = await ctx.send(embed=await embeds.generate(msg,"GroundDug Auto-Moderation","Mass Caps Lock Spam - Would you like to enable this feature?"))
                await msg.add_reaction(tick)
                await msg.add_reaction(cross)

                def check(reaction, user):
                    return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))
                
                if str(reaction) == tick:
                    await msg.delete()
                    msg = await embeds.generate("GroundDug Auto-Moderation","Changing up your Auto-Moderation!")
                    msg = await embeds.add_field(msg,"Mass Caps Lock Spam","What percentage of the message would you like Mass Caps Lock Spam to trigger? Say a number between 0-100 (%)")
                    msg = await ctx.send(embed=msg)

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
                        await msg.delete()
                        return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                    if int(message.content) > 100:
                        guildSettings["automod"]["caps"] = 100
                    elif int(message.content) < 0:
                        guildSettings["automod"]["caps"] = 0
                    else:
                        guildSettings["automod"]["caps"] = int(message.content)
                else:
                    guildSettings["automod"]["caps"] = 0

            elif str(reaction) == one:
                msg = await embeds.generate("GroundDug Auto-Moderation","Changing up your Auto-Moderation!")
                msg = await embeds.add_field(msg,"Anti-Invite","Would you like to enable this feature?")
                msg = await ctx.send(embed=msg)
                await msg.add_reaction(tick)
                await msg.add_reaction(cross)

                def check(reaction, user):
                    return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                if str(reaction) == tick:
                    guildSettings["automod"]["antiInvite"] = True
                else:
                    guildSettings["automod"]["antiInvite"] = False

            elif str(reaction) == two:
                msg = await embeds.generate("GroundDug Auto-Moderation","Changing up your Auto-Moderation!")
                msg = await embeds.add_field(msg,"Anti-URL","Would you like to enable this feature?")
                msg = await ctx.send(embed=msg)
                await msg.add_reaction(tick)
                await msg.add_reaction(cross)

                def check(reaction, user):
                    return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                if str(reaction) == tick:
                    guildSettings["automod"]["antiURL"] = True
                else:
                    guildSettings["automod"]["antiURL"] = False
            elif str(reaction) == three:
                msg = await embeds.generate("GroundDug Auto-Moderation","Changing up your Auto-Moderation!")
                msg = await embeds.add_field(msg,"Profanity Filter","Would you like to enable this feature?")
                msg = await ctx.send(embed=msg)
                await msg.add_reaction(tick)
                await msg.add_reaction(cross)

                def check(reaction, user):
                    return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                if str(reaction) == tick:
                    guildSettings["automod"]["profanity"] = True
                else:
                    guildSettings["automod"]["profanity"] = False

            elif str(reaction) == four:
                msg = await embeds.generate("GroundDug Auto-Moderation","Changing up your Auto-Moderation!")
                msg = await embeds.add_field(msg,"Mass Ping Spam","Would you like to enable this feature?")
                msg = await ctx.send(embed=msg)
                await msg.add_reaction(tick)
                await msg.add_reaction(cross)

                def check(reaction, user):
                    return user == ctx.author and (str(reaction.emoji) == tick or str(reaction.emoji) == cross)

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.delete()
                    return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))
                
                if str(reaction) == tick:
                    msg = await embeds.generate("GroundDug Auto-Moderation","Setting up your Auto-Moderation!")
                    msg = await embeds.add_field(msg,"Mass Ping Spam","How many pings should Mass Ping Protection Activate with? Say a number of pings")
                    msg = await ctx.send(embed=msg)

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
                        await msg.delete()
                        return await ctx.send(embed=(await embeds.generate("You ran out of time!","Due to inactivity, `automod setup` has cancelled.")))

                    if int(message.content) < 0:
                        guildSettings["automod"]["massMentions"] = 0
                    else:
                        guildSettings["automod"]["massMentions"] = int(message.content)
                else:
                    guildSettings["automod"]["massMentions"] = 0

            await msg.delete()
            await dbUpdate("guilds",{"id": ctx.guild.id},{"automod": guildSettings["automod"]})
            msg = await embeds.generate("Auto-Moderation Changed Successfully",None)
            await ctx.send(embed=msg)

#IMPORTANT REGEX FOR INVITES,
# (?:https?://)?discord(?:app\.com/invite|\.gg)/?[a-zA-Z0-9]+/?
# (https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+[a-z] # THIS IS BETTER

def setup(bot):
    bot.add_cog(automod(bot))