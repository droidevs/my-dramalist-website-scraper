# This file will contain the code to scrape drama links.

from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from config import driver
import time

BASE_URL = "https://mydramalist.com"

def get_all_dramas_links(page=1, retries=0, max_retries=None, delay=0):
    """
    Scrape all drama links from the given MDL search page.
    Retries automatically on failure until success (or max_retries if set).
    """
    url = f"{BASE_URL}/search?adv=titles&ty=68&so=date&page={page}"
    print(f"🌐 Fetching page {page} (attempt {retries+1})")

    try:
        driver.get(url)
        elements = driver.find_elements(By.CSS_SELECTOR, "a.block")
        links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]

        l = len(links)
        if l == 20:
            print(f"✅ Found {l} drama links on page {page}")
        else:
            raise Exception("data not complete")
        return links

    except (TimeoutException, WebDriverException, Exception) as e:
        print(f"❌ Error on page {page}: {e}")

        if max_retries is None or retries < max_retries:
            print(f"🔄 Retrying in {delay} seconds... (attempt {retries+2})")
            time.sleep(delay)
            return get_all_dramas_links(page, retries=retries+1, max_retries=max_retries, delay=delay)
        else:
            print(f"🚫 Failed after {max_retries} attempts for page {page}")
            return []
