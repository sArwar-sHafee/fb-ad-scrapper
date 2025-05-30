"""
Browser setup and management for the Facebook Ad Scraper.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.config import BROWSER_SETTINGS

def setup_driver():
    """Set up and return a configured Chrome WebDriver.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    chrome_options = Options()
    
    # Apply browser settings from config
    if BROWSER_SETTINGS["headless"]:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={BROWSER_SETTINGS['window_size']}")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add a realistic user agent
    chrome_options.add_argument(f"--user-agent={BROWSER_SETTINGS['user_agent']}")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver
