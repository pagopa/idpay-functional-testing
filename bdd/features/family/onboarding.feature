@family
@onboarding
Feature: A family onboards an initiative

  Background:
    Given the initiative is "family"

  Scenario Outline: One member of a family onboards an initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are in the same family
    And citizens <citizens> have ISEE 19999 of type "ordinario"
    When the first citizen of <citizens> onboards
    Then the onboard of A is OK
    And the onboard of B is demanded
    And the onboard of C is demanded

    Examples: Citizens and ranking order
      | citizens        |
      | ["A", "B", "C"] |
