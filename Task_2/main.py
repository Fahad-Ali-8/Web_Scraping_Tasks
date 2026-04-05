from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import time
import pandas as pd

url = "https://books.toscrape.com/"
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--headless")

# Setting up selenium
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service , options=options)
wait = (driver,15)

# Opening Website
print("Opening website")
driver.get(url)
time.sleep(5)

# Parsing with beautifulsoup
print("Parcing with beautifulsoup")
soup = BeautifulSoup(driver.page_source,"lxml")
# driver.quit()

# finding all elements
book_rows = soup.select("li.col-xs-6")
for book in book_rows:
    title = book.select_one("h3 > a")
    price = book.select_one("div > p")

    # Rating
    rating_word = book.select_one("p.star-rating")["class"][1]
    rating_map = {
        "One": 1, "Two": 2, "Three": 3, "Four": 4,"Five": 5,
    }
    rating = rating_map[rating_word]
    avalability = book.select_one("p.instock")

    # Finding book category
    book_link = book.select_one("h3 > a")["href"]
    book_url = "https://books.toscrape.com/" + book_link 
    driver.get(book_url)
    detail_soup = BeautifulSoup(driver.page_source, "lxml")
    category = detail_soup.select("ul.breadcrumb li")[2].text.strip()
    
    print(title.text.strip())
    print(price.text.strip())
    print(rating)
    print(avalability.text.strip())
    print(category)
    print(book_url)
    print("")
driver.quit()