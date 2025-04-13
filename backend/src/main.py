from model import Vacancy, SiteVacancy, SiteVacancyDB, MainVacancy, MainVacancyDB
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from parser import parseJob

#App object
app = FastAPI()

from database import (
    fetch_one_job,
    fetch_duplicates,
    # insert_job,
    insert_site_job,
    insert_main_job,
    insert_duplicate,
    fetch_main_job,
    fetch_all_jobs,
    update_job,
    remove_job,
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
    result = 0#await fetch_one_job(url)
    if type(result) == MainVacancyDB:
        response['msg'] = 'Already in database'
    else:
        result = parseJob(url)
        if  type(result) != SiteVacancy:
            response['msg'] =  result
            return response

    response['vacancy'] = result

    duplicates = 0#await fetch_duplicates(result)
    if duplicates:
        response['duplicates'] = duplicates

    return response

#Adding vacancy to database
@app.post("/api/job", response_model=MainVacancyDB)
async def post_job(job: SiteVacancy):
    job.description = ""
    vacancy_dump = job.model_dump()
    # print(vacancy_dump)
    vacancy_dump.pop('url')
    # print(vacancy_dump)
    vacancy_dump['urlList'] = [job.url]
    vacancy_dump['site'] = "Main"
    # print(vacancy_dump)
    mainVacancy = MainVacancy(**vacancy_dump)
    # print(mainVacancy)
    mainVacancyId = await insert_main_job(mainVacancy)
    print(f"\n {mainVacancyId}\n")
    if mainVacancyId:
        # vacancy_dump = job.model_dump()
        # vacancy_dump['mainId'] = mainVacancyId
        vacancy_dump = job.model_dump()
        vacancy_dump['mainId'] = f"{mainVacancyId}"
        print(SiteVacancyDB(**vacancy_dump))
        result = await insert_site_job(SiteVacancyDB(**vacancy_dump))
        if result:
            mainVacancyDB_dump = mainVacancy.model_dump()
            mainVacancyDB_dump['id'] = mainVacancyId
            print(mainVacancyDB_dump)
            return 1#MainVacancyDB(**mainVacancyDB_dump)
        else:
            raise HTTPException(400, "Something went wrong")
    else:
        raise HTTPException(400, "Something went wrong")

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
