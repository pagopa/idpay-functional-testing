Feature: A merchant gets refunded if a transaction is discounted

Background:
    Given the initiative is "Scontoditipo8"
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  @refunds
  @Scontoditipo8
  Scenario: Merchant receives discount transaction refund
    Given the merchant 1 generates the transaction X of amount 1115 cents
    And the citizen A confirms the transaction X
    When the batch process confirms the transaction X
    Then the merchant 1 is refunded 11.15 euros

  @refunds
  @Scontoditipo8
  Scenario: An unpaid transaction is not present in the refunds file
    Given the merchant 1 generates the transaction X of amount 7000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A tries to pre-authorize the transaction Y
    And the latest pre-authorization fails
    When the batch process confirms the transaction X
    Then the merchant 1 is refunded 50.0 euros

  @refunds
  @Scontoditipo8
  @skip
  Scenario: After 10 transactions of amount 2000 cents each, the amount of rewards is equal to payment order
