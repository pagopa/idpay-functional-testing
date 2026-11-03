@bonus_elettrodomestici
@bonus_decoder
@family
@unsubscribe
Feature: The family beneficiary can unsubscribe from the selected Bonus

  Background:
    Given the initiative is active
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative
    And the onboard of A becomes OK within 300 seconds
    And the citizen B tries to onboard the initiative
    And the citizen C tries to onboard the initiative
    And the onboards of B C are family joined

  Scenario: Family members' rejected applications do not prevent the beneficiary's unsubscribe
    When the citizen A unsubscribes
    Then the onboard of A is unsubscribed
