from model import Vacancy
import os
# MongoDB driver
import motor.motor_asyncio

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]

print(MONGODB_CONNECTION_STRING)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client.JobStorage
collection = db.vacancies

async def fetch_one_job(url):
    job = await collection.find_one({"url":url})
    if job:
        return Vacancy(**job)
    else:
        return 0

async def fetch_duplicates(job):
    duplicates = []
    cursor = collection.find({"$and": 
                                [{"organization": job.organization},
                                 {"$or": 
                                    [{"position": job.position}, {"category": job.category}]
                                 }]})
    for item in await cursor.to_list(length=100):
        for url in item['url']:
            duplicates.append({'site': item['site'], 'url': url,
                            'organization': item['organization'], 'position': item['position']})
    return duplicates

async def insert_job(job):
    document = job
    result = await collection.insert_one(document)
    return document

async def insert_duplicate(duplicateUrl, url):
    await collection.update_one({"url":url},{"$addToSet":{"url":duplicateUrl}})
    document = await collection.find_one({"url":url})
    return document


async def fetch_all_jobs():
    jobs = []
    cursor = collection.find({})
    async for document in cursor:
        jobs.append(Vacancy(**document))
    return jobs



async def update_job(url, desc):
    await collection.update_one({"url":url},{"$set":{"description":desc}})
    document = await collection.find_one({"url":url})
    return document

async def remove_job(url):
    await collection.delete_one({"url":url})
    return True
