# src/pytestifypro/tests/features/test_wells_header.feature

@ui
Feature: Wells Header Validation
  As a tester
  I want to ensure that the well header details displayed on the UI are accurate
  So that users have confidence in the information presented

  Scenario Outline: Validate well header details for a specific UWI
    Given I have a well with UWI "<UWI>"
    When I open the well details page in the browser
    Then the UI should display the first production date as "<FirstProductionDate>"
    And the UI should display the last production date as "<LastProductionDate>"
    And the UI should display the well name as "<WellName>"
    And the UI should display the operator name as "<OperatorName>"
    And the UI should display the well status as "<WellStatus>"
    And the UI should display the hole direction as "<HoleDirection>"

  Examples:
    | UWI        | FirstProductionDate | LastProductionDate | WellName                          | OperatorName          | WellStatus  | HoleDirection |
    | 4231742813 | 8/1/2021            | 8/1/2024            | MIDNIGHT MATADOR 12-24 D #6LS      | BIRCH OPERATIONS INC  | Producing   | HORIZONTAL    |
