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

# config
BASE_URL = "https://automationexercise.com"
EMAIL = "assassin41@gmail.com"
PASSWORD = "Assassin_888"
OUTPUT_FILE = "Task_3/products.csv"
HEADERS = ["name", "price", "category"]

# driver setup
def init_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome()
    return driver

# WRITE CSV HEADERS UPFRONT (chunk-saving)
def init_csv(filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
    print(f"CSV initialized: {filepath}")

# append one product to csv 
def save_product(filepath, product):
    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(product)

# login
def login(driver, email, password):
    wait = WebDriverWait(driver, 10)
    driver.get(f"{BASE_URL}/login")

    assert "Automation Exercise" in driver.title    
    print("Home page is visible successfully")

    email_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='email']")))
    email_field.send_keys(email)

    password_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@data-qa='login-password']")))
    password_field.send_keys(password)

    login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-qa='login-button']")))
    login_btn.click()
    print("Logged in successfully")



    

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

print(f"Found {len(urls)} products")


products = []

for url in urls:
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".product-information")))  # wait for product info to load
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    name = soup.select_one(".product-information h2")
    price = soup.select_one(".product-information span span")
    category = soup.select_one(".product-information p")
    

    name2 = name.text.strip()
    price2 = price.text.strip() 
    category2 = category.text.strip().replace("Category: ", "")  if category else "N/A"

    products.append({
        "name": name2,
        "price": price2,
        "category": category2
    })
    

# export to CSV
df = pd.DataFrame(products)
df.to_csv("Task_3/products.csv", index=False)
print("Saved to products.csv!")

time.sleep(5)
driver.quit()


