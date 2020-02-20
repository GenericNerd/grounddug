#GroundDug Event Handler Module

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import cogs.utils.embeds as embeds
from cogs.utils.useful import getPrefix
import cogs.utils.dbhandle as db
import cogs.utils.useful as useful
import re

swearWords = ["4r5e", "5h1t", "5hit", "a55", "anal", "anus", "ar5e", "arrse", "arse", "ass", "ass-fucker", "asses", "assfucker", "assfukka", "asshole", "assholes", "asswhole", "a_s_s", "b!tch", "b00bs", "b17ch", "b1tch", "ballbag", "balls", "ballsack", "bastard", "beastial", "beastiality", "bellend", "bestial", "bestiality", "bi+ch", "biatch", "bitch", "bitcher", "bitchers", "bitches", "bitchin", "bitching", "bloody", "blow job", "blowjob", "blowjobs", "boiolas", "bollock", "bollok", "boner", "boob", "boobs", "booobs", "boooobs", "booooobs", "booooooobs", "breasts", "buceta", "bugger", "bum", "bunny fucker", "butt", "butthole", "buttmuch", "buttplug", "c0ck", "c0cksucker", "carpet muncher", "cawk", "chink", "cipa", "cl1t", "clit", "clitoris", "clits", "cnut", "cock", "cock-sucker", "cockface", "cockhead", "cockmunch", "cockmuncher", "cocks", "cocksuck", "cocksucked", "cocksucker", "cocksucking", "cocksucks", "cocksuka", "cocksukka", "cok", "cokmuncher", "coksucka", "coon", "cox", "crap", "cum", "cummer", "cumming", "cums", "cumshot", "cunilingus", "cunillingus", "cunnilingus", "cunt", "cuntlick", "cuntlicker", "cuntlicking", "cunts", "cyalis", "cyberfuc", "cyberfuck", "cyberfucked", "cyberfucker", "cyberfuckers", "cyberfucking", "d1ck", "damn", "dick", "dickhead", "dildo", "dildos", "dink", "dinks", "dirsa", "dlck", "dog-fucker", "doggin", "dogging", "donkeyribber", "doosh", "duche", "dyke", "ejaculate", "ejaculated", "ejaculates", "ejaculating", "ejaculatings", "ejaculation", "ejakulate", "f u c k", "f u c k e r", "f4nny", "fag", "fagging", "faggitt", "faggot", "faggs", "fagot", "fagots", "fags", "fanny", "fannyflaps", "fannyfucker", "fanyy", "fatass", "fcuk", "fcuker", "fcuking", "feck", "fecker", "felching", "fellate", "fellatio", "fingerfuck", "fingerfucked", "fingerfucker", "fingerfuckers", "fingerfucking", "fingerfucks", "fistfuck", "fistfucked", "fistfucker", "fistfuckers", "fistfucking", "fistfuckings", "fistfucks", "flange", "fook", "fooker", "fuck", "fucka", "fucked", "fucker", "fuckers", "fuckhead", "fuckheads", "fuckin", "fucking", "fuckings", "fuckingshitmotherfucker", "fuckme", "fucks", "fuckwhit", "fuckwit", "fudge packer", "fudgepacker", "fuk", "fuker", "fukker", "fukkin", "fuks", "fukwhit", "fukwit", "fux", "fux0r", "f_u_c_k", "gangbang", "gangbanged", "gangbangs", "gaylord", "gaysex", "goatse", "God", "god-dam", "god-damned", "goddamn", "goddamned", "hardcoresex", "heshe", "hoar", "hoare", "hoer", "homo", "hore", "horniest", "horny", "hotsex", "jack-off", "jackoff", "jap", "jerk-off", "jism", "jiz", "jizm", "jizz", "kawk", "knob", "knobead", "knobed", "knobend", "knobhead", "knobjocky", "knobjokey", "kock", "kondum", "kondums", "kum", "kummer", "kumming", "kums", "kunilingus", "l3i+ch", "l3itch", "labia", "lust", "lusting", "m0f0", "m0fo", "m45terbate", "ma5terb8", "ma5terbate", "masochist", "master-bate", "masterb8", "masterbat*", "masterbat3", "masterbate", "masterbation", "masterbations", "masturbate", "mo-fo", "mof0", "mofo", "mothafuck", "mothafucka", "mothafuckas", "mothafuckaz", "mothafucked", "mothafucker", "mothafuckers", "mothafuckin", "mothafucking", "mothafuckings", "mothafucks", "mother fucker", "motherfuck", "motherfucked", "motherfucker", "motherfuckers", "motherfuckin", "motherfucking", "motherfuckings", "motherfuckka", "motherfucks", "muff", "mutha", "muthafecker", "muthafuckker", "muther", "mutherfucker", "n1gga", "n1gger", "nazi", "nigg3r", "nigg4h", "nigga", "niggah", "niggas", "niggaz", "nigger", "niggers", "nob", "nob jokey", "nobhead", "nobjocky", "nobjokey", "numbnuts", "nutsack", "orgasim", "orgasims", "orgasm", "orgasms", "p0rn", "pawn", "pecker", "penis", "penisfucker", "phonesex", "phuck", "phuk", "phuked", "phuking", "phukked", "phukking", "phuks", "phuq", "pigfucker", "pimpis", "piss", "pissed", "pisser", "pissers", "pisses", "pissflaps", "pissin", "pissing", "pissoff", "poop", "porn", "porno", "pornography", "pornos", "prick", "pricks", "pron", "pube", "pusse", "pussi", "pussies", "pussy", "pussys", "rectum", "retard", "rimjaw", "rimming", "s hit", "s.o.b.", "sadist", "schlong", "screwing", "scroat", "scrote", "scrotum", "semen", "sex", "sh!+", "sh!t", "sh1t", "shag", "shagger", "shaggin", "shagging", "shemale", "shi+", "shit", "shitdick", "shite", "shited", "shitey", "shitfuck", "shitfull", "shithead", "shiting", "shitings", "shits", "shitted", "shitter", "shitters", "shitting", "shittings", "shitty", "skank", "slut", "sluts", "smegma", "smut", "snatch", "son-of-a-bitch", "spac", "spunk", "s_h_i_t", "t1tt1e5", "t1tties", "teets", "teez", "testical", "testicle", "tit", "titfuck", "tits", "titt", "tittie5", "tittiefucker", "titties", "tittyfuck", "tittywank", "titwank", "tosser", "turd", "tw4t", "twat", "twathead", "twatty", "twunt", "twunter", "v14gra", "v1gra", "vagina", "viagra", "vulva", "w00se", "wang", "wank", "wanker", "wanky", "whoar", "whore", "willies", "willy", "xrated", "xxx"]

