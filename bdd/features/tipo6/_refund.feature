Feature: A merchant gets refunded if a transaction is discounted

  Background:
    Given the initiative is "Scontoditipo6"
    And the citizen A is onboarded
    And the citizen B is onboarded

  @Refunds
  @Scontoditipo6
  Scenario: after the transaction X of amount 1 cents, the payment order is OK
    Given the merchant generates a transaction X of amount 1 cents
    When the citizen A confirms the transaction X
    Then the merchant get rewarded accordingly

  @Refunds
  @Scontoditipo6
  Scenario: an unpaid transaction is not present in the rewards file
    Given the merchan generates a transaction X of amount 2000 cents
    When the citizen A confirms the transactions X
    And the transaction X is not rewarded
    Then the merchant get not rewarded accordingly