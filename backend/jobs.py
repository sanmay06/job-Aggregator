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
    title = title.replace(" ", "-")
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
    print(f"Found {len(jobs_list)} jobs from internshala") 
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
                job_url = card.find('a', class_='text-adzuna-green-500')['href']

                jobs_list.extend(addDB(title, job_title, job_company_name, job_location, "NA", job_url, 'Adzuna'))
            except AttributeError:
                continue
    return jobs_list



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def jobRapido(title, location):
    jobs_list = []
    
    # 1. Setup Chrome Options (Headless = runs in background)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Uncomment this if you don't want to see the browser pop up
    options.add_argument('--disable-gpu')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # 2. Initialize the Browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # 3. Construct URL
    # JobRapido uses specific query params
    url = f"https://in.jobrapido.com/?w={title}&l={location}"
    print(f"Opening Browser for: {url}")
    
    driver.get(url)

    try:
        # 4. CRITICAL: Wait for the "result-item" to actually load
        # This solves the "Empty List" problem by waiting up to 10 seconds for data
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-item"))
        )
        
        # 5. Find elements using Selenium's find_elements
        cards = driver.find_elements(By.CLASS_NAME, "result-item")
        print(f"Cards Found: {len(cards)}")

        for card in cards:
            try:
                # Selenium uses 'find_element' (singular) on the card object
                # Note: We use .get_attribute('href') for links
                
                # Get Link (The <a> tag class is usually 'result-item__link')
                link_element = card.find_element(By.CLASS_NAME, "result-item__link")
                job_url = link_element.get_attribute('href')
                
                # Get Title (It's often inside the link text or a span)
                job_title = link_element.text.strip()
                
                # Get Company
                try:
                    job_company = card.find_element(By.CLASS_NAME, "result-item__company").text.strip()
                except:
                    job_company = "Confidential"

                # Get Location
                try:
                    job_salary = card.find_element(By.CLASS_NAME, "result-item__salary").text.strip()
                except:
                    job_salary = "Not Disclosed"
                
                try:
                    job_location = card.find_element(By.CLASS_NAME, "result-item__location").text.strip()
                except:
                    job_location = location

                print(f"Found: {job_title} | {job_company}")
                
                # Use addDB to format the job for the database
                jobs_list.extend(addDB(title, job_title, job_company, job_location, job_salary, job_url, 'JobRapido'))

            except Exception as e:
                # print(f"Skipping a card: {e}")
                continue

    except Exception as main_e:
        print(f"Main Error: {main_e}")
    
    finally:
        # Close the browser when done
        driver.quit()

    return jobs_list