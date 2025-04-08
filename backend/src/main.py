from model import Vacancy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from parser import parseJob

#App object
app = FastAPI()

from database import (
    fetch_one_job,
    fetch_all_jobs,
    insert_job,
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
    return {"Ping":"Pong"}

@app.get("/api/job")
async def get_jobs():
    response = await fetch_all_jobs()
    return response

@app.get("/api/parse/", response_model=Vacancy|str)
async def parse_job_from_url(url: str):
    response = await fetch_one_job(url)
    if response:
        return response
    else:
        return parseJob(url)
    
@app.get("/api/job/", response_model=Vacancy)
async def get_job_by_id(url: str):
    response = await fetch_one_job(url)
    if response:
        return response
    raise HTTPException(404, f"There is no job with this url {url}")

@app.post("/api/job", response_model=Vacancy)
async def post_job(job: Vacancy):
    response = await insert_job(job.model_dump())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")

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
