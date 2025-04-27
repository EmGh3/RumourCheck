import time

import requests
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from text_cleaning import clean_text

# Guardian API Config
API_KEY = "3bdff0c0-d04e-44a2-aedb-9cf2d0d6853c"  # Replace with your API key
BASE_URL = "https://content.guardianapis.com/search"
CSV_FILE = "../dataset/True_processed.csv"
csv.field_size_limit(1000000)

def fetch_articles(from_date=None):
    """Fetch articles from The Guardian API."""
    params = {
        "api-key": API_KEY,
        "show-fields": "body",
        "show-tags": "keyword",
        "page-size": 100,
        "order-by": "oldest",
        "section": "world",  # Only fetch World News
    }
    if from_date:
        params["from-date"] = from_date

    response = requests.get(BASE_URL, params=params)
    data = response.json()
    print(data["response"]["status"])
    return data["response"]["results"]

def parse_article(article):
    """Extract title, body, subject, and date from an article."""
    date_obj = datetime.strptime(article["webPublicationDate"], '%Y-%m-%dT%H:%M:%SZ')
    formatted_date = date_obj.strftime('%B %d, %Y')
    raw_title = article["webTitle"]
    clean_title = clean_text(BeautifulSoup(raw_title, "html.parser").get_text(separator=" ", strip=True))
    raw_body = article["fields"].get("body", "")
    clean_body = clean_text(BeautifulSoup(raw_body, "html.parser").get_text(separator=" ", strip=True))
    return {
        "title": clean_title,
        "text": clean_body,
        "subject": article["sectionName"],
        "date": formatted_date,
    }


def get_last_csv_date():
    """Get the most recent article date from CSV to avoid duplicates."""
    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            if not rows:
                return None

            last_line = rows[-1]
            last_date = last_line["date"].strip()  # Remove any whitespace

            date_obj = datetime.strptime(last_date, '%B %d, %Y')
            return (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")

    except (FileNotFoundError, IndexError, KeyError, ValueError) as e:
        print(f"Error reading CSV: {e}")
        return None

def save_to_csv(articles):
    """Save articles to CSV, appending if file exists."""
    fieldnames = ["title", "text", "subject", "date"]
    file_exists = False

    try:
        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(CSV_FILE, mode="a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for article in articles:
            writer.writerow(article)

def main():
    while True:
        last_date = get_last_csv_date()
        print(last_date)
        articles = fetch_articles(from_date=last_date)
        parsed_articles = [parse_article(article) for article in articles]
        if parsed_articles:
            save_to_csv(parsed_articles)
            print(f"Added {len(parsed_articles)} new articles to {CSV_FILE}")
            time.sleep(1)
        else:
            print("No new articles found.")
            break

if __name__ == "__main__":
    main()