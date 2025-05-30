import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

# Define the list of categories
CATEGORIES = ["cloths", "dress", "tshirt", "plastic"]

# Base URL for Facebook Ad Library
BASE_URL = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BD&is_targeted_country=false&media_type=all&q={CATEGORY}&search_type=keyword_unordered"

# List to store unique (category, Facebook page URL) tuples
unique_category_url_pairs = set()

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add a realistic user agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_urls_from_page(driver, category, max_scroll_attempts=5):
    """Extract Facebook page URLs from the loaded page."""
    # Wait for the page to load
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
    except TimeoutException:
        print(f"Timeout waiting for page to load for category '{category}'")
        return
    
    # Scroll down a few times to load more content
    for i in range(max_scroll_attempts):
        print(f"Scroll attempt {i+1}/{max_scroll_attempts}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load
    
    # Get the page source after scrolling
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    # Method 1: Find all divs with class "_3qn7" and extract the anchor tags from them
    divs = soup.find_all('div', class_="_3qn7")
    print(f"Found {len(divs)} divs with class '_3qn7'")
    
    for div in divs:
        links = div.find_all('a')
        for link in links:
            href = link.get('href')
            if href and 'facebook.com' in href:
                # Clean the URL if needed (remove tracking parameters, etc.)
                match = re.search(r'(https://www\.facebook\.com/[^/?]+)', href)
                if match:
                    clean_href = match.group(1)
                    unique_category_url_pairs.add((category, clean_href))
                    print(f"Added URL: {clean_href}")
                else:
                    unique_category_url_pairs.add((category, href))
                    print(f"Added URL (unclean): {href}")
    
    # Method 2: Find all links that have target="_blank" and might be Facebook page links
    target_blank_links = soup.find_all('a', target="_blank")
    print(f"Found {len(target_blank_links)} links with target='_blank'")
    
    for link in target_blank_links:
        href = link.get('href')
        if href and 'facebook.com' in href:
            # Clean the URL
            match = re.search(r'(https://www\.facebook\.com/[^/?]+)', href)
            if match:
                clean_href = match.group(1)
                unique_category_url_pairs.add((category, clean_href))
                print(f"Added URL: {clean_href}")
            else:
                unique_category_url_pairs.add((category, href))
                print(f"Added URL (unclean): {href}")

def main():
    driver = None
    try:
        driver = setup_driver()
        
        # Iterate through each category
        for category in CATEGORIES:
            print(f"\nProcessing category: {category}")
            # Construct the URL for the current category
            url = BASE_URL.format(CATEGORY=category)
            
            # Try to load the page with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"Attempt {attempt+1}/{max_retries} to load URL: {url}")
                    driver.get(url)
                    
                    # Extract URLs from the loaded page
                    extract_urls_from_page(driver, category)
                    
                    # If successful, break the retry loop
                    break
                    
                except Exception as e:
                    print(f"Error on attempt {attempt+1}: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in 5 seconds...")
                        time.sleep(5)
                    else:
                        print(f"Failed to process category '{category}' after {max_retries} attempts")
            
            # Add a delay between categories to avoid rate limiting
            time.sleep(5)
        
        # Save the unique (category, URL) pairs to a CSV file
        csv_file_path = "facebook_pages.csv"
        print(f"\nSaving unique (category, URL) pairs to {csv_file_path}...")
        
        try:
            with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                # Write the header row
                writer.writerow(["Category", "Page URL"])
                # Write the unique (category, URL) pairs
                for cat, page_url in sorted(list(unique_category_url_pairs)):
                    writer.writerow([cat, page_url])
            print(f"Successfully saved {len(unique_category_url_pairs)} unique (category, URL) pairs to {csv_file_path}")
        except IOError as e:
            print(f"Error writing to CSV file {csv_file_path}: {e}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
        print("\nScript finished.")

if __name__ == "__main__":
    main()