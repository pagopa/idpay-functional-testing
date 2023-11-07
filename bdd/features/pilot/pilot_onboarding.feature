@Scontoditipo1
@onboarding
Feature: Onboarding

  Background:
    Given the initiative is "Scontoditipo1"

  Scenario: A citizen under the minimum age tries to onboard unsuccessfully
    Given the citizen A is 17 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: A citizen who is just 18 tries to onboard
    Given the citizen A is 18 years old exactly
    When the citizen A tries to onboard
    Then the onboard of A is OK

  @skip
  Scenario: A citizen who is just 120 tries to onboard unsuccessfully
    Given the citizen A is 120 years old exactly
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: A citizen over the maximum age tries to onboard unsuccessfully
    Given the citizen A is 36 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: A citizen will be 36 years old the day after onboarding
    Given the citizen A is 36 years old tomorrow
    When the citizen A tries to onboard
    Then the onboard of A is OK

  Scenario: A citizen who denied PDND consent tries to onboard unsuccessfully
    Given the citizen A is 23 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A tries to save PDND consent not correctly
    Then the latest saving of consent failed because the consent was denied by the citizen
    And the onboard of A is KO

  Scenario: A citizen with self-declared incorrect criteria tries to onboard unsuccessfully
    Given the citizen A is 23 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A tries to insert wrong value in self-declared criteria
    Then the latest saving of consent failed because the citizen inserted the wrong value
    And the onboard of A is KO

  Scenario: A citizen under minimum age who denied PDND consent tries to onboard unsuccessfully
    Given the citizen A is 17 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A tries to save PDND consent not correctly
    Then the latest saving of consent failed because the consent was denied by the citizen
    And the onboard of A is KO

  Scenario: A citizen over the maximum age who denied PDND consent tries to onboard unsuccessfully
    Given the citizen A is 36 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A tries to save PDND consent not correctly
    Then the latest saving of consent failed because the consent was denied by the citizen
    And the onboard of A is KO

  Scenario: A citizen in age range who denied PDND consent tries to onboard unsuccessfully
    Given the citizen A is 25 years old tomorrow
    And the citizen A accepts terms and conditions
    When the citizen A inserts self-declared criteria
    Then the onboard of A is OK

  Scenario: A citizen in age range who denied PDND consent tries to onboard unsuccessfully
    Given the citizen A is 25 years old at most
    And the citizen A accepts terms and conditions
    When the citizen A tries to save PDND consent not correctly
    Then the latest saving of consent failed because the consent was denied by the citizen
    And the onboard of A is KO

  Scenario: A citizen who has not accepted the Terms and Conditions tries to onboard unsuccessfully
    Given the citizen A is 23 years old at most
    When the citizen A tries to save PDND consent correctly
    Then the latest saving of consent failed because the citizen did not accept T&C

  Scenario: A citizen tries to onboard a nonexistent initiative
    Given the citizen A is 21 years old exactly
    When the citizen A tries to accept terms and conditions on a nonexistent initiative
    Then the latest accept terms and conditions failed for initiative not found