# src/pytestifypro/tests/features/test_wells_header.feature

@ui
Feature: Wells Header Validation
  As a tester
  I want to ensure that the well header details displayed on the UI are accurate
  So that users have confidence in the information presented

  Scenario Outline: Validate well header details for a specific UWI
    Given I have a well with UWI "<UWI>"
    When I open the well details page in the browser
    Then the UI should display the first production date as expected
    And the UI should display the last production date as expected
    And the UI should display the well name as expected
    And the UI should display the operator name as expected
    And the UI should display the well status as expected
    And the UI should display the hole direction as expected

  Examples:
    | UWI        |
    | 4231742813 |
    | 4231742710 |
    | 4222738886 |
