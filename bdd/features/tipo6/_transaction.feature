Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo6"
    And the citizen A is onboarded
    And the citizen B is onboarded
    And the user can authorize only one transaction

  @transaction
  @Scontoditipo6
  Scenario: the transaction of amount 10000 cents, confirmed by the citizen creates the transaction of amount 8712 cents
    Given the merchant is qualified
    When the merchant generates a transaction X of amount 10000 cents
    And the citizien A confirms the transaction X
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo6
  Scenario: the transaction of amount 1 cents confirmed by the citizen creates the transaction of amount 1 cents
    Given the merchant is qualified
    When the merchant generates a transaction X of amount 1 cents
    And the citizien A confirms the transaction X
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo6
  Scenario: with transaction of amount 20000 cents, the citizen confirms within the available budget with
    Given the merchant is qualified
    When the merchant generates a transaction X of amount 20000 cents
    And the citizien A confirms the transaction X
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo6
  Scenario: user cannot confirm the second transaction Y because the initiative is one shot type
    Given the merchant is qualified
    And the merchant generates the transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    When the merchant generates the transaction Y of amount 1500 cents
    And the citizen A tries to confirm the transaction Y
    Then the transaction Y is not authorized

  @transaction
  @Scontoditipo6
  Scenario: user, after not having authorized the first transaction, authorizes a second transaction
    Given the merchant is qualified
    And the merchant generates the transaction X of amount 1000 cents
    And the citizien A does not authorize the transaction X
    When the merchant generates the transaction Y of amount 2000 cents
    And the citizen A confirms the transaction Y
    Then the transaction Y is authorized

  @transaction
  @Scontoditipo6
  Scenario: after confirmed transaction the second transaction is not authorized
    Given the merchant is qualified
    And the merchant generates the transaction X of amount 1000 cents
    And the citizien A confirms the transaction X
    When the merchant generates the transaction Y of amount 1900 cents
    And the citizen A tries to confirm the transaction Y after a thousandth of second from the transaction X
    Then the transaction Y is not authorized

  @transaction
  @Scontoditipo6
  Scenario: against two transactions generated by the same merchant the citizen, who confirms the first will receive error when confirming the second transaction
    Given the merchant are qualified
    And the merchant generates the transaction X of amount 1000 cents
    And the merchant generates the transaction Y of amount 1500 cents
    And the citizen A confirms the transaction X
    When citizen A  tries to confirm the transaction Y
    Then the transaction Y is not authorized

  @transaction
  @Scontoditipo1
  Scenario: against two transactions generated by two merchants the citizen, who confirms the first will receive error when confirming the second transaction
    Given the merchants are qualified
    And the merchant A generates the transaction X amount 1000 cents
    And the merchant B generates the transaction Y amount 1500 cents
    And the citizen A confirms the transaction Y
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized
