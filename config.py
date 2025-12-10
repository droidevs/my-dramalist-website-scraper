# This file will hold the configuration for the application.

from util.utils import get_selenium_driver

debug = True

driver = get_selenium_driver()
# Remove page load timeout (wait forever until page loads)
driver.set_page_load_timeout(1000)

BASE_URL = "https://mydramalist.com"
