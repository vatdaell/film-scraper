import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from dataclasses import dataclass

import os
import time
import re

URL = "https://downtowncamera.com/shop/categories/film/160830cc-7790-4399-9330-586545ab3e9b"
SLEEP_CONSTANT = 1


@dataclass
class Film:
    type: str
    format: str
    brand: str
    price: str
    inStock: bool
    description: str


def click_next(driver, className="d-pagination-next"):
    link = driver.find_element(By.CLASS_NAME, className)
    link.click()


def extract_type(description):
    if "135" in description:
        return "35mm"
    elif "120" in description:
        return "120"
    elif "4x5" in description:
        return '4x5" sheet film'
    elif "8x10" in description:
        return '8x10" sheet film'
    elif "Instant Film" in description:
        return "Instant Film"
    elif "i-Type Film" in description:
        return "i-Type Film"
    else:
        return "Other"


def get_type(description):
    if "Black and White" in description or "Black & White" in description:
        return "Black and White"
    elif "Colour Negative" in description:
        return "Colour Negative"
    elif "Colour" in description or "Color" in description:
        return "Colour"
    else:
        return "N/A"


def get_in_stock(film):
    f = film.find_all("div", {"class": "d-catalog-product-warning-text"})
    if(len(f) == 0):
        return True

    return "out of stock" in f[0]


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
chrome_driver = os.getcwd() + "/chromedriver.exe"

# Instantiate a webdriver
driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)

# Load the HTML page
driver.get(URL)

end = False
film_stocks = []
while not end:
    time.sleep(SLEEP_CONSTANT)
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        films = soup.find_all(
            "li", {"class": "d-catalog-cell-product"})
        for film in films:
            brand = film.find_all(
                "span", {"class": "d-catalog-product-brand"})[0].text.replace(u'\xa0', u'')
            description = film.find_all(
                "span", {"class": "d-catalog-product-name"})[0].text
            format = extract_type(description)
            price = film.find_all(
                "span", {"class": "d-catalog-product-price"})[0].text
            type = get_type(description)
            in_stock = get_in_stock(film)
            f = Film(brand=brand, format=format, price=price,
                     type=type, description=description, inStock=in_stock)
            film_stocks.append(f)
        click_next(driver)

    except NoSuchElementException:
        print("End Reached")
        end = True

print(film_stocks)
time.sleep(SLEEP_CONSTANT)
driver.quit()
