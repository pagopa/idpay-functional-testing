Feature: A merchant gets refunded if a transaction is discounted

  Background:
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  @refunds
  @Scontoditipo1
  Scenario: Merchant receive discount transaction refund
    Given the merchant 2 is qualified
    And the merchant 2 generates the transaction X of amount 30001 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the merchant 2 is refunded 300.0 euros
