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
    And the onboard of A becomes OK within 120 seconds
    And the merchant 1 is qualified

  Scenario: An onboarded citizen creates a barcode payment accepted by a merchant
    Given the citizen A creates the transaction X by Bar Code
    When the point of sale pos_1 of merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents with product GTIN TUMBLEDRYERS03
    Then with Bar Code the transaction X is authorized
