@bonus_decoder
@portale_enti
@reward_batch
Feature: Reward batch validation threshold of 50% for Bonus Decoder
  Background:
    Given the initiative is "bonus_decoder"
    And the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative
    And the onboard of A becomes OK within 300 seconds
    And the citizen B is 23 years old exactly
    And the citizen B has ISEE 24000 of type "ordinario"
    And the citizen B selects ISEE type "under_25000"
    And the citizen B tries to onboard the initiative
    And the onboard of B becomes OK within 300 seconds
    And the citizen C is 25 years old exactly
    And the citizen C has ISEE 24000 of type "ordinario"
    And the citizen C selects ISEE type "under_25000"
    And the citizen C tries to onboard the initiative
    And the onboard of C becomes OK within 300 seconds
    And the citizen D is 27 years old exactly
    And the citizen D has ISEE 24000 of type "ordinario"
    And the citizen D selects ISEE type "under_25000"
    And the citizen D tries to onboard the initiative
    And the onboard of D becomes OK within 300 seconds
    And the merchant 1 is qualified

  Scenario: L1 operator tries to validate unsuccessfully a reward batch without performing checks on at least 50% of the transactions
    Given the citizen A fully performs the transaction W by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the citizen B fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the citizen C fully performs the transaction Y by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the citizen D fully performs the transaction Z by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the transactions W, X, Y and Z are prepared, sent and evaluated in the same reward batch status EVALUATING
    And An operator with l1 role select transaction W from reward batch list and approve it
    When An operator with l1 role fails when tries to validate the reward batch containing transaction W for UNSATISFIED MINIMUM ELABORATION PERCENT
    Then the reward batch of transaction W is EVALUATING and assigned to l1

  Scenario: L1 Operator tries to validate successfully a reward batch after performing checks on at least 50% of the transactions
    Given the citizen A fully performs the transaction W by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the citizen B fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the citizen C fully performs the transaction Y by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the citizen D fully performs the transaction Z by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with default product GTIN
    And the transactions W, X, Y and Z are prepared, sent and evaluated in the same reward batch status EVALUATING
    And An operator with l1 role select transaction W from reward batch list and approve it
    And An operator with l1 role select transaction X from reward batch list and approve it
    When An operator with l1 role validating the reward batch containing transaction W
    Then the reward batch of transaction W is EVALUATING and assigned to l2


