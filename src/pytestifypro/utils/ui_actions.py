# src/pytestifypro/ui/utils/ui_actions.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
import os
from datetime import datetime
import pytest

from pytestifypro.ui.pages.wells_page import WellPageLocators  # Ensure file is well_page.py not wells_page.py

logger = logging.getLogger(__name__)

def wait_for_element(driver, locator, timeout=10):
    """Wait for the specified element to be visible on the page."""
    logger.debug(f"Waiting for element: {locator}")
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))
    logger.debug(f"Element visible: {locator}")

def get_text(driver, locator, timeout=10):
    """Retrieve text from a web element after waiting for its visibility."""
    wait_for_element(driver, locator, timeout)
    element = driver.find_element(*locator)
    text = element.text.strip()
    logger.info(f"Fetched text from {locator}: '{text}'")
    return text

def open_page(driver, url):
    """Navigate to a specified URL."""
    logger.info(f"Opening page: {url}")
    driver.get(url)
    allure.step(f"Open page: {url}")

def parse_date(date_str):
    """
    Attempt to parse a date string with multiple formats.
    Returns a datetime object if successful, else raises ValueError.
    """
    date_formats = ["%m/%d/%Y", "%-m/%-d/%Y", "%m-%d-%Y", "%-m-%-d-%Y"]  # Add more if necessary
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"No valid date format found for '{date_str}'")


def compare_values(field_name, actual, expected):
    """
    Compare actual and expected values with logging and assertion.
    If the field is a date, normalize the format before comparison.
    """
    logger.info(f"Comparing {field_name}: Expected='{expected}', Actual='{actual}'")

    if "date" in field_name.lower():
        try:
            actual_date = parse_date(actual)
            expected_date = parse_date(expected)
            assert actual_date == expected_date, f"{field_name} mismatch: '{actual}' != '{expected}'"
            logger.info(f"{field_name} matched successfully.")
        except ValueError as ve:
            logger.error(f"Date parsing error for {field_name}: {ve}")
            allure.attach(
                f"Date parsing error: {ve}",
                name="Date Parsing Error",
                attachment_type=allure.attachment_type.TEXT
            )
            pytest.fail(f"Date parsing error for {field_name}: {ve}")
    else:
        assert actual == expected, f"{field_name} mismatch: '{actual}' != '{expected}'"
        logger.info(f"{field_name} matched successfully.")

def click_element(driver, locator, timeout=10):
    """Click a web element identified by locator after waiting for it."""
    logger.debug(f"Clicking element: {locator}")
    wait_for_element(driver, locator, timeout)
    element = driver.find_element(*locator)
    element.click()
    logger.info(f"Clicked element: {locator}")
    allure.step(f"Clicked element: {locator}")

def input_text(driver, locator, text_to_input, timeout=10):
    """Input text into a field identified by locator after waiting for it."""
    logger.debug(f"Inputting text '{text_to_input}' into element: {locator}")
    wait_for_element(driver, locator, timeout)
    element = driver.find_element(*locator)
    element.clear()
    element.send_keys(text_to_input)
    logger.info(f"Entered text into element: {locator}")
    allure.step(f"Entered text '{text_to_input}' into {locator}")

def take_screenshot(driver, name="screenshot"):
    """Take a screenshot and attach it to the Allure report."""
    logger.debug(f"Taking screenshot: {name}")
    screenshot_path = f"./screenshots/{name}.png"
    os.makedirs("./screenshots", exist_ok=True)
    driver.save_screenshot(screenshot_path)
    allure.attach.file(screenshot_path, attachment_type=allure.attachment_type.PNG)
    logger.info(f"Screenshot taken and attached: {screenshot_path}")
    allure.step(f"Screenshot captured: {screenshot_path}")
