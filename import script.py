import os
import csv
import trafilatura
import re
import time
import requests
from urllib.parse import urlparse

# ---------------------------
# SETTINGS
# ---------------------------

import csv

articles = []

with open("C:\\Users\\Ethan Sibbett\\Downloads\\cleaned_urls_metadata.csv", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        articles.append({
            "url": row["url"],
            "label": row["label"],
            "outlet": row["outlet"],
            "person": row["person"]
        })

base_folder = "corpus"
metadata_file = "metadata.csv"
log_file = "log.txt"

os.makedirs(os.path.join(base_folder, "left"), exist_ok=True)
os.makedirs(os.path.join(base_folder, "right"), exist_ok=True)

# Write metadata header
with open(metadata_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
    "title", "author", "date", "outlet",
    "label", "word_count", "person", "url", "filename"
])

headers = {
    "User-Agent": "Mozilla/5.0 (Research Corpus Collection)"
}

for article in articles:
    url = article["url"]
    label = article["label"]

    try:
        print(f"Downloading: {url}")

        response = requests.get(url, headers=headers, timeout=15)
        downloaded = response.text

        metadata = trafilatura.extract_metadata(downloaded)
        text = trafilatura.extract(downloaded)

        if not text:
            raise Exception("No text extracted")

        tokens = re.findall(r"\b\w+\b", text.lower())
        word_count = len(tokens)

        outlet = urlparse(url).netloc.replace("www.", "")
        title = metadata.title if metadata and metadata.title else "N/A"
        author = metadata.author if metadata and metadata.author else "N/A"
        date = metadata.date if metadata and metadata.date else "N/A"

        filename = f"{label}_{len(tokens)}_{abs(hash(url))}.txt"
        filepath = os.path.join(base_folder, label, filename)

        # Save BODY TEXT ONLY
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text.strip())

        # Save metadata
        with open(metadata_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                title, author, date, outlet,
                label, word_count, url, filename
            ])

        time.sleep(2)  # Respectful delay

    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"{url} — {e}\n")
        print(f"Failed: {url}")

print("Done.")