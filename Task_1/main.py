from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
import pandas as pd

url = "https://remoteok.com/"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

# Setting up selenium
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# Opening the website
print("opening job site...")
driver.get(url)
time.sleep(5)

# scrolling to load more jobs
print("Scrolling to load more jobs")
for i in range(5):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(2)

# parsing with beautifulsoup
print("parsing jobs with beautifulsoup")
soup = BeautifulSoup(driver.page_source,"lxml")
driver.quit()

# creating an empty list so that later i can append all data
jobs = []

# finding all the data
job_rows = soup.select("tr.job")
for job in job_rows:
    title = job.select_one("h2[itemprop='title']")
    name = job.select_one("span.companyLink")
    location = job.select_one("div.location")
    job_link = job.get("data-href")
    tags = [tag.text.strip() for tag in job.select("span.tag")]

    title = title.text.strip() if title else "N/A"
    name = name.text.strip() if name else "N/A"
    location = location.text.strip() if location else "Remote"
    job_link = "https://remoteok.com/" +job_link if job_link else "N/A"
    tags = tags if tags else "N/A"

    # only printing jobs that are related to software engineering
    if "Software" in title:
        jobs.append({
        "job_title"     :title,   
        "compnay name"     :name,
        "compnay location" :location,
        "job link"         :job_link,
        "tags"             :tags
        })

# saving data to csv
if jobs:
    df = pd.DataFrame(jobs)
    df.to_csv("Task_1/jobs.csv", index=False, encoding="utf-8")
    print(f"\n Scraped {len(jobs)} jobs successfully!")
    print("Saved to jobs.csv")
    # print(df.head())
else:
    print("No jobs found!")