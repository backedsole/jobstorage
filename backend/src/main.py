from model import Vacancy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from parser import parseJob
from uuid import uuid4

#App object
app = FastAPI()

from database import (
    fetch_one_job,
    fetch_duplicates,
    insert_job,
    insert_duplicate,
    fetch_main_vacancy,
    fetch_site_vacancy,
    fetch_all_jobs,
    update_job,
    remove_job,
    fetch_job_by_id_main,
)

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"<h1>Use API</h1>"}

# Parsing vacancy from url
@app.get("/api/parse/")
async def parse_job_from_url(url: str):
    response = {}
    job = await fetch_main_vacancy(url)
    if type(job) == Vacancy:
        response['msg'] = 'Already in database'
        response['vacancy'] = job
        return response

    job = parseJob(url)
    if  type(job) != Vacancy:
        response['msg'] =  job
        return response

    response['vacancy'] = job

    duplicates = await fetch_duplicates(job)
    if duplicates:
        response['duplicates'] = duplicates

    return response

#Adding vacancy to database
@app.post("/api/job", response_model=Vacancy)
async def post_job(job: Vacancy):
    # print("aaa")
    # job.description = ""
    originaljobId = str(uuid4())
    # print(type(originaljobId))
    # print(originaljobId)
    # print(type(str(originaljobId)))
    # print(str(originaljobId))
    mainJobId = str(uuid4())
    # print(mainJobId)

    job.id = originaljobId
    job.mainId = mainJobId
    # print(job)
    
    response = await insert_job(job)
    if not response:
        raise HTTPException(400, "Something went wrong")
    # print("aaa11")
    job.id = mainJobId
    job.mainId = None
    job.originalUrls = [job.url]
    job.url = None
    job.site = "Main"
    # print("aaa22")
    # print(job)
    response = await insert_job(job)
    if not response:
        raise HTTPException(400, "Something went wrong")
    
    return job


#Adding duplicate vacancy to database document
@app.post("/api/job/duplicate", response_model=Vacancy)
async def post_duplicate(data: dict):
    print("aaa")
    print(data)
    print(type(data))
    response = await insert_duplicate(data["duplicateUrl"], data["url"])
    print("bbb")
    if response:
        return response
    raise HTTPException(400, "Something went wrong")

# @app.get("/api/job")
# async def get_jobs():
#     response = await fetch_all_jobs()
#     return response

# @app.get("/api/job/duplicates")
# async def get_jobs(url: str):
#     #response = {}
#     result = await fetch_one_job(url)
#     if type(result) == Vacancy:
#         duplicates = await fetch_duplicates(result)
#         return duplicates
#     else:  
#         raise HTTPException(404, f"There is no job with this url {url}")


    # if type(result) != Vacancy:
    #     result = parseJob(url)
    #     if  type(result) != Vacancy:
    #         return result
    
    # duplicates = fetch_duplicates(result)
    # full_response = {'vacancy': result, }
    #     return response
    # else:
    #     return parseJob(url)

# @app.get("/api/parse/", response_model=Vacancy|str)
# async def parse_job_from_url(url: str):
#     response = await fetch_one_job(url)
#     if response:
#         return response
#     else:
#         return parseJob(url)
    
@app.get("/api/job/", response_model=Vacancy)
async def get_job_by_id(url: str):
    response = await fetch_one_job(url)
    if response:
        return response
    raise HTTPException(404, f"There is no job with this url {url}")

@app.get("/api/job/main", response_model=Vacancy)
async def get_job_by_id_main(jobId: str):
    response = await fetch_job_by_id_main(jobId)
    if response:
        return response
    raise HTTPException(404, f"There is no job with this url {url}")


@app.put("/api/job", response_model=Vacancy)
async def put_job(url:str, desc:str):
    response = await update_job(url, desc)
    if response:
        return response
    raise HTTPException(404, f"There is no job with this url {url}")

@app.delete("/api/job/")
async def delete_job(url: str):
    response = await remove_job(url)
    if response:
        return "Succesfully deleted job"
    raise HTTPException(404, f"There is no job with ths title {url}")
