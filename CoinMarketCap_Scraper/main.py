from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import mysql.connector
from dotenv import load_dotenv
import time
import os

load_dotenv()
# config
BASE_URL = "https://coinmarketcap.com/?page={page_num}"
TOTAL_PAGES = 50
 
# database setup 
def init_db():
    conn = mysql.connector.connect(
        host     = "127.0.0.1",
        port     = 3306,
        user     = "root",
        password = os.getenv("DB_PASSWORD")
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS Crypto_DB")
    cursor.execute("USE Crypto_DB")
    cursor.execute("DROP TABLE IF EXISTS crypto")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crypto (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            name        VARCHAR(100),
            icon        VARCHAR(20),
            price       VARCHAR(50),
            change_24h  VARCHAR(20),
            marketcap   VARCHAR(50)
        )
    """)
    conn.commit()
    print("Database and table ready.")
    return conn, cursor

# save one row
def save_row(cursor, conn, data):
    cursor.execute("""
        INSERT INTO crypto (name, icon, price, change_24h, marketcap)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data["name"],
        data["icon"],
        data["price"],
        data["change_24h"],
        data["marketcap"]
    ))
    conn.commit()


# setup
def init_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

def scroll_page(driver):    
    for _ in range(20):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(0.5)
    
    time.sleep(3)  
    print("Scrolling done.")

# scraping data
def scrape_data(driver,cursor,conn,page_num):
    url = BASE_URL.format(page_num=page_num)
    driver.get(url)
    wait = WebDriverWait(driver , 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody tr")))
    # scroll to load all rows
    scroll_page(driver)

    soup = BeautifulSoup(driver.page_source,"lxml")

    # targeting data
    rows = soup.select("tbody tr")
    saved = 0
    for row in rows:
        name       = row.select_one("td:nth-child(3) p")
        icon       = row.select_one(".coin-item-symbol")
        price      = row.select_one("td:nth-child(4) span")
        change_24h = row.select_one("td:nth-child(5) span")
        marketcap  = row.select_one("td:nth-child(8) span")

        data = {
            "name"      : name.get_text(strip=True)       if name       else "N/A",
            "icon"      : icon.get_text(strip=True)       if icon       else "N/A",
            "price"     : price.get_text(strip=True)      if price      else "N/A",
            "change_24h": change_24h.get_text(strip=True) if change_24h else "N/A",
            "marketcap" : marketcap.get_text(strip=True)  if marketcap  else "N/A",
        }

        save_row(cursor, conn, data)
        saved += 1

    # print(f"[Page {page_num}/{TOTAL_PAGES}] Saved {saved} rows to database.")

# main
def main():
    conn, cursor = init_db()
    driver = init_driver()

    try:
        for page_num in range(1, TOTAL_PAGES + 1):
            scrape_data(driver,cursor, conn,page_num)
            print(f"[Page {page_num}/{TOTAL_PAGES}] Scraped successfully.")
    finally:
        time.sleep(5)
        driver.quit()
        cursor.close()
        conn.close()
        print("Done! All data saved to MySQL.")


if __name__ == "__main__":
    main()


