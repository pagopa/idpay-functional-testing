Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo8"
    And the merchant is qualified
    And the citizen A is onboarded
    And the citizen B is onboarded

  @transaction
  @Scontoditipo8
  Scenario: Transaction  of amount 1115 cents authorized by the citizen

  @transaction
  @Scontoditipo8
  Scenario: Transaction  amount 1114 cents is not authorized by the citizen

  @transaction
  @Scontoditipo8
  Scenario: Transaction amount 10001 cents is not authorized by the citizen

  @transaction
  @Scontoditipo8
  Scenario: After two transactions that partially erode the citizen’s budget, the third operation is rewarded with the remaining budget

  @transaction
  @Scontoditipo8
  Scenario: After a transactions, the citizen is refunded correctly 

  @transaction
  @Scontoditipo8
  Scenario: Transaction of amount 10000 cents authorized by the citizen