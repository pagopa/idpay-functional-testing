@ranking_initiative
@ranking
@unsubscribe
Feature: A citizen onboards an initiative with ranking

  Background:
    Given a new initiative "ranking_initiative"

  Scenario: Onboard citizen cannot unsubscribe before ranking
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 40000 of type "ordinario"
    And the citizen A onboards and waits for ranking
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is KO because the initiative has not started yet
    And the citizen A is onboard and waits for ranking

  @test
  @ranking_initiative_on_grace_period
  Scenario: A merchant cannot generate a transaction during the grace period
    Given the initiative is "Ranking_in_grace_period"
    And the initiative is in grace period
    And the initiative has a rank
    When the onboard citizen tries to unsubscribe
    Then the latest unsubscribe is KO because the initiative has not started yet
