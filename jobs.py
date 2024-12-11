import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def internshala(title, internshalla):
    job_url_list = []
    job_title_list = []
    job_salary_list = []
    job_company_name_list = []
    job_location_list = []

    for i in range(1, 5):  # Loop to parse through multiple pages on the website
        # Fetch page content
        response = requests.get(f"https://internshala.com/internships/{title}-internship/page-{i}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'container-fluid')
        #print(len(cards))  # Displays number of job listings on each page

        for card in cards:  # Loop to extract details from each card
            try:
                job_title = card.find('h3', 'job-internship-name').text.strip()
                #print(job_title)
                job_company_name = card.find('p', 'company-name').text.strip()
                #print(job_company_name)
                job_salary = card.find('span', 'stipend').text.strip()
                #print(job_salary)

                # Extract location
                location_container = card.find('div', class_='row-1-item locations')
                location = location_container.find('a').text.strip() if location_container else "Not specified"
                #print(location)

                # Extract job URL
                job_l = card.find('a', 'job-title-href')
                job_url = f"https://internshala.com/{job_l['href']}" if job_l else "Not specified"
                #print(job_url)

                # Check if the job URL already exists in the database
                if job_url in job_url_list:
                    continue  # Skip if the job URL already exists

                # Append details to lists
                job_title_list.append(job_title)
                job_company_name_list.append(job_company_name)
                job_salary_list.append(job_salary)
                job_location_list.append(location)
                job_url_list.append(job_url)

            except AttributeError:
                continue

    # Combine all data into a single list of dictionaries
    jobs_data = [
        {
            "title": job_title_list[i],
            "company_name": job_company_name_list[i],
            "salary": job_salary_list[i],
            "location": job_location_list[i],
            "url": job_url_list[i],
            "scraped_at": datetime.utcnow()  # Add a timestamp for when the data was scraped
        }
        for i in range(len(job_title_list))
    ]

    # Check if the category exists in the collection and only insert new jobs
    existing_jobs = internshalla.find_one({"category": title})

    # If the category exists, compare job URLs to avoid duplicates
    if existing_jobs:
        existing_job_urls = [job['url'] for job in existing_jobs.get(title, [])]

        # Filter out jobs that already exist in the database
        new_jobs = [job for job in jobs_data if job['url'] not in existing_job_urls]

        # Insert new jobs into MongoDB
        if new_jobs:
            internshalla.update_one(
                {"category": title},
                {"$push": {title: {"$each": new_jobs}}},
                upsert=True
            )
    else:
        # If the category doesn't exist, insert all jobs
        internshalla.insert_one({"category": title, title: jobs_data})

