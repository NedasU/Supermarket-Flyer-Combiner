from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import csv

def save_to_csv(offers):
    # Optionally write to CSV
    with open("../Flyer_reader/maxima_offers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["shop","title","price","old_price","discount","date_start","date_end","additional_info","img"])
        writer.writeheader()
        for o in offers:
            writer.writerow(o)


def scrape_maxima_offers(url="https://www.maxima.lt/pasiulymai"):
    opts = Options()
    opts.add_argument("--headless")  # runs Chrome in headless mode (no UI)
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=opts)
    driver.get(url)

    # Wait a bit for JS to load content — maybe 5 seconds; adjust if needed
    time.sleep(1)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Example: find all product cards — you need to inspect the page to confirm the correct selector
    # For demonstration, let's pick something generic like all divs with a class that seems repeated
    items = soup.select("div.offer-card, div.offer-item, div.product-card")  # adjust according to actual classes

    offers = []
    for item in items:
        title_el = item.select_one("h4, .mt-4 text-truncate text-truncate--2")
        old_price_div = item.select_one('.price-old')
        if old_price_div:
            old_price = old_price_div.get_text(strip=True).replace(",", ".")[:-1]  # remove currency symbol
        else:
            old_price_div = item.select_one("div.bg-white")
            if old_price_div:
                euros = old_price_div.select_one("div.price-eur")
                cents = old_price_div.select_one("span.price-cents")
                old_price = ""
                if euros:
                    old_price += euros.get_text(strip=True)
                if cents:
                    old_price += "." + cents.get_text(strip=True)
            else:
                old_price = None

        # New price (bg-primary)
        new_price_div = item.select_one("div.bg-primary")
        if new_price_div:
            euros = new_price_div.select_one("div.price-eur")
            cents = new_price_div.select_one("span.price-cents")
            new_price = ""
            if euros:
                new_price += euros.get_text(strip=True)
            if cents:
                new_price += "." + cents.get_text(strip=True)
        else:
            new_price = None

        discount_el = item.select_one(".offer-discount")
        active_until_date_div = item.select_one(".offer-dateTo-wrapper span")
        active_date_limiter_div = item.find(attrs={"data-bs-placement": "top"})
        if active_date_limiter_div:
            active_store_limiter = active_date_limiter_div.get("aria-label")
        else:
            active_store_limiter = ""

        title = title_el.get_text(strip=True) if title_el else None
        discount = discount_el.get_text(strip=True) if discount_el else None
        active_until_date = active_until_date_div.get_text(strip=True).split()[-1] if active_until_date_div else None

        img_div = item.select_one(".offer-image")
        img = img_div.find("img")['src'] if img_div.find("img") else ""

        offers.append({
            "shop": "maxima",
            "title": title,
            "price": new_price,
            "old_price": old_price,
            "discount": discount,
            "date_start": None,
            "date_end": active_until_date,
            "additional_info": active_store_limiter,
            "img": img,
        })


    driver.quit()
    save_to_csv(offers)