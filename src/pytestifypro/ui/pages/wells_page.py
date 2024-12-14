#src/pytestifypro/ui/pages/wells_page.py
import logging
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from .wells_page_locators import WellPageLocators

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class WellPage:
    def __init__(self, driver):
        self.driver = driver

    def get_version_options(self):
        """
        Retrieve all version options from the dropdown.
        """
        try:
            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable(WellPageLocators.VERSION_DROPDOWN)
            )
            dropdown = self.driver.find_element(*WellPageLocators.VERSION_DROPDOWN)
            dropdown.click()

            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located(WellPageLocators.VERSION_OPTIONS)
            )
            options = self.driver.find_elements(*WellPageLocators.VERSION_OPTIONS)
            version_texts = [option.text for option in options]
            logger.info(f"Fetched version options: {version_texts}")
            return version_texts
        except TimeoutException:
            logger.error("Timeout while fetching version options.")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while fetching version options: {e}")
            raise

    def select_version(self, version_name, timeout=20):
        """
        Select a specific version from the dropdown.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(WellPageLocators.VERSION_DROPDOWN)
            )
            dropdown = self.driver.find_element(*WellPageLocators.VERSION_DROPDOWN)
            dropdown.click()

            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(WellPageLocators.VERSION_OPTIONS)
            )
            options = self.driver.find_elements(*WellPageLocators.VERSION_OPTIONS)
            for option in options:
                if version_name in option.text:
                    option.click()
                    logger.info(f"Selected version: {version_name}")
                    return
            # If version not found
            logger.error(f"Version '{version_name}' not found in dropdown.")
            raise ValueError(f"Version '{version_name}' not found in dropdown.")
        except TimeoutException:
            logger.error("Timeout while selecting version.")
            raise ValueError(f"Version '{version_name}' not found in dropdown.")
        except Exception as e:
            logger.error(f"Unexpected error while selecting version: {e}")
            raise ValueError(f"Unexpected error: {e}")
