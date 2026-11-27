@bonus_elettrodomestici
@portale_enti
@reward_batch
Feature: Reward batch validation threshold of 15% for Bonus Elettrodomestici
  Background:
    Given the initiative is "bonus_elettrodomestici"
    And the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative
    And the onboard of A becomes OK within 300 seconds
    And the merchant 1 is qualified

  Scenario: L1 operator tries to validate unsuccessfully a reward batch without performing checks on at least 15% of the transactions
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    When An operator with l1 role fails when tries to validate the reward batch containing transaction X for UNSATISFIED MINIMUM ELABORATION PERCENT
    Then the reward batch of transaction X is EVALUATING and assigned to l1

  Scenario: L1 Operator tries to validate successfully a reward batch after performing checks on at least 15% of the transactions
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    When An operator with l1 role select transaction X from reward batch list and tries to approve it
    And An operator with l1 role validating the reward batch containing transaction X
    Then the reward batch of transaction X is EVALUATING and assigned to l2

