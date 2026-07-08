@bonus_elettrodomestici
@onboarding
Feature: Onboarding Bonus Elettrodomestici
  Background:
    Given the initiative is "bonus_elettrodomestici"

  Scenario: Citizen with ISEE lower than 25k tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is ON_EVALUATION

  Scenario: Citizen with ISEE equal or above 25k tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A has ISEE 30000 of type "ordinario"
    And the citizen A selects ISEE type "over_25000"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is ON_EVALUATION

  Scenario: Citizen with no declared ISEE tries to onboard successfully
    Given the citizen A is 21 years old exactly
    And the citizen A selects ISEE type "not_declared"
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is ON_EVALUATION

  Scenario: A citizen under the minimum age tries to onboard unsuccessfully
    Given the citizen A is 17 years old at most
    When the citizen A tries to onboard the initiative bonus_elettrodomestici
    Then the onboard of A is KO

  Scenario: Citizen with mismatching email tries to onboard unsuccessfully
    Given the citizen A has fiscal code random
    When the citizen A filled out mismatching email
    Then the citizen onboarding failed because the citizen inserted mismatch value

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
    Then the citizen onboarding failed because the consent was denied by the citizen

  Scenario: A citizen tries to onboard a nonexistent initiative
    Given the citizen A is 21 years old exactly
    When the citizen A tries to onboard on nonexistent initiative
    Then the citizen onboarding failed because initiative not found

  Scenario Outline: One member of a family onboards an initiative
    Given citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 19999 of type "ordinario"
    And the citizen <family members> selects ISEE type "under_25000"
    When the first citizen of <family members> onboards
    Then the onboard of A is OK
    And the onboards of <KO citizens> are KO

    Examples: Family members
      | KO citizens | family members |
      | B C         | A B C          |
