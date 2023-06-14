Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most

  @transaction
  @Scontoditipo1
  Scenario: the merchant tries to generate the trx
    Given the merchant 1 is qualified
    When the merchant 1 generates the transaction X of amount 30000 cents
    Then the transaction X is created

  @transaction
  @Scontoditipo1
  Scenario: the merchant not qualified tries to generate the trx
    Given the merchant 1 is not qualified
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created

  @transaction
  @Scontoditipo1
  Scenario: budget completely eroded with one trx
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 200000 cents
    When the citizen A confirms the transaction X
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo1
  Scenario: budget completely eroded with 10 trx
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generated 10 transactions of amount 3000 cents each
    When the citizen A confirms all the transaction
    Then the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo1
  Scenario: A transaction is not authorized if the budget is eroded
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the merchant 1 generates the transaction X of amount 200000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
  @Scontoditipo1
  Scenario: A transaction greater than the budget by 1 cent is authorized
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30001 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo1
  @need_fix
  Scenario: The transaction is not authorized before the expendable period
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the transaction is created before fruition period
    And the merchant 1 generates the transaction X of amount 30001 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
  @Scontoditipo1
  Scenario: The transaction is not authorized for onboarding citizen KO
    Given the merchant 1 is qualified
    And the citizen A is not onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
  @Scontoditipo1
  Scenario: The transaction is not authorized for ever registered citizen
    Given the merchant 1 is qualified
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
  @Scontoditipo1
  @need_fix
  Scenario: The transaction is not generated for an amount equal to 0 cents
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount 0 cents
    Then the transaction X is not created

  @transaction
  @Scontoditipo1
  @need_fix
  Scenario: the transaction expires, if not authorized within 3 days by the citizen
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the transaction is created 3 days ago
    And the merchant 1 generates the transaction X of amount 19999 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized
    And the transaction X expires

  @transaction
  @Scontoditipo1
  Scenario: against two transactions generated by the same merchant the citizen, who confirms the first will receive error when confirming the second transaction
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 10000 cents
    And the merchant 1 generates the transaction Y of amount 20000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction Y is created


  @transaction
  @Scontoditipo1
  Scenario: with two transactions generated by two merchants for the citizen to the confirmation of a transaction that erodes the budget to the second authorization receives error
    Given the merchant 1 is qualified
    And the merchant 2 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the merchant 2 generates the transaction Y of amount 30000 cents
    And the citizen A confirms the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction Y is not authorized

  @transaction
  @Scontoditipo1
  Scenario:
    Given the merchant is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant generates the transaction X of amount 30000 cents
    When the citizen A confirms the transaction X
    Then the citizen A is rewarded accordingly
    When the citizen B tries to confirm the transaction X
    Then the transaction X is not present
