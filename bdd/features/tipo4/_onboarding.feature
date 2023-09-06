@Scontoditipo4
@onboarding
Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo4"

  Scenario: The citizen tries to onboard on a closed initiative
    Given the citizen A has fiscal code random
    When the citizen A tries to accept terms and conditions
    Then the latest accept terms and conditions failed for initiative ended
    And the onboard of A is KO
