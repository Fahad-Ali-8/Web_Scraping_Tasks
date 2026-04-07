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

# Extracting all data i need
catogary = []




time.sleep(5)


