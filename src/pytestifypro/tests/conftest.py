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
from pytestifypro.utils.allure_reporter import AllureReporter
from pytestifypro.managers.queries_manager import SQLFileQueriesManager
from pytestifypro.utils.ui_actions import take_screenshot  # NEW
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pytestifypro.ui.pages.wells_page import WellPageLocators
from pytestifypro.ui.pages.login_page import LoginPage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def db_client(config):
    db_conf = config["database"]
    client = DBClient(
        host=db_conf["host"],
        port=db_conf["port"],
        user=db_conf["user"],
        password=db_conf["password"],
        database=db_conf["database"]
    )
    client.connect()
    yield client
    client.close()

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

@pytest.fixture(scope="session")
def queries_manager():
    # If using YAML-based:
    # return QueriesManager(queries_file='src/pytestifypro/data/queries.yaml')

    # If using SQL files-based:
    return SQLFileQueriesManager(base_dir='src/pytestifypro/data/queries')

@pytest.fixture
def test_setup():
    def _setup(feature, story, description, severity):
        AllureReporter.add_feature(feature)
        AllureReporter.add_story(story)
        AllureReporter.add_description(description)
        AllureReporter.add_severity(severity)
    return _setup

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
