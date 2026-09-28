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

  Scenario: Evaluating a sent reward batch rewards its invoiced transactions synchronously
    Given the citizen A fully performs the transaction X by Bar Code at point of sale pos_1 of merchant 1 of amount 20000 cents with product GTIN TUMBLEDRYERS03
    When the reward batch of transaction X is prepared and sent
    And the reward batch of transaction X is sent for evaluation
    Then the reward batch of transaction X is EVALUATING
    And with Bar Code the transaction X is rewarded
