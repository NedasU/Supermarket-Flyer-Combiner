import requests
from bs4 import BeautifulSoup
import csv
import time

# Define headers to mimic a real browser visit in order to avoid bot/scraper blocks
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36",
    "Accept-Language": "lt-LT,lt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}



# Function to get HTML content of a specific page number
def get_page_html(page_num):
    url = f"https://www.rimi.lt/e-parduotuve/lt/akcijos?currentPage={page_num}&pageSize=80"
    r = requests.get(url, headers=HEADERS)
    # Checking to see if the request was a success, otherwise raise an error
    if r.status_code != 200:
        raise Exception(f"Failed to fetch page {page_num}, status code: {r.status_code}") 
    return r.text

# Function to extract the items from the item grid if it exists.
def get_items_from_html(page_num):
    html = get_page_html(page_num)
    soup = BeautifulSoup(html, "html.parser")
    cards_grid = soup.select_one("ul.product-grid")
    return cards_grid.select("li.product-grid__item") if cards_grid else []

def format_price(price_str):
    """
    takes one price string and checks its format, then converts it to the standard format with a comma.
    - initial if check is for prices already in correct format
    - checking for the "." is for the "/vnt." ending
    - checking for "€" is for the " Eur" ending but might be not needed because of the initial check.
    - last case is for prices ending with /kg and the such.

    :param price_str: price entry from item description
    :return: formatted price string
    """
    if price_str[-4] == ",":
        return price_str.replace(",", ".")[:-1]
    elif price_str[-1] == ".":
        return (price_str[:-8] + "." + price_str[-8:-6])
    elif price_str[-1] == "€":
        return (price_str[:-3] + "." + price_str[-3:-1])
    else:
        return (price_str[:-6] + "." + price_str[-6:-4])

def extract_item_data(item):
    """
    Takes the param item and extracts relevant data from it based on the HTML structure
    and returns a dictionary with the extracted data.

    :param item: takes the item html to extract data from
    :return: dictionary with extracted data
    """
    # Title
    title_div = item.select_one(".card__details > .card__name")
    title = title_div.get_text(strip=True) if title_div else ""

    # Price and Old Price
    price_div = item.select_one(".card__image-wrapper .price-label  .price-label__body  .price-label__price")
    if price_div:
        price = format_price(price_div.get_text(strip=True))
        old_price_div = item.select_one(".card__details > .card__details-inner  .card__price-wrapper  .price-tag.card__price")
        old_price = format_price(old_price_div.get_text(strip=True)) if old_price_div else ""
    else:
        price_div = item.select_one(".card__details > .card__details-inner  .card__price-wrapper  .price-tag.card__price")
        price = format_price(price_div.get_text(strip=True)) if price_div else ""
        old_price_div = item.select_one(".card__details > .card__details-inner  .card__price-wrapper  .old-price-tag span")
        old_price = format_price(old_price_div.get_text(strip=True)) if old_price_div else ""

    # Image
    img_div = item.select_one(".card__image-wrapper  img")
    img = img_div['data-src'] if img_div else ""

    discount_div = item.select_one(".price-label__header.-red")
    discount = discount_div.get_text(strip=True) if discount_div else None

    return {
        "shop": "rimi",
        "title": title,
        "price": price,
        "old_price": old_price,
        "discount": discount,
        "date_start": None,
        "date_end": None,
        "additional_info": None,
        "img": img,
        }


# Saves the param offers (list of dictionaries) to a CSV file.
def save_to_csv(offers, filename="rimi_offers.csv"):
    with open(f"../Flyer_reader/{filename}", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["shop","title", "price", "old_price","discount","date_start","date_end","additional_info","img"])
        writer.writeheader()
        for offer in offers:
            writer.writerow(offer)

def scrape_rimi_offers():
    """
    Scrapes all Rimi offers by iterating through pages until no more items are found using a While loop.
    On each loop, checks to see if offers were found, to identify the last page of offers, and breaks the loop if none are found.
    calls the extract_item_data function to extract relevant data from each item found and saves it to offers list.
    Increments page variable after each page scraped. Returns all offers once done.

    :return: list of all offers found
    """
    page = 1
    offers = []

    while True:
        print("Scraping page:", page)
        items = get_items_from_html(page)
        if not items:
            break
        for item in items:
            offers.append(extract_item_data(item))
        page += 1
        # time.sleep(1)

    save_to_csv(offers)
