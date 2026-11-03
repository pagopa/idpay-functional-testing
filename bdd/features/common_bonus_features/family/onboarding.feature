@bonus_elettrodomestici
@bonus_decoder
@family
@onboarding
Feature: One beneficiary per family on the selected Bonus

  Background:
    Given the initiative is active

  Scenario Outline: The first applicant represents the family independently of the member order
    Given citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the citizen <representative> selects ISEE type "under_25000"
    When the citizen <representative> tries to onboard the initiative
    Then the onboard of <representative> becomes OK within 300 seconds
    When the citizen <second> tries to onboard the initiative
    And the citizen <third> tries to onboard the initiative
    Then the onboards of <second> <third> are family joined
    And the family beneficiary <representative> retains the configured Bonus budget

    Examples:
      | representative | second | third |
      | A              | B      | C     |
      | C              | A      | B     |

  Scenario: Separate families can each onboard one beneficiary
    Given citizens A B C D E F have fiscal code random
    And citizens A B C are in the same family
    And citizens D E F are in the same family
    And citizens A B C D E F have ISEE 19999 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    When the citizen A tries to onboard the initiative
    Then the onboard of A becomes OK within 300 seconds
    When the citizen D tries to onboard the initiative
    Then the onboard of D becomes OK within 300 seconds
    When the citizen B tries to onboard the initiative
    And the citizen E tries to onboard the initiative
    Then the onboards of B E are family joined
    And the family beneficiary A retains the configured Bonus budget
    And the family beneficiary D retains the configured Bonus budget
