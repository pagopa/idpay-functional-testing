@Scontoditipo5
@onboarding
Feature: Onboarding on an adhesion-closed initiative

  Background:
    Given the initiative is "Scontoditipo5"

  Scenario: The citizen tries to onboard after the end of the onboarding period
    Given the citizen A has fiscal code random
    When the citizen A tries to accept terms and conditions
    Then the latest accept terms and conditions failed for onboarding period ended
    And the onboard of A is KO

  Scenario: The citizen tries to onboard again after being already KO for onboarding period ended
    Given the citizen A has fiscal code random
    And the citizen A tries to accept terms and conditions
    And the latest accept terms and conditions failed for onboarding period ended
    And the onboard of A is KO
    When the citizen A tries to accept terms and conditions again
    Then the latest accept terms and conditions failed for onboarding period ended
