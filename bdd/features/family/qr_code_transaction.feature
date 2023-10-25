@family
@transaction
Feature: A member family can pay a transaction by QR Code

  Background:
    Given the initiative is "family"
    And the random merchant 1 is onboard
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    When the first citizen of A B C onboards
    Then the onboard of A is OK

  Scenario: A family member in status demanded by another member cannot pay a transaction
    Given the onboard of B is demanded
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen B tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard
    When the citizen A pre-authorizes the transaction X
    Then the transaction X is authorized

  @suspension
  Scenario: A family member pays a transaction, although another member is suspended
    Given the citizen B onboarded
    And the institution suspends correctly the citizen B
    And the merchant 1 generates the transaction X of amount 10000 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    Given the merchant 1 generates the transaction Y of amount 20000 cents
    When the citizen B tries to pre-authorize the transaction Y
    Then the latest pre-authorization fails because the user is suspended

  @unsubscribe
  Scenario: A family member pays a transaction, although another member has unsubscribed
    Given the citizen B onboarded
    And the citizen B is unsubscribed
    And the merchant 1 generates the transaction X of amount 10000 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    Given the merchant 1 generates the transaction Y of amount 20000 cents
    When the citizen B tries to pre-authorize the transaction Y
    Then the latest pre-authorization fails because the user is unsubscribed

  Scenario: A family member onboarded after another family member pays a transaction
    Given the merchant 1 generates the transaction X of amount 10000 cents
    And the citizen A confirms the transaction X
    And the transaction X is authorized
    When the citizen B onboarded
    Then the family member B has budget of 200 euros left
    And the family member A has budget of 200 euros left

  @refund
  Scenario: All family members pay a transaction and they are rewarded individually, sharing the budget
    Given the citizen B onboarded
    And the citizen C onboarded
    And the merchant 1 generates the transaction X of amount 10000 cents
    And the merchant 1 generates the transaction Y of amount 5000 cents
    And the merchant 1 generates the transaction Z of amount 7550 cents
    When the citizen A confirms the transaction X
    Then the family member A is rewarded with 100 euros
    And the family members A B C have budget of 200 euros left
    When the citizen B confirms the transaction Y
    Then the family member B is rewarded with 50 euros
    And the family members A B C have budget of 150 euros left
    When the citizen C confirms the transaction Z
    Then the family member C is rewarded with 75.50 euros
    And the family members A B C have budget of 74.50 euros left
    When the institution refunds the merchant 1 of 216.50 euros successfully
    Then the merchant 1 is refunded 216.50 euros

  @refund
  Scenario: Two family members pay a transaction and the second one exhausts the budget
    Given the citizen B onboarded
    And the merchant 1 generates the transaction X of amount 20000 cents
    And the merchant 1 generates the transaction Y of amount 15000 cents
    When the citizen A confirms the transaction X
    Then the family member A is rewarded with 200 euros
    And the family members A B have budget of 100 euros left
    When the citizen B confirms the transaction Y
    Then the family member B is rewarded with 100 euros
    And the family members A B have budget of 0 euros left
    When the institution refunds the merchant 1 of 300 euros successfully
    Then the merchant 1 is refunded 300 euros

  @refund
  Scenario: Two family members pay a transaction but the first one exhausted the budget
    Given the citizen B onboarded
    And the merchant 1 generates the transaction X of amount 35000 cents
    And the merchant 1 generates the transaction Y of amount 17000 cents
    When the citizen A confirms the transaction X
    Then the family member A is rewarded with 300 euros
    And the family members A B have budget of 0 euros left
    When the citizen B tries to pre-authorize the transaction Y
    Then the transaction Y is not authorized for budget eroded

