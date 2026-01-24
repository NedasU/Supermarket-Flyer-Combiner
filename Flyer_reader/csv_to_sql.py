import csv
import psycopg2
from datetime import datetime
import unicodedata
from iki_flyer_reader import scrape_iki_offers
from lidl_flyer_reader import scrape_lidl_offers
from maxima_flyer_reader import scrape_maxima_offers
from rimi_flyer_reader import scrape_rimi_offers
from dotenv import load_dotenv
import os
from pathlib import Path


dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path)

# --------------------- DB helper functions ---------------------
def scrape_date_check(shop, cur):
    today = datetime.today().date()

    if shop in ["iki", "maxima", "lidl"]:
        cur.execute(
            """
            SELECT MIN(date_end)
            FROM main_offers
            WHERE date_end IS NOT NULL AND shop = %s;
            """,
            (shop,)
        )
        row = cur.fetchone()
        min_end = row[0]  # date or None

        if min_end is None:
            return True  # no dated offers → scrape

        return min_end < today  # expired or expires today
    else:  # rimi
        cur.execute(
            "SELECT MAX(scraped_at) FROM main_offers WHERE shop = %s;",
            (shop,)
        )
        row = cur.fetchone()
        last_scraped = row[0]  # datetime or None

        if last_scraped is None:
            return True

        return last_scraped.date() < today

def convert_date(d):
    if not d or d.strip() == "" or "." not in d:
        return None
    
    month, day = d.split(".")
    year = datetime.now().year
    
    iso = f"{year}-{month}-{day}"
    try:
        parsed = datetime.strptime(iso, "%Y-%m-%d").date()
    except ValueError:
        return None
    
    if parsed < datetime.now().date() and month != str(datetime.now().month):
        parsed = parsed.replace(year=year + 1)

    return parsed

def price_to_cents(s):
    if "," in s:
        s = s.replace(",", ".")
    if not s or "." not in s:
        return None
    euros, cents = s.split(".")
    return int(euros) * 100 + int(cents)

def normalize(text: str) -> str:
    if text is None:
        return None
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()

def converter(names, cur, conn):
    total_rows = 0
    try:
        for name in names:
            print(f"Converting {name}_offers.csv to SQL")
            with open(f"../Flyer_reader/{name}_offers.csv", "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = []

                for r in reader:
                    rows.append((
                        r["shop"],
                        r["title"],
                        normalize(r["title"]),
                        price_to_cents(r["price"]) if r["price"] else None,
                        price_to_cents(r["old_price"]) if r["old_price"] else None,
                        r["discount"],
                        convert_date(r["date_start"]) if r["date_start"] else None,
                        convert_date(r["date_end"]) if r["date_end"] else None,
                        r["additional_info"],
                        r["img"],
                    ))
            if rows:
                cur.execute("DELETE FROM main_offers WHERE shop = %s;", (name,))
                total_rows += len(rows)

                cur.executemany(
                    """
                    INSERT INTO main_offers
                    (shop, title, title_normalized, price, old_price, discount,
                    date_start, date_end, additional_info, img)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (shop, title_normalized, date_start) DO NOTHING;
                    """, rows
                )

        if total_rows == 0:
            raise Exception("No scraped Data - Aborting DB changes")

        conn.commit()
        print(f"Committed {total_rows} rows")
    except Exception as e:
        conn.rollback()
        print("Rollback due to error:", e)
        raise

# --------------------- Main runner ---------------------
def run_scrapers_and_update_db():
    # Connect to DB
    conn = psycopg2.connect(f'dbname=grocery_discounts user=postgres password={os.getenv("POSTGRESQL_PASSWORD")}')
    cur = conn.cursor()

    shop_list = {
        "lidl": scrape_lidl_offers,
        "maxima": scrape_maxima_offers,
        "iki": scrape_iki_offers,
        "rimi": scrape_rimi_offers
    }

    shops_to_insert = []

    for shop, scrape_fn in shop_list.items():
        if scrape_date_check(shop, cur):
            scrape_fn()
            shops_to_insert.append(shop)

    if shops_to_insert:
        converter(shops_to_insert, cur, conn)
    else:
        print("No shops required scraping!")

    cur.close()
    conn.close()

# --------------------- Entry point ---------------------
if __name__ == "__main__":
    run_scrapers_and_update_db()
