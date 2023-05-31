Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "pilot"
    And the citizen is 25 years old at most

  @transaction
  @pilot
  Scenario: the merchant tries to generate the trx
    Given the merchant is qualified
    When the merchant tries to generate a transaction of amount 30000 cents
    Then the transaction is created

  @transaction
  @pilot
  @need_fix
  Scenario: the merchant not qualified tries to generate the trx
    Given the merchant is not qualified
    When the merchant tries to generate a transaction of amount 30000 cents
    Then the transaction is not created

  @transaction
  @pilot
  Scenario: budget completely eroded with one trx
    Given the citizen is onboard
    And the merchant generated a transaction of amount 200000 cents
    When the citizen authorizes the transaction
    Then the citizen is rewarded accordingly

  @transaction
  @pilot
  @need_fix
  Scenario: budget completely eroded with 10 trx
    Given the citizen is onboard
    And the merchant generated 10 transactions of amount 200000 cents
    When the citizen authorizes the transaction
    When the citizen confirms all the transaction
    Then the citizen is rewarded accordingly

  @transaction
  @pilot
  Scenario: A transaction is not authorized if the budget is eroded
    Given the citizen is onboard
    And the citizen's budget is eroded
    And the merchant generated a transaction of amount 200000 cents
    When the citizen tries to authorize the transaction
    Then the transaction is not authorized

  @transaction
  @pilot
  Scenario: A transaction greater than the budget by 1 cent is authorized
    Given the citizen is onboard
    And the merchant generated a transaction of amount 30001 cents
    When the citizen authorizes the transaction
    Then the transaction is authorized
    And the citizen is rewarded accordingly
