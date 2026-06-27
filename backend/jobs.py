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
    url_slug = title.replace(" ", "-")
    original_title = title  # Preserve the original title for DB storage

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

    for i in range(1, 2):
        url = f"https://internshala.com/internships/{url_slug}-internship-in-{location}/page-{i}/"
        # print(f"Fetching: {url}")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Internshala returned status {response.status_code}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        cards = soup.find_all('div', 'individual_internship')

        for card in cards:
            try:
                job_title_elem = card.find('h2', 'job-internship-name')
                job_title = job_title_elem.text.strip() if job_title_elem else ""

                job_company_name_elem = card.find('p', 'company-name')
                job_company_name = job_company_name_elem.text.strip() if job_company_name_elem else "Unknown"

                job_salary_elem = card.find('span', 'stipend')
                job_salary = job_salary_elem.text.strip() if job_salary_elem else "Not disclosed"

                location_tag = card.find('div', class_='locations')
                job_location = location_tag.text.strip() if location_tag else location

                job_url_elem = card.find('a', 'job-title-href')
                job_url = "https://internshala.com/" + job_url_elem['href'].lstrip('/') if job_url_elem and job_url_elem.has_attr('href') else ""

                if not job_title or not job_url:
                    continue

                jobs_list.extend(addDB(original_title, job_title, job_company_name, job_location, job_salary, job_url, 'Internshala'))
            except Exception as e:
                # print(f"Error parsing card: {e}")
                continue

    print(f"Found {len(jobs_list)} jobs from internshala")
    return jobs_list

def adzuna(title, location):
    jobs_list = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'no-cache',
    }

    url_slug_title = title.replace(" ", "-").lower()
    url_slug_location = location.replace(" ", "-").lower()

    for page in range(1, 3):
        url = f"https://www.adzuna.in/search/{url_slug_title}/{url_slug_location}?p={page}"
        print(f"Fetching Adzuna: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)

            if response.status_code == 429:
                print(f"Adzuna rate limited (429) - skipping")
                return jobs_list
            elif response.status_code != 200:
                print(f"Adzuna returned status {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            cards = soup.find_all('article', class_='a')

            if not cards:
                print(f"Adzuna: No cards found on page {page}")
                continue

            print(f"Adzuna: Found {len(cards)} cards on page {page}")

            for card in cards:
                try:
                    # Job title is in a heading (h2/h3) inside the article
                    heading = card.find(['h2', 'h3'])
                    job_title = heading.text.strip() if heading else ""

                    # Job URL is in the main <a> tag
                    job_link = card.find('a', href=True)
                    if not job_link:
                        continue
                    job_url = job_link['href']

                    if not job_title:
                        job_title = job_link.get('title', '') or job_link.text.strip()

                    if not job_title:
                        continue

                    # Company name
                    company_elem = card.find(class_='ui-company')
                    job_company = company_elem.text.strip() if company_elem else "Not disclosed"

                    # Location — clean up "+N" counters and extra whitespace from Adzuna HTML
                    location_elem = card.find(class_='ui-location')
                    if location_elem:
                        job_loc = location_elem.text.strip()
                        # Remove "+N" location counters (Adzuna shows "+1 location" etc.)
                        job_loc = re.sub(r'\+\d+\s*location[s]?', '', job_loc, flags=re.IGNORECASE)
                        # Collapse whitespace and strip
                        job_loc = re.sub(r'\s+', ' ', job_loc).strip()
                    else:
                        job_loc = location

                    jobs_list.extend(addDB(title, job_title, job_company, job_loc, "NA", job_url, 'Adzuna'))
                except Exception as e:
                    # print(f"Error parsing Adzuna card: {e}")
                    continue

        except requests.exceptions.RequestException as e:
            print(f"Adzuna request error: {e}")
            continue

    print(f"Found {len(jobs_list)} jobs from Adzuna")
    return jobs_list



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def timesjob(title, location):
    jobs_list = []

    # Setup Chrome Options
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Uncomment for background running
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(30)

        # TimesJobs URL structure
        url = f"https://www.timesjobs.com/job-search?searchBy=alnum&txtKeywords={title.replace(' ', '+')}&location={location.replace(' ', '+')}"
        print(f"Opening TimesJobs: {url}")

        driver.get(url)

        # Wait for job results to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "srp-job"))
            )
        except:
            print("TimesJobs: Job results did not load in time")

        # Scroll to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Find job cards
        cards = driver.find_elements(By.CLASS_NAME, "srp-job")
        print(f"TimesJobs: Found {len(cards)} job cards")

        for card in cards:
            try:
                # Job title and link
                title_elem = card.find_element(By.CLASS_NAME, "jr-tit")
                job_title = title_elem.text.strip()
                job_url = title_elem.find_element(By.TAG_NAME, 'a').get_attribute('href')

                # Company name
                try:
                    company_elem = card.find_element(By.CLASS_NAME, "srp-emp")
                    job_company = company_elem.text.strip()
                except:
                    job_company = "Confidential"

                # Location
                try:
                    loc_elem = card.find_element(By.CLASS_NAME, "srp-loc")
                    job_location = loc_elem.text.strip()
                except:
                    job_location = location

                # Salary (often hidden for non-registered users)
                try:
                    salary_elem = card.find_element(By.CLASS_NAME, "job-salary")
                    job_salary = salary_elem.text.strip()
                except:
                    job_salary = "Not disclosed"

                print(f"TimesJobs: {job_title} @ {job_company}")

                jobs_list.extend(addDB(title, job_title, job_company, job_location, job_salary, job_url, 'TimesJobs'))

            except Exception as e:
                # print(f"Skipping TimesJobs card: {e}")
                continue

    except Exception as e:
        print(f"TimesJobs error: {e}")
    finally:
        if driver:
            driver.quit()

    print(f"Found {len(jobs_list)} jobs from TimesJobs")
    return jobs_list


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