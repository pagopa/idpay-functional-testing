@bonus_elettrodomestici
@reward_batch
@reward_batch_counters
Feature: Reward batch counters are derived from current PostgreSQL transactions

  Background:
    Given the initiative is "bonus_elettrodomestici"
    And the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative bonus_elettrodomestici
    And the onboard of A becomes OK within 300 seconds
    And the merchant 1 is qualified

  @counter_created @counter_created_reversal
  Scenario: CREATED counters immediately exclude a reversed transaction and an empty batch freezes zero
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    Then the live counters of reward batch B match its current transactions
    When the point of sale pos_1 of merchant 1 reverses the transaction X by Bar Code
    Then the transaction X does not belong to a reward batch
    And the live counters of reward batch B match its current transactions
    And the reward batch named B contains 0 transactions
    And the counters of reward batch B are captured as empty_before_send
    When the merchant 1 prepares and sends the reward batch named B
    Then the reward batch named B is SENT
    And the live counters of reward batch B match its current transactions
    And reward batch B keeps the initial amount captured as empty_before_send

  @counter_sent @counter_sent_snapshot
  Scenario: SEND freezes initialAmountCents while the other applicable counters stay live
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    And the counters of reward batch B are captured as before_send
    When the reward batch of transaction X is prepared and sent
    Then the reward batch of transaction X is SENT
    And the live counters of reward batch B match its current transactions
    And reward batch B keeps the initial amount captured as before_send

  @counter_created @counter_created_postpone
  Scenario: Invoice replacement and POSTPONE update CREATED counters correctly
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    And the counters of reward batch B are captured as before_created_operations
    When the point of sale pos_1 of merchant 1 updates the invoice of transaction X by Bar Code
    Then the counters of reward batch B are unchanged from before_created_operations
    When the merchant 1 postpones transaction X to the next reward batch
    Then the live counters of reward batch B match its current transactions
    And the destination reward batch of transaction X has live counters matching its current transactions

  @counter_sent @counter_sent_invoice_update
  Scenario: Rejected invoice and reversal operations in SENT leave every counter unchanged
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    When the reward batch of transaction X is prepared and sent
    Then the reward batch of transaction X is SENT
    And the counters of reward batch B are captured as before_rejected_invoice_update
    When the point of sale pos_1 of merchant 1 tries to update the invoice of transaction X by Bar Code
    Then the invoice update of transaction X is rejected
    And the counters of reward batch B are unchanged from before_rejected_invoice_update
    When the point of sale pos_1 of merchant 1 tries to reverse the transaction X by Bar Code
    Then the reversal of transaction X is rejected by its reward batch
    And the counters of reward batch B are unchanged from before_rejected_invoice_update

  @counter_evaluating @counter_evaluating_invoice_update
  Scenario: An invoice update in EVALUATING updates both source and destination counters
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    And the counters of reward batch B are captured as before_invoice_reassignment
    When the merchant 1 updates the invoice of transaction X by Bar Code
    Then the transaction X belongs to a different current-month reward batch as SUSPENDED
    And the live counters of reward batch B match its current transactions
    And reward batch B keeps the initial amount captured as before_invoice_reassignment
    And the destination reward batch of transaction X has live counters matching its current transactions

  @counter_evaluating @counter_evaluating_actions
  Scenario: Approval and rejection actions update the live counters at every review level
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    When An operator with l1 role select transaction X from reward batch list and approve it
    Then the live counters of reward batch X match its current transactions
    When An operator with l1 role validating the reward batch containing transaction X
    And An operator with l2 role select transaction X from reward batch list and reject it
    Then the live counters of reward batch X match its current transactions

  @counter_approving @counter_approving_snapshot
  Scenario: APPROVING freezes suspendedAmountCents before suspended transactions are reassigned
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    And An operator with l1 role select transaction X from reward batch list and suspend it
    Then the live counters of reward batch X match its current transactions
    And the counters of reward batch X are captured as before_approving
    When An operator with l1 role validating the reward batch containing transaction X
    And An operator with l2 role validating the reward batch containing transaction X
    And An operator with l3 role tries to approve the reward batch containing transaction X
    Then the reward batch of transaction X is APPROVED
    And after approval, the transaction X belongs to a different current-month reward batch as SUSPENDED
    And the live counters of reward batch X match its current transactions
    And reward batch X keeps the suspended amount captured as before_approving

  @counter_evaluating @counter_evaluating_rejected
  Scenario: REJECTED counters remain live and are not snapshots
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    When An operator with l1 role select transaction X from reward batch list and reject it
    Then the live counters of reward batch X match its current transactions
