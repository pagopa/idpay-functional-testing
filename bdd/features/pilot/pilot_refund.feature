@Scontoditipo1
@refunds
Feature: Merchant refund

  Background:
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  Scenario: Merchant receives discount transaction refund
    Given the merchant 1 generates the transaction X of amount 20001 cents
    And the citizen A confirms the transaction X
    And the batch process confirms the transaction X
    And 1 second/s pass
    When the institution refunds the merchant 1 of 200.01 euros successfully
    Then the merchant 1 is refunded 200.01 euros

  Scenario: Citizen makes 4 transactions, then only 3 are confirmed
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the merchant 1 generates the transaction Z of amount 4000 cents
    And the merchant 1 generates the transaction K of amount 5000 cents
    And the citizen A confirms the transaction X
    When the batch process confirms the transaction X
    Given the citizen A confirms the transaction Y
    When the batch process confirms the transaction Y
    Given the citizen A confirms the transaction K
    When the batch process confirms the transaction K
    And 1 second/s pass
    Then the citizen A is rewarded with 80 euros
    When the institution refunds the merchant 1 of 80 euros successfully
    Then the merchant 1 is refunded 80 euros

  Scenario: Citizen makes 1 transaction, then the transaction is confirmed
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the merchant 1 generates the transaction Z of amount 4000 cents
    And the citizen A confirms the transaction X
    And the citizen A is rewarded with 10 euros
    And the batch process confirms the transaction X
    When the institution refunds the merchant 1 of 10 euros successfully
    Then the merchant 1 is refunded 10 euros

  Scenario: Citizen makes 2 transactions, then only 1 is confirmed
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the merchant 1 generates the transaction Z of amount 4000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A confirms the transaction Y
    And the citizen A is rewarded with 30 euros
    And the batch process confirms the transaction X
    And 1 second/s pass
    When the institution refunds the merchant 1 of 10 euros successfully
    Then the merchant 1 is refunded 10 euros

  Scenario: Citizen makes 3 transactions, then only 2 are confirmed
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the merchant 1 generates the transaction Z of amount 4000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A confirms the transaction Y
    And the citizen A is rewarded with 30 euros
    And the batch process confirms the transaction X
    And the batch process confirms the transaction Y
    When the institution refunds the merchant 1 of 30 euros successfully
    Then the merchant 1 is refunded 30 euros

  Scenario: Citizen makes 3 transactions, then all 3 are confirmed
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the merchant 1 generates the transaction Z of amount 4000 cents
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
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 2000 cents
    And the merchant 1 generates the transaction Z of amount 4000 cents
    And the merchant 1 generates the transaction K of amount 5000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A confirms the transaction Y
    And 1 second/s pass
    And the citizen A confirms the transaction Z
    And 1 second/s pass
    And the citizen A confirms the transaction K
    And the citizen A is rewarded with 120 euros
    And the batch process confirms the transaction X
    When the institution refunds the merchant 1 of 10 euros successfully
    Then the merchant 1 is refunded 10 euros

  Scenario: Merchant receives max refund for discounted transaction exceeding the citizen's budget
    Given the merchant 1 generates the transaction X of amount 30001 cents
    And the citizen A confirms the transaction X
    And the citizen A is rewarded with 300 euros
    And the batch process confirms the transaction X
    And 1 second/s pass
    When the institution refunds the merchant 1 of 300 euros successfully
    Then the merchant 1 is refunded 300 euros

  Scenario: After 10 transactions of amount 1500 cents each, the amount of rewards is equal to payment order
    Given the merchant 1 generated 10 transactions of amount 1500 cents each
    And the citizen A confirms each transaction
    And the citizen A is rewarded with 150 euros
    When the batch process confirms all the transactions
    And the institution refunds the merchant 1 of 150 euros successfully
    Then the merchant 1 is refunded 150.0 euros

  Scenario: Merchant receives discount transaction refund for 1 cents transaction
    Given the merchant 1 generates the transaction X of amount 1 cents
    And the citizen A confirms the transaction X
    And the citizen A is rewarded with 0.01 euros
    And the batch process confirms the transaction X
    When the institution refunds the merchant 1 of 0.01 euros successfully
    Then the merchant 1 is refunded 0.01 euros

  Scenario: Merchant do not receives refund if the institution payment fails
    Given the merchant 1 generates the transaction X of amount 20001 cents
    And the citizen A confirms the transaction X
    And the citizen A is rewarded with 200.01 euros
    And the batch process confirms the transaction X
    When the institution refunds the merchant 1 of 200.01 euros unsuccessfully
    Then the merchant 1 is not refunded 200.01 euros
