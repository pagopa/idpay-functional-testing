@ranking_initiative
@ranking
@unsubscribe
Feature: Unsubscription on an initiative for families with ranking

  Scenario Outline: Onboard family cannot unsubscribe before onboarding period end on a initiative with ranking
    Given citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 32568 of type "ordinario"
    And the first citizen of <family members 1> onboards and wait for ranking
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is KO because the initiative has not started yet
    And the citizen A is onboard and waits for ranking

    Examples: Family members
      | family members 1  |
      | A B C             |