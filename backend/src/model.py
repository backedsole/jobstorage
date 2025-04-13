from pydantic import BaseModel, Field
import datetime
from uuid import UUID, uuid4

class Vacancy(BaseModel):
    # id: UUID = Field(default_factory=uuid4, alias="_id")
    # url: list[str] | None = None
    # id: UUID = Field(default = None, alias = "_id")
    # url: list[str] | None = None
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


class SiteVacancy(Vacancy):
    url: str | None = None 

class SiteVacancyDB(SiteVacancy):
    id : UUID = Field(default_factory=uuid4, alias="_id")
    mainId : UUID | None = None


class MainVacancy(Vacancy):
    urlList: list[str] | None = None
    applyDate: datetime.datetime | None = None
    applySite: str | None = None
    applyCv: str | None = None

class MainVacancyDB(MainVacancy):
    id : UUID = Field(default_factory=uuid4, alias="_id")
