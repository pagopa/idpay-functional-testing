Feature: A merchant gets refunded if a transaction is discounted

  Background:
    Given the initiative is "Scontoditipo1"
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  @refunds
  @Scontoditipo1
  Scenario: Merchant receive discount transaction refund
    And the merchant 1 generates the transaction X of amount 30001 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the merchant 1 is refunded 300.0 euros

  @refunds
  @Scontoditipo1
  Scenario: after 10 transactions of amount 1500 cents each, the amount of rewards is equal to payment order
    Given the merchant 1 generated 10 transactions of amount 1500 cents each
    When the citizen A confirms all the transactions
    Then the merchant 1 is refunded 150.0 euros
