Feature: A merchant gets refunded if a transaction is discounted

  Background:
    Given the initiative is "Scontoditipo6"
    And the merchant 1 is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboarded

  @refunds
  @Scontoditipo6
  Scenario: After the transaction X of amount 1 cents, the payment order is OK
    Given the merchant 1 generates a transaction X of amount 1 cents
    When the citizen A confirms the transaction X
    Then the merchant 1 get rewarded accordingly

  @refunds
  @Scontoditipo6
  Scenario: An unpaid transaction is not present in the rewards file
    Given the merchant generates a transaction X of amount 2000 cents
    When the citizen A confirms the transactions X
    And the transaction X is not rewarded
    Then the merchant get not rewarded accordingly