from bs4 import BeautifulSoup
import requests
import tldextract
#from database import fetch_one_job
from model import Vacancy
from datetime import datetime



def parseJobRobotaUa(url: str):
    pass

def parseJobDouUa(url: str):
    pass

def parseJob(url: str):

    domains = ("work.ua", "robota.ua", "dou.ua")

    domain = tldextract.extract(url)
    #print(f"!!!{type(domain.registered_domain)}!!!")

    if domain.registered_domain not in domains:
        return "Domain not supported"
   
    try:
        html = requests.get(url)
        #print (html.status_code)
        if html.status_code != 200:
            return "Can't parse job"
    except requests.exceptions.RequestException:
        return "Can't contact site"
    
    if domain:
        match domain.registered_domain:
            case "work.ua":
                job = parseJobWorkUa(html.text)
            case "robota.ua":
                job = parseJobRobotaUa(html.text)
            case "dou.ua":
                job = parseJobDouUa(html.text)
        if job:
            job.url = url
            job.site = domain.registered_domain
            return job
        else:
            return "Can't parse job"

def parseJobWorkUa(html_text: str):
    
    soup = BeautifulSoup(html_text, 'lxml')

    job = Vacancy()

    try:
        position_tag = soup.find('h1', id='h1-name')
        #print(position_tag)
        #if position_tag.text:
        job.position = position_tag.text#.contents[0]
        #print(job.position)
        #else:
        #return 0
    except:
        return 0

    try:
        description_tag = soup.find('div', id='job-description')
        #print(description_tag.text[:100])
        #if description_tag.contents:
        #job.description = ""#.join(description_tag.contents.)
        # for tag in description_tag.contents:
        #     job.description = job.description.join(tag)
        job.description = "".join([str(x) for x in description_tag.contents])
        #print(job.description[:100])
        #else:
        #return 0
    except:
        return 0
    #newlist = [x for x in fruits if "a" in x]
    try:
        date_tag = soup.find('time')
        #print(date_tag.attrs['datetime'])
        date_time = datetime.strptime(date_tag.attrs['datetime'], "%Y-%m-%d %H:%M:%S")
    #    date_time = datetime.datetime.strptime(date_tag.attrs['datetime'], "%Y-%d %H:%M:%S")
        #print(date_time.strftime("%H:%M %B"))
        job.addedOnSite = date_time
        #print(job.addedOnSite)
    except:
        return 0
    
    try:
        company_tag = soup.find('span', class_='glyphicon-company').find_next_sibling().find('span', class_='strong-500')
        #print(company_tag)
        if company_tag.text:
            job.organization = company_tag.text
            #print(job.organization)
    except:
        pass

    try:
        address_tag = soup.find('span', class_='glyphicon-map-marker').find_parent()#.find_next_sibling()
        #print(address_tag.text[:20])
        if address_tag.text:
            job.officeAddress = address_tag.text.strip()
            #print(job.officeAddress.splitlines()[0])
    except:
        pass

    try:
        contacts_tag = soup.find('span', class_='glyphicon-phone').find_parent()
        #print(contacts_tag)
        if contacts_tag.text:
            job.recruiterContacts = contacts_tag.text
            #print(job.recruiterContacts)
    except:
        pass
    
    try:
        salary_tag = soup.find('span', class_='glyphicon-hryvnia-fill').find_parent()
        #print(salary_tag)
        if salary_tag.text:
            job.salary = " ".join(salary_tag.text.split())
            #print(job.salary)
    except:
        pass
    
    try:
        conditions_tag = soup.find('span', class_='glyphicon glyphicon-tick text-default glyphicon-large').find_parent()
        #print(conditions_tag)
        if conditions_tag.text:
            job.conditions = " ".join(conditions_tag.text.split())
            #print(job.conditions)
    except:
        pass

    #print(job)
    return job


"""     if 
        print(type(domains[0]))
    if  """
"""     job = fetch_one_job(url)
    if job:
        return job """




#parseJob('https://www.work111.ua/234/')
#status = parseJob('https://www.work111.ua/ggggg')
#print(status)
#status = parseJob('https://www.work.ua/en/jobs/6451234/')
#print(status)