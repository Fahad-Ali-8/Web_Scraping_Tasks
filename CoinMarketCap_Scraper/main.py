from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import os
import csv


# config
BASE_URL = "https://coinmarketcap.com/?page={page_num}"
OUTPUT_FILE = "crypto.csv"
HEADERS = ["name", "icon", "price","24h'%'change", "marketcap"]
TOTAL_PAGES = 5

# setup
def init_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

# WRITE CSV HEADERS UPFRONT (chunk-saving)
def init_csv(filepath):
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
    print(f"CSV initialized: {filepath}")

# APPEND ONE PRODUCT TO CSV 
def save_product(filepath, product):
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(product)

def scroll_page(driver):    
    for _ in range(20):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(0.5)
    
    time.sleep(3)  
    print("Scrolling done.")

# scraping data
def scrape_data(driver,page_num,filepath):
    url = BASE_URL.format(page_num=page_num)
    driver.get(url)
    wait = WebDriverWait(driver , 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr")))
    # scroll to load all rows
    scroll_page(driver)

    soup = BeautifulSoup(driver.page_source,"lxml")

    # targeting data
    rows = soup.select("tbody tr")
    for row in rows:
        name = row.select_one("td:nth-child(3) p")
        icon = row.select_one(".coin-item-symbol")
        price = row.select_one("td:nth-child(4) span")
        _24h_change = row.select_one("td:nth-child(5) span")
        marketcap = row.select_one("td:nth-child(8) span")

        crypto_data = {
        "name"  : name.get_text(strip=True) if name else "N/A",
        "icon"  : icon.get_text(strip=True) if icon else "N/A",
        "price"  : price.get_text(strip=True) if price else "N/A",
        "24h'%'change" : _24h_change.get_text(strip=True) if _24h_change else "N/A",
        "marketcap" : marketcap.get_text(strip=True) if marketcap else "N/A",
        }
        save_product(filepath, crypto_data) 

# main
def main():
    driver = init_driver()
    init_csv(OUTPUT_FILE)

    try:
        for page_num in range(1, TOTAL_PAGES + 1):
            scrape_data(driver,page_num,OUTPUT_FILE)
            print(f"[Page {page_num}/{TOTAL_PAGES}] Scraped successfully.")
    finally:
        time.sleep(5)
        driver.quit()
        print("Done! All data id saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()


