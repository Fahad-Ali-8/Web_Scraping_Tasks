from selenium import webdriver
from bs4 import BeautifulSoup
import pyodbc
import time
from selenium.webdriver.support.ui import WebDriverWait
# config
URL = "https://logitech.onlinesalestore.pk/collections/all"
# TOTAL_PAGES = 3

# database connection
def get_connection():
    conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "server=DESKTOP-9NI8UQ0;"
    "Database=logitech_scraper;"
    "Trusted_Connection=yes;"
    )
    return conn

# opening browser
def init_driver():
    driver = webdriver.Chrome()
    return driver

def scroll_page(driver):    
    for _ in range(20):
        driver.execute_script("window.scrollBy(0, 500)")
        time.sleep(0.5)
    
    time.sleep(3)  
    print("Scrolling done.")

# insert into database
def insert_db(cursor,product):
    sql = "INSERT INTO dbo.products (name, price, colours) VALUES (?, ?, ?)"
    values = (product["name"],product["price"], product["colours"])
    cursor.execute(sql,values)

# scraping data
def scrape_data(driver,cursor):
    driver.get(URL)

    # scroll to load all rows
    scroll_page(driver)
    soup = BeautifulSoup(driver.page_source,"lxml")
    products = soup.select("div.col-sm-4.col-xs-6.product-item")

    
    for product in products:
        name = product.select_one("h3.name")
        price = product.select_one(".price-new")
        swatches = product.select("div.swatch-element label")
        colors = []
        for swatch in swatches:
            color = swatch.get("title")
            colors.append(color)

        product = {
            "name" : name.text.strip() if name else "N/A",
            "price" : price.text.strip() if price else "N/A",
            "colours": ", ".join(colors) if colors else "N/A"
        }
        insert_db(cursor,product)

# main 
def main():
    driver = init_driver()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE dbo.products")
    conn.commit()

    try:
        scrape_data(driver,cursor)
        conn.commit()
    finally:
        time.sleep(3)
        driver.quit()
        conn.close()
        print("Done")

if __name__ == "__main__":
    main()
