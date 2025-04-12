from bs4 import BeautifulSoup
import requests
import tldextract
from model import Vacancy
from datetime import datetime
import re
import json
import locale

def parseJob(url: str):

    domains = ("work.ua", "robota.ua", "dou.ua")

    domain = tldextract.extract(url)
    # print(f"!!!{domain.registered_domain}!!!")

    if domain.registered_domain not in domains:
        return "Domain not supported"
   
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    }
    # print(headers)

    try:
        # print(url)
        html = requests.get(url, headers=headers)
        # print (html.status_code)
        # print(html.text)
        if html.status_code != 200:
            return "Can't parse job"
    except requests.exceptions.RequestException:
        return "Can't contact site"
    
    if domain:
        match domain.registered_domain:
            case "work.ua":
                job = parseJobWorkUa(html.text, url)
            case "robota.ua":
                job = parseJobRobotaUa(url)
            case "dou.ua":
                job = parseJobDouUa(html.text, url)
        if job:
            job.url = [url]
            job.site = domain.registered_domain
            return job
        else:
            return "Can't parse job"

# Parcer for robota.ua
def parseJobRobotaUa(url: str):
    
    # print(url)

    # x = re.search(r"vacancy[0-9]+", url)
    x = re.search(r"vacancy([0-9]+)", url)
    #print(x.groups()[0])
    if not(x):
        return 0
    jobId = x.groups()[0]
    #print(jobId)

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
        #job.addedOnSite = datetime.strptime(vacancy_json['sortDate'], "%Y-%m-%dT%H:%M:%S.%f")
        job.addedOnSite = datetime.strptime(vacancy_json['sortDate'][:16], "%Y-%m-%dT%H:%M")
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
        # print(schedules)
        for schedule in schedules:
            if 'name' in schedule:
                list.append(schedule['name'])
    badges = get_attr(lambda: vacancy_json['badges'])
    if badges:
        # print(badges)
        for badge in badges:
            if 'name' in badge:
                list.append(badge['name'])
    benefits = get_attr(lambda: vacancy_json['company']['miniProfile']['benefits'])
    if benefits:
        # print(benefits)
        for benefit in benefits:
            if 'name' in benefit:
                list.append(benefit['name'])

    job.conditions = ', '.join([str(x) for x in list if x != None and x != ''])

    job.closed = not get_attr(lambda: vacancy_json['isActive1'])
    # print(job.closed)

    return job

# Parcer for work.ua
def parseJobWorkUa(html_text: str, url: str):
    
    soup = BeautifulSoup(html_text, 'lxml')

    job = Vacancy()

    try:
        position_tag = soup.find('h1', id='h1-name')
        #print(position_tag)
        job.position = position_tag.text#.contents[0]
        #print(job.position)
    except:
        return 0

    try:
        description_tag = soup.find('div', id='job-description')
        #print(description_tag.text[:100])
        job.description = "".join([str(x) for x in description_tag.contents])
        #print(job.description[:100])
    except:
        return 0

    try:
        date_tag = soup.find('time')
        #print(date_tag.attrs['datetime'])
        # date_time = datetime.strptime(date_tag.attrs['datetime'], "%Y-%m-%d %H:%M:%S")
        date_time = datetime.strptime(date_tag.attrs['datetime'][:16], "%Y-%m-%d %H:%M")
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
        address_tag = soup.find('span', class_='glyphicon-map-marker').find_parent()
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

# Parcer for work.ua
def parseJobDouUa(html_text: str, url: str):
    
    soup = BeautifulSoup(html_text, 'lxml')
    # print(soup)
    job = Vacancy()

    try:
        position_tag = soup.find('h1')
        # print(position_tag)
        isClosed = re.search(r"вакансія неактивна", position_tag.text)
        if isClosed:
            job.closed = True
            job.position = position_tag.text.replace(f" (вакансія неактивна)", "")
        else:        
            job.position = position_tag.text
        # print (job.closed)
        # print(job.position)
    except:
        return 0

    try:
        description_tag = soup.find('div', class_='b-typo vacancy-section')
        #print(description_tag.text[:1000])
        job.description = "".join([str(x) for x in description_tag.contents])
        #print(job.description[:1000])
    except:
        return 0

    try:
        date_tag = soup.find('div', class_='date')
        # print(date_tag.text)
        date_str = re.search(r"[0-9][0-9]? .+ [0-9]{4}", date_tag.text)
        # print(date_str.group())
        locale.setlocale(locale.LC_ALL, 'uk_UA.utf8')
        date_time = datetime.strptime(date_str.group(), "%d %B %Y")
        locale.setlocale(locale.LC_ALL, 'C.utf8')
        # print(date_time)
        job.addedOnSite = date_time
        # print(job.addedOnSite)
    except:
        return 0
    
    try:
        salary_tag = soup.find('span', class_='salary')
        # print(salary_tag)
        if salary_tag.text:
            job.salary = salary_tag.text
            # print(job.salary)
    except:
        pass

    try:
        company_tag = soup.find('div', class_='l-n').find('a')
        #print(company_tag)
        if company_tag.text:
            job.organization = company_tag.text
            #print(job.organization)
    except:
        pass

    #print(job)
    return job


#parseJob('https://www.work111.ua/234/')
# status = parseJob('https://jobs.dou.ua/companies/obltelekom/vacancies/296214/')
# status = parseJob('https://robota.ua/company768991/vacancy10501268')
# status = parseJob('https://robota.ua/company1225366/vacancy10514772')
# status = parseJob('https://robota.ua/company1247745/vacancy10160894?cre=sauron&ref=recom_score&pos=dkp_recom_vacancy_hot')
# status = parseJob('https://robota.ua/company1225366/vacancy8564929?ref=search&cre=search_new&pos=dkp_search_new')

# status = parseJob('https://www.work.ua/en/jobs/6451234/')

# status = parseJob('https://robota.ua/company12801971/vacancy10425207')
# status = parseJob('https://jobs.dou.ua/companies/ooo-ukrnet/vacancies/299957/')
# print(status)
# print(status.recruiterContacts)



