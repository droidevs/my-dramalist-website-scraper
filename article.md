# Building a MyDramaList Scraper: A Deep Dive

This article provides a detailed walkthrough of a Python-based web scraper built to collect drama information from [MyDramaList.com](https://mydramalist.com). We will explore the project's architecture, the role of each file, and break down the code to understand how it navigates the web, extracts data, and stores it efficiently in a local database.

## Project Goal & Technology

The primary goal of this project is to automate the collection of data about TV dramas, movies, and specials from MyDramaList. This includes main details (like title, year, and rating), cast and crew information, and associated tags.

The project is built using:
- **Python**: The core programming language.
- **Selenium**: A powerful browser automation tool used to navigate the website and extract content, especially from dynamic, JavaScript-heavy pages.
- **SQLite**: A lightweight, file-based database used to store the scraped data in a structured and queryable format.
- **webdriver-manager**: A handy library to automatically manage the browser driver required by Selenium.

## Project Structure

The code is organized into several files, each with a distinct responsibility. This separation of concerns makes the project clean and easy to maintain.

```
mysramalist_scraper/
├── main.py                 # The main script that starts and orchestrates the scraping process.
├── config.py               # Configures and initializes the Selenium WebDriver instance.
├── conn.py                 # Handles the SQLite database connection and schema creation.
├── mydramalist.db          # The SQL file containing the database schema.
├── scrapers/
│   ├── link_scraper.py     # Contains the logic to find and collect URLs of individual drama pages.
│   └── drama_scraper.py    # Extracts all the detailed data from a single drama page.
└── util/
    └── utils.py            # A collection of helper functions for parsing data and interacting with web elements safely.
```

---

## Code Breakdown: A Line-by-Line Explanation

Let's dive into each file to understand how it contributes to the project.

### 1. `config.py` — Configuring the Web Driver

This file is the foundation of our browser automation. It sets up the Selenium WebDriver with specific options to make our scraper efficient and less detectable.

```python
# c:\Users\admin\Desktop\mysramalist_scraper\config.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

def get_selenium_driver(headless=False):
    """
    This function initializes and returns a Selenium Edge driver.
    """
    # Create an Options object to customize the browser's behavior.
    options = Options()
    
    # 'eager' tells the browser not to wait for images and stylesheets to fully load.
    # The scraper can start working as soon as the main HTML (DOM) is ready, which is much faster.
    options.page_load_strategy = "eager"
    
    # If headless=True, the browser runs in the background without a visible UI.
    if headless:
        options.add_argument('--headless=new')
        
    # These arguments help the scraper appear more like a regular user and avoid being blocked.
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.96 Safari/537.36')
    
    # webdriver-manager automatically downloads the correct Edge driver.
    service = Service(EdgeChromiumDriverManager().install())
    
    # Initialize the Edge driver with the service and custom options.
    driver = webdriver.Edge(service=service, options=options)
    return driver

# A global flag for toggling detailed print statements during scraping.
debug = True

# Create the global driver instance that will be imported and used by other files.
driver = get_selenium_driver()

# Set a very long page load timeout (1000 seconds). This prevents the script from crashing if a page is extremely slow to load.
driver.set_page_load_timeout(1000)

# Define the base URL for MyDramaList to be used throughout the project.
BASE_URL = "https://mydramalist.com"
```

### 2. `conn.py` — Setting Up the Database

This file handles all database interactions. It creates a connection to an SQLite database file and sets up the necessary tables by executing an external SQL script.

```python
# c:\Users\admin\Desktop\mysramalist_scraper\conn.py

import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """
    Establishes a connection to the SQLite database specified by the file name.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

# Create the connection to 'database.db'. If the file doesn't exist, it will be created.
conn = create_connection("database.db")

# This section reads SQL commands from the 'mydramalist.db' file to create the tables.
# This is a clean way to separate your SQL schema from your Python code.
with open("mydramalist.db", "r") as cache:
    conn.executescript(cache.read())

# A cursor object is created to execute SQL queries on the database.
# This global cursor is used by the drama_scraper to insert data.
cur = conn.cursor()
```

### 3. `util/utils.py` — The Utility Belt

This file contains helper functions that perform common, reusable tasks, keeping the main scraper code clean and readable.

```python
# c:\Users\admin\Desktop\mysramalist_scraper\util\utils.py
import re
from urllib.parse import urlparse
from config import driver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

def slugify(text):
    return re.sub(r'\W+', '_', text.lower()).strip('_')

def extract_drama_id(url):
    """
    Extracts the unique drama ID from a MyDramaList URL.
    Example: from "https://mydramalist.com/12345-some-drama" it returns "12345".
    """
    # From https://mydramalist.com/12345-move-to-heaven → "12345"
    # It parses the URL's path, strips the slashes, and splits by the hyphen.
    parts = urlparse(url).path.strip("/").split("-")
    # The ID is the first part of the path component. It returns the ID as a string.
    return parts if parts else int(re.search(r"/(\d+)-", url).group(1))

def safe_find(selector, attr="text", xpath=False):
    """
    A safe way to find a single element. If the element is not found, it returns None
    instead of crashing the script, which is crucial for robust scraping.
    """
    try:
        # It can find elements by CSS selector (default) or by XPath.
        el = driver.find_element(By.XPATH, selector) if xpath else driver.find_element(By.CSS_SELECTOR, selector)
        # It can return the element's text content or any other HTML attribute (like 'href').
        return el.get_attribute(attr) if attr != "text" else el.text.strip()
    except NoSuchElementException:
        return None

def safe_finds(selector, attr="text",xpath = False):
    """A safe way to find multiple elements. If no elements are found, it returns an empty list."""
    try:
        els = driver.find_elements(By.XPATH, selector) if xpath else driver.find_elements(By.CSS_SELECTOR, selector)
        if attr == "text":
            return [e.text.strip() for e in els]
        else:
            return [e.get_attribute(attr) for e in els]
    except:
        return []
```

### 4. `scrapers/link_scraper.py` — Finding the Dramas

This scraper's job is to navigate the search pages of MyDramaList and collect the URLs for all the dramas listed on a given page.

```python
# c:\Users\admin\Desktop\mysramalist_scraper\scrapers\link_scraper.py

from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from config import driver
import time

BASE_URL = "https://mydramalist.com"

def get_all_dramas_links(page=1, retries=0, max_retries=None, delay=0):
    """
    Scrapes all drama links from a specific search result page.
    Includes a retry mechanism to handle network errors or incomplete page loads.
    """
    # Constructs the URL for a specific page of search results.
    url = f"{BASE_URL}/search?adv=titles&ty=68&so=date&page={page}"
    print(f"🌐 Fetching page {page} (attempt {retries+1})")

    try:
        driver.get(url)
        # Finds all link elements that are children of a 'block' class. These are the drama links.
        elements = driver.find_elements(By.CSS_SELECTOR, "a.block")
        links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]

        l = len(links)
        # MyDramaList shows 20 dramas per page. This check ensures the page loaded completely.
        if l == 20:
            print(f"✅ Found {l} drama links on page {page}")
        else:
            # If we get fewer than 20 links, something is wrong, so we raise an exception to trigger a retry.
            raise Exception("data not complete")
        return links

    except (TimeoutException, WebDriverException, Exception) as e:
        # If any error occurs, this block catches it.
        print(f"❌ Error on page {page}: {e}")

        # It will retry indefinitely unless 'max_retries' is set.
        if max_retries is None or retries < max_retries:
            print(f"🔄 Retrying in {delay} seconds... (attempt {retries+2})")
            time.sleep(delay)
            # The function calls itself to retry the process (recursion).
            return get_all_dramas_links(page, retries=retries+1, max_retries=max_retries, delay=delay)
        else:
            print(f"🚫 Failed after {max_retries} attempts for page {page}")
            return []
```

### 5. `scrapers/drama_scraper.py` — Extracting the Details

This is the heart of the project. This scraper takes a single drama URL, visits the page, and meticulously extracts all the details, including navigating to the separate cast page.

```python
# c:\Users\admin\Desktop\mysramalist_scraper\scrapers\drama_scraper.py

from config import driver, debug
from util.utils import safe_find, extract_drama_id
from conn import conn, cur
import time, re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException

def scrape_drama(page=0, drn=0, url="", retries=0):
    """Scrapes a single drama page, extracts all data, and saves it to the database."""
    print(f"Started Scraping for drama with link << {url} >> ",)
    try:
        driver.get(url)
        # Extract the unique ID from the drama's URL.
        drama_id = extract_drama_id(url)

        # --- METADATA & DETAILS SCRAPING ---
        # Uses the 'safe_find' utility to get text from specific HTML elements.
        title = safe_find("h1.film-title")
        native_title = safe_find("//li[b[contains(text(), 'Native Title')]]/a", xpath= True)
        aka_titles = safe_find("//li[b[contains(text(),'Also Known As')]]/span[@class='mdl-aka-titles']",xpath = True)
        description = safe_find("div.show-synopsis")

        # This section iterates through a list of details and parses each one.
        details = driver.find_elements(By.CSS_SELECTOR, ".show-detailsxss li")
        # Initialize all detail variables to None to ensure they exist before the loop.
        year, country, dtype, episodes, duration, content_rating, ranked, popularity, rating = \
            None, None, None, None, None, None, None, None, None

        for li in details:
            txt = li.text.strip()
            # It checks the text of each list item to identify the piece of data it contains.
            if txt.startswith("Country:"):
                country = txt.replace("Country:", "").strip()
            elif txt.startswith("Type:"):
                dtype = txt.replace("Type:", "").strip()
            elif txt.startswith("Episodes:"):
                # Use regex to remove all non-digit characters to get a clean number.
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
                # Use a regular expression to find the 4-digit year.
                match = re.search(r"\b(\d{4})\b", txt)
                if match:
                    year = int(match.group(1))
            elif txt.startswith("Score:"):
                # Use a regular expression to find the rating number (which can be a decimal).
                match = re.search(r"([\d.]+)", txt)
                if match:
                    rating = float(match.group(1))

        # --- DATABASE INSERTION (DRAMA) ---
        # An `INSERT OR REPLACE` query is used. If a drama with the same `drama_id` already exists,
        # its record will be updated. Otherwise, a new record is inserted. This prevents duplicates.
        cur.execute("""
            INSERT OR REPLACE INTO dramas
            (drama_id, title, native_title, aka_titles, year, country, type, episodes,
             duration, rating, ranked, popularity, content_rating, description, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (drama_id, title, native_title, aka_titles, year, country, dtype,
              episodes, duration, rating, ranked, popularity, content_rating,
              description, url))

        # --- TAGS SCRAPING ---
        # Find all tag links within the tag list.
        tags = driver.find_elements(By.CSS_SELECTOR, "li.show-tags span a")
        for t in tags:
            tag_name = t.text.strip()
            href = t.get_attribute("href")
            # Extract the unique tag ID from its URL using a regular expression.
            tag_id = int(re.search(r"th=(\d+)", href).group(1))
            
            # `INSERT OR IGNORE` adds the tag only if it doesn't already exist in the 'tags' table.
            cur.execute("INSERT OR IGNORE INTO tags (tag_id, name) VALUES (?, ?)", (tag_id, tag_name))
            # Create the relationship between this drama and this tag in the 'drama_tags' junction table.
            cur.execute("INSERT OR IGNORE INTO drama_tags (drama_id, tag_id) VALUES (?, ?)", (drama_id, tag_id))

        # --- CAST SCRAPING ---
        # The scraper navigates to the dedicated "cast" page for the drama.
        cast_url = url + "/cast"
        driver.get(cast_url)

        # Find the main container for cast and crew information.
        box_body = driver.find_element(By.CSS_SELECTOR, "div.box-body")
        # Get all role sections (e.g., "Director", "Main Role", "Support Role").
        sections = box_body.find_elements(By.CSS_SELECTOR, "h3.header.b-b.p-b")

        for section in sections:
            role_name = section.text.strip()  # e.g., "Director", "Composer", "Main Role", etc.

            # The list of people is in a `<ul>` element that is the next sibling of the section header.
            ul = section.find_element(By.XPATH, "following-sibling::ul[1]")
            li_items = ul.find_elements(By.CSS_SELECTOR, "li.list-item")

            for li in li_items:
                try:
                    # Find the link containing the person's name and profile URL.
                    a_tag = li.find_element(By.CSS_SELECTOR, "a.text-primary")
                    cast_name = a_tag.text.strip()
                    href = a_tag.get_attribute("href")
                    # Extract the unique person ID from their profile URL.
                    cast_id_match = re.search(r"/people/(\d+)", href)
                    if cast_id_match:
                        cast_id = int(cast_id_match.group(1))
                    else:
                        continue # Skip if no ID can be found.

                    # The specific role (e.g., character name) is often in a <small> tag.
                    role_detail = ""
                    try:
                        role_detail = li.find_element(By.CSS_SELECTOR, "small").text.strip()
                    except:
                        # If no specific role is found, fall back to the general section name (e.g., "Director").
                        role_detail = role_name

                    # `INSERT OR IGNORE` adds the person only if they don't already exist.
                    cur.execute(
                        "INSERT OR IGNORE INTO casts (cast_id, name) VALUES (?, ?)",
                        (cast_id, cast_name)
                    )
                    # Create the relationship between the drama, the person, and their role.
                    cur.execute(
                        "INSERT OR IGNORE INTO drama_casts (drama_id, cast_id, role) VALUES (?, ?, ?)",
                        (drama_id, cast_id, role_detail)
                    )

                except Exception as e:
                    print("Skipping an entry:", e)
                    continue

        # Commits all the database changes for this drama at once.
        conn.commit()
        
        print(f" page {page} drama {drn} -> ✅ Scraped drama {title} ({drama_id})")

    except WebDriverException as e:
        # A simple retry mechanism for individual drama scraping.
        print(f"⚠️ Error scraping {url}, retrying... attempt {retries+1}")
        print(e.msg)
        time.sleep(3)
        # The function calls itself to retry the process.
        scrape_drama(page,drn, url, retries=retries+1)
```

### 6. `main.py` — The Orchestrator

This is the entry point of our application. It's a simple script that controls the overall flow: get links from a page, then scrape each link.

```python
# c:\Users\admin\Desktop\mysramalist_scraper\main.py

from scrapers.drama_scraper import scrape_drama
from scrapers.link_scraper import get_all_dramas_links

# This ensures the code runs only when the script is executed directly.
if __name__ == '__main__':
    # This loop determines which search pages to scrape. range(0, 1) scrapes the first page.
    # To scrape the first 50 pages, you would change it to range(0, 50).
    for page in range(0, 1):
        # 1. Get all drama links from the current page.
        links = get_all_dramas_links(page)
        # 2. Loop through each link.
        for i, link in enumerate(links):
            # 3. Scrape all details for that link.
            scrape_drama(page, i, link)
```

---

## Conclusion

This project is a great example of a robust and well-structured web scraper. By separating concerns into different files (config, database, scrapers, utils), the code becomes modular and easy to manage. Key features like the retry mechanism in `link_scraper`, the safe element finders in `utils.py`, and the detailed parsing in `drama_scraper.py` all contribute to a powerful data collection tool. The use of a structured SQLite database at the end ensures that the collected data is not just a pile of text, but a valuable, queryable dataset.