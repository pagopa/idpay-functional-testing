@Scontoditipo1
@onboarding
Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo1"

  Scenario: User under the minimum age tries onboarding unsuccessfully
    Given the citizen A is 17 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: User just 18 tries onboarding
    Given the citizen A is 18 years old exactly
    When the citizen A tries to onboard
    Then the onboard of A is OK

  @skip
  Scenario: User just 120 tries onboarding unsuccessfully
    Given the citizen A is 120 years old exactly
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: User over the maximum age tries onboarding unsuccessfully
    Given the citizen A is 36 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: The user will be 36 years old the day after onboarding
    Given the citizen A is 36 years old tomorrow
    When the citizen A tries to onboard
    Then the onboard of A is OK

  Scenario: User with self-declared incorrect criteria tries onboarding unsuccessfully
    Given the citizen A is 23 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A insert self-declared criteria not correctly
    Then the onboard of A is KO

  Scenario: User under minimum age and with incorrect self-declared criteria tries onboarding unsuccessfully
    Given the citizen A is 17 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A insert self-declared criteria not correctly
    Then the onboard of A is KO

  Scenario: User over the maximum age and with incorrect self-declared criteria tries onboarding unsuccessfully
    Given the citizen A is 36 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A insert self-declared criteria not correctly
    Then the onboard of A is KO

  Scenario: User in age range with self-declared correct criteria tries onboarding unsuccessfully
    Given the citizen A is 25 years old tomorrow
    And the citizen A accepts terms and conditions
    When the citizen A insert self-declared criteria correctly
    Then the onboard of A is OK

  Scenario: User in age range with self-declared incorrect criteria tries onboarding unsuccessfully
    Given the citizen A is 25 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A insert self-declared criteria not correctly
    Then the onboard of A is KO

  Scenario: The user who has not accepted the Terms and conditions cannot onboard
    Given the citizen A is 23 years old at most
    When the citizen A tries to insert only self-declared criteria correctly
    Then the latest PDND autorcertification call failed
