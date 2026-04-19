from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pyodbc

# config
BASE_URL = "https://www.beauchampestates.com"
SALE_URL = f"{BASE_URL}/london/luxury-properties-for-sale-in-london"
RENT_URL = f"{BASE_URL}/london/luxury-properties-for-rent-in-london" 
OUTPUT_FILE = "beauchamp_all.csv"

# db config
SERVER = "DESKTOP-9NI8UQ0"
DATABASE = "BeauChamp_DB"
CONN_STR = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"

# ── db ──────────────────────────────────────────────────────────────────────

def get_connection():
    return pyodbc.connect(CONN_STR)

def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (
            SELECT * FROM sysobjects WHERE name='properties' AND xtype='U'
        )
        CREATE TABLE properties (
            id          INT IDENTITY(1,1) PRIMARY KEY,
            title       NVARCHAR(500),
            address     NVARCHAR(500),
            price       NVARCHAR(100),
            beds        NVARCHAR(50),
            baths       NVARCHAR(50),
            sqft        NVARCHAR(50),
            url         NVARCHAR(1000),
            type        NVARCHAR(10),
            contact     NVARCHAR(100),
            image_url   NVARCHAR(1000)
        )
    """)
    conn.commit()
    print("Table ready.")

def insert_listing(conn, listing):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO properties
            (title, address, price, beds, baths, sqft, url, type, contact, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        listing["title"],
        listing["address"],
        listing["price"],
        listing["beds"],
        listing["baths"],
        listing["sqft"],
        listing["url"],
        listing["type"],
        listing["contact"],
        listing["image_url"],
    )
    conn.commit()

# opening browser
def get_driver():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    return driver

# scrolling to load more data
def scroll_page(driver):
    for _ in range(40):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(1)
    time.sleep(3)
    print("Scrolling done.")

# parcing main page
def get_soup(driver, url):
    driver.get(url)
    time.sleep(3)
    scroll_page(driver)
    return BeautifulSoup(driver.page_source, "html.parser")

# parcing single property page
def get_detail_soup(driver, url):
    driver.get(url)
    time.sleep(3)
    return BeautifulSoup(driver.page_source, "html.parser")

# targeting the css selectors
def scrape_data(soup, listing_type):
    cards = soup.select("article")
    listings = []

    for card in cards:
        # Title & URL
        link_tag = card.select_one("a.expand-interaction__action")
        title = link_tag.get_text(strip=True) if link_tag else "N/A"
        url = (BASE_URL + link_tag["href"]) if link_tag and link_tag.get("href") else "N/A"

        if url == "N/A":
            continue

        # Address
        address_tag = card.select_one("p.block")
        address = address_tag.get_text(strip=True) if address_tag else "N/A"

        # Price
        price = "N/A"
        for div in card.select("div"):
            text = div.get_text(strip=True)
            if text.startswith("£"):
                price = text
                break

        # Beds, Baths, Sqft
        beds = baths = sqft = "N/A"
        for tag in card.select("p, span"):
            text = tag.get_text(strip=True)
            if "bed" in text and beds == "N/A":
                beds = text
            elif "bath" in text and baths == "N/A":
                baths = text
            elif "sqft" in text and sqft == "N/A":
                sqft = text

        listings.append({
            "title": title,
            "address": address,
            "price": price,
            "beds": beds,
            "baths": baths,
            "sqft": sqft,
            "url": url,
            "type": listing_type,
            "contact": "N/A",
            "image_url": "N/A",
        })

        # deduplicate by url
    seen = set()
    unique = []
    for item in listings:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    
    return unique

# scrapinf single property page 
def scrape_detail(soup):
    # contact number
    contact = "N/A"
    tel_tag = soup.select_one("a[href^='tel:']")
    if tel_tag:
        contact = tel_tag.get_text(strip=True).replace("Tel: ", "")

    # first image url
    image_url = "N/A"
    img_tag = soup.select_one("img[src*='admin.beauchampestates.com']")
    if img_tag:
        image_url = img_tag["src"]

    return contact, image_url


# main
def main():
    print("Connecting to SQL Server...")
    conn = get_connection()
    create_table(conn)
    driver = get_driver()
    print("Starting Selenium driver...")    
    try:
        # --- FOR SALE ---
        print("Loading sale listings...")
        soup = get_soup(driver, SALE_URL)
        sale_listings = scrape_data(soup, listing_type="sale")
        print(f"Found {len(sale_listings)} sale listings.")

        # --- FOR RENT ---
        print("Loading rent listings...")
        soup = get_soup(driver, RENT_URL)
        rent_listings = scrape_data(soup, listing_type="rent")
        print(f"Found {len(rent_listings)} rent listings.")

        all_listings = sale_listings + rent_listings
        print(f"Total: {len(all_listings)} listings. Now visiting detail pages...")

        # --- DETAIL PAGES ---
        for i, listing in enumerate(all_listings):
            print(f"[{i+1}/{len(all_listings)}] {listing['url']}")
            detail_soup = get_detail_soup(driver, listing["url"])
            contact, image_url = scrape_detail(detail_soup)
            listing["contact"] = contact
            listing["image_url"] = image_url

            insert_listing(conn, listing)
            time.sleep(1)  # polite delay between requests

        print(f"Done. {len(all_listings)} listings inserted into BeauChamp_DB.")

    finally:
        driver.quit()
        conn.close()

if __name__ == "__main__":
    main()
