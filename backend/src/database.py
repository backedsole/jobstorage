from model import SiteVacancy, SiteVacancyDB, MainVacancy, MainVacancyDB
import os
# MongoDB driver
import motor.motor_asyncio

MONGODB_CONNECTION_STRING = os.environ["MONGODB_CONNECTION_STRING"]

print(MONGODB_CONNECTION_STRING)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STRING)
db = client.JobStorage
collection = db.vacancies2

async def fetch_one_job(url):
    job = await collection.find_one({"url":url})
    if job:
        return SiteVacancyDB(**job)
    else:
        return 0
    
async def fetch_site_job(url):
    job = await collection.find_one({"url": url})
    if job:
        return SiteVacancyDB(**job)
    else:
        return 0   

async def fetch_main_job(id):
    job = await collection.find_one({"_id": id})
    if job:
        return MainVacancyDB(**job)
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

async def insert_site_job(job: SiteVacancy):
    result = await collection.insert_one(job.model_dump())
    if result:
        return result.inserted_id
    else:
        return 0
    
async def insert_main_job(job: MainVacancy):
    result = await collection.insert_one(job.model_dump())
    if result:
        return result.inserted_id
    else:
        return 0
    
# async def insert_job(job: SiteVacancy):
#     # job.description = ""
#     vacancy_dump = job.model_dump()
#     # print(vacancy_dump)
#     url = job.url
#     vacancy_dump.pop('url')
#     # print(vacancy_dump)
#     vacancy_dump['urlList'] = [job.url]
#     vacancy_dump['site'] = "Main"
#     # print(vacancy_dump)
#     mainVacancy = MainVacancy(**vacancy_dump)
#     # print(mainVacancy)
#     result = await collection.insert_one(mainVacancy.model_dump())
#     # print(result.inserted_id)
#     mainVacancyId = result.inserted_id
#     vacancy_dump = job.model_dump()
#     vacancy_dump['mainId'] = mainVacancyId
#     result = await collection.insert_one(vacancy_dump)
#     # print(mainVacancyId)
#     return mainVacancyId

async def insert_duplicate(duplicateUrl, url):
    await collection.update_one({"url":url},{"$addToSet":{"url":duplicateUrl}})
    document = await collection.find_one({"url":url})
    return document


async def fetch_all_jobs():
    jobs = []
    cursor = collection.find({})
    async for document in cursor:
        jobs.append(SiteVacancyDB(**document))
    return jobs



async def update_job(url, desc):
    await collection.update_one({"url":url},{"$set":{"description":desc}})
    document = await collection.find_one({"url":url})
    return document

async def remove_job(url):
    await collection.delete_one({"url":url})
    return True
