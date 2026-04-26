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

# db config
SERVER = "DESKTOP-9NI8UQ0"
DATABASE = "BeauChamp_DB"
CONN_STR = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;"

# db 
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
            phone       NVARCHAR(100),
            whatsapp    NVARCHAR(100),
            email       NVARCHAR(100),
            image_url   NVARCHAR(1000)
        )
    """)
    conn.commit()

    cursor.execute("TRUNCATE TABLE properties")  
    conn.commit()
    print("Table ready and cleared.")


def insert_listing(conn, listing):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO properties
            (title, address, price, beds, baths, sqft, url, type, phone, whatsapp, email, image_url)
        VALUES (?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        listing["title"],
        listing["address"],
        listing["price"],
        listing["beds"],
        listing["baths"],
        listing["sqft"],
        listing["url"],
        listing["type"],
        listing["phone"],
        listing["whatsapp"],
        listing["email"],
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


def get_urls_from_listings(soup):
    urls = []
    seen = set()

    cards = soup.select("article")
    for card in cards:
        link_tag = card.select_one("a.expand-interaction__action")
        if not link_tag or not link_tag.get("href"):
            continue
        url = BASE_URL + link_tag["href"]
        if url not in seen:
            seen.add(url)
            urls.append(url)

    return urls

# targeting the css selectors
def scrape_data(soup):

    # title
    title_tag = soup.select_one("h1.type-style-2")
    title = title_tag.get_text(strip=True) if title_tag else "N/A"

    # address
    address_tag = soup.select_one("p.type-style-eyebrow.mb-8")
    address = address_tag.get_text(strip=True) if address_tag else "N/A"

    # price
    price_tag = soup.select_one("p.type-style-2")
    price = price_tag.get_text(strip=True) if price_tag else "N/A"

     # beds, baths, sqft — all in same grid structure
    beds = baths = sqft = "N/A"
    grid_divs = soup.select("div.grid p.type-style-eyebrow")
    for label_tag in grid_divs:
        label = label_tag.get_text(strip=True).lower()
        value_tag = label_tag.find_next_sibling("p")
        value = value_tag.get_text(strip=True) if value_tag else "N/A"
        if "bed" in label:
            beds = value
        elif "bath" in label:
            baths = value
        elif "int" in label:
            sqft = value

    # phone
    phone = "N/A"
    phone_tag = soup.select_one("a[href^='tel:']")
    if phone_tag:
        phone = phone_tag.get_text(strip=True).replace("Tel:", "").strip() if phone else "N/A"

    # whatsapp
    whatsapp = "N/A"
    wa_tag = soup.select_one("a[href^='https://wa.me/+']")
    if wa_tag:
        span = wa_tag.select_one("span")
        whatsapp = span.get_text(strip=True).replace("Whatsapp:", "").strip() if span else "N/A"

    # email
    email = "N/A"
    email_tag = soup.select_one("a[href^='mailto:']")
    if email_tag:
        email = email_tag["href"].replace("mailto:", "")

    # image
    image_url = "N/A"
    img_tag = soup.select_one("img.w-full[src*='admin.beauchampestates.com']")
    if img_tag:
        image_url = img_tag["src"]

    return {
        "title": title,
        "address": address,
        "price": price,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "phone": phone,
        "whatsapp": whatsapp,
        "email": email,
        "image_url": image_url,
    }

def process_listings(driver, conn, listings_url, listing_type):
    print(f"\nLoading {listing_type} listings page...")
    soup = get_soup(driver, listings_url)
    urls = get_urls_from_listings(soup)
    print(f"Found {len(urls)} {listing_type} urls. Now visiting each one...")

    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url}")
        detail_soup = get_detail_soup(driver, url)
        data = scrape_data(detail_soup)

        listing = {
            **data,
            "url": url,
            "type": listing_type,
        }

        insert_listing(conn, listing)
        print(f"Saved: {listing['title']}")
        time.sleep(1)


# main
def main():
    print("Connecting to SQL Server...")
    conn = get_connection()
    create_table(conn)

    print("Starting Selenium driver...")
    driver = get_driver()

    try:
        process_listings(driver, conn, SALE_URL, "sale")
        process_listings(driver, conn, RENT_URL, "rent")
    finally:
        driver.quit()
        conn.close()
if __name__ == "__main__":
    main()
