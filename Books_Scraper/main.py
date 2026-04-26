from bs4 import BeautifulSoup
from selenium import webdriver
import requests
import time 
import pyodbc

# config
BASE_URL = "https://books.toscrape.com/"

# database connection
def get_connection():
    conn = pyodbc.connect(
        "DRIVER={ODBC DRIVER 17 FOR SQL SERVER};"
        "SERVER=DESKTOP-9NI8UQ0;"
        "DATABASE=Scraper_DB;"
        "TRUSTED_CONNECTION=YES;"
    )
    return conn

# saving in database 
def create_table(conn):
    cursor = conn.cursor()
    cursor.execute("""
    IF NOT EXISTS(
        SELECT * FROM sysobjects WHERE name='Books_DB' AND xtype='U'               
    )
    CREATE TABLE Books_DB(
                   id INT IDENTITY(1,1) PRIMARY KEY,
                   title       NVARCHAR(500),
                   price       NVARCHAR(100),
                   avalibility NVARCHAR(100),
                   rating      NVARCHAR(100),
                   catogary    NVARCHAR(100)
    )               
""")
    conn.commit()
    cursor.execute("TRUNCATE TABLE Books_DB")
    conn.commit()
    print("Table is ready and clear")

# insert one book
def insert_book(conn,book):
    cursor = conn.cursor()
    cursor.execute("INSER INTO Books_DB (title,price,avalibility,rating,catogary)(?, ?, ?, ?, ?)",
        book["title"],
        book["price"],
        book["avalibility"],
        book["rating"],
        book["catogary"]
)
    conn.commit()
    cursor.close()
    
# opening browser
def init_driver():
    driver = webdriver.Chrome()
    return driver

# parcing main page

# parcing single book
# targeting css selectors
# main
