@discount_bar_code
@refunds
Feature: A merchant gets refunded if a transaction by Bar Code is discounted

  Background:
    Given the initiative is "discount_bar_code"
    And the citizen A has fiscal code random
    And the citizen A is onboard
    And the random merchant 1 is onboard

  Scenario: A merchant is refunded for a transaction made by Bar Code
    Given the citizen A creates the transaction X by Bar Code
    And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
    And with Bar Code the transaction X is authorized
    And the citizen A is rewarded with 200 euros
    When the batch process confirms the transaction X
    And the institution refunds the merchant 1 of 200 euros successfully
    Then the merchant 1 is refunded 200 euros

  Scenario: A merchant is refunded for a transaction made by Bar Code that exhausted the budget of citizen
    Given the citizen A creates the transaction X by Bar Code
    And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
    And with Bar Code the transaction X is authorized
    And the citizen A is rewarded with 200 euros
    And the batch process confirms the transaction X
    And the citizen A creates the transaction Y by Bar Code
    When the merchant 1 authorizes the transaction Y by Bar Code of amount 20000 cents
    Then the citizen A is rewarded with 300 euros
    When the batch process confirms the transaction Y
    And the institution refunds the merchant 1 of 300 euros successfully
    Then the merchant 1 is refunded 300 euros

  Scenario: A merchant is not refunded for a transaction made by Bar Code because the institution payment fails
    Given the citizen A creates the transaction X by Bar Code
    And the merchant 1 authorizes the transaction X by Bar Code of amount 25000 cents
    And with Bar Code the transaction X is authorized
    And the citizen A is rewarded with 250 euros
    When the batch process confirms the transaction X
    And the institution refunds the merchant 1 of 250 euros unsuccessfully
    Then the merchant 1 is not refunded 250 euros
