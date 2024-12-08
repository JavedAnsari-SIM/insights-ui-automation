# pytestifypro

**pytestifypro** is a Python testing framework that enhances pytest by offering utility functions and streamlined configurations. It simplifies writing, executing, and managing tests, making it easier to achieve robust and reliable testing outcomes.

## Features

- **Enhanced Logging Utilities**: Comprehensive logging functions for various levels, including info, warning, error, and critical.
- **Flexible URL Formatting**: Utility to dynamically format URLs with parameters, combining a base URL and endpoint.
- **Schema Validation**: Built-in support for JSON schema validation to ensure data integrity and compliance.
- **Advanced Comparison**: Recursive JSON comparison to identify discrepancies between expected and actual data.
- **Priority Management**: Assign priorities to JSON fields or paths, with the ability to customize priorities via YAML configuration.
- **Difference Reporting**: Enhanced reporting of differences in JSON comparisons, with prioritized messages.
- **Configuration Management**: Centralized configuration using YAML files for base URLs, endpoints, and schemas, streamlining test setups.
- **Robust Test Utilities**: Functions for managing retries, logging response times, and handling HTTP operations (GET, POST, PUT, DELETE).
- **Docker Integration**: Build and run tests within Docker containers.
- **Session Management**: Check Docker status and manage Docker sessions.
- **Allure Reporting**: 
  - **Feature Management**: Add and manage features, stories, descriptions, and severity levels in Allure reports.
  - **Dynamic Reporting**: Generate and serve interactive Allure reports to visualize test results.
  - **Attachment and Step Reporting**: Attach files and add steps to enhance report details.

## Installation

To use `pytestifypro`, you need to have Python 3.12 or higher installed. You can set up the environment and install dependencies using `Poetry`.

1. **Clone the Repository**:
   ```bash
   git clone <REPOSITORY_URL>
   cd <REPOSITORY_NAME>

2. **Install Dependencies**:
   ```
   curl -sSL https://install.python-poetry.org | python3 -
   poetry install
   ```

3. **Activate the Virtual Environment**:
   ```
   poetry shell
   ```

## Docker Requirements

Docker is required to run the tests using the provided Docker image. Make sure Docker is installed and running on your machine. If Docker is not installed, follow the installation guide for your operating system:

- [Docker Installation Guide](https://docs.docker.com/get-docker/)

### Starting Docker

If Docker is not running, you can start it by following these steps:

- **For macOS**: Open the Docker Desktop application.
- **For Windows**: Open Docker Desktop from the Start menu.
- **For Linux**: Run `sudo systemctl start docker` in the terminal.

### Troubleshooting

If you encounter errors related to Docker not running, make sure Docker is properly installed and the Docker daemon is active.

## Checking Docker Status

Before running Docker commands, you can check if Docker is running by executing the following Python script:

```bash
python scripts/check_docker.py
```

## Usage

### 1. **Writing Tests**:
   You can create test files under the src/pytestifypro/tests directory. Here’s a basic example:
###### src/pytestifypro/tests/sample_test.py
```bash    
    from pytestifypro.utils.utils import log_info, format_url
        
    def test_format_url():
    base_url = "http://example.com"
    endpoint = "api/test"
    expected = "http://example.com/api/test"
    assert format_url(base_url, endpoint) == expected
    
    def test_log_info(caplog):
    log_info("Test message")
    assert "INFO: Test message" in caplog.text    
```
### 2. **Running Tests**:
- Use Poetry to run tests and generate a coverage report:
   ```bash
     poetry run pytest
     ```
   - Or, use pytest directly:
```BASH   
    pytest --cov=src/pytestifypro --cov-report=term-missing
```
## Running Tests with Docker

You can run the tests in a Docker container by building and running the Docker image.

### Build the Docker Image

```bash
docker build -t pytestifypro:latest .
````
### Run Tests Using Docker
```
docker run --rm pytestifypro:latest
```
### Running Tests Without Docker

If you do not want to use Docker, you can run the tests directly using Poetry. Follow these steps:

1. **Install Dependencies**

    ```bash
    poetry install
    ```

2. **Run Tests**

    ```bash
    poetry run pytest
    ```

## CI/CD Pipeline Setup

