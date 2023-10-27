@discount_bar_code
@refunds
Feature: A merchant gets refunded if a transaction by Bar Code is discounted

  Background:
    Given the initiative is "discount_bar_code"
    And the citizen A has fiscal code random
    And the citizen A is onboard
    And the random merchant 1 is onboard

  Scenario: A merchant gets refunded about a transaction by Bar Code
    Given the citizen A creates the transaction X by Bar Code
    And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
    And with Bar Code the transaction X is authorized
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 200 euros
    When the institution refunds the merchant 1 of 200 euros successfully
    Then the merchant 1 is refunded 200 euros

  Scenario: A merchant gets refunded about a transaction by Bar Code that exhausted the budget of citizen
    Given the citizen A creates the transaction X by Bar Code
    And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
    And with Bar Code the transaction X is authorized
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 200 euros
    Given the citizen A creates the transaction Y by Bar Code
    And the merchant 1 authorizes the transaction Y by Bar Code of amount 20000 cents
    When the batch process confirms the transaction Y
    Then the citizen A is rewarded with 300 euros
    When the institution refunds the merchant 1 of 300 euros successfully
    Then the merchant 1 is refunded 300 euros

  Scenario: A merchant does not get refunded because the institution payment fails
    Given the citizen A creates the transaction X by Bar Code
    And the merchant 1 authorizes the transaction X by Bar Code of amount 25000 cents
    And with Bar Code the transaction X is authorized
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 250 euros
    When the institution refunds the merchant 1 of 250 euros unsuccessfully
    Then the merchant 1 is not refunded 250 euros
