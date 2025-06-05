import csv
from datetime import datetime

input_file = "clickholecontent.txt"
output_csv = "../dataset/Fake_new.csv"

with open(input_file, "r", encoding="utf-8") as infile, \
     open(output_csv, "w", encoding="utf-8", newline="") as outfile:

    writer = csv.DictWriter(outfile, fieldnames=["title", "text", "subject", "date"])
    writer.writeheader()

    raw_articles = infile.read().split("<|startoftext|>")
    for raw_article in raw_articles:
        if not raw_article.strip():
            continue
        content = raw_article.replace("<|endoftext|>", "").strip()
        parts = content.split("\n\n")
        if len(parts) < 2:
            continue
        title = parts[0]
        body = " ".join(parts[1:])
        writer.writerow({
            "title": title,
            "text": body,
            "subject": "Fake",  # Or "Satire"
            "date": datetime.now().strftime("%Y-%m-%d")
        })
