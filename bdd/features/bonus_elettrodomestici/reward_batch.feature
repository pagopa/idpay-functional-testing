@bonus_elettrodomestici
@transaction
@bar_code
@reward_batch
Feature: Reward batches for Bonus Elettrodomestici barcode payments

  Background:
    Given the initiative is "bonus_elettrodomestici"
    And the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative bonus_elettrodomestici
    And the onboard of A becomes OK within 300 seconds
    And the merchant 1 is qualified

  @reward_batch_counter
  Scenario: Point of sale invoice updates are rejected while the reward batch is SENT or EVALUATING
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    When the reward batch of transaction X is prepared and sent
    And the counters of reward batch B are captured as after_send
    And the point of sale pos_1 of merchant 1 tries to update the invoice of transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 tries to reverse the transaction X by Bar Code
    And the reward batch of transaction X is sent for evaluation
    And the point of sale pos_1 of merchant 1 tries to update the invoice of transaction X by Bar Code
    Then the invoice update of transaction X is rejected
    And the reversal of transaction X is rejected by its reward batch
    And the reward batch of transaction X is EVALUATING
    And the live counters of reward batch B match its current transactions
    And reward batch B keeps the initial amount captured as after_send

  Scenario: Evaluating a sent reward batch rewards its invoiced transactions synchronously
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    When the reward batch of transaction X is prepared and sent
    And the reward batch of transaction X is sent for evaluation
    Then the reward batch of transaction X is EVALUATING
    And with Bar Code the transaction X is rewarded

  @reward_batch_counter
  Scenario: A merchant updates an invoice while the reward batch is EVALUATING
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    And the transaction X is prepared, sent and evaluated in reward batch status EVALUATING
    And the counters of reward batch B are captured as before_invoice_reassignment
    When the merchant 1 updates the invoice of transaction X by Bar Code
    Then the transaction X belongs to a different current-month reward batch as SUSPENDED
    And the live counters of reward batch B match its current transactions
    And reward batch B keeps the initial amount captured as before_invoice_reassignment
    And the destination reward batch of transaction X has live counters matching its current transactions

  Scenario: An invoiced payment is associated with a reward batch
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 tries to authorize the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    Then the transaction X belongs to a reward batch

  @reward_batch_counter
  Scenario: Reversing an invoiced payment removes it from its reward batch
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    When the point of sale pos_1 of merchant 1 reverses the transaction X by Bar Code
    Then the transaction X does not belong to a reward batch
    And the live counters of reward batch B match its current transactions

  @reward_batch_counter
  Scenario: A merchant sends an empty reward batch
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the transaction X belongs to the reward batch named B
    When the point of sale pos_1 of merchant 1 reverses all transactions in the reward batch named B
    And the merchant 1 prepares and sends the reward batch named B
    Then the reward batch named B is SENT
    And the reward batch named B contains 0 transactions
    And the live counters of reward batch B match its current transactions
    And reward batch B has zero initial amount
