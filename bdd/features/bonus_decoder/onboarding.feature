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

  Scenario: Citizen without email tries to onboard successfully
    Given the citizen A has fiscal code random
    When the citizen A onboards the initiative bonus_decoder without an email
    Then the onboard of A is OK

  Scenario: A citizen with self-declared incorrect criteria tries to onboard unsuccessfully
    Given the citizen A has fiscal code random
    When the citizen A tries to insert wrong value in self-declared criteria
    Then the citizen onboarding failed because the citizen inserted the wrong value

  Scenario: Family members join first family's onboarding
    Given citizens A B C have fiscal code random
    And citizens A B C are in the same family
    When the citizen A tries to onboard
    And the citizen B tries to onboard
    And the citizen C tries to onboard
    Then the onboards of B C are family joined
