"""
Data handling functions for the Facebook Ad Scraper.
"""

import csv
import os
from src.config import get_output_file, OUTPUT_DIR

def save_to_csv(unique_category_url_pairs):
    """Save the unique (category, URL) pairs to a CSV file.
    
    Args:
        unique_category_url_pairs: Set of tuples containing (category, URL) pairs
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Get the output file path with current date
        output_file = get_output_file()
        
        with open(output_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            # Write the header row
            writer.writerow(["Category", "Page URL"])
            # Write the unique (category, URL) pairs
            for cat, page_url in sorted(list(unique_category_url_pairs)):
                writer.writerow([cat, page_url])
        print(f"Successfully saved {len(unique_category_url_pairs)} unique (category, URL) pairs to {output_file}")
        return True
    except IOError as e:
        print(f"Error writing to CSV file {output_file}: {e}")
        return False
