@family_ranking_initiative
@ranking
@family
@onboarding
Feature: A family onboards an initiative with ranking

  Scenario Outline: Families are ranked correctly ordered by ISEE after ranking publication of initiative
    Given a new initiative "family_ranking_initiative"
    And citizens <family members 1> have fiscal code random
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
    And the family members <demanded citizens> are not in ranking

    Examples: Citizens and ranking order
      | family members 1  | family members 2 | eligible citizens | demanded citizens | ordered citizens |
      | A B C             | D E F            | A D               | B C E F           | D A              |

  Scenario Outline: Given many onboarding of citizens from the same family, the ranking will be published with only the citizen of the family who onboarded first
    Given a new initiative "family_ranking_initiative"
    And citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 25038 of type "ordinario"
    And citizens <family members 2> have fiscal code random
    And citizens <family members 2> are in the same family
    And citizens <family members 2> have ISEE 20426 of type "ordinario"
    And citizens <family members 3> have fiscal code random
    And citizens <family members 3> are in the same family
    And citizens <family members 3> have ISEE 35000 of type "ordinario"
    And citizens <family members 4> have fiscal code random
    And citizens <family members 4> are in the same family
    And citizens <family members 4> have ISEE 42010 of type "ordinario"
    And the first citizen of <family members 1> onboards and wait for ranking
    And the first citizen of <family members 2> onboards and wait for ranking
    And the first citizen of <family members 3> onboards and wait for ranking
    And the first citizen of <family members 4> onboards and wait for ranking
    And the citizen B onboards and waits for ranking
    And the citizen F onboards and waits for ranking
    And the citizen H onboards and waits for ranking
    When the ranking period ends
    And the institution publishes the ranking
    Then <eligible citizens> are elected
    And the onboard of B is elected
    And the onboard of F is elected
    And the onboard of H is not eligible
    And the onboard of C is demanded
    And the family members <not ranked citizens> are not in ranking

    Examples: Citizens and ranking order
      | family members 1  | family members 2 | family members 3 | family members 4 | eligible citizens | not ranked citizens |
      | A B C             | D                | E F              | G H I            | A D E             | B C F H I           |

  Scenario Outline: Two families, with same ISEE, onboard to a ranking initiative but the second one is not in ranking for budget exhaustion
    Given a new initiative "family_ranking_initiative"
    And citizens <family members 1> have fiscal code random
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
    And the citizen H has status not eligible in ranking
    And the onboard of I is not eligible

    Examples: Citizens and ranking order
      | family members 1  | family members 2 | family members 3 | family members 4 | eligible citizens | demanded citizens |
      | A                 | B C D            | E F G            | H I              | A B E             | C D F G           |

  Scenario Outline: Two families tries to onboard on a ranking initiative but they don't meet the ISEE requirements
    Given a new initiative "family_ranking_initiative"
    And citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 50000 of type "ordinario"
    And citizens <family members 2> have fiscal code random
    And citizens <family members 2> are in the same family
    And citizens <family members 2> have ISEE 68700 of type "ordinario"
    When the citizen A tries to onboard
    And the citizen D tries to onboard
    Then the onboards of <family members 1> are KO
    Then the onboards of <family members 2> are KO
    When the ranking period ends
    And the institution publishes the ranking
    Then the citizen A has status KO in ranking
    And the citizen D has status KO in ranking
    And the family members <not ranked citizens> are not in ranking

    Examples: Citizens and ranking order
      | family members 1  | family members 2 | not ranked citizens |
      | A B C             | D E F            | B C E F             |

  Scenario Outline: A family, with an higher ISEE than other families, is not in ranking for budget exhaustion even if it onboards first
    Given a new initiative "family_ranking_initiative"
    And citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 49999 of type "ordinario"
    And citizens <family members 2> have fiscal code random
    And citizens <family members 2> are in the same family
    And citizens <family members 2> have ISEE 37654 of type "ordinario"
    And citizens <family members 3> have fiscal code random
    And citizens <family members 3> are in the same family
    And citizens <family members 3> have ISEE 29870 of type "ordinario"
    And citizens <family members 4> have fiscal code random
    And citizens <family members 4> are in the same family
    And citizens <family members 4> have ISEE 25789 of type "ordinario"
    And the first citizen of <family members 1> onboards and wait for ranking
    And the first citizen of <family members 2> onboards and wait for ranking
    And the first citizen of <family members 3> onboards and wait for ranking
    And the first citizen of <family members 4> onboards and wait for ranking
    When the ranking period ends
    And the institution publishes the ranking
    Then <eligible citizens> are elected
    And <eligible citizens> are ranked in the correct order
    And the onboards of <demanded citizens> are demanded
    And the family members <demanded citizens> are not in ranking
    And the citizen A has status not eligible in ranking

    Examples: Citizens and ranking order
      | family members 1  | family members 2 | family members 3 | family members 4 | eligible citizens | demanded citizens |
      | A                 | B C D            | E F G            | H I              | H E B             | C D F G I         |