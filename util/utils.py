# This file will contain utility functions.

import re
from urllib.parse import urlparse
from config import driver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_selenium_driver(headless=False):
    options = Options()
    # Only wait until DOMContentLoaded (not images, styles, etc.)
    options.page_load_strategy = "eager"
    if headless:
        options.add_argument('--headless=new')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36')
    # ✅ Use Service wrapper
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def slugify(text):
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def extract_drama_id(url):
    # From https://mydramalist.com/12345-move-to-heaven → "12345"
    parts = urlparse(url).path.strip("/").split("-")
    return parts[0] if parts else None

def safe_find(selector, attr="text", xpath= False):
    """Safe extractor for Selenium elements."""
    try:
        el = driver.find_element(By.XPATH, selector) if xpath else driver.find_element(By.CSS_SELECTOR, selector)
        return el.get_attribute(attr) if attr != "text" else el.text.strip()
    except NoSuchElementException:
        return None

def safe_finds(selector, attr="text",xpath = False):
    try:
        els = driver.find_elements(By.XPATH, selector) if xpath else driver.find_elements(By.CSS_SELECTOR, selector)
        if attr == "text":
            return [e.text.strip() for e in els]
        else:
            return [e.get_attribute(attr) for e in els]
    except:
        return []
