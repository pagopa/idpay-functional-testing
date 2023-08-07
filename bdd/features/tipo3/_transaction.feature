Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo3"
    And the initiative's budget is totally allocated

  @transaction
  @Scontoditipo3
  Scenario: The merchant tries to generate a transaction when the budget of the initiative is totally allocated
    Given the merchant 2 is qualified
    When the merchant 2 generates the transaction X of amount 150000 cents
    Then the transaction X is created
