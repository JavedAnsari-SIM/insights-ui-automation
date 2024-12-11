# src/pytestifypro/ui/utils/ui_actions.py
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import allure
import os

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

def compare_values(field_name, actual, expected):
    """Compare actual and expected values with logging and assertion."""
    logger.info(f"Comparing {field_name}: Expected='{expected}', Actual='{actual}'")
    assert actual == expected, f"{field_name} mismatch: '{actual}' != '{expected}'"
    allure.step(f"{field_name} matches expected value")

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
