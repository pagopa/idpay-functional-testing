@Scontoditipo4
@onboarding
Feature: Onboarding on a closed initiative

  Background:
    Given the initiative is "Scontoditipo4"

  Scenario: The citizen tries to onboard on a closed initiative
    Given the citizen A has fiscal code random
    When the citizen A tries to accept terms and conditions
    Then the latest accept terms and conditions failed for onboarding period ended
    And the onboard of A is KO
