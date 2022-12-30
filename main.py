from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from dataclasses import dataclass

import re
import csv
import os
import time
BASE_URL = "https://downtowncamera.com"
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
    link: str
    expired: str
    iso: int


def click_next(driver, className="d-pagination-next"):
    link = driver.find_element(By.CLASS_NAME, className)
    link.click()


def data_class_to_list(films):
    result = []
    for film in films:
        result.append([film.brand, film.type, film.format,
                       film.price, film.description, film.inStock, film.link, film.expired, film.iso])
    return result


def write_to_csv(header, films, filename):
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write the data
        writer.writerows(films)


def extract_type(description):
    if "135" in description or "35mm" in description:
        return "35mm"
    elif "120" in description:
        return "120"
    elif "620" in description:
        return "620"
    elif "110" in description:
        return "110"
    elif "600" in description:
        return "600 Film"
    elif "4x5" in description or "4X5" in description:
        return '4x5" sheet film'
    elif "5x7" in description:
        return '5x7" sheet film'
    elif "8x10" in description:
        return '8x10" sheet film'
    elif "11x14" in description:
        return '11x14" sheet film'
    elif "Instax Mini" in description:
        return 'Instax Mini Film'
    elif "Instax Square" in description:
        return 'Instax Square Film'
    elif "Instax Wide" in description:
        return 'Instax Wide Film'
    elif "Instant Film" in description:
        return "Instant Film"
    elif "i-Type Film" in description:
        return "i-Type Film"
    elif "Super 8" in description:
        return "Super 8"
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


def get_link(film):
    f = film.find_all("a", {"class": "d-catalog-product"}, href=True)[0]
    return f['href']


def get_expired(description):
    return "expired" in description.lower()


# Instantiate options
opts = Options()
opts.add_argument("--headless")
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

            iso_matcher = re.search(r"ISO\s\d+", description)
            iso_2_matcher = re.search(r"\d+\sISO", description)
            if(iso_2_matcher is not None):
                iso = iso_2_matcher.group(0)
            else:
                iso = iso_matcher.group(
                    0) if iso_matcher is not None else "N/A"
            type = get_type(description)
            in_stock = get_in_stock(film)
            link = BASE_URL + get_link(film)
            expired = get_expired(description)
            f = Film(brand=brand, format=format, price=price,
                     type=type, description=description, inStock=in_stock, link=link, expired=expired, iso=iso)
            film_stocks.append(f)
        click_next(driver)

    except NoSuchElementException:
        print("End Reached")
        end = True


time.sleep(SLEEP_CONSTANT)
driver.quit()


write_to_csv(["brand", "type", "format",
                       "price", "description", "inStock", "link", "expired", "iso"], data_class_to_list(film_stocks), "films.csv")
