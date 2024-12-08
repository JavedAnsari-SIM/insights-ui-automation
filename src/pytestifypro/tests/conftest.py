import subprocess
import time
import yaml
import pytest
import logging
import os
from pytestifypro.client.api_client import APIClient
from pytestifypro.managers.priority_manager import SimplePriorityManager
from pytestifypro.reporters.difference_reporter import SimpleDifferenceReporter
from pytestifypro.utils.check_docker import check_docker
from pytestifypro.utils.allure_reporter import AllureReporter

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
    selected_env = os.getenv('TEST_ENV', 'dev')

    # Ensure selected environment exists in the config
    if selected_env not in config_data['environments']:
        raise ValueError(f"Environment '{selected_env}' not found in config.")

    # Return the config for the selected environment
    return config_data['environments'][selected_env]
# def config():
#     with open('src/pytestifypro/config/config.yaml') as f:
#         config_data = yaml.safe_load(f)
#     return config_data

@pytest.fixture(scope="session")
def schema_config():
    with open('src/pytestifypro/config/schema_config.yaml') as f:
        schema_data = yaml.safe_load(f)
    return schema_data

@pytest.fixture(scope="session", autouse=True)
def start_wiremock():
    """Start and stop WireMock server using Docker for tests."""
    # Start WireMock using Docker
    try:
        subprocess.run(["docker-compose", "up", "-d"], cwd="./", check=True)
        print("WireMock server started.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start WireMock server: {e}")
        pytest.fail("Failed to start WireMock server")

    # Wait for WireMock to be fully started
    time.sleep(10)  # Adjust the sleep time if necessary

    yield

    # Stop WireMock after tests
    try:
        subprocess.run(["docker-compose", "down"], cwd="./", check=True)
        print("WireMock server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop WireMock server: {e}")
        pytest.fail("Failed to stop WireMock server")


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