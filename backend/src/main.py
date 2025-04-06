from model import Vacancy
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/api/job/{title}", response_model=Vacancy)
async def get_job_by_id(title):
    response = await fetch_one_job(title)
    if response:
        return response
    raise HTTPException(404, f"There is no job with ths title {title}")

@app.post("/api/job", response_model=Vacancy)
async def post_job(job: Vacancy):
    response = await insert_job(job.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")

@app.put("/api/job", response_model=Vacancy)
async def put_job(title:str, desc:str):
    response = await update_job(title, desc)
    if response:
        return response
    raise HTTPException(404, f"There is no job with ths title {title}")

@app.delete("/api/job/{title}")
async def delete_job(title):
    response = await remove_job(title)
    if response:
        return "Succesfully deleted job"
    raise HTTPException(404, f"There is no job with ths title {title}")