This project uses Jenkins for continuous integration and continuous deployment (CI/CD). The pipeline is configured to automatically build and test the code upon each push to the `main` branch.

# Jenkins Implementation for pytestifypro Framework

## Overview

This README provides an overview of the Jenkins setup for the pytestifypro framework. Jenkins is configured to build Docker images, run tests, and handle the deployment pipeline efficiently.

## Jenkins Setup

### Prerequisites
- Jenkins installed and running (preferably using Docker).
- Docker installed on the Jenkins server.
- Git repository containing the pytestifypro framework.

### Jenkinsfile

The `Jenkinsfile` is located in the root of the repository and defines the pipeline for building, testing, and deploying the application. It includes:

1. **Pipeline Definition**: Specifies stages for building Docker images, running tests, and handling post-build actions.
2. **Build Stage**: Builds Docker images for the `pytestifypro` application and `WireMock` service.
3. **Test Stage**: Executes tests inside the Docker containers and generates reports.
4. **Post-Build Actions**: Archives test results and reports for review.

### Key Stages in Jenkinsfile

1. **Build Stage**
   ```groovy
   stage('Build') {
       steps {
           script {
               docker.build('pytestifypro-image', '-f Dockerfile .')
           }
       }
   }
   ```
2. **Test Stage**
    ```groovy
    stage('Test') {
    steps {
        script {
            docker.image('pytestifypro-image').inside {
                sh 'pytest --alluredir=allure-results'
                allure([
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }
    }
    ```
3. **Post-Build Actions**
    ```groovy
   stage('Post-Build') {
    steps {
        archiveArtifacts artifacts: '**/allure-results/**', allowEmptyArchive: true
    }
    }
   ```
## Docker Integration
The docker-compose.yml file is used to define and run multi-container Docker applications. It includes:

- WireMock Service: Mock server for testing APIs.
- pytestifypro Service: Main application service for running tests.

## Webhooks
   - Webhooks should be set up in your GitHub repository to trigger the Jenkins pipeline on code changes. Ensure the webhook points to the public Jenkins URL.

## Troubleshooting
- Port Conflicts: Ensure no other services are using the ports specified in docker-compose.yml.
- Dependency Issues: Verify Dockerfile dependencies and ensure they are correctly installed.
- Test Failures: Review test logs for detailed error messages and adjust test configurations as needed.

# Configuration

## pytest.ini Configuration

The `pytest.ini` file is located in the root directory and is used to configure pytest options:

```ini
[pytest]
addopts = --maxfail=5 --disable-warnings -q
testpaths =
    src/pytestifypro/tests
```

## Environment Configuration
pytestifypro supports flexible environment configurations using YAML files. This allows you to define different settings for various environments, such as development, staging, and production. Each environment can have its own base URL, WireMock URL, endpoints, and mock data.

