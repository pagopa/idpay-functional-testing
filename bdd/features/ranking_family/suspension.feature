@ranking_initiative
@ranking
@suspension
Feature: Suspension on an initiative for families with ranking

  Scenario: The Institution cannot suspend a citizen before onboarding period end on a initiative for families with ranking
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 40000 of type "ordinario"
    And the citizen A onboards and waits for ranking
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen