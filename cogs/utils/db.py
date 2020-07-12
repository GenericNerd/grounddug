# GroundDug Database Handler

import asyncio
import pymongo
from bson.int64 import Int64
from motor import motor_asyncio

connectionString = "mongodb://root:GQAbun9Tb44kTC1T3XYM8VI3v1DpCwEnQU0GntIdMbMID5V6hI0MAcHKzFZF0f79@195.201.6.72:27017/?authSource=admin&retryWrites=true&w=majority"
# connectionString = "mongodb+srv://GroundDug:qLuVr1KFT8rr29sU@grounddug-z0fef.mongodb.net/test?retryWrites=true&w=majority"
asyncDBClient = motor_asyncio.AsyncIOMotorClient(connectionString, io_loop=asyncio.get_event_loop())
nsyncDBClient = pymongo.MongoClient(connectionString)
asyncDB = asyncDBClient["grounddug"]
nsyncDB = nsyncDBClient["grounddug"]
# asyncDB = asyncDBClient
# nsyncDB = nsyncDBClient

async def find(database,filter):
    documents = []
    async for document in asyncDB[database].find({}):
        documents.append(document)
    print(documents)
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
    print(nsyncDB[database].find_one(filter))
    print(nsyncDB["guilds"].find_one({"id": Int64(526427196072525836)}))
    return nsyncDB[database].find_one(filter)

def nsyncFindAll(database,filter):
    return nsyncDB[database].find(filter)