class events(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"\n{self.bot.user.name}\nOnline\nFrom {str(datetime.utcnow()).split('.')[0]} UTC")
        await self.bot.change_presence(status=discord.Status.dnd,activity=discord.Game("Booting up!"))
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate("I'm online",f"As of {str(datetime.utcnow()).split('.')[0]} UTC, I am performing my member checks now!")))
        for guild in self.bot.guilds:
            for member in guild.members:
                if (await db.dbFind("users", {"guild": guild.id, "user": member.id})) == None:
                    if member.id == guild.owner_id:
                        await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True,"WARN_MEMBERS": True,"MUTE_MEMBERS": True,"KICK_MEMBERS": True,"BAN_MEMBERS": True,"ADMINISTRATOR": True}, "strikes": {}})
                    else:
                        await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False,"WARN_MEMBERS": False,"MUTE_MEMBERS": False,"KICK_MEMBERS": False,"BAN_MEMBERS": False,"ADMINISTRATOR": False}, "strikes": {}})
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate("Checks completed!",f"I am now fully online as of {str(datetime.utcnow()).split('.')[0]} UTC")))
        await self.bot.change_presence(status=discord.Status.online,activity=discord.Game(f"{await useful.getPrefix(self.bot,self.bot.get_guild(526427196072525836))}help to get started"))

    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        data = {
            "id": guild.id,
            "prefix": "g!",
            "channel": 0,
            "logs": {
                "misc": False,
                "logs": False,
                "mod": False,
                "perms": False,
                "automod": False,
            },
            "raid_mode": False,
            "cases": 0,
            "automod": {
                "caps": 0,
                "antiInvite": False,
                "antiURL": False,
                "profanity": False,
                "massMentions": 0
            }}
        await db.dbInsert("guilds",data)
        for member in guild.members:
            if member.guild_permissions.administrator:
                await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": True, "WARN_MEMBERS": True, "MUTE_MEMBERS": True, "KICK_MEMBERS": True, "BAN_MEMBERS": True, "ADMINISTRATOR": True}, "strikes": {}})
            else:
                await db.dbInsert("users",{"guild": guild.id, "user": member.id, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}})
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate(f"I have joined {guild.name}",f"{guild.name} has {guild.member_count} members")))

    @commands.Cog.listener()
    async def on_guild_remove(self,guild):
        await db.dbRemoveMany("users",{"guild": guild.id})
        await db.dbRemove("guilds",{"id": guild.id})
        await self.bot.get_channel(664541295448031295).send(embed=(await embeds.generate(f"I have left {guild.name}",f"{guild.name} had {guild.member_count} members :(")))

    @commands.Cog.listener()
    async def on_member_join(self,member):
        if not (await db.dbFind("guilds",{"id": member.guild.id}))["raid_mode"]:
            await db.dbInsert("users",{"guild": member.guild.id, "user": member.id, "permissions": {
                "MANAGE_MESSAGES": False,
                "WARN_MEMBERS": False,
				"MUTE_MEMBERS": False,
				"KICK_MEMBERS": False,
				"BAN_MEMBERS": False,
				"ADMINISTRATOR": False}, "strikes": {}})
        else:
            try:
                await member.send(embed=(await embeds.generate(f"{member.guild.name} is currently on lockdown","Please try to join again in a couple of hours")))
            except Exception:
                pass
            finally:
                await member.kick(reason="Guild is on lockdown")

    @commands.Cog.listener()
    async def on_member_remove(self,member):
        await db.dbRemove("users",{"guild": member.guild.id, "user": member.id})

    @commands.Cog.listener()
    async def on_message(self,ctx):
        if ctx.guild != None:
            guild = await db.dbFind("guilds",{"id": ctx.guild.id})
            channel = self.bot.get_channel(guild["channel"])
            removed = False
            async def RuleViolator(msg,text,channel):
                global removed
                await msg.delete()
                await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator} {text} in #{ctx.channel.name}",f"`{ctx.content}`")))
                guildDB = await db.dbFind("guilds",{"id": ctx.guild.id})
                userDB = await db.dbFind("users",{"guild": ctx.guild.id, "user": user.id})
                userDB["strikes"][str(guildDB["cases"])] = {"moderator": ctx.author.id, "reason": text.capitalize()}
                await db.dbUpdate("users",{"_id": userDB["_id"]},{"strikes": userDB["strikes"]})
                await db.dbUpdate("guilds",{"_id": guildDB["_id"]},{"cases": guildDB["cases"] + 1})
                removed = True
            if not removed and guild["automod"]["antiInvite"] and re.search("(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com\/invite)\/.+[a-z]",ctx.content):
                await RuleViolator(ctx,"tried to advertise",channel)
            if not removed and guild["automod"]["antiURL"] and re.search(r"(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))",ctx.content):
                await RuleViolator(ctx,"tried to post a link",channel)
            if not removed and guild["automod"]["profanity"]:
                for word in swearWords:
                    if word in ctx.content.lower():
                        await RuleViolator(ctx,"tried to swear",channel)
                        break
            if not removed and guild["automod"]["caps"] > 0 and len(ctx.content) > 0 and guild["automod"]["caps"] < (sum(1 for x in ctx.content if str.isupper(x))/len(ctx.content))*100:
                await RuleViolator(ctx,"used too many CAPS",channel)
            if not removed and guild["automod"]["massMentions"] > 0 and len(ctx.raw_mentions) > guild["automod"]["massMentions"]:
                await RuleViolator(ctx,"pinged too many people",channel)

    @commands.Cog.listener()
    async def on_command(self,ctx):
        if ctx.guild != None:
            guild = await db.dbFind("guilds",{"id": ctx.guild.id})
            channel = self.bot.get_channel(guild["channel"])
            command_base = (ctx.message.content).split((await getPrefix(self.bot,ctx)))[1].split(" ")[0]
            command_list = ["admin","logs","perms","developer","dev","automod"]
            if not command_base in command_list and guild["logs"]["misc"]:
                try:
                    await channel.send(embed=(await embeds.generate(f"{ctx.author.name}#{ctx.author.discriminator}",f"Ran `{ctx.message.content}` in <#{ctx.channel.id}>")))
                except:
                    pass

    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        prefix = await getPrefix(self.bot,ctx)
        if isinstance(error,commands.MissingRequiredArgument):
            await embeds.error(ctx,f"{error} - Use {prefix}help to find the required arguments")
        elif isinstance(error,commands.CommandNotFound):
            pass
        elif isinstance(error,commands.CheckFailure):
            await embeds.error(ctx,f"You do not have the valid permissions to run this command")
        else:
            await embeds.error(ctx,f"{error} - Report to developers")

def setup(bot):
	bot.add_cog(events(bot))