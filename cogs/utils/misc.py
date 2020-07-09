# GroundDug Misc Utility Functions

import asyncio
import cogs.utils.db as db
import cogs.utils.logger as logger
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

def zalgoDetect(message):
    words = []
    for word in message.split():
        char = [unicodedata.category(c) for c in word]
        score = sum([char.count(zalgo) for zalgo in zalgoCategory]) / len(word)
        words.append(score)
    finalScore = numpy.percentile(words, 75)
    return finalScore

def zalgoClean(message):
    for line in message:
        cleanString = "".join([character for character in unicodedata.normalize("NFD",line) if unicodedata.category(character) not in zalgoCategory])
        logger.info(f"{cleanString=}")
        return cleanString