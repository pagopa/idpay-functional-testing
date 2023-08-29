@Scontoditipo3
@transaction
Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo3"
    And the initiative's budget is totally allocated
    And the random merchant 1 is onboard

  Scenario: The merchant tries to generate a transaction when the budget of the initiative is totally allocated
    When the merchant 1 generates the transaction X of amount 150000 cents
    Then the transaction X is created