Example Configuration (src/pytestifypro/config/config.yaml):
```yaml
environments:
  dev:
    base_url: "https://dev.api.example.com"
    wiremock_base_url: "http://localhost:8080"
    endpoints:
      upi_payment_status: "/upi/payment/status"
    upi_payment:
      success:
        payload:
          transactionId: "1234567890"
        response:
          status: "SUCCESS"
          transactionId: "1234567890"
          amount: "100.00"
          currency: "INR"
          message: "Payment successful"
          upiId: "user@upi"
      failure:
        payload:
          transactionId: "1234567891"
        response:
          status: "FAILURE"
          transactionId: "1234567891"
          amount: "100.00"
          currency: "INR"
          message: "Payment failed"
          errorCode: "INSUFFICIENT_FUNDS"
      pending:
        payload:
          transactionId: "1234567892"
        response:
          status: "PENDING"
          transactionId: "1234567892"
          amount: "100.00"
          currency: "INR"
          message: "Payment is pending"
          upiId: "user@upi"
  staging:
    base_url: "https://staging.api.example.com"
    wiremock_base_url: "http://localhost:8080"
    endpoints:
      upi_payment_status: "/upi/payment/status"
    upi_payment:
      success:
        payload:
          transactionId: "1234567890"
        response:
          status: "SUCCESS"
          transactionId: "1234567890"
          amount: "100.00"
          currency: "INR"
          message: "Payment successful"
          upiId: "user@upi"
      failure:
        payload:
          transactionId: "1234567891"
        response:
          status: "FAILURE"
          transactionId: "1234567891"
          amount: "100.00"
          currency: "INR"
          message: "Payment failed"
          errorCode: "INSUFFICIENT_FUNDS"
      pending:
        payload:
          transactionId: "1234567892"
        response:
          status: "PENDING"
          transactionId: "1234567892"
          amount: "100.00"
          currency: "INR"
          message: "Payment is pending"
          upiId: "user@upi"
  prod:
    base_url: "https://jsonplaceholder.typicode.com"
    wiremock_base_url: "http://localhost:8080"
    endpoints:
      upi_payment_status: "/upi/payment/status"
    upi_payment:
      success:
        payload:
          transactionId: "1234567890"
        response:
          status: "SUCCESS"
          transactionId: "1234567890"
          amount: "100.00"
          currency: "INR"
          message: "Payment successful"
          upiId: "user@upi"
      failure:
        payload:
          transactionId: "1234567891"
        response:
          status: "FAILURE"
          transactionId: "1234567891"
          amount: "100.00"
          currency: "INR"
          message: "Payment failed"
          errorCode: "INSUFFICIENT_FUNDS"
      pending:
        payload:
          transactionId: "1234567892"
        response:
          status: "PENDING"
          transactionId: "1234567892"
          amount: "100.00"
          currency: "INR"
          message: "Payment is pending"
          upiId: "user@upi"
```
## Schema Configuration
pytestifypro supports JSON schema validation to ensure data integrity and compliance. You can define schemas for different API responses and validate against these schemas during tests.

Example Schema Configuration (src/pytestifypro/config/schema_config.yaml):
```yaml
schemas:
  upi_payment_response:
    type: object
    properties:
      status:
        type: string
      transactionId:
        type: string
      amount:
        type: string
      currency:
        type: string
      message:
        type: string
      upiId:
        type: string
    required:
      - status
      - transactionId
      - amount
      - currency
      - message
```
## Priority and Difference Management
pytestifypro now supports priority-based difference management for JSON comparisons:

### Priority Manager
Configure priorities for different JSON paths via YAML files (e.g., src/pytestifypro/config/priority_map.yaml).

Example Priority Map (src/pytestifypro/config/priority_map.yaml):
```yaml
priority_map:
  upi_payment_status:
    ".status": "P1"
    ".transactionId": "P1"
    ".amount": "P2"
    ".currency": "P3"
    ".message": "P2"
```
## Difference Reporter
Customizable reporters that output discrepancies with assigned priorities.

## How to Use Configuration Files
- Define Your Configuration: Place your YAML configuration files in the src/pytestifypro/config/ directory.
- Load Configurations: pytestifypro automatically loads and applies the configurations during test execution based on the environment specified.


## Allure Reporting Integration

**pytestifypro** supports Allure reporting to enhance the visibility and management of test results. This section provides information on how to set up and use Allure reporting within your testing framework.

### Setup

1. **Install Dependencies**:
   Ensure you have the `allure-pytest` package installed. You can add it to your `pyproject.toml` file or install it directly:

   ```bash
   poetry add allure-pytest
2. **Update conftest.py**: Add a fixture to manage Allure reporting details. This fixture allows you to set features, stories, descriptions, and severity levels for your tests:
```python
# src/pytestifypro/tests/conftest.py
import pytest
from pytestifypro.utils.allure_reporter import AllureReporter

@pytest.fixture
def test_setup():
    def _setup(feature, story, description, severity):
        AllureReporter.add_feature(feature)
        AllureReporter.add_story(story)
        AllureReporter.add_description(description)
        AllureReporter.add_severity(severity)
    return _setup

```
3. **Update allure_reporter.py**: Implement Allure reporting functions for features, stories, descriptions, severity, attachments, and steps:
```python
# src/pytestifypro/utils/allure_reporter.py
import allure

