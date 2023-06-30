Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo6"
    And the citizen A is 20 years old at most
    And the citizen A is onboarded
    And the citizen B is 20 years old at most
    And the citizen B is onboarded

  @transaction
  @Scontoditipo6
  Scenario: the transaction of amount 10000 cents, confirmed by the citizen creates the transaction of amount 8712 cents
    Given the merchant 1 is qualified
    When the merchant 1 generates a transaction X of amount 10000 cents
    And the citizen A confirms the transaction X
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo6
  Scenario: the transaction of amount 1 cents confirmed by the citizen creates the transaction of amount 1 cents
    Given the merchant 1 is qualified
    When the merchant 1 generates a transaction X of amount 1 cents
    And the citizen A confirms the transaction X
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo6
  Scenario: with transaction of amount 20000 cents, the citizen confirms within the available budget with
    Given the merchant 1 is qualified
    When the merchant 1 generates a transaction X of amount 20000 cents
    And the citizen A confirms the transaction X
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo6
  Scenario: user cannot confirm the second transaction Y because the initiative is one shot type
    Given the merchant 1 is qualified
    And the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    When the merchant 1 generates the transaction Y of amount 1500 cents
    And the citizen A tries to confirm the transaction Y
    Then the transaction Y is not authorized

  @transaction
  @Scontoditipo6
  Scenario: user, after not having authorized the first transaction, authorizes a second transaction
    Given the merchant 1 is qualified
    And the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A does not authorize the transaction X
    When the merchant 1 generates the transaction Y of amount 2000 cents
    And the citizen A confirms the transaction Y
    Then the transaction Y is authorized

  @transaction
  @Scontoditipo6
  Scenario: after confirmed transaction the second transaction is not authorized
    Given the merchant 1 is qualified
    And the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    When the merchant 1 generates the transaction Y of amount 1900 cents
    And the citizen A tries to confirm the transaction Y after a thousandth of second from the transaction X
    Then the transaction Y is not authorized

  @transaction
  @Scontoditipo6
  Scenario: against two transactions generated by the same merchant the citizen, who confirms the first will receive error when confirming the second transaction
    Given the merchant 1 is qualified
    And the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 generates the transaction Y of amount 1500 cents
    And the citizen A confirms the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction Y is not authorized

  @transaction
  @Scontoditipo6
  @wip
  Scenario: against two transactions generated by two merchants the citizen, who confirms the first will receive error when confirming the second transaction
   Given the merchant 1 is qualified
   And the merchant 2 is qualified
   And the merchant 1 generates the transaction X of amount 1000 cents
   And the merchant 2 generates the transaction Y of amount 1500 cents
   And the citizen A confirms the transaction X
   When the citizen A tries to confirm the transaction Y
   Then the transaction Y is not authorized
