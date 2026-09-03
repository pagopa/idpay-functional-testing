@bonus_elettrodomestici
@transaction
@bar_code
Feature: Barcode payments for Bonus Elettrodomestici

  Background:
    Given the initiative is "bonus_elettrodomestici"
    And the citizen A is 21 years old exactly
    And the citizen A has ISEE 24000 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative bonus_elettrodomestici
    And the onboard of A becomes OK within 300 seconds
    And the merchant 1 is qualified

  Scenario: An onboarded citizen creates a barcode payment accepted by a merchant
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    Then with Bar Code the transaction X is authorized

  Scenario: A merchant captures an authorized barcode payment
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    Then with Bar Code the transaction X is captured

  Scenario: A point of sale cancels an authorized barcode payment
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 requests cancellation of the transaction X by Bar Code
    Then the point of sale cancellation of transaction X succeeds

  Scenario: A point of sale cannot cancel a captured barcode payment
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 requests cancellation of the transaction X by Bar Code
    Then the point of sale cancellation is rejected because the transaction is captured
    And with Bar Code the transaction X is captured

  Scenario: A merchant invoices a captured barcode payment
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    Then with Bar Code the transaction X is invoiced

  Scenario: A merchant invoices an already invoiced barcode payment
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code

  Scenario: A merchant reverses an invoiced barcode payment
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 reverses the transaction X by Bar Code
    Then with Bar Code the transaction X is refunded
