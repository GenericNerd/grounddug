#GroundDug Database handling

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import pymongo
from motor import motor_asyncio
from bson.objectid import ObjectId

# # # # # # #
# VARIABLES #
# # # # # # #

client = motor_asyncio.AsyncIOMotorClient("mongodb+srv://Fabio:^P*4k6A$c1I4@grounddug-z0fef.mongodb.net/test?retryWrites=true&w=majority")
clientnsync = pymongo.MongoClient("mongodb+srv://Fabio:^P*4k6A$c1I4@grounddug-z0fef.mongodb.net/test?retryWrites=true&w=majority")
db = client.grounddug
dbnsync = clientnsync.grounddug

# # # # # # #
# FUNCTIONS #
# # # # # # #

async def dbUpdate(localdb,finder,update):
    await db[localdb].update_one(finder,{"$set":update})
    
def dbNSyncFind(localdb,finder):
    return dbnsync[localdb].find_one(finder)

async def dbFind(localdb,finder):
    return await db[localdb].find_one(finder)

async def dbInsert(localdb,data):
    await db[localdb].insert_one(data)

async def dbRemove(localdb,finder):
    await db[localdb].delete_one(finder)

async def dbRemoveMany(localdb,finder):
    await db[localdb].delete_many(finder)