# src/pytestifypro/ui/pages/login_page.py

import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pytestifypro.ui.pages.login_page_locators import LoginPageLocators
from selenium.common.exceptions import StaleElementReferenceException


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoginPage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def click_sso_login(self):
        """Click the 'Log in with Azure' button."""
        try:
            self.wait.until(EC.element_to_be_clickable(LoginPageLocators.SSO_LOGIN_BUTTON)).click()
            logger.info("SSO Login button found clicked.")
        except TimeoutException:
            logger.error("SSO Login button not found or not clickable.")

    def enter_username(self, username):
        """Enter the username in the login form."""
        try:
            username_field = self.wait.until(EC.presence_of_element_located(LoginPageLocators.USERNAME_FIELD))
            username_field.clear()
            username_field.send_keys(username)
            logger.info("Successfully entered the username.")
        except TimeoutException:
            logger.error("Username field not found.")

    def click_next(self):
        """Click the 'Next' button after entering the username."""
        try:
            self.wait.until(EC.element_to_be_clickable(LoginPageLocators.NEXT_BUTTON)).click()
            logger.info("Successfully clicked the next button.")
        except TimeoutException:
            logger.error("Next button not found or not clickable.")

    def enter_password(self, password):
        """Enter the password in the login form."""
        try:
            password_field = self.wait.until(EC.presence_of_element_located(LoginPageLocators.PASSWORD_FIELD))
            password_field.clear()
            password_field.send_keys(password)
            logger.info("Successfully entered the password.")
        except TimeoutException:
            logger.error("Password field not found.")

    def click_sign_in(self):
        """Click the 'Sign in' button after entering the password, with retries."""
        retries = 3
        for attempt in range(retries):
            try:
                sign_in_button = self.wait.until(EC.element_to_be_clickable(LoginPageLocators.SIGN_IN_BUTTON))
                sign_in_button.click()
                logger.info("Successfully clicked the signin button.")
                return
            except StaleElementReferenceException:
                logger.warning(
                    f"Stale element encountered on sign_in button. Retrying... (Attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    continue
                else:
                    logger.error("Failed to click 'Sign In' button due to stale element reference.")
                    raise
            except TimeoutException:
                logger.error("Sign in button not found or not clickable.")
                raise

    def click_stay_signed_in(self):
        """Click the 'Stay Signed In' button with robust handling for stale elements."""
        retries = 3
        for attempt in range(retries):
            try:
                logger.info("Attempting to click 'Stay Signed In' button...")
                # Re-locate the element in every retry
                stay_signed_in_button = self.wait.until(
                    EC.element_to_be_clickable(LoginPageLocators.STAY_SIGNED_IN_BUTTON)
                )
                stay_signed_in_button.click()
                logger.info("'Stay Signed In' button clicked successfully.")
                return
            except StaleElementReferenceException:
                logger.warning(f"Stale element encountered. Retrying... (Attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    continue
                else:
                    logger.error("Failed to click 'Stay Signed In' button due to stale element reference.")
                    raise
            except TimeoutException:
                logger.error("Timeout waiting for 'Stay Signed In' button to become clickable.")
                raise

        # Optional: Refresh the page and try again as a last resort
        logger.info("Refreshing the page to attempt clicking 'Stay Signed In' button again...")
        self.driver.refresh()
        stay_signed_in_button = self.wait.until(
            EC.element_to_be_clickable(LoginPageLocators.STAY_SIGNED_IN_BUTTON)
        )
        stay_signed_in_button.click()
        logger.info("'Stay Signed In' button clicked successfully after page refresh.")
