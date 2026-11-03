@bonus_elettrodomestici
@reward_batch
@reward_batch_counter
Feature: Reward batch counters are derived from current PostgreSQL transactions

  Background:
    Given the initiative is "bonus_elettrodomestici"
    And the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative bonus_elettrodomestici
    And the onboard of A becomes OK within 300 seconds
    And the merchant 1 is qualified

  Scenario: Batch counters remain accurate after an invoice update
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    When the point of sale pos_1 of merchant 1 tries to update the invoice of transaction X by Bar Code
    Then the invoice update of transaction X is successful
    And the live counters of reward batch B match its current transactions

  Scenario: Postponing a transaction updates the source and next-month batch counters
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    When the merchant 1 postpones transaction X to the next reward batch
    Then the live counters of reward batch B match its current transactions
    And the destination reward batch of transaction X has live counters matching its current transactions

  Scenario: Batch counters reflect a transaction rejected by an L2 operator
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    And An operator with l1 role select transaction X from reward batch list and approve it
    And An operator with l1 role validating the reward batch containing transaction X
    And the reward batch of transaction X is EVALUATING and assigned to l2
    When An operator with l2 role select transaction X from reward batch list and tries to reject it
    Then the transaction X is REJECTED in its reward batch
    And the reward batch of transaction X is EVALUATING and assigned to l2
    And the live counters of reward batch X match its current transactions
