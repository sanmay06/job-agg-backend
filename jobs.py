import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def addDB(job, title, name, location, salary, url, db, website):
    """
    Inserts job data into the database (MongoDB).

    :param job: Job category (e.g., title of the job)
    :param title: Job title
    :param name: Company name
    :param location: Job location
    :param salary: Salary details
    :param url: URL of the job posting
    :param db: MongoDB collection object
    :param website: Source website
    """
    if salary:
        salary_numbers = re.findall(r'\d+', salary)
    #print(salary_numbers,"\t")
        if len(salary_numbers) == 4:
            salary_min = int(salary_numbers[0])*1000+int(salary_numbers[1])  # the first number (10000)
            salary_max = int(salary_numbers[2])*1000+int(salary_numbers[3])  # the second number (10323)
            salary_value = (salary_min + salary_max) / 2  # calculate the average
        elif salary_numbers:
            salary_value = int(salary_numbers[0])*1000+int(salary_numbers[1])  # if only one number is found, use it directly
        else:
            salary_value = 0
    else:
        salary_value = 0

    job_data = {
        "title": title,
        "company_name": name,
        "salary": salary_value,
        "obtained salary":salary,
        "location": location,
        "url": url,
        "scraped_at": datetime.utcnow(),
        "website": website
    }


    db.update_one(
        {"category": job},
        {"$push": {"jobs": job_data}},
        upsert=True
    )

def internshala(title, db, location):
    for i in range(1, 5):
        response=requests.get(f"https://internshala.com/internships/{title}-internship-in-{location}/page-{i}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'container-fluid')

        for card in cards:
            try:
                job_title = card.find('h3','job-internship-name').text
                job_company_name = card.find('p','company-name').text
                job_salary = card.find('span','stipend').text
                location_tag = card.find('div', class_='row-1-item locations')
                job_location = location_tag.text.strip() if location_tag else "Not specified"
                job_url ="https://internshala.com/"+card.find('a','job-title-href')['href']

                addDB(title, job_title, job_company_name, job_location, job_salary, job_url, db, 'Internshala')
            except AttributeError:
                continue

def adzuna(title, db, location):
    base_url = "https://www.adzuna.in/search"
    for i in range(1, 5):
        response = requests.get(f"{base_url}?&q={title}&p={i}&w={location}")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('article', class_='a')

        for card in cards:
            try:
                job_title = card.find('a', class_='text-base').text.strip()
                job_company_name = card.find('div', class_='ui-company').text.strip()
                job_location = card.find('div', class_='ui-location').text.strip()
                job_url = "https://www.adzuna.in/" + card.find('a', class_='text-adzuna-green-500')['href']

                addDB(title, job_title, job_company_name, job_location, "NA", job_url, db, 'Adzuna')
            except AttributeError:
                continue

def Times_job(title, db, location):
    base_url = "https://www.timesjobs.com/candidate/job-search.html?"
    response = requests.get(f"{base_url}?searchType=personalizedSearch&from=submit&searchTextSrc=&searchTextText=&txtKeywords={title}&txtLocation={location}")
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.find_all('li', class_='clearfix')

    for card in cards:
        try:
            job_title = card.find('a').text.strip()
            job_company_name = card.find('h3', class_='joblist-comp-name').text.strip()
            salary_tag = card.find('span', class_='salary')
            job_salary = salary_tag.text.strip() if salary_tag else "Not specified"
            job_location=card.find('li','srp-zindex').text.strip()
            job_l=card.find('a')
            job_url = "https://www.timesjobs.com/"+job_l['href']
            #print(job_url)
            addDB(title, job_title, job_company_name, job_location, job_salary, job_url, db, 'TimesJobs')
        except AttributeError:
            continue

def jobRapido(title, db, location):
    base_url = "https://in.jobrapido.com"
    for i in range(1, 5):
        response = requests.get(f"{base_url}/{title}-jobs-in-{location}?p={i}")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_='result-item')

        for card in cards:
            try:
                job_title = card.find('div', class_='result-item__title').text.strip()
                job_company_name = card.find('div', class_='result-item__company').text.strip()
                job_location = card.find('div', class_='result-item__location').text.strip()
                job_url = card.find('a', class_='result-item__link')['href']

                addDB(title, job_title, job_company_name, job_location, None, job_url, db, 'JobRapido')
            except AttributeError:
                continue
