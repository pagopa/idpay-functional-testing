@bonus_elettrodomestici
@onboarding
Feature: Onboarding Bonus Elettrodomestici
  Background:
    Given the initiative is "bonus_elettrodomestici"

  Scenario: Citizen onboards successfully
    Given the citizen A has fiscal code random
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is OK

  Scenario: Citizen with ISEE lower than 25k tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is OK

  Scenario: Onboarded citizen with ISEE lower than 25k has a wallet with correct budget
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is OK
    And the wallet of A is refundable with 200 euros budget

  Scenario: Citizen with ISEE equal or above 25k tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 30000 of type "ordinario"
    And the citizen A selects ISEE type "over_25000"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is OK

  Scenario: Onboarded citizen with ISEE equal or above 25k has a wallet with correct budget
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 30000 of type "ordinario"
    And the citizen A selects ISEE type "over_25000"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is OK
    And the wallet of A is refundable with 100 euros budget

  Scenario: Citizen with no declared ISEE tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A selects ISEE type "not_declared"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is OK

  Scenario: Onboarded citizen with no declared ISEE has a wallet with correct budget
    Given the citizen A is 21 years old exactly
    And the citizen A selects ISEE type "not_declared"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is OK
    And the wallet of A is refundable with 100 euros budget

  Scenario: A citizen with self-declared incorrect criteria tries to onboard unsuccessfully
    Given the citizen A has fiscal code random
    When the citizen A tries to insert wrong value in self-declared criteria
    Then the citizen onboarding failed because the citizen inserted the wrong value

  Scenario: Family members join first family's onboarding
    Given citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the citizen A B C selects ISEE type "under_25000"
    When the citizen A tries to onboard
    And the citizen B tries to onboard
    And the citizen C tries to onboard
    Then the onboards of B C are family joined
