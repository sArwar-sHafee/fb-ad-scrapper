import requests
from bs4 import BeautifulSoup
import csv

# Define the list of categories
CATEGORIES = ["cloths", "dress", "tshirt", "plastic"]

# Base URL for Facebook Ad Library
BASE_URL = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BD&is_targeted_country=false&media_type=all&q={CATEGORY}&search_type=keyword_unordered"

# List to store unique Facebook page URLs
unique_page_urls = set()

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
        # Note: Class order doesn't matter in CSS selectors.
        target_classes = "xt0psk2 x1hl2dhg xt0b8zv x8t9es0 x1fvot60 xxio538 xjnfcd9 xq9mrsl x1yc453h x1h4wwuj x1fcty0u"
        # Constructing the selector string by joining class names with dots
        css_selector = "a." + ".".join(target_classes.split())
        
        anchor_tags = soup.select(css_selector)
        
        print(f"Found {len(anchor_tags)} links for category '{category}'")

        # Extract href attribute from each anchor tag
        for tag in anchor_tags:
            href = tag.get("href")
            if href:
                unique_page_urls.add(href)

# Save the unique URLs to a CSV file
csv_file_path = "facebook_pages.csv"
print(f"\nSaving unique URLs to {csv_file_path}...")

try:
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Page URL"])
        # Write the unique URLs
        for page_url in unique_page_urls:
            writer.writerow([page_url])
    print(f"Successfully saved {len(unique_page_urls)} unique URLs to {csv_file_path}")
except IOError as e:
    print(f"Error writing to CSV file {csv_file_path}: {e}")

print("\nScript finished.")
# Acknowledgment of potential scraping prevention mechanisms
print("\nNote: Facebook may have mechanisms to prevent or limit scraping (e.g., CAPTCHAs, IP blocking).")
print("This script uses a direct scraping approach and its effectiveness may vary.")
