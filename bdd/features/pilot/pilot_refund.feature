@Scontoditipo1
@refunds
Feature: A merchant gets refunded if a transaction is discounted

  Background:
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the random merchant 2 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  Scenario: Merchant receive discount transaction refund
    Given the merchant 1 generates the transaction X of amount 20001 cents
    And the citizen A confirms the transaction X
    When the batch process confirms the transaction X
    Then the merchant 1 is refunded 200.01 euros

  Scenario: Citizen makes 4 transactions, then only 3 are confirmed
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the merchant 1 generates the transaction Z of amount 4000 cents
    And the merchant 1 generates the transaction K of amount 5000 cents
    Given the citizen A confirms the transaction X
    Then the citizen A is rewarded with 10 euros
    When the batch process confirms the transaction X
    Given the citizen A confirms the transaction Y
    Then the citizen A is rewarded with 20 euros
    When the batch process confirms the transaction Y
    Given the citizen A confirms the transaction K
    When the batch process confirms the transaction K
    Then the citizen A is rewarded with 40 euros
    And the merchant 1 is refunded 80 euros

  Scenario: Citizen makes 1 transactions, then the transaction is confirmed
    Given the merchant 2 generates the transaction X of amount 1000 cents
    And the merchant 2 generates the transaction Y of amount 2000 cents
    And the merchant 2 generates the transaction Z of amount 4000 cents
    And the citizen A confirms the transaction X
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 10 euros
    And the merchant 2 is refunded 10 euros

  Scenario: Citizen makes 2 transactions, then only 1 is confirmed
    Given the merchant 2 generates the transaction X of amount 1000 cents
    And the merchant 2 generates the transaction Y of amount 2000 cents
    And the merchant 2 generates the transaction Z of amount 4000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A confirms the transaction Y
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 30 euros
    And the merchant 2 is refunded 10 euros

  Scenario: Citizen makes 3 transactions, then only 2 are confirmed
    Given the merchant 2 generates the transaction X of amount 1000 cents
    And the merchant 2 generates the transaction Y of amount 2000 cents
    And the merchant 2 generates the transaction Z of amount 4000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A confirms the transaction Y
    When the batch process confirms the transaction X
    And the batch process confirms the transaction Y
    Then the citizen A is rewarded with 30 euros
    And the merchant 2 is refunded 30 euros

  Scenario: Citizen makes 3 transactions, then all 3 are confirmed
    Given the merchant 2 generates the transaction X of amount 1000 cents
    And the merchant 2 generates the transaction Y of amount 2000 cents
    And the merchant 2 generates the transaction Z of amount 4000 cents
    Given the citizen A confirms the transaction X
    When 1 second/s pass
    Given the citizen A confirms the transaction Y
    When 1 second/s pass
    Given the citizen A confirms the transaction Z
    When the batch process confirms the transaction Y
    And the batch process confirms the transaction X
    And the batch process confirms the transaction Z
    Then the citizen A is rewarded with 70 euros

  Scenario: Citizen makes 4 transactions, then only 1 is confirmed
    Given the merchant 2 generates the transaction X of amount 1000 cents
    And the merchant 2 generates the transaction Y of amount 2000 cents
    And the merchant 2 generates the transaction Z of amount 4000 cents
    And the merchant 2 generates the transaction K of amount 5000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A confirms the transaction Y
    And 1 second/s pass
    And the citizen A confirms the transaction Z
    And 1 second/s pass
    And the citizen A confirms the transaction K
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 120 euros
    And the merchant 2 is refunded 10 euros

  Scenario: Merchant receive max refund for discounted transaction exceeding the citizen's budget
    Given the merchant 1 generates the transaction X of amount 30001 cents
    And the citizen A confirms the transaction X
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 300 euros
    And the merchant 1 is refunded 300 euros

  Scenario: After 10 transactions of amount 1500 cents each, the amount of rewards is equal to payment order
    Given the merchant 1 generated 10 transactions of amount 1500 cents each
    And the citizen A confirms each transaction
    When the batch process confirms all the transactions
    Then the merchant 1 is refunded 150.0 euros

  Scenario: Merchant receive discount transaction refund for 1 cents transaction
    Given the merchant 1 generates the transaction X of amount 1 cents
    And the citizen A confirms the transaction X
    When the batch process confirms the transaction X
    Then the merchant 1 is refunded 0.01 euros
