@family_ranking_initiative
@ranking
@suspension
Feature: Suspension on an initiative for families with ranking

  Scenario Outline: The Institution cannot suspend a citizen before onboarding period end on a initiative for families with ranking
    Given a new initiative "family_ranking_initiative"
    And citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 21570 of type "ordinario"
    And the first citizen of <family members 1> onboards and wait for ranking
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen

    Examples: Family members
      | family members 1  |
      | A B C             |