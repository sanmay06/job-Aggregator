import requests
from bs4 import BeautifulSoup
import re

def clean_and_split_locations(location):
    """Splits multiple locations and removes invalid ones."""
    if not location:
        return []  

    location = location.lower()

    invalid_terms = ["not specified", "remote", "flexible", "hybrid"]

    for term in invalid_terms:
        location = location.replace(f"({term})", "").strip()

    delimiters = [",", "/", "&", " or ", " and "]

    for delimiter in delimiters:
        location = location.replace(delimiter, ",")

    locations = [loc.strip().title() for loc in location.split(",") if loc.strip() and loc not in invalid_terms]

    return locations

def addDB(job, title, name, location, salary, url, website):
    min_salary = None
    max_salary = None
    salary_value = None

    if salary:
        salary_numbers = re.findall(r'\d+', salary)

        if len(salary_numbers) == 2:  # Salary range case
            min_salary = int(salary_numbers[0]) * 1000
            max_salary = int(salary_numbers[1]) * 1000
            salary_value = None  # Set salary to NULL since we have a range
        elif len(salary_numbers) == 4:  # Salary range case
            min_salary = int(salary_numbers[0]) * 1000 + int(salary_numbers[1])
            max_salary = int(salary_numbers[2]) * 1000 + int(salary_numbers[3])
            salary_value = None  
        elif len(salary_numbers) == 1:  # Single salary case
            salary_value = int(salary_numbers[0])

    # Get cleaned list of locations
    location_list = clean_and_split_locations(location)

    # Create a separate job entry for each valid location
    jobs = []
    for loc in location_list:
        jobs.append({
            "job_title": title,
            "link": url,
            "title": job,
            "companyname": name,
            "salary": salary_value,
            "minsalary": min_salary,
            "maxsalary": max_salary,
            "location": loc.lower(),
            "website": website
        })

    
    return jobs  # Return list of job entries

def internshala(title, location):
    jobs_list = []
    for i in range(1, 2):
        response = requests.get(f"https://internshala.com/internships/{title}-internship-in-{location}/page-{i}/")
        # print(f"https://internshala.com/internships/{title}-internship-in-{location}/page-{i}/")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'container-fluid')

        for card in cards:
            try:
                job_title = card.find('h3','job-internship-name').text.strip()
                job_company_name = card.find('p','company-name').text.strip()
                job_salary = card.find('span','stipend').text.strip()
                location_tag = card.find('div', class_='row-1-item locations')
                job_location = location_tag.text.strip() if location_tag else "Not specified"
                job_url = "https://internshala.com/" + card.find('a', 'job-title-href')['href']

                jobs_list.extend(addDB(title, job_title, job_company_name, job_location, job_salary, job_url, 'Internshala'))
            except AttributeError:
                continue
    return jobs_list

def adzuna(title, location):
    jobs_list = []
    base_url = "https://www.adzuna.in/search"
    for i in range(1, 2):
        response = requests.get(f"{base_url}?&q={title}&p={i}&w={location}")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('article', class_='a')

        for card in cards:
            try:
                job_title = card.find('a', class_='text-base').text.strip()
                job_company_name = card.find('div', class_='ui-company').text.strip()
                job_location = card.find('div', class_='ui-location').text.strip()
                job_url = "https://www.adzuna.in/" + card.find('a', class_='text-adzuna-green-500')['href']

                jobs_list.extend(addDB(title, job_title, job_company_name, job_location, "NA", job_url, 'Adzuna'))
            except AttributeError:
                continue
    return jobs_list



def jobRapido(title, location):
    jobs_list = []
    base_url = "https://in.jobrapido.com"
    for i in range(1, 2):
        response = requests.get(f"{base_url}/{title}-jobs-in-{location}?p={i}")
        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', class_='result-item')

        for card in cards:
            try:
                job_title = card.find('div', class_='result-item__title').text.strip()
                job_company_name = card.find('div', class_='result-item__company').text.strip()
                job_location = card.find('div', class_='result-item__location').text.strip()
                job_url = card.find('a', class_='result-item__link')['href']

                jobs_list.extend(addDB(title, job_title, job_company_name, job_location, None, job_url, 'JobRapido'))
            except AttributeError:
                continue
    return jobs_list
