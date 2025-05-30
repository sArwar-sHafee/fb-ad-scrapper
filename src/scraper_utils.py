"""
Utility functions for the Facebook Ad Scraper.
"""

import re
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.config import SCRAPER_SETTINGS

def extract_urls_from_page(driver, category, unique_category_url_pairs):
    """Extract Facebook page URLs from the loaded page.
    
    Args:
        driver: Selenium WebDriver instance
        category: The category being processed
        unique_category_url_pairs: Set to store unique (category, URL) pairs
        
    Returns:
        None, updates unique_category_url_pairs set in-place
    """
    # Wait for the page to load
    try:
        WebDriverWait(driver, SCRAPER_SETTINGS["page_load_timeout"]).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        )
    except TimeoutException:
        print(f"Timeout waiting for page to load for category '{category}'")
        return
    
    # Get the number of results from the heading element
    scroll_attempts = SCRAPER_SETTINGS["max_scroll_attempts"]  # Default value
    try:
        # Wait for the results heading to appear
        results_element = WebDriverWait(driver, SCRAPER_SETTINGS["page_load_timeout"]).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='heading' and contains(text(), 'results')]"))
        )
        results_text = results_element.text  # e.g., "~43,000 results"
        
        # Extract the number from the text
        match = re.search(r'~?(\d+(?:,\d+)*)', results_text)
        if match:
            # Remove commas and convert to integer
            results_count = int(match.group(1).replace(',', ''))
            # Calculate scroll attempts (results / 100)
            calculated_attempts = results_count // 100
            # Use the calculated value, but not less than max_scroll_attempts
            scroll_attempts = max(calculated_attempts, SCRAPER_SETTINGS["max_scroll_attempts"])
            print(f"Found {results_count} results, setting scroll attempts to {scroll_attempts}")
    except Exception as e:
        print(f"Could not extract results count: {e}. Using default scroll attempts.")
    
    # Scroll down to load more content
    for i in range(scroll_attempts):
        print(f"Scroll attempt {i+1}/{scroll_attempts}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCRAPER_SETTINGS["scroll_delay"])  # Wait for content to load
    
    # Get the page source after scrolling
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    # Method 1: Find all divs with class "_3qn7" and extract the anchor tags from them
    divs = soup.find_all('div', class_="_3qn7")
    print(f"Found {len(divs)} divs with class '_3qn7'")
    
    for div in divs:
        links = div.find_all('a')
        for link in links:
            process_link(link, category, unique_category_url_pairs)
    
    # Method 2: Find all links that have target="_blank" and might be Facebook page links
    target_blank_links = soup.find_all('a', target="_blank")
    print(f"Found {len(target_blank_links)} links with target='_blank'")
    
    for link in target_blank_links:
        process_link(link, category, unique_category_url_pairs)

def process_link(link, category, unique_category_url_pairs):
    """Process a link element and add to unique pairs if valid.
    
    Args:
        link: BeautifulSoup link element
        category: The category being processed
        unique_category_url_pairs: Set to store unique (category, URL) pairs
    """
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
