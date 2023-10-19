@ranking_initiative
@ranking
@suspension
Feature: A citizen onboards an initiative with ranking

  Background:
    Given a new initiative "ranking_initiative"

  Scenario: The Institution cannot suspend a citizen before onboarding period end
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 40000 of type "ordinario"
    And the citizen A onboards and waits for ranking
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen

  Scenario: The Institution cannot suspend a citizen during grace period before ranking publication
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 40000 of type "ordinario"
    And the citizen A onboards and waits for ranking
    And the ranking period ends
    And the ranking is produced
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen
