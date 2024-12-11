# src/pytestifypro/tests/steps/test_wells_header_steps.py

import os
import logging
import allure
from pytest_bdd import given, when, then, scenarios, parsers
from pytestifypro.ui.pages.wells_page import WellPageLocators
from pytestifypro.utils.ui_actions import get_text, open_page, compare_values


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Link the feature file
scenarios('../features/test_wells_header.feature')

@given(parsers.parse('I have a well with UWI "{uwi}"'))
def i_have_a_well_with_uwi(uwi):
    """Store the UWI for use in other steps."""
    return uwi

@when("I open the well details page in the browser")
def i_open_the_well_details_page_in_browser(config, authenticated_driver, uwi, verify_navigation):
    """Navigate to the well details page using the provided UWI and verify navigation."""
    base_url = config["selenium"]["base_url"]
    url = f"{base_url}/wells/{uwi}"
    logger.info(f"Attempting to open well details page for UWI: {uwi} at URL: {url}")
    # Navigate to the well details page
    authenticated_driver.get(url)
    # Log the current URL after navigation
    current_url = authenticated_driver.current_url
    logger.info(f"Current URL after navigation: {current_url}")

    logger.info(f"Navigated to well details page: {url}")

    # Perform navigation verification after opening the page
    verify_navigation(authenticated_driver, uwi)
    logger.info(f"Verified navigation to the well details page for UWI: {uwi}")
    allure.step(f"Opened well details page for UWI: {uwi}")

@then(parsers.parse('the UI should display the first production date as "{FirstProductionDate}"'))
def assert_first_production_date(authenticated_driver, FirstProductionDate):
    """Assert that the first production date on the UI matches the expected value."""
    actual_date = get_text(authenticated_driver, WellPageLocators.FIRST_PRODUCTION_DATE)
    compare_values("First Production Date", actual_date, FirstProductionDate)

@then(parsers.parse('the UI should display the last production date as "{LastProductionDate}"'))
def assert_last_production_date(authenticated_driver, LastProductionDate):
    """Assert that the last production date on the UI matches the expected value."""
    actual_date = get_text(authenticated_driver, WellPageLocators.LAST_PRODUCTION_DATE)
    compare_values("Last Production Date", actual_date, LastProductionDate)

@then(parsers.parse('the UI should display the well name as "{WellName}"'))
def assert_well_name(authenticated_driver, WellName):
    """Assert that the well name on the UI matches the expected value."""
    actual_name = get_text(authenticated_driver, WellPageLocators.SRP_WELL_NAME)
    compare_values("Well Name", actual_name, WellName)

@then(parsers.parse('the UI should display the operator name as "{OperatorName}"'))
def assert_operator_name(authenticated_driver, OperatorName):
    """Assert that the operator name on the UI matches the expected value."""
    actual_operator = get_text(authenticated_driver, WellPageLocators.CURRENT_OPERATOR)
    compare_values("Operator Name", actual_operator, OperatorName)

@then(parsers.parse('the UI should display the well status as "{WellStatus}"'))
def assert_well_status(authenticated_driver, WellStatus):
    """Assert that the well status on the UI matches the expected value."""
    actual_status = get_text(authenticated_driver, WellPageLocators.SRP_WELL_STATUS)
    compare_values("Well Status", actual_status, WellStatus)

@then(parsers.parse('the UI should display the hole direction as "{HoleDirection}"'))
def assert_hole_direction(authenticated_driver, HoleDirection):
    """Assert that the hole direction on the UI matches the expected value."""
    actual_direction = get_text(authenticated_driver, WellPageLocators.HOLE_DIRECTION)
    compare_values("Hole Direction", actual_direction, HoleDirection)
