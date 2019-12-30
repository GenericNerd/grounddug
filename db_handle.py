#PXB Database handling

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord
from discord.ext import commands
import asyncio
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

# # # # # # #
# VARIABLES #
# # # # # # #

client = pymongo.MongoClient("mongodb+srv://Fabio:^P*4k6A$c1I4@pxb-z0fef.mongodb.net/test?retryWrites=true&w=majority")
db = client.pxb

# # # # # # #
# FUNCTIONS #
# # # # # # #

async def dbUpdate(localdb,finder,update):
    db[localdb].update_one(finder,{"$set":update})
    
def dbNSyncFind(localdb,finder):
    return db[localdb].find_one(finder)

async def dbFind(localdb,finder):
    return db[localdb].find_one(finder)

async def dbInsert(localdb,data):
    db[localdb].insert_one(data)

async def dbRemove(localdb,finder):
    db[localdb].delete_one(finder)

async def dbRemoveMany(localdb,finder):
    db[localdb].delete_many(finder)