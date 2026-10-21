@bonus_elettrodomestici
@onboarding
Feature: Onboarding Bonus Elettrodomestici
  Background:
    Given the initiative is active

  Scenario: Citizen with ISEE lower than 25k tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    When the citizen A tries to onboard the initiative
    Then the onboard of A is ON_EVALUATION

  Scenario: Citizen with ISEE equal or above 25k tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 30000 of type "ordinario"
    And the citizen A selects ISEE type "over_25000"
    When the citizen A tries to onboard the initiative
    Then the onboard of A is ON_EVALUATION

  Scenario: Citizen with no declared ISEE tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A selects ISEE type "not_declared"
    When the citizen A tries to onboard the initiative
    Then the onboard of A is ON_EVALUATION