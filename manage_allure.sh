#!/bin/bash

# Paths
ALLURE_RESULTS_DIR="./allure-results"
ALLURE_REPORT_DIR="./allure-report"
HISTORY_DIR="${ALLURE_RESULTS_DIR}/history"

# Step 1: Preserve the history from the previous report
if [ -d "${ALLURE_REPORT_DIR}/history" ]; then
    echo "Preserving history from the previous report..."
    cp -r "${ALLURE_REPORT_DIR}/history" "${HISTORY_DIR}"
else
    echo "No existing history found. This might be the first run."
fi
# Step 2: Clean allure-results
echo "Cleaning allure-results directory..."
rm -rf "${ALLURE_RESULTS_DIR}"
mkdir -p "${ALLURE_RESULTS_DIR}"

# Step 3: Run the tests
echo "Running tests and generating allure results..."
poetry run pytest -m "well_with_versions" --alluredir="${ALLURE_RESULTS_DIR}" --log-cli-level=INFO -s

# Step 4: Generate the Allure report
echo "Generating Allure report..."
allure generate "${ALLURE_RESULTS_DIR}" --clean -o "${ALLURE_REPORT_DIR}"

# Step 5: Copy the history back to the report directory
if [ -d "${HISTORY_DIR}" ]; then
    echo "Moving history to the new report..."
    cp -r "${HISTORY_DIR}" "${ALLURE_REPORT_DIR}/history"
else
    echo "No history data found to move to the new report."
fi

# Step 6: Open the report (optional)
echo "Opening Allure report..."
allure open "${ALLURE_REPORT_DIR}"
