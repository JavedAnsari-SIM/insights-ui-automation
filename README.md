# pytestifypro

**pytestifypro** is a robust Python testing framework designed for both backend (BE) and UI test automation. Initially built for backend testing, it now includes advanced features for UI testing, specifically tailored for the Stronghold Insights project. It simplifies writing, executing, and managing tests while ensuring high-quality outcomes.

---

## Features

### Core Framework Features:

- **Enhanced Logging Utilities**: Comprehensive logging for various levels (info, warning, error, critical).
- **Dynamic URL Formatting**: Utility to format URLs dynamically with parameters.
- **Schema Validation**: JSON schema validation to ensure data integrity.
- **Recursive JSON Comparison**: Identify discrepancies between expected and actual data.
- **Priority-based Reporting**: Assign priorities to JSON fields or paths for detailed reporting.
- **Configuration Management**: YAML-based configuration for seamless test setups.
- **Test Utilities**: Retry mechanisms, response time logging, and HTTP operations (GET, POST, PUT, DELETE).
- **Docker Support**: Build and run tests within Docker containers.
- **Allure Reporting**:
  - Dynamic reporting with features, stories, and severity levels.
  - Attachment and step-based reporting for detailed insights.

### UI Test Automation Features:

- **Selenium Integration**: Enhanced support for browser automation.
- **BDD with pytest-bdd**: Streamlined BDD-based test writing.
- **Custom Utilities for UI Automation**:
  - Element interaction: Click, input, wait.
  - Navigation and validation.
  - Dynamic locator handling.
- **Allure-enhanced Visual Reporting**: Attach screenshots, steps, and validations to reports.
- **Reusable Page Object Model (POM)**: Structure for modular and maintainable UI tests.

### Insights Project-Specific Features:

- **Authentication Flow**: Azure SSO authentication implemented in the `authenticated_driver` fixture.
- **Wells Page Navigation**: Tests for navigating and validating well details pages.
- **Database Verification**: PostgreSQL integration for backend validation.
- **Config-driven Flexibility**: Environment-specific configurations for sandbox and production setups.

---

## Installation

### Prerequisites

- **Python**: Version 3.12 or higher.
- **Poetry**: For dependency management.
- **Docker**: Optional, for containerized test execution.

### Steps

1. **Clone the Repository**:
   ```bash
   git clone <REPOSITORY_URL>
   cd pytestifypro
   ```

2. **Install Dependencies**:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   poetry install
   ```

3. **Activate the Virtual Environment**:
   ```bash
   poetry shell
   ```

---

## Docker Requirements

Docker is required to run the tests using the provided Docker image. Make sure Docker is installed and running on your machine. If Docker is not installed, follow the installation guide for your operating system:

- [Docker Installation Guide](https://docs.docker.com/get-docker/)

### Starting Docker

- **For macOS**: Open the Docker Desktop application.
- **For Windows**: Open Docker Desktop from the Start menu.
- **For Linux**: Run `sudo systemctl start docker` in the terminal.

### Troubleshooting

If you encounter errors related to Docker not running, make sure Docker is properly installed and the Docker daemon is active.

### Checking Docker Status

Before running Docker commands, you can check if Docker is running by executing the following Python script:

```bash
python scripts/check_docker.py
```

---

## Configuration

### Environment-Specific Configurations

Located in `src/pytestifypro/config/config.yaml`:

```yaml
environments:
  sandbox:
    selenium:
      base_url: "https://title-chaining-sandbox.herokuapp.com"
      browser: "chrome"
      headless: false
    database:
      host: "localhost"
      port: 5433
      user: "postgres"
      password: "postgres"
      database: "title_chaining"
```

### Pytest Configuration

Located in `pytest.ini`:

```ini
[pytest]
addopts = --maxfail=5 --disable-warnings -q
markers =
    mock: Mark tests for mock endpoints.
    real: Mark tests for real endpoints.
testpaths =
    src/pytestifypro/tests
```

---

## Usage

### Writing Tests

You can create test files under the `src/pytestifypro/tests` directory. Example:

**Test File**: `src/pytestifypro/tests/sample_test.py`
```python
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

### Running Tests

To run tests, use the following command:

```bash
TEST_ENV=sandbox poetry run pytest -m "not mock" --alluredir=allure-results --log-cli-level=INFO -s
```

#### With Docker

1. **Build Docker Image**:
   ```bash
   docker build -t pytestifypro:latest .
   ```

2. **Run Tests**:
   ```bash
   docker run --rm pytestifypro:latest
   ```

#### Generate and View Allure Reports

```bash
allure serve allure-results
```

---

## Directory Structure

```plaintext
src/pytestifypro/
├── config/         # Configuration files
├── tests/          # Test files
│   ├── features/   # BDD feature files
│   ├── steps/      # Step definitions for BDD
├── ui/             # UI test automation modules
│   ├── pages/      # Page Object Model classes
│   ├── utils/      # Utility functions for UI automation
└── utils/          # General utilities for backend and UI testing
```

---

## CI/CD Pipeline Setup

### Jenkins Setup

#### Prerequisites
- Jenkins installed and running (preferably using Docker).
- Docker installed on the Jenkins server.
- Git repository containing the `pytestifypro` framework.

#### Jenkinsfile

Located in the root of the repository, defines the pipeline for building, testing, and deploying the application.

1. **Build Stage**:
   ```groovy
   stage('Build') {
       steps {
           script {
               docker.build('pytestifypro-image', '-f Dockerfile .')
           }
       }
   }
   ```

2. **Test Stage**:
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

3. **Post-Build Actions**:
   ```groovy
   stage('Post-Build') {
       steps {
           archiveArtifacts artifacts: '**/allure-results/**', allowEmptyArchive: true
       }
   }
   ```

---

## Writing UI Tests

### Example UI Test

**Feature File**: `src/pytestifypro/tests/features/test_well_header.feature`
```gherkin
Feature: Validate Well Header
  Scenario: Validate header for a specific well
    Given I have a well with UWI "4222740198"
    When I open the well details page in the browser
    Then the header should display correct information
```

**Step Definition**: `src/pytestifypro/tests/steps/test_wells_header_steps.py`
```python
@when("I open the well details page in the browser")
def i_open_the_well_details_page_in_browser(config, authenticated_driver, uwi, verify_navigation):
    base_url = config["selenium"]["base_url"]
    url = f"{base_url}/wells/{uwi}"
    open_page(authenticated_driver, url)
    verify_navigation(authenticated_driver, uwi)
```

**Page Object**: `src/pytestifypro/ui/pages/wells_page.py`
```python
class WellPageLocators:
    HEADER = ("xpath", "//h1")
```

---

## Contribution Guidelines

1. **Create a Branch**:
   ```bash
   git checkout -b feature/<feature-name>
   ```

2. **Make Changes**:
   Update code and tests.

3. **Commit Changes**:
   ```bash
   git commit -m "<commit-message>"
   ```

4. **Push Changes**:
   ```bash
   git push origin feature/<feature-name>
   ```

5. **Create Pull Request**:
   Submit a pull request for review.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contact

For questions or issues, contact **Javed Ansari** at [javed.ansari@strongholdindia.com](mailto:javed.ansari@strongholdindia.com).
