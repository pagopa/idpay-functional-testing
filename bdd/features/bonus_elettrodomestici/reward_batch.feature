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

  Scenario: Invoice updates are suspended while the reward batch is SENT
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    Then the transaction X belongs to a reward batch
    When the reward batch of transaction X is prepared and sent
    And the point of sale pos_1 of merchant 1 tries to update the invoice of transaction X by Bar Code
    Then the invoice update of transaction X is rejected while its reward batch is SENT
    When the specific reward batch of transaction X is evaluated
    And the point of sale pos_1 of merchant 1 updates the invoice of transaction X by Bar Code
    Then the transaction X belongs to a different current-month reward batch as SUSPENDED

  Scenario: An invoiced payment is associated with a reward batch
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    Then the transaction X belongs to a reward batch

  Scenario: Reversing an invoiced payment removes it from its reward batch
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    Then the transaction X belongs to a reward batch
    When the point of sale pos_1 of merchant 1 reverses the transaction X by Bar Code
    Then the transaction X does not belong to a reward batch
