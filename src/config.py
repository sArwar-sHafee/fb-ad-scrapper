"""
Configuration settings for the Facebook Ad Scraper.
"""

import os
import datetime

# Define the list of categories to search for
CATEGORIES = ["cloth"]

# Base URL for Facebook Ad Library
BASE_URL = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BD&is_targeted_country=false&media_type=all&q={CATEGORY}&search_type=keyword_unordered"

# Output directory path
OUTPUT_DIR = "contents"

# Function to generate output file path with current date
def get_output_file():
    """Generate output file path with current date as filename."""
    today = datetime.datetime.now().astimezone(datetime.timezone(datetime.timedelta(hours=6))).strftime("%d-%m-%Y_%H:%M")
    return os.path.join(OUTPUT_DIR, f"ad_{today}.csv")

# Browser settings
BROWSER_SETTINGS = {
    "headless": True,
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Scraper settings
SCRAPER_SETTINGS = {
    "max_scroll_attempts": 100,
    "scroll_delay": 5,
    "page_load_timeout": 3000,
    "max_retries": 3,
    "retry_delay": 5,
    "category_delay": 5
}
