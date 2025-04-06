from pydantic import BaseModel
import datetime

class Vacancy(BaseModel):
    title: str
    category: str
    position: str
    organization: str
    officeAddress: str
    englishLevel: str
    tags: list
    description: str
    recruiterContacts: str
    addedToBase: datetime.datetime
    addedOnSite: datetime.datetime