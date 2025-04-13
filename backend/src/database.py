from model import Vacancy
import os
# MongoDB driver
import motor.motor_asyncio
from uuid import UUID, uuid4

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]

print(MONGODB_CONNECTION_STRING)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client.JobStorage
collection = db.vacancies2

async def fetch_one_job(url: str):
    try:
        job = await collection.find_one({"url": url})
        return Vacancy(**job)
    except:
        return 0
    
async def fetch_main_job_by_id(id: str):
    try:
        job = await collection.find_one({"id": id})
        return Vacancy(**job)
    except:
        return 0
    
async def fetch_site_vacancy(url: str):
    try:
        job = await collection.find_one({"url": url})
        return Vacancy(**job)
    except:
        return 0
    
async def fetch_main_vacancy(url: str):
    try:
        job = await collection.find_one({"originalUrls": url})
        return Vacancy(**job)
    except:
        return 0

async def fetch_duplicates(job: Vacancy):
    duplicates = []
    cursor = collection.find({"$and": 
                                [{"organization": job.organization},
                                 {"$or": 
                                    [{"position": job.position}, {"category": job.category}]
                                 }]})
    for item in await cursor.to_list(length=100):
        print(item)
        if item['url']:
            duplicates.append({'mainId': item['mainId'], 'url': item['url'],
                                'organization': item['organization'], 'position': item['position']})
        else:
            print("else")
            duplicates.append({'mainId': item['id'], 'site': 'Main',
                            'organization': item['organization'], 'position': item['position']})
    return duplicates

async def insert_job(job: Vacancy):
    try:
        # print("here")
        # print(job)
        # print(job.model_dump_json())
        result = await collection.insert_one(job.model_dump())
        # print(result)
        # print(result.inserted_id)
        return result
    except Exception as we:
        # print(we)
        return 0

async def insert_duplicate(duplicateUrl, mainId):
    result = await collection.update_one({"id": mainId},{"$addToSet": {"originalUrls": duplicateUrl}})
    return result


async def fetch_all_jobs():
    jobs = []
    cursor = collection.find({})
    async for document in cursor:
        jobs.append(Vacancy(**document))
    return jobs



# async def update_job(url, desc):
#     # await collection.update_one({"url":url},{"$set":{"description":desc}})

#     document = await collection.find_one({"url":url})
#     return document

async def delete_job(id):
    try:
        result = await collection.delete_one({"id": id})
        return result.deleted_count
    except:
        return 0
