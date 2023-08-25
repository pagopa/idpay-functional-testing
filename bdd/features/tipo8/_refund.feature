@Scontoditipo8
@refunds
Feature: A merchant gets refunded if a transaction is discounted

  Background:
    Given the initiative is "Scontoditipo8"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  Scenario: Merchant receives discount transaction refund
    Given the merchant 1 generates the transaction X of amount 1115 cents
    And the citizen A confirms the transaction X
    When the batch process confirms the transaction X
    Then the merchant 1 is refunded 11.15 euros

  Scenario: An unpaid transaction is not present in the refunds file
    Given the merchant 1 generates the transaction X of amount 7000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A tries to pre-authorize the transaction Y
    And the latest pre-authorization fails
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 50 euros
    And the merchant 1 is refunded 50 euros

  Scenario: After 5 transactions of amount 2000 cents each, the amount of rewards is equal to payment order
    Given the citizen B is 26 years old at most
    And the citizen B is onboard
    And the citizen C is 27 years old at most
    And the citizen C is onboard
    And the citizen D is 28 years old at most
    And the citizen D is onboard
    And the citizen E is 29 years old at most
    And the citizen E is onboard
    And the merchant 1 generates the transaction X of amount 2000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the citizen B confirms the transaction Y
    And the merchant 1 generates the transaction Z of amount 2000 cents
    And the citizen C confirms the transaction Z
    And the merchant 1 generates the transaction W of amount 2000 cents
    And the citizen D confirms the transaction W
    And the merchant 1 generates the transaction U of amount 2000 cents
    And the citizen E confirms the transaction U
    When the batch process confirms all the transactions
    Then the merchant 1 is refunded 100.0 euros
