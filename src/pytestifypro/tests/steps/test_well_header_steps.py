# src/pytestifypro/tests/steps/wells_header_steps.py

import logging
import allure
import pytest
from datetime import datetime
import re
from pytest_bdd import given, when, then, scenarios, parsers
from pytestifypro.ui.pages.wells_page import WellPage
from pytestifypro.ui.pages.wells_page_locators import WellPageLocators
from pytestifypro.utils.ui_actions import get_dropdown_options
from pytestifypro.utils.ui_actions import get_text, open_page, compare_values
from pytestifypro.utils.ui_actions import reorder_versions_for_ui
from pytestifypro.managers.queries_manager import SQLFileQueriesManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Link the feature file
scenarios('../features/test_well_header.feature')


@given(parsers.parse('I have a well with UWI "{uwi}"'))
def i_have_a_well_with_UWI(uwi, fetch_expected_data, request):
    """
    Store the UWI and fetch expected data from the database.
    """
    expected_data = fetch_expected_data(uwi)
    # Attach the data to the request node for access in other steps
    request.node.expected_data = expected_data
    request.node.current_UWI = uwi
    logger.info(f"Stored UWI: {uwi}")
    with allure.step(f"I have a well with UWI: {uwi}"):
        logger.info(f"Fetched expected data for UWI: {uwi}")
        logger.debug(f"Expected Data: {expected_data}")

@when("I fetch the available versions for the well from the database")
def fetch_versions_from_db(db_client, request):
    """
    Fetch current and historical versions for the UWI from the database.
    """
    uwi = request.node.current_UWI

    # Access queries_manager from db_client
    queries_manager = db_client["queries_manager"]

    # Query the database for current version
    current_version_query = queries_manager.get_query("get_well_versions.sql", specific_query="current_version")
    logger.info(f"Executing current version query: {current_version_query} with parameters: ({uwi},)")
    db_client["cursor"].execute(current_version_query, (uwi,))
    current_version = db_client["cursor"].fetchone()

    if not current_version:
        pytest.fail(f"No current version found for UWI: {uwi}")

    # Query the database for historical versions
    historical_versions_query = queries_manager.get_query("get_well_versions.sql", specific_query="previous_versions")
    logger.info(f"Executing historical versions query: {historical_versions_query} with parameters: ({uwi},)")
    db_client["cursor"].execute(historical_versions_query, (uwi,))
    historical_versions = db_client["cursor"].fetchall()

    # Prepare versions for UI validation
    versions = []

    # Fetch well header details for current version
    well_header_query_current = queries_manager.get_query("get_well_header_details.sql")
    logger.info(f"Executing current well header details query: {well_header_query_current} with parameters: ({uwi},)")
    db_client["cursor"].execute(well_header_query_current, (uwi,))
    well_details_current = db_client["cursor"].fetchone()

    if not well_details_current:
        pytest.fail(f"No well details found for UWI: {uwi} in current version.")

    # Update version metadata for current version
    well_details_current.update({
        "Version Name": "Version 3 Current",
        "Date Range": "12/13/2024 12:36 PM",
        "first_production_date": well_details_current["first_production_date"],
        "last_production_date": well_details_current["last_production_date"]
    })

    logger.debug(f"Current version details: {well_details_current}")

    versions.append(well_details_current)

    # Fetch production dates queries
    first_production_date_query = queries_manager.get_query("get_historical_production_dates.sql", specific_query="first_production_date")
    last_production_date_query = queries_manager.get_query("get_historical_production_dates.sql", specific_query="last_production_date")

    logger.debug(f"Fetched first_production_date_query: {first_production_date_query}")
    logger.debug(f"Fetched last_production_date_query: {last_production_date_query}")

    # Fetch well header details for historical versions
    for idx, version in enumerate(historical_versions, start=1):
        # Extract start and end periods from the fetched row
        start_period = version["start_period"]  # This should be a timestamp with time zone
        end_period = version["end_period"]      # This could be a timestamp with time zone or None

        # Format the date range string
        if not end_period:
            date_range = f"{start_period.strftime('%m/%d/%Y %I:%M %p')} - –"
        else:
            date_range = f"{start_period.strftime('%m/%d/%Y %I:%M %p')} - {end_period.strftime('%m/%d/%Y %I:%M %p')}"

        # Execute the first production date query
        try:
            logger.info(f"Executing first production date query for UWI: {uwi}, sys_period_start: {start_period}")
            db_client["cursor"].execute(
                first_production_date_query,
                (uwi, start_period, uwi, start_period, start_period)
            )
            first_production_result = db_client["cursor"].fetchone()
            first_production_date = first_production_result["first_production_date"].strftime('%m/%d/%Y') if first_production_result and first_production_result["first_production_date"] else "–"
            logger.debug(f"First Production Date: {first_production_date}")
        except Exception as e:
            pytest.fail(f"Failed to execute first production date query for UWI {uwi} and sys_period_start {start_period}: {e}")

        # Execute the last production date query
        try:
            logger.info(f"Executing last production date query for UWI: {uwi}, sys_period_start: {start_period}")
            db_client["cursor"].execute(
                last_production_date_query,
                (uwi, start_period, uwi, start_period, start_period)
            )
            last_production_result = db_client["cursor"].fetchone()
            last_production_date = last_production_result["last_production_date"].strftime('%m/%d/%Y') if last_production_result and last_production_result["last_production_date"] else "–"
            logger.debug(f"Last Production Date: {last_production_date}")
        except Exception as e:
            pytest.fail(f"Failed to execute last production date query for UWI {uwi} and sys_period_start {start_period}: {e}")

        # Fetch well header details using the existing query
        try:
            logger.info(f"Executing well header details query for UWI: {uwi}")
            db_client["cursor"].execute(well_header_query_current, (uwi,))
            well_details_history = db_client["cursor"].fetchone()
            if not well_details_history:
                pytest.fail(f"No well details found for UWI: {uwi} in historical version: {idx}")
        except Exception as e:
            pytest.fail(f"Failed to execute well header details query for UWI {uwi} and sys_period_start {start_period}: {e}")

        # Update version metadata with fetched production dates
        version_number = len(historical_versions) - idx + 1
        well_details_history.update({
            "Version Name": f"Version {version_number}",
            "Date Range": date_range,
            "first_production_date": first_production_date,
            "last_production_date": last_production_date
        })

        logger.debug(f"Historical version {version_number} details: {well_details_history}")

        versions.append(well_details_history)

    # Store the versions for validation
    request.node.versions = versions
    logger.info(f"Versions stored in request node for UWI {uwi}: {versions}")


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


@then("the UI should display all available versions for the well in the dropdown")
def validate_versions_on_ui(authenticated_driver, request):
    """
    Validate that all versions fetched from the database are displayed in the UI dropdown.
    """
    if not hasattr(request.node, "versions"):
        pytest.fail("Versions not set in request.node. Ensure the 'fetch_versions_from_db' step was executed.")

    # Reorder and renumber the database versions to match UI display order
    reordered_versions = reorder_versions_for_ui(request.node.versions)

    logger.info(f"Expected versions (reordered and renumbered): {reordered_versions}")

    # Extract only 'Version Name' and 'Date Range' from reordered_versions
    expected_versions = [{"Version Name": v["Version Name"], "Date Range": v["Date Range"]} for v in reordered_versions]

    # Fetch actual versions from the UI dropdown
    well_page = WellPage(authenticated_driver)
    actual_versions = well_page.get_version_options()
    logger.info(f"Actual versions from UI: {actual_versions}")

    # Normalize actual versions
    transformed_actual_versions = []
    for version in actual_versions:
        if " (" in version:
            version_name, date_range = version.split(" (", 1)
            date_range = date_range.rstrip(")")
        else:
            version_name = version.strip()
            date_range = None

        if not version_name or version_name.startswith("("):
            continue

        transformed_actual_versions.append({"Version Name": version_name, "Date Range": date_range})

    # Log both expected and actual versions for better debugging
    logger.debug(f"Expected versions (only relevant fields): {expected_versions}")
    logger.debug(f"Transformed actual versions: {transformed_actual_versions}")

    # Assert both lists match
    assert expected_versions == transformed_actual_versions, \
        f"Mismatch: Expected {expected_versions}, got {transformed_actual_versions}"


@when("I iterate through each available version and select it")
def iterate_and_select_versions(authenticated_driver, request):
    """
    Iterate through each version from the dropdown, select it, and store the selected version.
    """
    if not hasattr(request.node, "versions"):
        pytest.fail("Versions not set in request.node. Ensure the 'fetch_versions_from_db' step was executed.")

    # Reorder and renumber the versions to match UI display order
    reordered_versions = reorder_versions_for_ui(request.node.versions)

    well_page = WellPage(authenticated_driver)

    for version in reordered_versions:
        ui_version_name = version["Version Name"]
        logger.info(f"Selecting version: {ui_version_name}")
        well_page.select_version(ui_version_name)

        # Store the selected version for validation
        request.node.selected_version = version

        # Log the stored version details
        logger.debug(f"Selected version stored: {version}")

        # Optionally, you can assert that necessary keys exist
        required_keys = ["first_production_date", "last_production_date"]
        missing_keys = [key for key in required_keys if key not in version]
        if missing_keys:
            pytest.fail(f"Selected version is missing keys: {missing_keys}")


@then("the UI should display the first production date as expected")
def assert_first_production_date(authenticated_driver, request):
    """
    Validate that the first production date displayed matches the expected value.
    """
    selected_version = request.node.selected_version
    logger.debug(f"Selected version data: {selected_version}")

    # Ensure 'first_production_date' exists
    if 'first_production_date' not in selected_version:
        pytest.fail("Selected version does not contain 'first_production_date'.")

    expected_date = selected_version["first_production_date"]
    actual_date = get_text(authenticated_driver, WellPageLocators.FIRST_PRODUCTION_DATE)
    compare_values("First Production Date", actual_date, expected_date)


@then("the UI should display the last production date as expected")
def assert_last_production_date(authenticated_driver, request):
    """
    Validate that the last production date displayed matches the expected value.
    """
    selected_version = request.node.selected_version
    logger.debug(f"Selected version data: {selected_version}")

    # Ensure 'last_production_date' exists
    if 'last_production_date' not in selected_version:
        pytest.fail("Selected version does not contain 'last_production_date'.")

    expected_date = selected_version["last_production_date"]
    actual_date = get_text(authenticated_driver, WellPageLocators.LAST_PRODUCTION_DATE)
    compare_values("Last Production Date", actual_date, expected_date)


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
