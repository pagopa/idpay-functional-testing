Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo8"
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboarded
    And the citizen B is 25 years old at most
    And the citizen B is onboarded

  @transaction
  @Scontoditipo8
  Scenario: Transaction of amount 1115 cents authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 1115 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is authorized

  @transaction
  @Scontoditipo8
  Scenario: Transaction of amount 1114 cents is not authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 1114 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
  @Scontoditipo8
  Scenario: Transaction of amount 10001 cents is not authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 10001 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
  @Scontoditipo8
  Scenario: Transaction of amount 10000 cents authorized by the citizen
    Given the merchant 1 generates the transaction X of amount 10000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is authorized

  @transaction
  @Scontoditipo8
  Scenario: After a transaction, the citizen is rewarded correctly
    When the merchant 1 generates the transaction X of amount 2000 cents
    And the citizen A confirms the transaction X
    Then the citizen A is rewarded with 20 euros
