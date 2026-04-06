from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from urllib.parse import urljoin

headers = {"User-Agent": "Chrome/5.0"}
url = "https://books.toscrape.com/"
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 15)

print("Opening website")
driver.get(url)

books = []
while True:
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.col-xs-6")))
    print("Scraping page:", driver.current_url)

    soup = BeautifulSoup(driver.page_source, "lxml")
    book_rows = soup.select("li.col-xs-6")

    for book in book_rows:
        title        = book.select_one("h3 > a")["title"]
        price        = book.select_one("p.price_color").text
        rating_word  = book.select_one("p.star-rating")["class"][1]
        rating_map   = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
        rating       = rating_map[rating_word]
        availability = book.select_one("p.instock").get_text(strip=True)

        book_link = book.select_one("h3 > a")["href"].strip()
        book_url  = urljoin(driver.current_url, book_link)

        try:
            response    = requests.get(book_url, headers=headers, timeout=10)
            detail_soup = BeautifulSoup(response.text, "lxml")
            breadcrumbs = detail_soup.select("ul.breadcrumb li")
            category    = breadcrumbs[2].get_text(strip=True) if len(breadcrumbs) > 2 else "Unknown"
        except:
            category = "Unknown"

        books.append({
            "Title"        : title,
            "Price"        : price,
            "Rating"       : rating,
            "Availability" : availability,
            "Category"     : category,
            "Link"         : book_url
        })

    next_buttons = driver.find_elements(By.XPATH, "//li[@class='next']/a")
    if next_buttons:
        next_buttons[0].click()
        wait.until(EC.staleness_of(next_buttons[0]))
        time.sleep(1)
    else:
        print("Last page reached")
        break

driver.quit()

if books:
    df = pd.DataFrame(books)
    df.to_csv("Books.csv", index=False, encoding="utf-8-sig")
    print(f"Scraped {len(books)} books successfully!")
    print("Saved to Books.csv")
else:
    print("No books found!")