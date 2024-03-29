# GroundDug Database Handler

import asyncio
import pymongo
from motor import motor_asyncio

connectionString = "mongodb://grounddug:eXJeX5e4yDPiocwg6mvw5kNDfBB0Bp7k@195.201.6.72:27017/grounddug?authSource=grounddug&retryWrites=true&w=majority"
# connectionString = "mongodb+srv://GroundDug:qLuVr1KFT8rr29sU@grounddug-z0fef.mongodb.net/test?retryWrites=true&w=majority"
asyncDBClient = motor_asyncio.AsyncIOMotorClient(connectionString, io_loop=asyncio.get_event_loop())
nsyncDBClient = pymongo.MongoClient(connectionString)
asyncDB = asyncDBClient["grounddug"]
nsyncDB = nsyncDBClient["grounddug"]

async def find(database,fltr):
    return await asyncDB[database].find_one(fltr)

async def findAll(database,fltr):
    return asyncDB[database].find(fltr)

async def insert(database,data):
    await asyncDB[database].insert_one(data)

async def getUser(guild,user):
    userData = await find("users",{"guild": guild, "user": user})
    if userData == None:
        userData = {"guild": guild, "user": user, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}}
        await insert("users",userData)
    return await find("users",{"guild": guild, "user": user})

async def getVoteUser(user):
    voteUser =  await find("voteUsers", {"user": user})
    if voteUser == None:
        voteUserData = {"user": user, "votes": 0, "linkedTo": None}
        await insert("voteUsers", voteUserData)
    return await find("voteUsers", {"user": user})

async def remove(database,fltr):
    await asyncDB[database].delete_one(fltr)

async def removeMany(database,fltr):
    await asyncDB[database].delete_many(fltr)

async def update(database,fltr,update):
    await asyncDB[database].update_one(fltr,{"$set": update})

def nsyncFind(database,fltr):
    return nsyncDB[database].find_one(fltr)

def nsyncFindAll(database,fltr):
    return nsyncDB[database].find(fltr)
