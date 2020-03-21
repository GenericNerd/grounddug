# GroundDug Database Handler

import asyncio
import pymongo
from motor import motor_asyncio

connection_String = "mongodb+srv://GroundDug:qLuVr1KFT8rr29sU@grounddug-z0fef.mongodb.net/test?retryWrites=true&w=majority"
async_DB_Client = motor_asyncio.AsyncIOMotorClient(connection_String)
nsync_DB_Client = pymongo.MongoClient(connection_String)
async_DB = async_DB_Client.grounddug
nsync_DB = nsync_DB_Client.grounddug

async def find(database,filter):
    return await async_DB[database].find_one(filter)

async def findAll(database,filter):
    return await async_DB[database].find(filter)

async def insert(database,data):
    await async_DB[database].insert_one(data)

async def remove(database,filter):
    await async_DB[database].delete_one(filter)

async def removeMany(database,filter):
    await async_DB[database].delete_many(filter)

async def update(database,filter,update):
    await async_DB[database].update_one(filter,{"$set": update})

def nsyncFind(database,filter):
    return nsync_DB[database].find_one(filter)

def nsyncFindAll(database,filter):
    return nsync_DB[database].find(filter)