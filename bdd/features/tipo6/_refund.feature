@Scontoditipo6
@refunds
Feature: A merchant gets refunded if a transaction is discounted

  Background:
    Given the initiative is "Scontoditipo6"
    And the random merchant 1 is onboard
    And the citizen A is 20 years old at most
    And the citizen A is onboarded

  Scenario: A transaction of amount 1 cents is included in the payment order
    Given the merchant 1 generates the transaction X of amount 1 cents
    And the citizen A confirms the transaction X
    And the batch process confirms the transaction X
    When the institution refunds the merchant 1 of 0.01 euros successfully
    Then the merchant 1 is refunded 0.01 euros
