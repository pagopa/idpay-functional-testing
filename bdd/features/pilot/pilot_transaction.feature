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
