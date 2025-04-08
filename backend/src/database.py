from model import Vacancy
import os
# MongoDB driver
import motor.motor_asyncio

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]

print(MONGODB_CONNECTION_STRING)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client.JobStorage
collection = db.jobs

async def fetch_one_job(url):
    document = await collection.find_one({"url":url})
    return document

async def fetch_all_jobs():
    jobs = []
    cursor = collection.find({})
    async for document in cursor:
        jobs.append(Vacancy(**document))
    return jobs

async def insert_job(job):
    document = job
    result = await collection.insert_one(document)
    return document

async def update_job(url, desc):
    await collection.update_one({"url":url},{"$set":{"description":desc}})
    document = await collection.find_one({"url":url})
    return document

async def remove_job(url):
    await collection.delete_one({"url":url})
    return True
