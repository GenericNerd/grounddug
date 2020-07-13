# GroundDug Misc Utility Functions

import asyncio
import cogs.utils.db as db
import cogs.utils.logger as logger
import cogs.utils.embed as embed
import os
import unicodedata
import numpy

environment = os.getenv("GD_ENV", "beta")
zalgoCategory = ["Mn", "Me"]

async def getPrefix(bot,message):
    # Return gb! prefix if files are in beta environment
    if environment == "beta":
        return "gb!"
    # Return g! prefix for status
    elif message == None:
        return "g!"
    # Return g! prefix if not in a guild (e.g. DMs)
    elif not message.guild:
        return "g!"
    # Get guild prefix from DB
    else:
        guild = await db.find("guilds",{"id": message.guild.id})
        return guild["prefix"]

async def zalgoDetect(message:str):
    # Create an array called words
    words = []
    # Split the message by its spaces, and iterate through each word
    for word in message.split():
        # For each character in the word, get what category of unicode it is in
        char = [unicodedata.category(c) for c in word]
        # Add how many of the characters are in the zalgoCategory var divided by the length of the word
        score = sum([char.count(zalgo) for zalgo in zalgoCategory]) / len(word)
        words.append(score)
        # Append the zalgo score to the array called words
    finalScore = numpy.percentile(words, 75)
    # Return the 75th percentile of the score of words
    return finalScore

async def zalgoClean(message:str):
    # Create an empty string
    cleanString = ""
    for char in unicodedata.normalize("NFD",message):
        # For each normalised character in the message, add it to the string unless it is a zalgoCategory char
        if unicodedata.category(char) not in zalgoCategory:
            cleanString += char
    return cleanString

async def sendModLog(self,ctx,action,member=None):
    #0xff8400 - human
    guild = await db.find("guilds",{"id": ctx.guild.id})
    if guild["logs"]["mod"]:
        channel = self.bot.get_channel(guild["channel"])
        try:
            await channel.send(embed=(await embed.generate(f"{ctx.author.name} {action}",f"{action}")))
        except:
            pass

async def sendAutoModLog(self,guild,content,member=None):
    #0xe64100 - auto
    pass