from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv


def is_percentage(text):
    if not text:
        return False
    return "%" in text or text.replace(" ", "").startswith("-") and text.endswith("%")

def save_to_csv(offers):
    with open("../Flyer_reader/iki_offers.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["shop","title", "price","old_price","discount","date_start", "date_end","additional_info","img"])
        writer.writeheader()
        for item in offers:
            writer.writerow(item)

def scrape_iki_offers():
    # Launch Chrome with webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    URL = "https://iki.lt/akcijos/savaites-akcijos/"
    driver.get(URL)
    time.sleep(1)


    # Scroll until no new content loads
    scroll_pause = 2  # seconds
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # fully loaded
        last_height = new_height

    print("Finished loading all promotions.")

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    # Find the container with all promotions
    cards_container = soup.find("div", {"data-content": "promotions"})
    if not cards_container:
        raise Exception("Promotions container not found")

    cards = cards_container.find_all("div", class_="tag_class-savaites-akcijos")

    items = []
    for card in cards:
        # Title
        title_elem = card.select_one("p.akcija_title")
        title = title_elem.get_text(strip=True) if title_elem else None
        
        # Image
        img_src = card.select_one("img.card-img-top")
        img = img_src['src'] if img_src and img_src.has_attr('src') else None


        # Price & Discount Logic
        price = None
        discount = ""
        additional_info = ""
        old_price = None

        price_block = card.select_one(".price_block_wrapper")

        if price_block:
            raw_text = price_block.get_text(" ", strip=True)

            # Case 1: This is actually a discount, not a price (e.g. "-30%")
            if is_percentage(raw_text):
                discount = "".join(raw_text)
                price = None

            else:
                # Try extracting normal price (2.99 format)
                try:
                    price_int = price_block.select_one(".price_int").text.strip()
                    price_cents = price_block.select_one(".price_cents span.sub").text.strip()
                    price = round(float(price_int) + float(price_cents) / 100, 2)
                except:
                    price = None

            # Old price (if exists)
            old_price_div = price_block.select_one(".price_old_block")
            old_price = old_price_div.get_text(".", strip=True) if old_price_div else ""


        # Additional Info
        # Extra promo info (like "Su pigintuvu -50%")
        wrapper = card.select_one(".price_block_rounded_red_wrapper, .price_block_red_wrapper")
        extra_text = wrapper.get_text(" ", strip=True) if wrapper else ""

        if is_percentage(extra_text) and not discount:
            discount = "".join(extra_text.split())
        elif not discount:
            if extra_text.startswith("Su pigintuvu"):
                extra_texts = extra_text.split()
                extra_text = (" ".join(extra_texts[:2]) + " " + ".".join(extra_texts[2:])) 
            discount = extra_text
        else:
            additional_info = extra_text

        store_limiter = card.select(".akcija__wrap-top > .promo-top-wrapper > .promo_bottom_item > .store-list-item__hearts img")
        if store_limiter:
            additional_info += (" " + ("X"*len(store_limiter)))

        # Dates
        split_parts = card.select_one(".m-0.w-100.akcija_description.text-center").text.strip().split()
        item_active_date_start = split_parts[1]
        item_active_date_end = split_parts[-1]

        # Appending List
        items.append({"shop": "iki",
                    "title": title,
                    "price": price,
                    "old_price": old_price,
                    "discount": discount,
                    "date_start": item_active_date_start,
                    "date_end": item_active_date_end,
                    "additional_info": additional_info,
                    "img": img,
                    })

    # Quiting driver
    driver.quit()
    save_to_csv(items)
