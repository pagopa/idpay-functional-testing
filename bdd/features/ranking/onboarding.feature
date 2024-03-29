@ranking_initiative
@ranking
@onboarding
Feature: A citizen onboards an initiative with ranking

  Background:
    Given a new initiative "ranking_initiative"

  Scenario Outline: Citizens with different ISEE onboard to ranking initiative in the correct order, given by ISEE value
    Given citizens <citizens> have fiscal code random
    And the citizen A has ISEE 39999 of type "ordinario"
    And the citizen C has ISEE 19999 of type "ordinario"
    And the citizen B has ISEE 29999 of type "ordinario"
    And <citizens> onboard in order and wait for ranking
    When the ranking period ends
    And the institution publishes the ranking
    Then <citizens> are elected
    And <ordered citizens> are ranked in the correct order

    Examples: Citizens and ranking order
      | citizens | ordered citizens |
      | A B C    | C B A            |

  Scenario Outline: Citizens, with same ISEE, onboard to ranking initiative in the correct order, is given by onboarding time
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> have ISEE 39999 of type "ordinario"
    And <citizens> onboard in order and wait for ranking
    When the ranking period ends
    And the institution publishes the ranking
    Then <citizens> are elected
    And <ordered citizens> are ranked in the correct order

    Examples: Citizens and ranking order
      | citizens        | ordered citizens |
      | C B A           | C B A            |

  Scenario Outline: A citizen who denied PDND consent tries onboarding unsuccessfully
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> have ISEE 39999 of type "ordinario"
    And the citizen A onboards and waits for ranking
    And the citizen B accepts terms and conditions
    And the citizen B saves PDND consent not correctly
    When the ranking period ends
    And the institution publishes the ranking
    Then the citizen B is not in rank

    Examples: Citizens
      | citizens   |
      | A B        |

  Scenario Outline: Onboarding result depends on citizens' ISEE
    Given citizens <citizens> have fiscal code random
    And the citizen A has ISEE 50001 of type "ordinario"
    And the citizen C has ISEE 50000 of type "ordinario"
    And the citizen B has ISEE 4050.54 of type "ordinario"
    When the citizen A tries to onboard
    And the citizen B tries to onboard
    And the citizen C tries to onboard
    Then the onboard of A is KO
    And the citizen B is waiting for ranking
    And the citizen C is waiting for ranking

    Examples: Citizens with different
      | citizens        |
      | A B C           |

  @skip
  Scenario: A citizen receives KO if it tries to onboard during grace period
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 40000 of type "ordinario"
    And the ranking period ends
    And the ranking is produced
    When the citizen A tries to onboard
    Then the onboard of A is KO

  @budget
  Scenario Outline: Citizen, with worse criteria then other citizens, is not in ranking for budget exhaustion even if it onboards first
    Given citizens <citizens> have fiscal code random
    And the citizen F has ISEE 39999 of type "ordinario"
    And the citizen F onboards and waits for ranking
    And citizens <eligible citizens> have ISEE 29999 of type "ordinario"
    And <eligible citizens> onboard in order and wait for ranking
    When the ranking period ends
    And the institution publishes the ranking
    Then <eligible citizens> are elected
    And <eligible citizens> are ranked in the correct order
    And the citizen F has status not eligible in ranking

    Examples: Citizens and ranking order
      | citizens    | eligible citizens |
      | A B C D E F | A B C D E         |
