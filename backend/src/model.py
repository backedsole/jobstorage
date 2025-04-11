from pydantic import BaseModel
import datetime

class Vacancy(BaseModel):
    url: list[str] | None = None 
    site: str | None = None
    category: str | None = None 
    position: str | None = None 
    organization: str | None = None 
    officeAddress: str | None = None 
    englishLevel: str | None = None 
    tags: list[str] | None = None 
    description: str | None = None 
    recruiterContacts: str | None = None
    salary: str | None = None
    conditions: str | None = None
    addedToBase: datetime.datetime | None = None 
    addedOnSite: datetime.datetime | None = None
    closed: bool = False 
    comment: str | None = None
    applyDate: datetime.datetime | None = None
    applySite: str | None = None
    applyCv: str | None = None