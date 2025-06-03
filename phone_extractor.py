import csv
import os

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    input_csv_path = "contents/test_input.csv"
    # Output path is managed by save_phone_numbers_to_csv in data_handler.py
    # For clarity, we can define it here but it's not directly passed to the save function
    # if we stick to the current save_phone_numbers_to_csv implementation.
    # output_csv_path = "contents/extracted_phones.csv" # This was the original plan
    # However, save_phone_numbers_to_csv in data_handler.py creates timestamped files in "phone_numbers/"

    print(f"Starting phone extraction process...")
    print(f"Reading input from: {input_csv_path}")

    # Check if input file exists
    if not os.path.exists(input_csv_path):
        print(f"Error: Input CSV file not found at {input_csv_path}")
        print("Please ensure the input file exists. For example, it might be created by a previous step or manually.")
        # Example content for contents/test_input.csv if needed for a quick test:
        # print("Example content for 'contents/test_input.csv':")
        # print("Category,URL")
        # print("Tech,https://www.example.com/tech_page_with_phone")
        # print("Retail,https://www.example.com/retail_page_with_phone")
        exit(1) # Exit if input file is crucial and missing

    url_data = read_input_csv(input_csv_path)

    if not url_data:
        print("No data read from input CSV or an error occurred. Exiting.")
        exit(1)

    print(f"Successfully read {len(url_data)} URLs from {input_csv_path}.")

    # Initialize Selenium WebDriver
    print("Initializing Selenium WebDriver (Chrome headless)...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # The webdriver executable should be in PATH or specify executable_path
    # For GitHub Actions, chromedriver is often pre-installed and in PATH
    try:
        driver = webdriver.Chrome(options=options)
        print("WebDriver initialized successfully.")
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Ensure Chrome and ChromeDriver are correctly installed and configured.")
        exit(1)

    all_results = []

    print(f"Processing {len(url_data)} items...")
    for item in url_data:
        url = item.get('url')
        category = item.get('category')

        if not url:
            print(f"Skipping item with missing URL: {item}")
            continue

        print(f"Extracting phone from URL: {url} (Category: {category})")
        phone_number = extract_phone_from_url(driver, url)

        result = {'url': url, 'category': category, 'phone_number': phone_number}
        all_results.append(result)
        if phone_number:
            print(f"Found phone: {phone_number} for {url}")
        else:
            print(f"No phone found for {url}")

    # Quit WebDriver
    print("Closing WebDriver...")
    driver.quit()

    # Save results
    # The save_phone_numbers_to_csv function from data_handler.py creates its own filename
    # and saves it in the 'phone_numbers' directory.
    # It also uses headers: "Category", "URL", "Phone Number"
    print(f"Saving {len(all_results)} results...")
    if all_results:
        save_successful = save_phone_numbers_to_csv(all_results) # No output_csv_path needed as argument
        if save_successful:
            print(f"Results saved successfully by save_phone_numbers_to_csv (check 'phone_numbers' directory).")
        else:
            print(f"Failed to save results using save_phone_numbers_to_csv.")
    else:
        print("No results to save.")

    print("Phone extraction process completed.")

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
