"""
Main module for the Facebook Ad Scraper.
"""

import time
from src.config import CATEGORIES, BASE_URL, SCRAPER_SETTINGS
from src.browser import setup_driver
from src.scraper_utils import extract_urls_from_page
from src.data_handler import save_to_csv

def main():
    """Main function to run the Facebook Ad Scraper."""
    # Set to store unique (category, Facebook page URL) tuples
    unique_category_url_pairs = set()
    driver = None
    
    try:
        print("Starting Facebook Ad Scraper...")
        driver = setup_driver()
        
        # Iterate through each category
        for category in CATEGORIES:
            print(f"\nProcessing category: {category}")
            # Construct the URL for the current category
            url = BASE_URL.format(CATEGORY=category)
            
            # Try to load the page with retries
            max_retries = SCRAPER_SETTINGS["max_retries"]
            for attempt in range(max_retries):
                try:
                    print(f"Attempt {attempt+1}/{max_retries} to load URL: {url}")
                    driver.get(url)
                    
                    # Extract URLs from the loaded page
                    extract_urls_from_page(driver, category, unique_category_url_pairs)
                    
                    # If successful, break the retry loop
                    break
                    
                except Exception as e:
                    print(f"Error on attempt {attempt+1}: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {SCRAPER_SETTINGS['retry_delay']} seconds...")
                        time.sleep(SCRAPER_SETTINGS["retry_delay"])
                    else:
                        print(f"Failed to process category '{category}' after {max_retries} attempts")
            
            # Add a delay between categories to avoid rate limiting
            time.sleep(SCRAPER_SETTINGS["category_delay"])
        
        # Save the unique (category, URL) pairs to a CSV file
        save_to_csv(unique_category_url_pairs)
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.quit()
        print("\nScript finished.")

if __name__ == "__main__":
    main()
