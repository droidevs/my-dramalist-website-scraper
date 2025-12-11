# This file will contain the code to scrape drama details.
from config import driver

def scrape_drama(url=""):
    """Scrape a single drama page."""
    print(f"Started Scraping for drama with link << {url} >> ")
    driver.get(url)
    # drama_id from URL
    drama_id = int(re.search(r"/(\d+)-", url).group(1))
    print(f"Scraping drama {drama_id}")