from bs4 import BeautifulSoup
import requests
import tldextract
#from database import fetch_one_job
from model import Vacancy
from datetime import datetime
import re
import httpx
import json




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
                job = parseJobRobotaUa(url)
            case "dou.ua":
                job = parseJobDouUa(html.text)
        if job:
            job.url = [url]
            job.site = domain.registered_domain
            return job
        else:
            return "Can't parse job"

# Parcer for robota.ua
def parseJobRobotaUa(url: str):
    
    # jobId = url[url.find("vacancy")+7:url.find("?")+1]
    # print(url[url.find("vacancy")+7:url.find("?")+1])
    # url = url+"?"
    # x = url.find("?")
    # if x == -1:
    #     print(url[url.find("vacancy")+7:])
    # else:
    #     print(url[(url.find("vacancy")+7):(url.find("?"))])

    print(url)

    x = re.search(r"vacancy[0-9]+", url)
    if not(x):
        return 0
    y = re.search(r"[0-9]+", x.group())
    if not(y):
        return 0
    jobId = y.group()
    print(jobId)

    query = '{"query":"query getPublishedVacancy($id: ID!,                     , $trackView: Boolean) {\\n  publishedVacancy(id: $id, trackView: $trackView) {\\n    ...PublishedVacancyPage\\n    __typename\\n  }\\n}\\n\\nfragment PublishedVacancyPage on Vacancy {\\n  title\\n  city {\\n    name\\n    __typename\\n  }\\n  company {\\n    ...CompanyInfo\\n    __typename\\n  }\\n  salary {\\n    comment\\n    amount\\n    amountFrom\\n    amountTo\\n    __typename\\n  }\\n  sortDate\\n  address {\\n    name\\n    district {\\n      name\\n      __typename\\n    }\\n    metro {\\n      name\\n      __typename\\n    }\\n    __typename\\n  }\\n  distanceText\\n  badges {\\n    ...Badge\\n    __typename\\n  }\\n  fullDescription\\n  contacts {\\n    name\\n    phones\\n    socials\\n    __typename\\n  }\\n  isActive\\n  branch {\\n    name\\n    __typename\\n  }\\n  schedules {\\n    name\\n    __typename\\n  }\\n}\\n\\nfragment CompanyInfo on Company {\\n  name\\n  miniProfile {\\n    ...CompanyMiniProfileInfo\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment CompanyMiniProfileInfo on CompanyMiniProfile {\\n  description\\n  benefits {\\n    name\\n    __typename\\n  }\\n  __typename\\n}\\n\\nfragment Badge on PublishedVacancyBadge {\\n  name\\n  __typename\\n}\\n\\n","variables":{"id":"' + jobId + '","trackView":false,"isBrowser":true},"operationName":"getPublishedVacancy"}'
    endpoint = 'https://dracula.robota.ua/'   
    # print(query)

    headers = {"content-type": "application/json",}

    try:
        response = requests.post(endpoint, data=query, headers=headers)

        vacancy_json = (json.loads(response.content.decode('utf-8')))['data']['publishedVacancy']
        print(vacancy_json)
        job = Vacancy()

        job.position = vacancy_json['title'].strip()
        #print(job.position)
        job.addedOnSite = datetime.strptime(vacancy_json['sortDate'], "%Y-%m-%dT%H:%M:%S.%f")
        #print(job.addedOnSite)
        job.description = vacancy_json['fullDescription'].strip()
        #print(job.description)
    except:
        return 0
  
    def get_attr(cb, default = None):
        try:    
            return cb()
        except:
            return default

    job.organization = get_attr(lambda: vacancy_json['company']['name'])

    list = [get_attr(lambda: vacancy_json['contacts']['name'])]
    list += get_attr(lambda: vacancy_json['contacts']['phones'], [])
    list += get_attr(lambda: vacancy_json['contacts']['socials'], [])

    job.recruiterContacts = ', '.join([str(x) for x in list if x != None and x != ''])

    list = [get_attr(lambda: vacancy_json['city']['name'])]
    list.append(get_attr(lambda: vacancy_json['address']['name']))
    list.append(get_attr(lambda: vacancy_json['address']['district']['name']))
    list.append(get_attr(lambda: vacancy_json['address']['metro']['name']))

    job.officeAddress = ', '.join([str(x) for x in list if x != None and x != ''])
    
    list = [get_attr(lambda: vacancy_json['salary']['amount'])]
    list.append(get_attr(lambda: vacancy_json['salary']['amountFrom']))
    list.append(get_attr(lambda: vacancy_json['salary']['amountTo']))
    list.append(get_attr(lambda: vacancy_json['salary']['comment']))
    
    job.salary = ', '.join([str(x) for x in list if x != None and x != ''])
   
    list = []
    schedules = get_attr(lambda: vacancy_json['schedules'])
    if schedules:
        print(schedules)
        for schedule in schedules:
            if 'name' in schedule:
                list.append(schedule['name'])
    badges = get_attr(lambda: vacancy_json['badges'])
    if badges:
        print(badges)
        for badge in badges:
            if 'name' in badge:
                list.append(badge['name'])
    benefits = get_attr(lambda: vacancy_json['company']['miniProfile']['benefits'])
    if benefits:
        print(benefits)
        for benefit in benefits:
            if 'name' in benefit:
                list.append(benefit['name'])

    job.conditions = ', '.join([str(x) for x in list if x != None and x != ''])

    return job



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
# status = parseJob('https://robota.ua/company768991/vacancy10501268')
status = parseJob('https://robota.ua/company1225366/vacancy10514772')
# status = parseJob('https://robota.ua/company1247745/vacancy10160894?cre=sauron&ref=recom_score&pos=dkp_recom_vacancy_hot')
# status = parseJob('https://robota.ua/company1225366/vacancy8564929?ref=search&cre=search_new&pos=dkp_search_new')
print(status)
#status = parseJob('https://www.work.ua/en/jobs/6451234/')
# print(status.recruiterContacts)



