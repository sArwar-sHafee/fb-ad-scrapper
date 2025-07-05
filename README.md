# Facebook Ad Scraper & Phone Extractor

This project contains scripts to scrape Facebook Ad Library for page URLs based on categories and then extract phone numbers from those Facebook pages.

## Project Overview

The project is divided into two main components:

1.  **Facebook Ad Scraper (`main.py`)**:
    *   Searches the Facebook Ad Library for specified categories (e.g., "cloth", "fashion") targeting a specific region (currently Bangladesh).
    *   Uses Selenium and headless Chrome to browse the Ad Library, scroll through results, and identify links to Facebook Pages.
    *   Saves the unique pairs of (search category, Facebook Page URL) into CSV files in the `contents/` directory. Output filenames are timestamped (e.g., `ad_DD-MM-YYYY_HH:MM.csv`).

2.  **Phone Number Extractor (`phone_extractor.py`)**:
    *   Reads an input CSV file (expected to be `contents/test_input.csv`) containing Facebook Page URLs. This input file should ideally be one of the outputs from the Ad Scraper.
    *   Visits each Facebook Page URL using Selenium and headless Chrome.
    *   Attempts to find and extract phone numbers from the page content by looking for specific HTML structures.
    *   Saves the results (category, URL, extracted phone number) into CSV files in the `phone_numbers/` directory. Output filenames are timestamped (e.g., `extracted_phones_YYYY-MM-DD_HH-MM-SS.csv`).

## Code Structure

```
.
├── .github/workflows/         # GitHub Actions workflows
│   ├── manual_scrape.yml      # Workflow for running the Ad Scraper
│   └── phone_extraction_workflow.yml # Workflow for running the Phone Extractor
├── .gitignore
├── README.md                  # This file
├── contents/                  # Output directory for Ad Scraper & input for Phone Extractor
│   └── test_input.csv         # Example input for phone_extractor.py
├── main.py                    # Main script for Facebook Ad Scraper
├── phone_extractor.py         # Main script for Phone Number Extractor
├── requirements.txt           # Python dependencies
├── run_scraper.sh             # Shell script to run the Ad Scraper (main.py)
├── scripts/                   # Older/Alternative scraper implementations
│   ├── scraper_bs4.py
│   └── scraper_selenium.py
└── src/                       # Source code for the Ad Scraper
    ├── __init__.py
    ├── browser.py             # Selenium WebDriver setup
    ├── config.py              # Configuration (categories, URLs, scraper settings)
    ├── data_handler.py        # CSV saving logic
    └── scraper_utils.py       # URL extraction and page interaction logic
```

## How to Run

### Prerequisites

*   Python 3.x
*   pip (Python package installer)
*   Google Chrome browser
*   ChromeDriver (must be compatible with your Chrome version and in your system's PATH)

### 1. Facebook Ad Scraper

This script will collect Facebook Page URLs from the Ad Library.

**Steps:**

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure categories (Optional):**
    Edit `src/config.py` to modify the `CATEGORIES` list if needed.

4.  **Run the scraper:**
    Using the Python script directly:
    ```bash
    python main.py
    ```
    Or using the shell script:
    ```bash
    chmod +x run_scraper.sh
    ./run_scraper.sh
    ```
    Output CSV files containing (Category, Page URL) will be saved in the `contents/` directory.

### 2. Phone Number Extractor

This script will attempt to extract phone numbers from the URLs collected by the Ad Scraper.

**Steps:**

1.  **Ensure prerequisites and dependencies are installed** (as above).

2.  **Prepare input CSV:**
    *   The script expects an input file named `test_input.csv` in the `contents/` directory.
    *   This file should have `Category` and `URL` columns. You can rename one of the output files from the Ad Scraper to `test_input.csv` or modify the `input_csv_path` variable in `phone_extractor.py`.
    *   Example `contents/test_input.csv`:
        ```csv
        Category,URL
        cloth,https://www.facebook.com/examplepage1
        fashion,https://www.facebook.com/examplepage2
        ```

3.  **Run the phone extractor:**
    ```bash
    python phone_extractor.py
    ```
    Output CSV files containing (Category, URL, Phone Number) will be saved in the `phone_numbers/` directory.

## GitHub Actions

The repository includes GitHub Actions workflows in `.github/workflows/`:

*   **`manual_scrape.yml`**: Allows manual triggering of the Ad Scraper (`main.py`). It will commit and push any new CSV files generated in the `contents/` directory.
*   **`phone_extraction_workflow.yml`**: Allows manual triggering of the Phone Extractor (`phone_extractor.py`). It includes steps to install Chrome and the correct ChromeDriver version. It will commit and push any new CSV files generated in the `phone_numbers/` directory.

## Important Notes

*   **Scraping Facebook:** Facebook's website structure changes frequently. The HTML class names and selectors used in this project (especially in `src/scraper_utils.py` for ad scraping and `phone_extractor.py` for phone number extraction) are specific and may break if Facebook updates its site. This can cause the scrapers to fail or not find data. Regular maintenance and updates to the selectors might be required.
*   **ChromeDriver:** Ensure your ChromeDriver version matches your installed Google Chrome browser version. The `phone_extraction_workflow.yml` attempts to handle this automatically in the GitHub Actions environment.
*   **Rate Limiting/Blocks:** Extensive scraping can lead to IP blocks or captchas from Facebook. The scripts include some delays, but be mindful of scraping etiquette and potential consequences.
*   **Input for Phone Extractor:** The `phone_extractor.py` script currently uses a hardcoded input file path (`contents/test_input.csv`). For more flexible use, consider modifying it to accept the input file path as a command-line argument.
```
