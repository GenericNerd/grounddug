# GroundDug Database Handler

import asyncio
import pymongo
from motor import motor_asyncio

connectionString = "mongodb://grounddug:eXJeX5e4yDPiocwg6mvw5kNDfBB0Bp7k@195.201.6.72:27017/grounddug?connectTimeoutMS=10000&authSource=grounddug&authMechanism=SCRAM-SHA-1"
asyncDBClient = motor_asyncio.AsyncIOMotorClient(connectionString, io_loop=asyncio.get_event_loop())
nsyncDBClient = pymongo.MongoClient(connectionString)
# asyncDB = asyncDBClient.grounddug
# nsyncDB = nsyncDBClient.grounddug
print(dir(asyncDBClient))
asyncDB = asyncDBClient
nsyncDB = nsyncDBClient

async def find(database,filter):
    return await asyncDB[database].find_one(filter)

async def findAll(database,filter):
    return asyncDB[database].find(filter)

async def insert(database,data):
    await asyncDB[database].insert_one(data)

async def getUser(guild,user):
    try:
        return await find("users",{"guild": guild, "user": user})
    except pymongo.errors.OperationFailure as e:
        userData = {"guild": guild, "user": user, "permissions": {"MANAGE_MESSAGES": False, "WARN_MEMBERS": False, "MUTE_MEMBERS": False, "KICK_MEMBERS": False, "BAN_MEMBERS": False, "ADMINISTRATOR": False}, "strikes": {}}
        await insert("users",userData)
        return userData

async def getVoteUser(user):
    try:
        return await find("voteUsers", {"user": user})
    except pymongo.errors.OperationFailure as e:
        voteUserData = {"user": user, "votes": 0, "linkedTo": None}
        await insert("voteUsers", voteUserData)
        return voteUserData

async def remove(database,filter):
    await asyncDB[database].delete_one(filter)

async def removeMany(database,filter):
    await asyncDB[database].delete_many(filter)

async def update(database,filter,update):
    await asyncDB[database].update_one(filter,{"$set": update})

def nsyncFind(database,filter):
    return nsyncDB[database].find_one(filter)

def nsyncFindAll(database,filter):
    return nsyncDB[database].find(filter)