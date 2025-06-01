import csv
import os
import collections # Moved import collections to the top

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.data_handler import save_phone_numbers_to_csv # Added import

def read_input_csv(file_path):
    """
    Reads a CSV file, extracts 'URL' and 'Category' from each row.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list: A list of dictionaries, where each dictionary has 'url' and 'category' keys.
              Returns an empty list if there's a FileNotFoundError or CSV parsing error.
    """
    results = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            # Use DictReader to directly access columns by header name
            reader = csv.DictReader(csvfile)
            for row in reader:
                url = row.get('URL', '') # Default to empty string if 'URL' column is missing
                category = row.get('Category', '') # Default to empty string if 'Category' column is missing or empty

                # Ensure URL is present, otherwise it might not be useful
                if not url:
                    print(f"Warning: Row found with missing URL in {file_path}: {row}")
                    continue # Skip rows with no URL

                results.append({'url': url, 'category': category})
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []
    except csv.Error as e:
        print(f"Error parsing CSV file {file_path}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        return []
    return results

if __name__ == '__main__':
    # The dummy CSV 'contents/test_input.csv' should have been created in a previous step.
    # If not, this test block might fail or act on an empty/non-existent file.
    # For robust testing, especially in isolated environments, it's good practice
    # to ensure the test file is created here if it doesn't exist.

    dummy_csv_dir = "contents"
    dummy_csv_path = os.path.join(dummy_csv_dir, "test_input.csv")

    # Ensure the directory exists (create_file_with_block in previous step should handle this)
    # os.makedirs(dummy_csv_dir, exist_ok=True) # Not strictly needed if previous tool call succeeded

    # The content for the dummy CSV file (matches what was intended for create_file_with_block)
    dummy_csv_content = """Category,URL,OtherColumn
Tech,http://example.com/tech,Data1
Retail,http://example.com/retail,Data2
,http://example.com/nocat,Data3
Food,http://example.com/food,Data4
"""
    # Verify the file was created (or create it if it's missing for some reason in a test setup)
    # This is more of a safeguard for standalone script execution.
    # In this multi-turn agent flow, the previous step explicitly created it.
    if not os.path.exists(dummy_csv_path):
        print(f"Test file {dummy_csv_path} not found. Attempting to create it for the test.")
        try:
            os.makedirs(dummy_csv_dir, exist_ok=True)
            with open(dummy_csv_path, 'w', newline='', encoding='utf-8') as f:
                f.write(dummy_csv_content)
            print(f"Test file {dummy_csv_path} created.")
        except Exception as e:
            print(f"Failed to create test file {dummy_csv_path}: {e}")
            # Exit if test file can't be created, as test will fail.
            exit(1)

    print(f"Attempting to read: {dummy_csv_path}")
    extracted_data = read_input_csv(dummy_csv_path)

    print("\nExtracted data:")
    if extracted_data:
        for item in extracted_data:
            print(item)
    else:
        print("No data extracted or an error occurred.")

    # Example of expected output for verification (optional, but good for testing)
    expected_data = [
        {'url': 'http://example.com/tech', 'category': 'Tech'},
        {'url': 'http://example.com/retail', 'category': 'Retail'},
        {'url': 'http://example.com/nocat', 'category': ''}, # Category is empty string
        {'url': 'http://example.com/food', 'category': 'Food'}
    ]

    # Basic assertion for the test
    # Note: Comparing lists of dicts can be tricky if order is not guaranteed.
    # For this specific implementation, order is preserved.
    if collections.Counter(map(tuple, map(sorted, map(dict.items, extracted_data)))) == \
       collections.Counter(map(tuple, map(sorted, map(dict.items, expected_data)))):
        print("\nTest passed: Extracted data matches expected data.")
    else:
        print("\nTest failed: Extracted data does not match expected data.")
        print(f"Expected: {expected_data}")
        print(f"Got: {extracted_data}")

    # Test with a non-existent file
    print("\nTesting with a non-existent file:")
    non_existent_data = read_input_csv("non_existent_file.csv")
    if not non_existent_data:
        print("Correctly returned empty list for non-existent file.")
    else:
        print(f"Test failed: Expected empty list, got {non_existent_data}")

    # Cleanup: Remove the dummy CSV file and directory if desired
    # try:
    #     os.remove(dummy_csv_path)
    #     os.rmdir(dummy_csv_dir) # rmdir only removes empty directories
    #     print(f"\nCleaned up {dummy_csv_path} and {dummy_csv_dir}")
    # except OSError as e:
    #     print(f"\nError during cleanup: {e}")
    #     print("(This is normal if other files are in 'contents' or dir doesn't exist)")


def extract_phone_from_url(driver, url):
    """
    Extracts a phone number from a given URL using Selenium and BeautifulSoup.

    Args:
        driver: A Selenium WebDriver instance.
        url (str): The URL to scrape.

    Returns:
        str: The extracted phone number, or an empty string if not found or an error occurs.
    """
    try:
        driver.get(url)
        # Wait for the body element to be present, indicating basic page load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Specific class names for locating the elements
        # These are very long and specific; ensure they are exact.
        outer_div_class = "x9f619 x1n2onr6 x1ja2u2z x78zum5 xdt5ytf x193iq5w xeuugli x1r8uery x1iyjqo2 xs83m0k xamitd3 xsyo7zv x16hj40l x10b6aqq x1yrsyyn"
        span_class = "x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h"

        phone_number_text = ""

        # Find the outer div
        # Note: BeautifulSoup's find method with a class string containing spaces will look for elements
        # that have *all* these classes. This is usually what's intended.
        outer_div = soup.find("div", class_=outer_div_class)

        if outer_div:
            # Find the span within the outer div
            phone_span = outer_div.find("span", class_=span_class)
            if phone_span:
                phone_number_text = phone_span.get_text(strip=True)
                if phone_number_text:
                    print(f"Successfully extracted phone: {phone_number_text} from {url}")
                    return phone_number_text
                else:
                    print(f"Warning: Found phone span for {url}, but it contained no text.")
            else:
                print(f"Warning: Phone number span not found within the specified div for URL: {url}")
        else:
            # Attempt to find the span directly if the outer div structure is not strictly as expected,
            # or if the class names apply to a more deeply nested structure.
            # This is a fallback / alternative search.
            print(f"Warning: Outer div with class '{outer_div_class}' not found for URL: {url}. Attempting to find span directly.")
            phone_span_direct = soup.find("span", class_=span_class)
            if phone_span_direct:
                # Check if this directly found span is within a div that has *some* of the outer div classes,
                # to reduce false positives if the span class is reused elsewhere.
                # This is an approximation, as checking all classes is too strict.
                # For now, we'll trust the span class is specific enough if outer_div is not found.
                phone_number_text = phone_span_direct.get_text(strip=True)
                if phone_number_text:
                    print(f"Successfully extracted phone (direct span search): {phone_number_text} from {url}")
                    return phone_number_text
                else:
                    print(f"Warning: Found phone span directly for {url}, but it contained no text.")
            else:
                print(f"Warning: Phone number span not found directly either for URL: {url}")

        if not phone_number_text:
             print(f"Warning: Phone number not found on page for URL: {url}")
        return ""

    except TimeoutException:
        print(f"Warning: Page load timed out for URL: {url}")
        return ""
    except Exception as e:
        # Catching a broad exception for any other Selenium/BeautifulSoup errors
        print(f"Error extracting phone number from URL {url}: {e}")
        return ""
