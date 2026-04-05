from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

url = "https://remoteok.com/"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")


service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

# Opening the website
print("opening job site...")
driver.get(url)
time.sleep(5)

# scrolling to load more jobs
#print("Scrolling to load more jobs")
#for i in range(5):
#driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
#time.sleep(2)

# parsing with beautifulsoup
print("parsing jobs with beautifulsoup")
soup = BeautifulSoup(driver.page_source,"lxml")
driver.quit()

# # finding all job titles
job_rows = soup.select("tr.job")
for job in job_rows:
    title = job.select_one("h2[itemprop='title']")
    name = job.select_one("span.companyLink")
    location = job.select_one("div.location")
    job_link = job.get("data-href")

    title = title.text.strip() if title else "N/A"
    name = name.text.strip() if name else "N/A"
    location = location.text.strip() if location else "Remote"
    Job_link = "https://remoteok.com/" +job_link if job_link else "N/A"

    print(f"job_title        :{title}")    
    print(f"compnay name     :{name}")
    print(f"compnay location :{location}")
    print(f"job link         :{Job_link}")
    print("")

# # finding company names
# compnay_rows = soup.select("td.compnay")
# for compnay in compnay_rows:
