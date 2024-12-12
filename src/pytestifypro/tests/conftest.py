import subprocess
import time
import yaml
import pytest
import logging
import os
from urllib.parse import urlparse, urlunparse
from pytestifypro.client.api_client import APIClient
from pytestifypro.managers.priority_manager import SimplePriorityManager
from pytestifypro.reporters.difference_reporter import SimpleDifferenceReporter
from pytestifypro.utils.check_docker import check_docker
from pytestifypro.managers.queries_manager import SQLFileQueriesManager
from pytestifypro.utils.ui_actions import take_screenshot  # NEW
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pytestifypro.ui.pages.wells_page import WellPageLocators
from pytestifypro.ui.pages.login_page import LoginPage
from pathlib import Path
import allure
import psycopg2
from psycopg2.extras import RealDictCursor


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def queries_manager():
    # If using SQL files-based:
    return SQLFileQueriesManager(base_dir='src/pytestifypro/data/queries')

# Database client fixture
@pytest.fixture(scope="session")
def db_client(config, queries_manager):
    """
    Fixture to establish a database connection and provide methods to execute queries.
    """
    db_config = config['database']
    try:
        connection = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        logger.info("Database connection established.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        pytest.exit("Database connection failed.")

    yield {
        'connection': connection,
        'cursor': cursor,
        'queries_manager': queries_manager
    }

    try:
        cursor.close()
        connection.close()
        logger.info("Database connection closed.")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")

# Fixture to fetch expected data from the database based on UWI
@pytest.fixture(scope='function')
def fetch_expected_data(db_client):
    """
    Fetch expected data from the database based on the provided UWI.
    """
    def _fetch(UWI):
        query = db_client['queries_manager'].get_query('get_well_header_details.sql')
        logger.info(f"Executing query: {query} with parameters: {(UWI,)}")
        try:
            db_client['cursor'].execute(query, (UWI,))
            result = db_client['cursor'].fetchone()
            if not result:
                pytest.fail(f"No data found for UWI: {UWI}")
            logger.info(f"Fetched data for UWI {UWI}: {result}")
            return result
        except Exception as e:
            pytest.fail(f"Failed to execute query for UWI {UWI}: {e}")
    return _fetch

@pytest.fixture(scope="session")
def driver(config):
    sel_conf = config["selenium"]
    options = ChromeOptions()
    if sel_conf.get("headless", True):
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    logger.info("Initializing WebDriver...")
    driver_path = sel_conf.get("driver_path", None)
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    logger.info("Tearing down WebDriver...")
    driver.quit()

@pytest.fixture(scope="session")
def authenticated_driver(driver, config):
    """Authenticate using Azure SSO before running tests."""
    # Navigate to the base URL to initiate authentication
    base_url = config["selenium"]["base_url"]
    driver.get(base_url)
    logger.info(f"Navigated to {base_url} for authentication.")

    # Initialize the LoginPage object
    login_page = LoginPage(driver)

    # Perform login actions
    try:
        login_page.click_sso_login()
        logger.info("Clicked SSO Login button.")
        # Enter username and proceed
        login_page.enter_username(os.getenv("SSO_USERNAME"))
        login_page.click_next()
        logger.info("Successfully entered username.")
        # Enter password and sign in
        login_page.enter_password(os.getenv("SSO_PASSWORD"))
        login_page.click_sign_in()
        logger.info("Successfully entered password.")

        try:
            login_page.click_stay_signed_in()
            logger.info("Successfully logged in via Azure SSO.")
        except TimeoutException:
            logger.info("No 'Stay signed in?' prompt detected.")

        # Log the current URL after login
        current_url = driver.current_url
        logger.info(f"Post-login, navigated to: {current_url}")

        # Normalize URLs for comparison
        def normalize_url(url):
            parsed = urlparse(url)
            return urlunparse(parsed._replace(path=parsed.path.rstrip('/')))

        normalized_base_url = normalize_url(base_url)
        normalized_current_url = normalize_url(current_url)

        logger.info(f"Normalized Base URL: {normalized_base_url}")
        logger.info(f"Normalized Current URL: {normalized_current_url}")

        # Assert that post-login redirection is correct
        assert normalized_current_url == normalized_base_url, \
            f"Unexpected redirection to {current_url}. Expected: {base_url}"

    except TimeoutException as e:
        logger.warning(f"SSO login elements not found: {e}")

    return driver

@pytest.fixture(scope="function")
def verify_navigation():
    def _verify(driver, uwi):
        """
        Verify navigation to the wells page using the dynamic UWI.
        """
        retries = 2
        well_id_locator = WellPageLocators.well_id_link(uwi)
        for attempt in range(retries):
            try:
                logger.info(f"Verifying navigation to the page for UWI: {uwi}")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(well_id_locator)
                )
                logger.info(f"Successfully navigated to the wells page for UWI: {uwi}")
                return
            except TimeoutException:
                if attempt < retries - 1:
                    logger.warning(f"Retrying navigation for UWI {uwi} (Attempt {attempt + 1})...")
                    driver.refresh()
                else:
                    logger.error(f"Navigation verification failed for UWI {uwi}. Current URL: {driver.current_url}")
                    raise Exception(f"Navigation verification failed for UWI {uwi}")
    return _verify

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Hook to capture screenshot on failure
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        driver_fixture = item.funcargs.get('driver', None)
        if driver_fixture:
            test_name = report.nodeid.replace("::", "_")
            logger.warning(f"Test failed, taking screenshot: {test_name}")
            take_screenshot(driver_fixture, name=test_name)