class AllureReporter:
    @staticmethod
    def add_feature(feature_name: str):
        allure.dynamic.feature(feature_name)

    @staticmethod
    def add_story(story_name: str):
        allure.dynamic.story(story_name)

    @staticmethod
    def add_description(description: str):
        allure.dynamic.description(description)

    @staticmethod
    def add_severity(severity_level: str):
        allure.dynamic.severity(severity_level)

    @staticmethod
    def attach_file(name: str, content: bytes, attachment_type=allure.attachment_type.TEXT):
        allure.attach(name=name, body=content, attachment_type=attachment_type)

    @staticmethod
    def add_step(step_name: str):
        with allure.step(step_name):
            pass
```
### Running Tests with Allure
1. ***Run Tests***: Execute your tests and generate Allure results:

```bash
Copy code
poetry run pytest --alluredir=allure-results
````
2. ***Generate and View Allure Report***: Use the following command to generate and serve the Allure report:
```bash
Copy code
allure serve allure-results
```

## **Contribution Guidelines**:
    To contribute to the development of pytestifypro, follow these steps:
   - **Create a New Branch**:
       ```BASH
         git checkout -b feature/my-feature
       ```
   - **Make Your Changes**:
        Edit code and write tests as needed.
- 
  - **Commit Your Changes**:
      ```BASH
      git add .
      git commit -m "Add new feature or fix bug"
      ```
  - **Push Your Changes**:
      ```BASH
      git push origin feature/my-feature
      ```
  - **Create a Pull Request**:
        Open a pull request on the repository to merge your changes.

## WireMock Integration

### Setting Up WireMock

To test your APIs using WireMock:

1. **Directory Structure**:
   - Place your WireMock mappings in the `wiremock/mappings` directory.
   - Place your response files in the `wiremock/__files` directory.

2. **Running WireMock**:
   - **New Addition**: WireMock can be started and stopped automatically using `pytest` fixtures. See [conftest.py](./src/pytestifypro/tests/conftest.py) for details.
   - **Multiple Markers Handling**: You can now specify markers in your tests to indicate whether to use mock endpoints or real endpoints. The conftest.py has been updated to handle these markers and set up the correct environment.

3. **Writing Tests**:
   - **Mock Endpoint Test**: Use the @pytest.mark.mock decorator to indicate that a test should use mock endpoints. 
   - **Real Endpoint Test**: Use the @pytest.mark.real decorator for tests that should interact with real endpoints.

### Example Test
#### Mock End Point Example
```python
import pytest
import requests

@pytest.mark.mock
def test_sample_response_with_mock():
    response = requests.get("http://localhost:8080/api/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Sample response from WireMock"}

```
#### Real End Point Example
```python
import pytest
import requests

@pytest.mark.real
def test_sample_response_with_real():
    response = requests.get("http://api.realendpoint.com/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Sample response from Real Endpoint"}
```

### Summary

- **Automate Setup**: Use `pytest` fixtures to manage WireMock lifecycle.
- **Handle Multiple Environments**: New Addition: Use pytest markers to switch between mock and real endpoints seamlessly.
- **Enhance Coverage**: Add more tests and mappings.
- **CI/CD Integration**: Configure your CI/CD pipeline to handle WireMock.
- **Update Documentation**: Provide clear instructions on using WireMock.

If you need help with any of these steps or have additional questions, let me know!

## API Documentation

### APIClient Class
- get(url, headers=None, params=None): Sends a GET request.
  -  Parameters:
     - url: The URL to send the request to. 
     - headers: Optional headers to include in the request. 
     - params: Optional parameters to include in the request. 
  - Returns: Response object.
- post(url, headers=None, data=None, json=None): Sends a POST request.
  - Parameters:
    - url: The URL to send the request to. 
    - headers: Optional headers. 
    - data: Optional data to send in the request body. 
    - json: Optional JSON to send in the request body.
  - Returns: Response object. 

## Utility Functions
- format_url(base_url, endpoint): Combines a base URL and endpoint.
- validate_json_schema(response_json, schema): Validates JSON response against a schema.
- compare_json(expected, actual, path=""): Compares two JSON objects recursively. 
- load_schema(file_path='src/pytestifypro/config/schema_config.yaml'): Loads JSON schema from a YAML file.
- assert_no_differences(differences: list[str]): Asserts that there are no differences in the JSON comparison and logs differences if found.

## License
This project is licensed under the MIT License - see the LICENSE file for details.


## Contact
For any questions or issues, please contact javed.ansari@strongholdindia.com
