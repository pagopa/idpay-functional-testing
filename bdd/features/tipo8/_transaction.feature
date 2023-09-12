@Scontoditipo8
@transaction
Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo8"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboarded

  Scenario: Transaction of amount 1115 cents authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 1115 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is authorized

  Scenario: Transaction of amount 1114 cents is not authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 1114 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  Scenario: Transaction of amount 10001 cents is not authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 10001 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  Scenario: Transaction of amount 10000 cents authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 10000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is authorized

  @need_fix
  Scenario: After a transaction, the citizen is rewarded for the maximum allowed for a day
    Given the merchant 1 generates the transaction X of amount 7000 cents
    When the citizen A confirms the transaction X
    Then the citizen A is rewarded with 50 euros
