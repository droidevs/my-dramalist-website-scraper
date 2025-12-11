# This file will contain the code to scrape drama details.
from config import driver, debug
from util.utils import safe_find
import time, re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

def scrape_drama(page= 0,drn = 0,url="", retries=0):
    """Scrape a single drama page with retry support."""
    print(f"Started Scraping for drama with link << {url} >> ",)
    try:
        driver.get(url)
        # drama_id from URL
        drama_id = int(re.search(r"/(\d+)-", url).group(1))

        # Title & metadata
        title = safe_find("h1.film-title")
        if debug:
            print(f"1. title retrieved : {title}")
        native_title = safe_find("//li[b[contains(text(), 'Native Title')]]/a", xpath= True)
        if debug:
            print(f"2. native title retrieved : {native_title}")
        aka_titles = safe_find("//li[b[contains(text(),'Also Known As')]]/span[@class='mdl-aka-titles']",xpath = True)
        if debug:
            print(f"3. aka title retrieved : {aka_titles}")
        # Description
        description = safe_find("div.show-synopsis")
        if debug:
            print(f"4. desc retrieved : {description}")
        details = driver.find_elements(By.CSS_SELECTOR, ".show-detailsxss li")
        year, country, dtype, episodes, duration, content_rating, ranked, popularity, rating = \
            None, None, None, None, None, None, None, None, None

        for li in details:
            txt = li.text.strip()
            print(txt)
            if txt.startswith("Country:"):
                country = txt.replace("Country:", "").strip()
            elif txt.startswith("Type:"):
                dtype = txt.replace("Type:", "").strip()
            elif txt.startswith("Episodes:"):
                episodes = int(re.sub(r"\D", "", txt.replace("Episodes:", "").strip()) or 0)
            elif txt.startswith("Duration:"):
                duration = txt.replace("Duration:", "").strip()
            elif txt.startswith("Content Rating:"):
                content_rating = txt.replace("Content Rating:", "").strip()
            elif txt.startswith("Ranked:"):
                ranked = int(re.sub(r"\D", "", txt.replace("Ranked:", "")) or 0)
            elif txt.startswith("Popularity:"):
                popularity = int(re.sub(r"\D", "", txt.replace("Popularity:", "")) or 0)
            elif txt.startswith("Aired:"):
                match = re.search(r"\b(\d{4})\b", txt)
                if match:
                    year = int(match.group(1))
            elif txt.startswith("Score:"):
                match = re.search(r"([\d.]+)", txt)
                if match:
                    rating = float(match.group(1))

    except WebDriverException as e:
        print(f"⚠️ Error scraping {url}, retrying... attempt {retries+1}")
        print(e.msg)
        time.sleep(3)
        scrape_drama(page,drn, url, retries=retries+1)
