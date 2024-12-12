# src/pytestifypro/tests/steps/wells_header_steps.py

import logging
from pytest_bdd import given, when, then, scenarios, parsers
from pytestifypro.ui.pages.wells_page import WellPageLocators
from pytestifypro.utils.ui_actions import get_text, open_page, compare_values
import allure
import pytest

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Link the feature file
scenarios('../features/test_wells_header.feature')


@given(parsers.parse('I have a well with UWI "{uwi}"'))
def i_have_a_well_with_UWI(uwi, fetch_expected_data, request):
    """
    Store the UWI and fetch expected data from the database.
    """
    expected_data = fetch_expected_data(uwi)
    # Attach the data to the request node for access in other steps
    request.node.expected_data = expected_data
    request.node.current_UWI = uwi
    with allure.step(f"I have a well with UWI: {uwi}"):
        logger.info(f"Fetched expected data for UWI: {uwi}")
        logger.debug(f"Expected Data: {expected_data}")


@when("I open the well details page in the browser")
def i_open_the_well_details_page_in_browser(config, authenticated_driver, request, verify_navigation):
    """
    Navigate to the well details page using the provided UWI and verify navigation.
    """
    uwi = request.node.current_UWI
    with allure.step("I open the well details page in the browser"):
        base_url = config["selenium"]["base_url"]
        url = f"{base_url}/wells/{uwi}"
        logger.info(f"Attempting to open well details page for UWI: {uwi} at URL: {url}")

        # Navigate to the well details page
        authenticated_driver.get(url)
        logger.info(f"Current URL after navigation: {authenticated_driver.current_url}")
        logger.info(f"Navigated to well details page: {url}")

        # Verify navigation
        verify_navigation(authenticated_driver, uwi)
        logger.info(f"Verified navigation to the well details page for UWI: {uwi}")


@then("the UI should display the first production date as expected")
def assert_first_production_date(authenticated_driver, request):
    """
    Assert that the first production date on the UI matches the expected value from the DB.
    """
    expected = request.node.expected_data['first_production_date']
    with allure.step(f'The UI should display the first production date as "{expected}"'):
        actual_date = get_text(authenticated_driver, WellPageLocators.FIRST_PRODUCTION_DATE)
        compare_values("First Production Date", actual_date, expected)


@then("the UI should display the last production date as expected")
def assert_last_production_date(authenticated_driver, request):
    """
    Assert that the last production date on the UI matches the expected value from the DB.
    """
    expected = request.node.expected_data['last_production_date']
    with allure.step(f'The UI should display the last production date as "{expected}"'):
        actual_date = get_text(authenticated_driver, WellPageLocators.LAST_PRODUCTION_DATE)
        compare_values("Last Production Date", actual_date, expected)


@then("the UI should display the well name as expected")
def assert_well_name(authenticated_driver, request):
    """
    Assert that the well name on the UI matches the expected value from the DB.
    """
    expected = request.node.expected_data['srp_well_name']
    with allure.step(f'The UI should display the well name as "{expected}"'):
        actual_name = get_text(authenticated_driver, WellPageLocators.SRP_WELL_NAME)
        compare_values("Well Name", actual_name, expected)


@then("the UI should display the operator name as expected")
def assert_operator_name(authenticated_driver, request):
    """
    Assert that the operator name on the UI matches the expected value from the DB.
    """
    expected = request.node.expected_data['current_operator']
    with allure.step(f'The UI should display the operator name as "{expected}"'):
        actual_operator = get_text(authenticated_driver, WellPageLocators.CURRENT_OPERATOR)
        compare_values("Operator Name", actual_operator, expected)


@then("the UI should display the well status as expected")
def assert_well_status(authenticated_driver, request):
    """
    Assert that the well status on the UI matches the expected value from the DB.
    """
    expected = request.node.expected_data['srp_well_status']
    with allure.step(f'The UI should display the well status as "{expected}"'):
        actual_status = get_text(authenticated_driver, WellPageLocators.SRP_WELL_STATUS)
        compare_values("Well Status", actual_status, expected)


@then("the UI should display the hole direction as expected")
def assert_hole_direction(authenticated_driver, request):
    """
    Assert that the hole direction on the UI matches the expected value from the DB.
    """
    expected = request.node.expected_data['hole_direction']
    with allure.step(f'The UI should display the hole direction as "{expected}"'):
        actual_direction = get_text(authenticated_driver, WellPageLocators.HOLE_DIRECTION)
        compare_values("Hole Direction", actual_direction, expected)
