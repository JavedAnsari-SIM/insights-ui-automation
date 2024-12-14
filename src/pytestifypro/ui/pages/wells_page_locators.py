from selenium.webdriver.common.by import By

class WellPageLocators:
    # Well version dropdown locators
    VERSION_DROPDOWN = (By.CSS_SELECTOR, "div[class*='_versionSwitcherContainer'] button")
    VERSION_OPTIONS = (By.CSS_SELECTOR, "ul[class*='_versionSwitcherList'] li span")
    SELECTED_VERSION = (By.CSS_SELECTOR, "span[class*='_selectedVersionLabel']")

    # Well details section locators
    SRP_WELL_NAME = (By.XPATH, "//dt[text()='SRP Well Name']/following-sibling::dd")
    CURRENT_OPERATOR = (By.XPATH, "//dt[text()='Current Operator']/following-sibling::dd")
    SRP_WELL_STATUS = (By.XPATH, "//dt[text()='SRP Well Status']/following-sibling::dd")
    HOLE_DIRECTION = (By.XPATH, "//dt[text()='Hole Direction']/following-sibling::dd")
    PERMIT_DATE = (By.XPATH, "//dt[text()='Permit Date']/following-sibling::dd/time")
    SPUD_DATE = (By.XPATH, "//dt[text()='Spud Date']/following-sibling::dd/time")
    RIG_RELEASE_DATE = (By.XPATH, "//dt[text()='Rig Release Date']/following-sibling::dd/time")
    COMPLETION_DATE = (By.XPATH, "//dt[text()='Completion Date']/following-sibling::dd/time")
    FIRST_PRODUCTION_DATE = (By.XPATH, "//dt[text()='First Production Date']/following-sibling::dd/time")
    LAST_PRODUCTION_DATE = (By.XPATH, "//dt[text()='Last Production Date']/following-sibling::dd/time")

    # Dynamic well ID locator based on the given UWI
    @staticmethod
    def well_id_link(uwi):
        """Return the locator for the well ID link based on the UWI."""
        return (By.XPATH, f"//a[@href='/wells/{uwi}']")
