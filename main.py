from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup

import os
import time
import re

URL = "https://downtowncamera.com/shop/categories/film/160830cc-7790-4399-9330-586545ab3e9b"


def get_total_pages(soup):
    e = soup.find_all("div", {"class": "d-pagination"})
    return re.findall(r'\d+', e[0].text)[1]


# Instantiate options
opts = Options()
opts.add_argument(" — headless")
opts.add_argument("start-maximized")
opts.add_argument("disable-infobars")
opts.add_argument("--disable-extensions")
opts.add_argument("--disable-gpu")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--no-sandbox")

# Set the location of the webdriver
chrome_driver = os.getcwd() + "chromedriver.exe"

# Instantiate a webdriver
driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)

# Load the HTML page
driver.get(URL)
end = False
while not end:
    try:
        link = driver.find_element(By.CLASS_NAME, "d-pagination-next")

        # Scrape here 

        link.click()
        time.sleep(5)
    except NoSuchElementException:
        print("End Reached")
        end = True

time.sleep(2)