@pytest.fixture(scope="session", autouse=True)
def test_setup():
    config_path = Path("src/pytestifypro/config/config.yaml")
    if config_path.exists():
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
    else:
        config = {}

    environment_name = "sandbox"
    env_config = config.get("environments", {}).get(environment_name, {})
    selenium_config = env_config.get("selenium", {})
    executor_config = env_config.get("executor", {})

    base_url = selenium_config.get("base_url", "Not Specified")
    browser = selenium_config.get("browser", "Not Specified")
    headless = selenium_config.get("headless", "false")

    executor_name = executor_config.get("name", "Not Specified")
    executor_type = executor_config.get("type", "Not Specified")
    report_name = executor_config.get("report_name", "Not Specified")

    # Create allure-results directory if it doesn't exist
    allure_results_path = Path("allure-results")
    allure_results_path.mkdir(exist_ok=True)

    # Write environment details to environment.properties
    env_properties = [
        f"Environment={environment_name}",
        f"Base_URL={base_url}",
        f"Browser={browser}",
        f"Headless={headless}",
        f"Executor_Name={executor_name}",
        f"Executor_Type={executor_type}",
        f"Report_Name={report_name}"
    ]

    (allure_results_path / "environment.properties").write_text("\n".join(env_properties))

@pytest.fixture
def priority_manager():
    return SimplePriorityManager(priority_map_file='src/pytestifypro/config/priority_map.yaml')

@pytest.fixture
def reporter():
    return SimpleDifferenceReporter()

@pytest.fixture(scope="session")
def config():
    with open('src/pytestifypro/config/config.yaml') as f:
        config_data = yaml.safe_load(f)

    # Select environment based on an environment variable or default to 'dev'
    selected_env = os.getenv('TEST_ENV', 'sandbox')

    # Ensure selected environment exists in the config
    if selected_env not in config_data['environments']:
        raise ValueError(f"Environment '{selected_env}' not found in config.")

    # Return the config for the selected environment
    return config_data['environments'][selected_env]

@pytest.fixture(scope="session")
def schema_config():
    with open('src/pytestifypro/config/schema_config.yaml') as f:
        schema_data = yaml.safe_load(f)
    return schema_data

# @pytest.fixture(scope="session", autouse=True)
# def start_wiremock():
#     """Start and stop WireMock server using Docker for tests."""
#     # Start WireMock using Docker
#     try:
#         subprocess.run(["docker-compose", "up", "-d"], cwd="./", check=True)
#         print("WireMock server started.")
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to start WireMock server: {e}")
#         pytest.fail("Failed to start WireMock server")
#
#     # Wait for WireMock to be fully started
#     time.sleep(10)  # Adjust the sleep time if necessary
#
#     yield
#
#     # Stop WireMock after tests
#     try:
#         subprocess.run(["docker-compose", "down"], cwd="./", check=True)
#         print("WireMock server stopped.")
#     except subprocess.CalledProcessError as e:
#         print(f"Failed to stop WireMock server: {e}")
#         pytest.fail("Failed to stop WireMock server")


@pytest.fixture(scope='session', autouse=True)
def docker_check():
    with open("/tmp/docker_check.log", "a") as log_file:
        log_file.write("Starting Docker check...\n")

        # Skip the Docker check if running inside a Docker container
        if os.path.exists('/.dockerenv') or os.path.exists('/proc/1/cgroup'):
            log_file.write("Inside Docker container, skipping Docker check.\n")
            return

        if not check_docker():
            log_file.write("Docker check failed, exiting pytest.\n")
            pytest.exit("Docker is required to run these tests. Please start Docker and try again.")

        log_file.write("Docker check passed.\n")


@pytest.fixture(scope="session")
def docker_setup():
    # Setup code for Docker environment
    yield
    # Teardown code for Docker environment


@pytest.fixture(scope="function")
def api_client(config, request):
    print(f"Markers detected: {list(request.node.keywords.keys())}")
    """
    Fixture to provide a reusable API client with the ability to choose
    between real and mock environments based on test markers.
    """
    use_mock = request.node.get_closest_marker("mock") is not None
    use_real = request.node.get_closest_marker("real") is not None

    if use_mock and use_real:
        raise ValueError("Test cannot be marked with both 'mock' and 'real'")
    elif use_mock:
        base_url = config['wiremock_base_url']
        #endpoints = {key: value for key, value in config['endpoints'].items()}
    elif use_real:
        base_url = config['base_url']
        #endpoints = {key: value for key, value in config['endpoints'].items()}
    else:
        raise ValueError("Test must be marked with either 'mock' or 'real'")

    # Save base URL to a temporary config file if needed
    temp_config_path = 'temp_config.yaml'
    with open(temp_config_path, 'w') as file:
        yaml.dump({'base_url': base_url}, file)

    client = APIClient(base_url=base_url)

    yield client
    client.close()

    os.remove(temp_config_path)  # Clean up the temporary config file


@pytest.fixture(scope='session', autouse=True)
def configure_logging():
    """
    Fixture to configure logging settings for all tests.
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow to run"
    )
