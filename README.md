# MyDramaList Scraper

A Python-based web scraper designed to collect comprehensive information about dramas from MyDramaList.com. It uses Selenium to navigate the website, extract details about dramas—including metadata, cast, and tags—and stores the collected data in a structured SQLite database.

## Features

- **Drama Link Collection**: Scrapes drama links from the main search/browse pages.
- **Detailed Information**: Extracts detailed information for each drama, such as native title, year, country, number of episodes, rating, popularity, and synopsis.
- **Cast & Crew Scraping**: Navigates to the cast page for each drama to get a full list of actors, directors, and other crew members.
- **Tag Extraction**: Gathers all associated tags for each drama.
- **Robust & Resilient**: Implements an automatic retry mechanism to handle network errors or page load failures, ensuring data collection is as complete as possible.
- **Database Storage**: Stores all scraped data in a well-structured SQLite database for easy querying and analysis.
- **Automated WebDriver Management**: Uses `webdriver-manager` to automatically download and manage the appropriate ChromeDriver.

## Tech Stack & Requirements

- Python 3.x
- Selenium
- webdriver-manager

You can install the necessary packages using the following command:
```bash
pip install selenium webdriver-manager
```

## How to Use

1.  **Clone the repository** or place all the project files in a single directory.

2.  **Install the required libraries** as mentioned above.

3.  **Run the main script**:
    ```bash
    python main.py
    ```

4.  The script will start the scraping process. It will first fetch links to dramas page by page and then visit each link to scrape the detailed information.

5.  All data will be stored in a `database.db` file, which is created automatically in the project's root directory.

### Configuration

- You can adjust the number of pages to scrape by modifying the `range` in `main.py`. For example, to scrape the first 10 pages:
  ```python
  # main.py
  if __name__ == '__main__':
      for page in range(0, 10): # Scrapes pages 0 through 9
          links = get_all_dramas_links(page)
          for i, link in enumerate(links):
              scrape_drama(page, i, link)
  ```
- Headless browsing can be enabled in `config.py` for running the scraper in the background without a visible browser window.
  ```python
  # config.py
  driver = get_selenium_driver(headless=True)
  ```

## Project Structure

```
mysramalist_scraper/
├── scrapers/
│   ├── link_scraper.py     # Scrapes drama links from search pages.
│   └── drama_scraper.py    # Scrapes detailed information for a single drama.
├── util/
│   └── utils.py            # Utility functions for parsing and safe data extraction.
├── main.py                 # Main entry point to run the scraper.
├── config.py               # Selenium WebDriver configuration.
├── conn.py                 # Database connection and schema setup.
└── database.db             # (Generated) SQLite database file.
```

## Database Schema

The scraper creates a SQLite database (`database.db`) with the following tables:

### `dramas`
Stores the main information for each drama.
- `drama_id` (INTEGER, PRIMARY KEY): The unique ID from MyDramaList.
- `title` (TEXT)
- `native_title` (TEXT)
- `aka_titles` (TEXT): Also Known As titles.
- `year` (INTEGER)
- `country` (TEXT)
- `type` (TEXT): e.g., "Drama", "Movie".
- `episodes` (INTEGER)
- `duration` (TEXT)
- `rating` (REAL)
- `ranked` (INTEGER): The rank on MyDramaList.
- `popularity` (INTEGER)
- `content_rating` (TEXT)
- `description` (TEXT)
- `url` (TEXT, UNIQUE)

### `tags`
Stores unique tags.
- `tag_id` (INTEGER, PRIMARY KEY): The unique ID for the tag.
- `name` (TEXT, UNIQUE)

### `casts`
Stores unique cast and crew members.
- `cast_id` (INTEGER, PRIMARY KEY): The unique ID for the person.
- `name` (TEXT, UNIQUE)

### `drama_tags` & `drama_casts`
These are relational tables that link dramas to their respective tags and cast members, establishing many-to-many relationships.

---