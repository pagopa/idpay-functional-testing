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

  Scenario: Invoice replacement and POSTPONE update CREATED counters correctly
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    And the counters of reward batch B are captured as before_created_operations
    When the point of sale pos_1 of merchant 1 updates the invoice of transaction X by Bar Code
    And the merchant 1 postpones transaction X to the next reward batch
    Then the live counters of reward batch B match its current transactions
    And the destination reward batch of transaction X has live counters matching its current transactions

  Scenario: Approval and rejection actions keep REJECTED counters live at every review level
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    When An operator with l1 role select transaction X from reward batch list and approve it
    And An operator with l1 role validating the reward batch containing transaction X
    And An operator with l2 role select transaction X from reward batch list and reject it
    Then the live counters of reward batch X match its current transactions

  Scenario: APPROVING freezes suspendedAmountCents before suspended transactions are reassigned
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    And An operator with l1 role select transaction X from reward batch list and suspend it
    And the counters of reward batch X are captured as before_approving
    When An operator with l1 role validating the reward batch containing transaction X
    And An operator with l2 role validating the reward batch containing transaction X
    And An operator with l3 role tries to approve the reward batch containing transaction X
    Then the reward batch of transaction X is APPROVED
    And after approval, the transaction X belongs to a different current-month reward batch as SUSPENDED
    And the live counters of reward batch X match its current transactions
    And reward batch X keeps the suspended amount captured as before_approving
