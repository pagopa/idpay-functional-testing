@ranking_initiative
@ranking
@suspension
Feature: A citizen onboards an initiative with ranking

  Background:
    Given a new initiative "ranking_initiative"

  Scenario: The Institution cannot suspend an onboard citizen before ranking
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 40000 of type "ordinario"
    And the citizen A onboards and waits for ranking
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen

  Scenario: The Institution tries to suspend an onboard citizen during grace period and receives an KO result
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 40000 of type "ordinario"
    And the citizen A onboards and waits for ranking
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen
