@bonus_decoder
@onboarding
Feature: Onboarding Bonus Decoder
  Background:
    Given the initiative is "bonus_decoder"

  Scenario: Citizen onboards successfully
    Given the citizen A has fiscal code random
    When the citizen A tries to onboard the initiative bonus_decoder
    Then the onboard of A is OK

  Scenario: Citizen onboarding allocate correct budget for initiative
    Given the citizen A is 21 years old exactly
    When the citizen A tries to onboard the initiative bonus_decoder
    Then the onboard of A is OK
    And the wallet of A is refundable with 70 euros budget

  Scenario: Citizen who has not paid Canone TV tries to onboard unsuccessfully
    Given the citizen A is 21 years old exactly
    Given the citizen A has not payed Canone TV
    When the citizen A tries to onboard the initiative bonus_decoder
    Then the onboard of A is KO

  Scenario: Citizen with mismatching email tries to onboard unsuccessfully
    Given the citizen A has fiscal code random
    When the citizen A filled out mismatching email
    Then the citizen onboarding failed because the citizen inserted mismatch value

  Scenario: Citizen without email tries to onboard successfully
    Given the citizen A has fiscal code random
    When the citizen A onboards the initiative bonus_decoder without an email
    Then the onboard of A is OK

  Scenario: A citizen with self-declared incorrect criteria tries to onboard unsuccessfully
    Given the citizen A has fiscal code random
    When the citizen A tries to insert wrong value in self-declared criteria
    Then the citizen onboarding failed because the citizen inserted the wrong value

  Scenario: A citizen who has not accepted the Terms and Conditions tries to onboard unsuccessfully
    Given the citizen A is 21 years old exactly
    When the citizen A tries to save PDND consent correctly
    Then the citizen onboarding failed because the citizen did not accept T&C

  Scenario: A citizen who denied PDND consent tries to onboard unsuccessfully
    Given the citizen A is 21 years old exactly
    And the citizen A accepts terms and conditions
    When the citizen A tries to save PDND consent not correctly
    Then the onboard of A is in error with value ONBOARDING_UNSATISFIED_REQUIREMENTS

  Scenario: A citizen tries to onboard a nonexistent initiative
    Given the citizen A is 21 years old exactly
    When the citizen A tries to onboard on nonexistent initiative
    Then the citizen onboarding failed because initiative not found

  Scenario: A citizen tries to onboard a non published initiative
    Given the citizen A is 21 years old exactly
    And the new initiative A is created but not published
    When the citizen A tries to onboard the initiative A
    Then the citizen onboarding failed because initiative not published

  Scenario: A citizen tries to onboard a non started initiative
    Given the citizen A is 21 years old exactly
    And the new initiative NOT_STARTED is created
    When the citizen A tries to onboard the initiative NOT_STARTED
    Then the citizen onboarding failed because initiative not started

  Scenario: A citizen tries to onboard an initiative with residual budget less than 100 euros
    Given the citizen A is 21 years old exactly
    And the new initiative budget_exhausted is created
    When the citizen A tries to onboard the initiative budget_exhausted
    Then the citizen onboarding failed because initiative budget exhausted

  Scenario: One member of a family onboards an initiative
    Given citizens A B C have fiscal code random
    And citizens A B C are in the same family
    When the first citizen of A B C onboards
    And the citizen B tries to onboard
    And the citizen C tries to onboard
    Then the onboard of A is OK
    And the onboards of B C are family joined

  Scenario: An unsubscribed citizen onboards the same initiative again successfully
    Given the citizen A is 21 years old exactly
    And the citizen A tries to onboard the initiative bonus_decoder
    And the onboard of A is OK
    And the citizen A unsubscribes
    And the onboard of A is unsubscribed
    When the citizen A tries to onboard the initiative bonus_decoder
    Then the onboard of A is OK