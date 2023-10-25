@ranking_initiative
@ranking
@transaction
Feature: A merchant creates a transaction and a citizen tries to confirm it during grace period on an initiative with ranking

  @skip
  Scenario: A new ranking initiative is generate in order to create the conditions to test grace period after ranking publication
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

  Scenario: A merchant cannot generate a transaction during the grace period
    Given the initiative is "Ranking_in_grace_period"
    And the random merchant 1 is onboard
    And the ranking period ends
    And the ranking is produced
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because it is out of valid period

  @skip
  Scenario: The merchant can generate a transaction after the publication of the ranking
    Given the initiative is "Ranking_fruition_open"
    And the initiative is in fruition period
    And the initiative has a rank
    And the random merchant 1 is onboard
    When the merchant 1 generates the transaction X of amount 100 cents
    Then the transaction X is created

  @skip
  Scenario: An elected citizen authorizes a transaction during the fruition period after ranking publication
    Given the initiative is "Ranking_fruition_open"
    And the initiative is in fruition period
    And the initiative has a rank
    And the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 1 cents
    When the elected citizen confirms the transaction x
    Then the transaction X is authorized
    And the citizen A is rewarded with 0.01 euros

  @skip
  Scenario: An unelected citizen cannot authorize a transaction during the fruition period after ranking publication
    Given the initiative is "Ranking_fruition_open"
    And the initiative is in fruition period
    And the initiative has a rank
    And the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 1 cents
    When the unelected citizen tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard

  @skip
  Scenario: A not eligible citizen cannot authorize a transaction during the fruition period after ranking publication
    Given the initiative is "Ranking_fruition_open"
    And the initiative is in fruition period
    And the initiative has a rank
    And the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 1 cents
    When the not eligible citizen tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard
