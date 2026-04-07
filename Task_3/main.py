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


driver = webdriver.Chrome()
driver.get("https://automationexercise.com/login")
headers = {"User-Agent": "Chrome/5.0"}
# Checking if the websites loads or not
assert "Automation Exercise" in driver.title
print("Home page is visible successfully")

# login
# filling email and password 
wait = WebDriverWait(driver, 10)
email = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email']")))
email.send_keys(f"assassin41@gmail.com")

password = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@data-qa='login-password']")))
password.send_keys(f"Assassin_888")

# clicking on login button
login = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-qa='login-button']")))
login.click()



# clicking products button
products_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='/products']")))
products_btn.click()

soup = BeautifulSoup(driver.page_source, "html.parser")
product_links = soup.select("a[href^='/product_details/']")
urls = []
for link in product_links:
    full_url = urljoin("https://automationexercise.com", link["href"])
    urls.append(full_url)

print(urls)


products = []

for url in urls:
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-information")))  # wait for product info to load
    # time.sleep(2)  # let the page load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    print(f"Visiting: {url}")
    name = soup.select_one(".product-information h2")
    price = soup.select_one(".product-information span span")
    category = soup.select_one(".product-information p")
    
    name2 = name.text.strip()
    price2 = price.text.strip() 
    category2 = category.text.strip() if category else "N/A"
    # products.append({
    #     "name": name,
    #     "price": price,
    #     "category": category
    # })
    
    print(f"Scraped: {name2} | {price2} | {category2}")
time.sleep(5)


