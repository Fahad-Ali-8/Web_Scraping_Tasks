from selenium import webdriver
from bs4 import BeautifulSoup
import pyodbc
import time

# config
URL = "https://telemart.pk/computer.html?page=1"
TOTAL_PAGES = 3

# database connection
def get_connection():
    conn = pyodbc.connect(
    "{ODBC Driver 17 for SQL Server};"
    "server=DESKTOP-9NI8UQ0;"
    "Database=Scraper_db;"
    "Trusted_Connection=yes;"
    )
    return conn

# opening browser
def init_driver():
    driver = webdriver.Chrome()
    return driver

# insert into database
def insert_db(cursor,crypto):
    sql = "INSERT INTO scrapdata (name, price) VALUES (?, ?)"
    values = (crypto["name"],crypto["price"])
    cursor.execute(sql,values)

# scraping data
  
    