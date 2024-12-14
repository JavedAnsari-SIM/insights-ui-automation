#src/pytestifypro/tests/features/test_well_header.feature

@well_with_versions
Feature: Wells Header Validation
  As a tester
  I want to ensure that the well header details displayed on the UI are accurate as per the selected well versions
  So that users have confidence in the information presented

  Scenario Outline: Verify available versions in the well header version dropdown
    Given I have a well with UWI "<UWI>"
    When I fetch the available versions for the well from the database
    And I open the well details page in the browser
    Then the UI should display all available versions for the well in the dropdown

  Examples:
    | UWI        |
    | 4231742813 |
    | 4231742808 |
    | 4222738886 |
    | 4232934481 |
    | 4222738869 |
    | 4222738707 |



  Scenario Outline: Validate well header details for each version selection
    Given I have a well with UWI "<UWI>"
    When I fetch the available versions for the well from the database
    And I open the well details page in the browser
    And I iterate through each available version and select it
    Then the UI should display the first production date as expected
    And the UI should display the last production date as expected
    And the UI should display the well name as expected
    And the UI should display the operator name as expected
    And the UI should display the well status as expected
    And the UI should display the hole direction as expected

  Examples:
    | UWI        |
    | 4231742813 |
    | 4231742808 |
    | 4222738886 |
    | 4232934481 |
    | 4222738869 |
    | 4222738707 |
