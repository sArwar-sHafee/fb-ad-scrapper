"""
Data handling functions for the Facebook Ad Scraper.
"""

import csv
import os
from datetime import datetime # Added datetime
from src.config import get_output_file, OUTPUT_DIR

PHONE_NUMBERS_DIR = "phone_numbers" # New directory constant

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

def save_phone_numbers_to_csv(data_list):
    """
    Saves data (category, url, phone_number) to a CSV file in the PHONE_NUMBERS_DIR.

    Args:
        data_list (list): A list of dictionaries, each with 'category', 'url',
                          and 'phone_number' keys.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        os.makedirs(PHONE_NUMBERS_DIR, exist_ok=True)

        filename = f"extracted_phones_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        full_path = os.path.join(PHONE_NUMBERS_DIR, filename)

        with open(full_path, mode='w', newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            # Write the header row
            csv_writer.writerow(["Category", "URL", "Phone Number"])
            # Write the data rows
            for item in data_list:
                csv_writer.writerow([
                    item.get('category', ''),
                    item.get('url', ''),
                    item.get('phone_number', '')
                ])
        print(f"Successfully saved {len(data_list)} records to {full_path}")
        return True
    except IOError as e:
        print(f"Error saving phone numbers to CSV {full_path}: {e}")
        return False
    except Exception as e: # Catch other potential errors
        print(f"An unexpected error occurred while saving phone numbers: {e}")
        return False

if __name__ == '__main__':
    # Test for save_phone_numbers_to_csv
    print("Testing save_phone_numbers_to_csv...")
    sample_phone_data = [
        {'category': 'TestCat1', 'url': 'http://test1.com', 'phone_number': '111-222-3333'},
        {'category': 'TestCat2', 'url': 'http://test2.com', 'phone_number': '444-555-6666'},
        {'category': '', 'url': 'http://test3.com', 'phone_number': '777-888-9999'}
    ]

    save_successful = save_phone_numbers_to_csv(sample_phone_data)

    if save_successful:
        print("save_phone_numbers_to_csv executed, check output message for success.")
        # Find the created file to clean up
        # This is a bit simplified; assumes it's the only/newest CSV in the dir
        try:
            files = sorted(
                [os.path.join(PHONE_NUMBERS_DIR, f) for f in os.listdir(PHONE_NUMBERS_DIR) if f.startswith("extracted_phones_") and f.endswith(".csv")],
                key=os.path.getmtime
            )
            if files:
                latest_file = files[-1]
                print(f"Attempting to read back {latest_file} for verification (optional check)...")
                # Basic verification: read header
                with open(latest_file, mode='r', newline='', encoding='utf-8') as f_read:
                    reader = csv.reader(f_read)
                    header = next(reader)
                    if header == ["Category", "URL", "Phone Number"]:
                        print(f"Header verification successful for {latest_file}.")
                    else:
                        print(f"Header verification failed for {latest_file}. Expected {['Category', 'URL', 'Phone Number']}, got {header}")

                print(f"Attempting to remove {latest_file}...")
                os.remove(latest_file)
                print(f"Removed {latest_file}.")
                # Try to remove the directory if it's empty
                if not os.listdir(PHONE_NUMBERS_DIR):
                    os.rmdir(PHONE_NUMBERS_DIR)
                    print(f"Removed directory {PHONE_NUMBERS_DIR} as it was empty.")
                else:
                    print(f"Directory {PHONE_NUMBERS_DIR} is not empty, not removing.")
            else:
                print("No test file found to clean up.")
        except Exception as e:
            print(f"Error during test cleanup: {e}")
    else:
        print("save_phone_numbers_to_csv failed as per its return value.")
