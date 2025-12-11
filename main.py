# This is the main entry point for the application.

from scrapers.drama_scraper import scrape_drama
from scrapers.link_scraper import get_all_dramas_links


if __name__ == '__main__':
    links = get_all_dramas_links(1)
    for i,link in enumerate(links):
        scrape_drama(link)