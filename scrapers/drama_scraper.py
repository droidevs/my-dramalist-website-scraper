# This file will contain the code to scrape drama details.
from config import driver, debug
from util.utils import safe_find
from conn import conn, cur
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
        # Save drama
        cur.execute("""
            INSERT OR REPLACE INTO dramas
            (drama_id, title, native_title, aka_titles, year, country, type, episodes,
             duration, rating, ranked, popularity, content_rating, description, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (drama_id, title, native_title, aka_titles, year, country, dtype,
              episodes, duration, rating, ranked, popularity, content_rating,
              description, url))

        # ---------- TAGS ----------
        tags = driver.find_elements(By.CSS_SELECTOR, "li.show-tags span a")
        for t in tags:
            tag_name = t.text.strip()
            href = t.get_attribute("href")
            tag_id = int(re.search(r"th=(\d+)", href).group(1))
            if debug:
                print(f"tag {tag_id} -> {tag_name}")
            # insert tag
            cur.execute("INSERT OR IGNORE INTO tags (tag_id, name) VALUES (?, ?)", (tag_id, tag_name))
            # relation
            cur.execute("INSERT OR IGNORE INTO drama_tags (drama_id, tag_id) VALUES (?, ?)", (drama_id, tag_id))

        # ---------- CAST ----------
        # open cast page explicitly
        cast_url = url + "/cast"
        driver.get(cast_url)
        #time.sleep(2)

        # find the box-body containing cast/crew info
        box_body = driver.find_element(By.CSS_SELECTOR, "div.box-body")

        # get all role sections
        sections = box_body.find_elements(By.CSS_SELECTOR, "h3.header.b-b.p-b")

        for section in sections:
            role_name = section.text.strip()  # e.g., "Director", "Composer", "Main Role", etc.

            # the corresponding <ul> is the next sibling
            ul = section.find_element(By.XPATH, "following-sibling::ul[1]")
            li_items = ul.find_elements(By.CSS_SELECTOR, "li.list-item")

            for li in li_items:
                try:
                    a_tag = li.find_element(By.CSS_SELECTOR, "a.text-primary")
                    cast_name = a_tag.text.strip()
                    href = a_tag.get_attribute("href")
                    cast_id_match = re.search(r"/people/(\d+)", href)
                    if cast_id_match:
                        cast_id = int(cast_id_match.group(1))
                    else:
                        continue

                    # sometimes the role is in a small tag inside the div
                    role_detail = ""
                    try:
                        role_detail = li.find_element(By.CSS_SELECTOR, "small").text.strip()
                    except:
                        role_detail = role_name  # fallback to section name

                    if debug:
                        print(f"{role_name} -> {cast_name} ({role_detail})")

                except Exception as e:
                    print("Skipping an entry:", e)
                    continue

        conn.commit()
        
        print(f" page {page} drama {drn} -> ✅ Scraped drama {title} ({drama_id})")

    # ... exception handling
    except WebDriverException as e:
        print(f"⚠️ Error scraping {url}, retrying... attempt {retries+1}")
        print(e.msg)
        time.sleep(3)
        scrape_drama(page,drn, url, retries=retries+1)
