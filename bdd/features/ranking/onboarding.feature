@ranking_initiative
@ranking
Feature: A citizen onboards an initiative with ranking

  Background:
    Given a new initiative "ranking_initiative"

  Scenario Outline: Citizens with different ISEE onboard to ranking initiative in the correct order, given by ISEE value.
    Given citizens <citizens> have fiscal code random
    And the citizen A has ISEE 39999 of type "ordinario"
    And the citizen C has ISEE 19999 of type "ordinario"
    And the citizen B has ISEE 29999 of type "ordinario"
    When <citizens> onboard in order and wait for ranking
    And the ranking period ends and the institution publishes the ranking
    Then <citizens> are elected
    And <ordered citizens> are ranked in the correct order

    Examples: Citizens and ranking order
      | citizens        | ordered citizens |
      | ["A", "B", "C"] | ["C", "B", "A"]  |

  Scenario Outline: Citizens, with same ISEE, onboard to ranking initiative in the correct order, is given by onboarding time.
    Given the citizen A has fiscal code random
    And citizens <citizens> have fiscal code random
    And citizens <citizens> have ISEE 39999 of type "ordinario"
    When <citizens> onboard in order and wait for ranking
    When the ranking period ends and the institution publishes the ranking
    Then <citizens> are elected
    And <ordered citizens> are ranked in the correct order

    Examples: Citizens and ranking order
      | citizens        | ordered citizens |
      | ["C", "B", "A"] | ["C", "B", "A"]  |
