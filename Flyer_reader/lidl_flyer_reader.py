import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

BASE = "https://www.lidl.lt"

def save_to_csv(offers):
    # Writing to CSV
    with open("../Flyer_reader/lidl_offers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["shop","title","price","old_price","discount","date_start","date_end","additional_info","img"])
        writer.writeheader()
        for o in offers:
            writer.writerow(o)


def get_weekly_sales_url():
    """
    Accesses the Base url of Lidl Lithuania to find the current weeks sales url
    by accessing the a-tags href inside the div with name attribute "savaitės akcijos"
    """
    html = requests.get(BASE).text
    soup = BeautifulSoup(html, "html.parser")

    # finding the div with name attribute that includes "savaitės akcijos" and throws error if not found
    div_node = soup.find("div", {"name": re.compile("savaitės akcijos", re.I)})
    if not div_node:
        raise Exception("Could not locate weekly offers text.")

    # Take the direct a-element child which has a href attribute. Throws error if not found
    link = div_node.find("a", href=True)
    if not link:
        raise Exception("No link found inside weekly offers block.")

    # returns the base url + the href found to provide the updated weekly sales url
    return BASE + link["href"]

def scroll_to_bottom(driver, step=800, pause=0.2, max_no_change=4):
    """
    Imitate scrolling in order to allow all products to load on Lidl's website
    in order to scrape all items.
    """
    selector = ".product-grid-box"
    last_count = 0
    no_change_rounds = 0

    while True:
        # Scrolls steps and pauses for a set time (0.2s in this case)
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(pause)

        # Count loaded items in order to compare
        items = driver.find_elements(By.CSS_SELECTOR, selector)
        count = len(items)

        # Condiional check to see if no new items are being loaded.
        # Checks multiple times based on max_no_change parameter to see if end is actually reached
        if count == last_count:
            no_change_rounds += 1
        else:
            no_change_rounds = 0  # reset if new items arrived

        if no_change_rounds >= max_no_change:
            break  # no more items loading

        last_count = count


def scrape_lidl_offers(url=None):
    # Gets the url for the updated weeks sales if not provided
    if url is None:
        url = get_weekly_sales_url()

    # Run selenium to load JS content and run function to scroll to bottom
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless")  # runs Chrome in headless mode (no UI)
    driver = webdriver.Chrome(options=opts)

    driver.get(url)

    # Scroll to load all products (uses progressive loader above)
    scroll_to_bottom(driver)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Selecting all product areas
    items = soup.select(".product-grid-box")  # adjust according to actual classes

    # Iterating over all the product categories and extracting data and saving to list
    offers = []
    for item in items:
        title_el = item.select_one(".product-grid-box__title")
        title = title_el.get_text(strip=True) if title_el else ""
        title += " " + item.select_one(".ods-price__footer").get_text(strip=True) if item.select_one("div.ods-price__footer") else ""
        old_price_div = item.select_one('.ods-price__stroke-price')
        old_price = old_price_div.get_text(strip=True).replace(",", ".")[:-1] if old_price_div else ""
        new_price_div = item.select_one(".ods-price__value")
        if new_price_div:
            new_price = new_price_div.get_text(strip=True).replace(",", ".")[:-1]
        else:
            new_price = None
        active_date_div = item.select_one(".product-grid-box__availabilities")
        active_date_end = ""
        active_date_start = ""
        # Checking to see if there is an active date period (from-to) or just a from date
        if active_date_div:
            active_date = active_date_div.get_text(strip=True).split()
            if len(active_date) > 3:
                active_date_start = ".".join(active_date[:2])
                active_date_end = ".".join(active_date[3:])
            else:
                active_date_start = ".".join(active_date[1:])

        discount_el = item.select_one(".ods-price__box-content-wrapper")
        discount = discount_el.get_text(strip=True) if discount_el else None
        img_div = item.select_one(".odsc-image-gallery__item.odsc-image-gallery__item--active")
        img = img_div.find("img")['src'] if img_div.find("img") else ""

        # Saving all data to list in dictionary format
        offers.append({
            "shop": "lidl",
            "title": title,
            "price": new_price,
            "old_price": old_price,
            "discount": discount,
            "date_start": active_date_start,
            "date_end": active_date_end,
            "additional_info": None,
            "img": img,
        })


    driver.quit()
    save_to_csv(offers)