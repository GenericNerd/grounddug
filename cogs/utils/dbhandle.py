#GroundDug Database Handler

import asyncio
import pymongo
from motor import motor_asyncio

connection = "mongodb+srv://Fabio:^P*4k6A$c1I4@grounddug-z0fef.mongodb.net/test?retryWrites=true&w=majority"
asyncClient = motor_asyncio.AsyncIOMotorClient(connection)
nsyncClient = pymongo.MongoClient(connection)
asyncdb = asyncClient.grounddug
nsyncdb = nsyncClient.grounddug

async def dbUpdate(db,finder,update):
    await asyncdb[db].update_one(finder,{"$set": update})

def dbNSyncFind(db,finder):
    return nsyncdb[db].find_one(finder)

async def dbFind(db,finder):
    return await asyncdb[db].find_one(finder)

async def dbFindAll(db,finder):
    return asyncdb[db].find(finder)

async def dbInsert(db,data):
    await asyncdb[db].insert_one(data)

async def dbRemove(db,finder):
    await asyncdb[db].delete_one(finder)

async def dbRemoveMany(db,finder):
    await asyncdb[db].delete_many(finder)

async def itemExist(db,finder):
    if dbFind(db,finder) is None:
        return True
    else:
        return False