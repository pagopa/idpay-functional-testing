@family_ranking_initiative
@ranking
@unsubscribe
Feature: Unsubscription on an initiative for families with ranking

  Background:
    Given a new initiative "family_ranking_initiative"

  Scenario Outline: Onboard family cannot unsubscribe before onboarding period end on a initiative with ranking
    Given citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 32568 of type "ordinario"
    And the first citizen of <family members 1> onboards and waits for ranking
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is KO because the initiative has not started yet
    And the citizen A is still waiting for ranking

    Examples: Family members
      | family members 1  |
      | A B C             |

  Scenario Outline: Onboard family cannot unsubscribe before grace period end on a initiative with ranking
    Given citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 32568 of type "ordinario"
    And the first citizen of <family members 1> onboards and waits for ranking
    And the ranking period ends
    And the ranking is produced
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is KO because the initiative has not started yet
    And the citizen A is still waiting for ranking

    Examples: Family members
      | family members 1  |
      | A B C             |
