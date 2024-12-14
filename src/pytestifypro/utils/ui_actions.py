# src/pytestifypro/ui/utils/ui_actions.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
import os
from datetime import datetime

import pytest

from pytestifypro.ui.pages.wells_page_locators import WellPageLocators

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

def get_dropdown_options(driver, timeout=20):
    """
    Fetch options from the dropdown menu.
    """
    WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(WellPageLocators.VERSION_DROPDOWN)
    )
    driver.find_element(*WellPageLocators.VERSION_DROPDOWN).click()

    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(WellPageLocators.VERSION_OPTIONS)
    )
    options = driver.find_elements(*WellPageLocators.VERSION_OPTIONS)
    return [option.text.strip() for option in options]

def normalize_value(value, placeholder="–"):
    """
    Normalize a value for comparison. Replace None or missing data with a placeholder.
    """
    return value if value else placeholder


def parse_date(date_str):
    """
    Attempt to parse a date string with multiple formats.
    Returns a datetime object if successful, else raises ValueError.
    """
    date_formats = [
        "%m/%d/%Y",                  # e.g., '08/01/2021'
        "%m/%d/%Y %I:%M %p",         # e.g., '12/13/2024 12:36 PM'
        "%m/%d/%Y %H:%M",            # e.g., '12/13/2024 12:36'
        "%-m/%-d/%Y",                # e.g., '8/1/2024' (Unix/Linux)
        "%m-%d-%Y",                  # e.g., '08-01-2021'
        "%-m-%-d-%Y",                # e.g., '8-1-2021' (Unix/Linux)
        "%m/%d/%y",                  # e.g., '08/01/21'
        "%m/%d/%y %I:%M %p",         # e.g., '12/13/24 12:36 PM'
        "%m/%d/%y %H:%M",            # e.g., '12/13/24 12:36'
    ]  # Add more if necessary
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"No valid date format found for '{date_str}'")


def reorder_versions_for_ui(versions):
    """
    Reorder and renumber versions to match the UI display order:
    - Current version first.
    - Historical versions in reverse chronological order by end date of the date range.
    - Assign version numbers starting from the total number of versions down to 1.
    - Current version is named 'Version {n} Current'.
    - Historical versions are named 'Version {n-1}', 'Version {n-2}', etc.

    :param versions: List of RealDictRow objects with version details.
    :return: List of dicts with updated 'Version Name' and 'Date Range' while retaining other fields.
    """
    # Extract the "Current" version
    current_version = next((v for v in versions if "Current" in v["Version Name"]), None)

    # Extract historical versions
    historical_versions = [
        v for v in versions if "Current" not in v["Version Name"]
    ]

    # Sort historical versions by the end date of their date range in descending order
    def parse_end_date(date_str):
        """
        Parses the end date from the date range string.
        Example input: '12/13/2024 12:36 PM - 12/15/2024 02:00 PM'
        Returns a datetime object.
        """
        try:
            # Split the date range string to extract the end date
            end_date_str = date_str.split(' - ')[1]
            return parse_date(end_date_str)
        except IndexError:
            # If there's no end date, assign the earliest possible date
            return datetime.min

    historical_versions.sort(key=lambda v: parse_end_date(v["Date Range"]), reverse=True)

    # Combine current version (if it exists) with the sorted historical versions
    sorted_versions = ([current_version] if current_version else []) + historical_versions

    # Total number of versions
    total_versions = len(sorted_versions)

    # Renumber the versions while retaining all other fields
    renamed_versions = []
    for idx, version in enumerate(sorted_versions):
        new_version_number = total_versions - idx  # Assign higher numbers first
        if "Current" in version["Version Name"]:
            new_version_name = f"Version {new_version_number} Current"
        else:
            new_version_name = f"Version {new_version_number}"

        # Create a copy of the version to avoid mutating the original
        renamed_version = version.copy()
        renamed_version["Version Name"] = new_version_name
        # 'Date Range' remains unchanged

        renamed_versions.append(renamed_version)

    return renamed_versions
