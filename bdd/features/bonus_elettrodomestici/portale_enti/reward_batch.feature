@bonus_elettrodomestici
@portale_enti
@reward_batch
Feature: Reward batches for Bonus Elettrodomestici and Refund Approval Process
  Background:
    Given the initiative is "bonus_elettrodomestici"
   And the citizen A is 21 years old exactly
   And the citizen A has ISEE 24000 of type "ordinario"
   And the citizen A selects ISEE type "under_25000"
   And the citizen A tries to onboard the initiative bonus_elettrodomestici
   And the onboard of A becomes OK within 300 seconds
   And the merchant 1 is qualified


  Scenario: L1 operator tries to validate unsuccessfully a reward batch without performing checks on at least 15% of the transactions
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    When An operator with l1 role fails when tries to validate the reward batch containing transaction X for UNSATISFIED MINIMUM ELABORATION PERCENT
    Then the reward batch of transaction X is EVALUATING and assigned to l1

  Scenario: L1 Operator tries to validate successfully a reward batch after performing checks on at least 15% of the transactions
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    When An operator with l1 role select transaction X from reward batch list and tries to approve it
    And An operator with l1 role validating the reward batch containing transaction X
    Then the reward batch of transaction X is EVALUATING and assigned to l2

  Scenario: L2 Operator reject one transaction of reward batch and then approve the reward batch
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the citizen B is 23 years old exactly
    And the citizen B has ISEE 24000 of type "ordinario"
    And the citizen B selects ISEE type "under_25000"
    And the citizen B tries to onboard the initiative bonus_elettrodomestici
    And the onboard of B becomes OK within 300 seconds
    And the citizen B fully performs the transaction Y by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transactions X and Y are prepared, sent and evaluated in the same reward batch status EVALUATING
    When An operator with l1 role select transaction X from reward batch list and tries to approve it
    And An operator with l1 role validating the reward batch containing transaction X
    And the reward batch of transaction X is EVALUATING and assigned to l2
    And An operator with l2 role select transaction Y from reward batch list and reject it
    And An operator with l2 role validating the reward batch containing transaction Y
    Then the reward batch of transaction Y is EVALUATING and assigned to l3

  Scenario: L3 Operator approves the reward batch
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    And An operator with l1 role select transaction X from reward batch list and approve it
    And An operator with l1 role validating the reward batch containing transaction X
    And the reward batch of transaction X is EVALUATING and assigned to l2
    And An operator with l2 role validating the reward batch containing transaction X
    And the reward batch of transaction X is EVALUATING and assigned to l3
    When An operator with l3 role tries to approve the reward batch containing transaction X
    Then the reward batch of transaction X is APPROVED

  Scenario: Operator downloads the approved reward batch report
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    And An operator with l1 role select transaction X from reward batch list and approve it
    And An operator with l1 role validating the reward batch containing transaction X
    And the reward batch of transaction X is EVALUATING and assigned to l2
    And An operator with l2 role validating the reward batch containing transaction X
    And the reward batch of transaction X is EVALUATING and assigned to l3
    When An operator with l3 role tries to approve the reward batch containing transaction X
    And the reward batch of transaction X is APPROVED
    And An operator with l3 role downloads the approved reward batch report of transaction X after 30 seconds
    Then the approved reward batch report of transaction X is downloaded
