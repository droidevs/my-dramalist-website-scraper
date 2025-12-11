# This file will contain utility functions.

import re
from urllib.parse import urlparse
from config import driver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By



def slugify(text):
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def extract_drama_id(url):
    # From https://mydramalist.com/12345-move-to-heaven → "12345"
    parts = urlparse(url).path.strip("/").split("-")
    return parts[0] if parts else int(re.search(r"/(\d+)-", url).group(1))

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
