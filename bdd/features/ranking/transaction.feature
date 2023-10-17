#@ranking_initiative
@ranking
@transaction
Feature: A merchant creates a transaction and a citizen tries to confirm it during grace period on an initiative with ranking

  @skip
  Scenario: A new ranking initiative is generate in order to create the conditions to test grace period
    Given a new initiative "Ranking_in_grace_period"
    And the citizen A has fiscal code random
    And the citizen B has fiscal code random
    And the citizen C has fiscal code random
    And the citizen A has ISEE 19999 of type "ordinario"
    And the citizen C has ISEE 29999 of type "ordinario"
    And the citizen B has ISEE 59999 of type "ordinario"
    When the citizen A tries to onboard
    And the citizen B tries to onboard
    And the citizen C tries to onboard
    And the ranking period ends
    And the institution publishes the ranking

  @skip
  Scenario: A new ranking initiative is generate in order to create the conditions to test fruition period
    Given a new initiative "Ranking_fruition_open"
    And the citizen A has fiscal code random
    And the citizen B has fiscal code random
    And the citizen C has fiscal code random
    And the citizen A has ISEE 19999 of type "ordinario"
    And the citizen C has ISEE 29999 of type "ordinario"
    And the citizen B has ISEE 59999 of type "ordinario"
    When the citizen A tries to onboard
    And the citizen B tries to onboard
    And the citizen C tries to onboard
    And the ranking period ends
    And the institution publishes the ranking

  Scenario: The merchant cannot generate a transaction during the onboarding period
    Given a new initiative "ranking_initiative"
    And the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because it is out of valid period

  @test
  @ranking_initiative_on_grace_period
  Scenario: A merchant cannot generate a transaction during the grace period
    Given the initiative is "Ranking_in_grace_period"
    And the initiative is in grace period
    And the initiative has a rank
    And the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because it is out of valid period
