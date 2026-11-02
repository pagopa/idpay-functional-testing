@bonus_elettrodomestici
@bonus_decoder
@family
@transaction
@bar_code
@refunds
Feature: A family beneficiary's invoiced Barcode payment can be reversed

  Background:
    Given the initiative is active
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the citizen A selects ISEE type "under_25000"
    And the citizen A tries to onboard the initiative
    And the onboard of A becomes OK within 300 seconds
    And the citizen B tries to onboard the initiative
    And the citizen C tries to onboard the initiative
    And the onboards of B C are family joined
    And the merchant 1 is qualified

  Scenario: The merchant reverses the family beneficiary payment after invoicing
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with default product GTIN
    And the point of sale pos_1 of merchant 1 captures the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 invoices the transaction X by Bar Code
    And the point of sale pos_1 of merchant 1 reverses the transaction X by Bar Code
    Then with Bar Code the transaction X is refunded
