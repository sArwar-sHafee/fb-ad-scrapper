import requests
from bs4 import BeautifulSoup
import csv

# Define the list of categories
CATEGORIES = ["cloths", "dress", "tshirt", "plastic"]

# Base URL for Facebook Ad Library
BASE_URL = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BD&is_targeted_country=false&media_type=all&q={CATEGORY}&search_type=keyword_unordered"

# List to store unique (category, Facebook page URL) tuples
# Using a set of tuples to automatically handle uniqueness of (category, URL) pairs
unique_category_url_pairs = set()

# Function to fetch and parse HTML content
def fetch_and_parse(url):
    try:
        response = requests.get(url, timeout=10)  # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None

# Iterate through each category
for category in CATEGORIES:
    print(f"Processing category: {category}")
    # Construct the URL for the current category
    url = BASE_URL.format(CATEGORY=category)

    # Fetch and parse the HTML content
    soup = fetch_and_parse(url)

    if soup:
        # Find all anchor tags with the specified classes
        # The selector finds <a> tags that have all the specified classes.
        target_classes = "xt0psk2 x1hl2dhg xt0b8zv x8t9es0 x1fvot60 xxio538 xjnfcd9 xq9mrsl x1yc453h x1h4wwuj x1fcty0u"
        # Constructing the selector string by joining class names with dots
        css_selector = "a." + ".".join(target_classes.split())
        
        anchor_tags = soup.select(css_selector)
        
        print(f"Found {len(anchor_tags)} links for category '{category}'")

        # Extract href attribute from each anchor tag
        for tag in anchor_tags:
            href = tag.get("href")
            if href:
                # Add the (category, URL) pair to the set
                unique_category_url_pairs.add((category, href))

# Save the unique (category, URL) pairs to a CSV file
csv_file_path = "facebook_pages.csv"
print(f"\nSaving unique (category, URL) pairs to {csv_file_path}...")

try:
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Category", "Page URL"])
        # Write the unique (category, URL) pairs
        # Sort for consistent output, though not strictly required by prompt
        for cat, page_url in sorted(list(unique_category_url_pairs)): 
            writer.writerow([cat, page_url])
    print(f"Successfully saved {len(unique_category_url_pairs)} unique (category, URL) pairs to {csv_file_path}")
except IOError as e:
    print(f"Error writing to CSV file {csv_file_path}: {e}")

print("\nScript finished.")