from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv
import time

# config
BASE_URL = "https://www.beauchampestates.com"
SALE_URL = f"{BASE_URL}/london/luxury-properties-for-sale-in-london"
RENT_URL = f"{BASE_URL}/london/luxury-properties-for-rent-in-london" 
OUTPUT_FILE = "beauchamp_all.csv"

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

# parcing html
def get_soup(driver, url):
    driver.get(url)
    time.sleep(3)
    scroll_page(driver)
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
        })

        # deduplicate by url
    seen = set()
    unique = []
    for item in listings:
        if item["url"] not in seen:
            seen.add(item["url"])
            unique.append(item)
    
    return unique

# saving data to csv
def save_to_csv(listings, filename, write_header=False):
    fieldnames = ["title", "address", "price", "beds", "baths", "sqft", "url", "type"]
    mode = "w" if write_header else "a"
    with open(filename, mode, newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(listings)

# main
def main():
    print("Starting Selenium driver...")
    driver = get_driver()

    try:
        # --- FOR SALE ---
        print("Loading sale listings...")
        soup = get_soup(driver, SALE_URL)
        sale_listings = scrape_data(soup, listing_type="sale")
        save_to_csv(sale_listings, OUTPUT_FILE, write_header=True)
        print(f"Sale done: {len(sale_listings)} listings saved.")

        # --- FOR RENT ---
        print("Loading rent listings...")
        soup = get_soup(driver, RENT_URL)
        rent_listings = scrape_data(soup, listing_type="rent")
        save_to_csv(rent_listings, OUTPUT_FILE, write_header=False)
        print(f"Rent done: {len(rent_listings)} listings saved.")

        print(f"Total: {len(sale_listings) + len(rent_listings)} listings in {OUTPUT_FILE}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
