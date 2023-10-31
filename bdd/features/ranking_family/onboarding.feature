@family_ranking_initiative
@ranking
@family
@onboarding
Feature: A family onboards an initiative with ranking

  Background:
    Given a new initiative "family_ranking_initiative"

    Scenario Outline: Families are ranked correctly ordered by ISEE after ranking publication of initiative
      Given citizens <family members 1> have fiscal code random
      And citizens <family members 1> are in the same family
      And citizens <family members 1> have ISEE 32568 of type "ordinario"
      And citizens <family members 2> have fiscal code random
      And citizens <family members 2> are in the same family
      And citizens <family members 2> have ISEE 19999 of type "ordinario"
      And the first citizen of <family members 1> onboards and wait for ranking
      And the first citizen of <family members 2> onboards and wait for ranking
      When the ranking period ends
      And the institution publishes the ranking
      Then <eligible citizens> are elected
      And the onboards of <demanded citizens> are demanded
      And <ordered citizens> are ranked in the correct order

      Examples: Citizens and ranking order
        | family members 1  | family members 2 | eligible citizens | demanded citizens | ordered citizens |
        | A B C             | D E F            | A D               | B C E F           | D A              |

    Scenario Outline: A citizen tries to onboard on a ranking initiative when another one of the same family already onboarded
      Given citizens <family members 1> have fiscal code random
      And citizens <family members 1> are in the same family
      And citizens <family members 1> have ISEE 25000 of type "ordinario"
      And the first citizen of <family members 1> onboards and wait for ranking
      And the citizen B onboards and waits for ranking
      When the ranking period ends
      And the institution publishes the ranking
      Then <eligible citizens> are elected
      And the onboard of B is elected
      And the onboard of C is demanded

      Examples: Citizens and ranking order
        | family members 1  | eligible citizens |
        | A B C             | A                 |

    Scenario Outline: Two families, with same ISEE, onboard to ranking initiative but the second one is not in ranking for budget exhaustion
      Given citizens <family members 1> have fiscal code random
      And citizens <family members 1> are in the same family
      And citizens <family members 1> have ISEE 12000 of type "ordinario"
      And citizens <family members 2> have fiscal code random
      And citizens <family members 2> are in the same family
      And citizens <family members 2> have ISEE 20426 of type "ordinario"
      And citizens <family members 3> have fiscal code random
      And citizens <family members 3> are in the same family
      And citizens <family members 3> have ISEE 35000 of type "ordinario"
      And citizens <family members 4> have fiscal code random
      And citizens <family members 4> are in the same family
      And citizens <family members 4> have ISEE 35000 of type "ordinario"
      And the first citizen of <family members 1> onboards and wait for ranking
      And the first citizen of <family members 2> onboards and wait for ranking
      And the first citizen of <family members 3> onboards and wait for ranking
      And the first citizen of <family members 4> onboards and wait for ranking
      When the ranking period ends
      And the institution publishes the ranking
      Then <eligible citizens> are elected
      And the onboards of <demanded citizens> are demanded
      And the citizen H is not eligible
      And the onboard of I is not eligible

      Examples: Citizens and ranking order
        | family members 1  | family members 2 | family members 3 | family members 4 | eligible citizens | demanded citizens |
        | A                 | B C D            | E F G            | H I              | A B E             | C D F G           |