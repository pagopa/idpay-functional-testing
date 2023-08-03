Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most

  @transaction
  @Scontoditipo1
  Scenario: The merchant tries to generate the trx
    Given the merchant 1 is qualified
    When the merchant 1 generates the transaction X of amount 30000 cents
    Then the transaction X is created

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: The merchant tries to generate a transaction through MIL
    Given the merchant 1 is qualified
    When the merchant 1 generates the transaction X of amount 30000 cents through MIL
    Then the transaction X is created

  @transaction
  @Scontoditipo1
  Scenario: The merchant not qualified tries to generate the trx
    Given the merchant 1 is not qualified
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because the merchant is not qualified

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: The merchant not qualified tries to generate the trx through MIL
    Given the merchant 1 is not qualified
    When the merchant 1 tries to generate the transaction X of amount 30000 cents through MIL
    Then the transaction X is not created because the merchant is not qualified

  @transaction
  @Scontoditipo1
  @need_fix
  Scenario: The merchant tries to generate the transaction with wrong acquirer ID
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount 30000 cents with wrong acquirer ID
    Then the transaction X is not created

  @transaction
  @Scontoditipo1
  @MIL
  @need_fix
  Scenario: The merchant tries to generate the transaction with wrong acquirer ID through MIL
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount 30000 cents with wrong acquirer ID
    Then the transaction X is not created

  @transaction
  @Scontoditipo1
  Scenario: The budget is completely eroded with one trx
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: The budget is completely eroded with one trx through MIL
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

  @transaction
  @Scontoditipo1
  Scenario: The second time a transaction is pre-authorized by the same citizen an error is returned
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A tries to pre-authorize the transaction X
    Then the transaction X is already authorized
    And the citizen A is rewarded with 300 euros

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: The second time a transaction, created through MIL, is pre-authorized by the same citizen an error is returned
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    When the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A tries to pre-authorize the transaction X
    Then the transaction X is already authorized
    And the citizen A is rewarded with 300 euros

  @transaction
  @Scontoditipo1
  Scenario: A transaction of 1 cent is authorized
    Given the merchant 2 is qualified
    And the citizen A is onboard
    And the merchant 2 generates the transaction X of amount 1 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 0.01 euros

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: A transaction, created through MIL, of 1 cent is authorized
    Given the merchant 2 is qualified
    And the citizen A is onboard
    And the merchant 2 generates the transaction X of amount 1 cents through MIL
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 0.01 euros

  @transaction
  @Scontoditipo1
  Scenario: Citizen's budget is completely eroded with 10 trx
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generated 10 transactions of amount 3000 cents each
    When the citizen A confirms all the transactions
    Then the citizen A is rewarded with 300 euros

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: Citizen's budget is completely eroded with 10 trx, created through MIL
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generated 10 transactions of amount 3000 cents each through MIL
    When the citizen A confirms all the transactions
    Then the citizen A is rewarded with 300 euros

  @transaction
  @Scontoditipo1
  Scenario: A transaction is not authorized if the budget is eroded
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the merchant 1 generates the transaction X of amount 200000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: A transaction, created through MIL, is not authorized if the budget is eroded
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the merchant 1 generates the transaction X of amount 200000 cents through MIL
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded

  @transaction
  @Scontoditipo1
  Scenario: A transaction greater than the budget by 1 cent is authorized
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30001 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: A transaction, created through MIL, greater than the budget by 1 cent is authorized
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30001 cents through MIL
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

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
  @MIL
  Scenario: The transaction, created through MIL, is not authorized for onboarding citizen KO
    Given the merchant 1 is qualified
    And the citizen A is not onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
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
  @MIL
  Scenario: The transaction, created through MIL, is not authorized for ever registered citizen
    Given the merchant 1 is qualified
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
  @Scontoditipo1
  Scenario: The transaction cannot be authorized again if an ever registered citizen tried to authorize it
    Given the merchant 1 is qualified
    And the citizen A is not onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A tries to pre-authorize the transaction X
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: The transaction, created through MIL, cannot be authorized again if an ever registered citizen tried to authorize it
    Given the merchant 1 is qualified
    And the citizen A is not onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A tries to pre-authorize the transaction X
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @transaction
  @Scontoditipo1
  Scenario: The transaction is not generated for an amount equal to 0 cents
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount 0 cents
    Then the transaction X is not created for invalid amount

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: The transaction is not generated for an amount equal to 0 cents through MIL
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount 0 cents through MIL
    Then the transaction X is not created for invalid amount

  @transaction
  @Scontoditipo1
  Scenario: The transaction is not generated for an amount equal to -1 cents
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount -1 cents
    Then the transaction X is not created for invalid amount

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: The transaction is not generated for an amount equal to -1 cents through MIL
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount -1 cents through MIL
    Then the transaction X is not created for invalid amount

  @transaction
  @Scontoditipo1
  Scenario: Against two transactions generated by the same merchant the citizen, who confirms the first will receive error when confirming the second transaction
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 10000 cents
    And the merchant 1 generates the transaction Y of amount 20000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction Y is created

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: Against two transactions generated by the same merchant through MIL the citizen, who confirms the first will receive error when confirming the second transaction
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 10000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 20000 cents through MIL
    When the citizen A tries to confirm the transaction X
    Then the transaction Y is created

  @transaction
  @Scontoditipo1
  Scenario: With two transactions generated by two merchants for the citizen to the confirmation of a transaction that erodes the budget to the second authorization receives error
    Given the merchant 1 is qualified
    And the merchant 2 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 15000 cents
    And the merchant 2 generates the transaction Y of amount 30000 cents
    And the citizen A confirms the transaction Y
    When the citizen A tries to confirm the transaction X
    Then the latest pre-authorization fails
    And the transaction X is not authorized for budget eroded

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: With two transactions generated by two merchants through MIL for the citizen to the confirmation of a transaction that erodes the budget to the second authorization receives error
    Given the merchant 1 is qualified
    And the merchant 2 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the merchant 2 generates the transaction Y of amount 30000 cents through MIL
    And the citizen A confirms the transaction Y
    When the citizen A tries to confirm the transaction X
    Then the latest pre-authorization fails
    And the transaction X is not authorized for budget eroded

  @transaction
  @Scontoditipo1
  Scenario: If a transaction is authorized by citizen A, B receives an error upon pre-authorizing the same transaction.
    Given the merchant 1 is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A confirms the transaction X
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: If a transaction, created through MIL, is authorized by citizen A, B receives an error upon pre-authorizing the same transaction.
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A confirms the transaction X
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @transaction
  @Scontoditipo1
  Scenario: 2 transactions cannot be authorized by the same citizen if at least one second has not passed between authorizations.
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction Y is exceeding rate limit

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: 2 transactions, created through MIL, cannot be authorized by the same citizen if at least one second has not passed between authorizations.
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 3000 cents through MIL
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction Y is exceeding rate limit

  @transaction
  @Scontoditipo1
  Scenario: 2 transactions can be authorized by different citizens even if one second has not passed between authorizations.
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen B tries to confirm the transaction Y
    Then the transaction X is authorized
    And the transaction Y is authorized

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: 2 transactions, created though MIL, can be authorized by different citizens even if one second has not passed between authorizations.
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 3000 cents through MIL
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen B tries to confirm the transaction Y
    Then the transaction X is authorized
    And the transaction Y is authorized

  @transaction
  @Scontoditipo1
  Scenario: One second after a rate limit failure the transaction can be authorized.
    Given the merchant 1 is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A confirms, immediately before the next step, the transaction X
    And the citizen A tries to confirm the transaction Y
    And the transaction Y is exceeding rate limit
    When 1 second/s pass
    And the citizen A confirms the transaction Y
    Then the transaction Y is authorized

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: One second after a rate limit failure the transaction, created through MIL, can be authorized.
    Given the merchant 1 is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 3000 cents through MIL
    And the citizen A confirms, immediately before the next step, the transaction X
    And the citizen A tries to confirm the transaction Y
    And the transaction Y is exceeding rate limit
    When 1 second/s pass
    And the citizen A confirms the transaction Y
    Then the transaction Y is authorized

  @transaction
  @Scontoditipo1
  Scenario: 2 transactions are authorized correctly by the same citizen if authorizations are 1 second apart one from the other.
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A confirms the transaction X
    When 1 second/s pass
    And the citizen A tries to confirm the transaction Y
    Then the transaction Y is authorized

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: 2 transactions, created through MIL, are authorized correctly by the same citizen if authorizations are 1 second apart one from the other.
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 3000 cents through MIL
    And the citizen A confirms the transaction X
    When 1 second/s pass
    And the citizen A tries to confirm the transaction Y
    Then the transaction Y is authorized

  @transaction
  @Scontoditipo1
  Scenario: Citizen A (with eroded budget) fails to authorize a transaction, citizen B fail authorizing the same transaction because it is already assigned
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 200000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: Citizen A (with eroded budget) fails to authorize a transaction, created through MIL, citizen B fail authorizing the same transaction because it is already assigned
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 200000 cents through MIL
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @transaction
  @Scontoditipo1
  Scenario: If citizen A pre-authorizes the transactions X and Y, and the transaction X is authorized eroding A's budget, A receives an error upon authorizing the transaction Y
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the merchant 1 generates the transaction Y of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    And the citizen A confirms the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros
    And the transaction Y is not authorized for budget eroded

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: If citizen A pre-authorizes the transactions X and Y through MIL, and the transaction X is authorized eroding A's budget, A receives an error upon authorizing the transaction Y
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 300000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    And the citizen A confirms the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros
    And the transaction Y is not authorized for budget eroded

  @transaction
  @Scontoditipo1
  Scenario: If citizen A pre-authorizes the transactions X and Y, and the transaction X is authorized eroding A's budget, Y remains identified
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the merchant 1 generates the transaction Y of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    When the citizen A confirms the transaction X
    Then the transaction Y is identified

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: If citizen A pre-authorizes the transactions X and Y through MIL, and the transaction X is authorized eroding A's budget, Y remains identified
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 300000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    When the citizen A confirms the transaction X
    Then the transaction Y is identified

  @transaction
  @Scontoditipo1
  Scenario: Citizen pre-authorize 2 times a transaction and it is still identified
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen A tries to pre-authorize the transaction X
    Then the transaction X is identified

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: Citizen pre-authorize 2 times a transaction through MIL and it is still identified
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    When the citizen A tries to pre-authorize the transaction X
    Then the transaction X is identified

  @transaction
  @Scontoditipo1
  Scenario: Citizen tries to pre-authorize a transaction already pre-authorized by another citizen
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen B tries to pre-authorize the transaction X
    Then the latest pre-authorization fails
    And the transaction X is identified

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: Citizen tries to pre-authorize a transaction, created through MIL, already pre-authorized by another citizen
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    When the citizen B tries to pre-authorize the transaction X
    Then the latest pre-authorization fails
    And the transaction X is identified

  @transaction
  @Scontoditipo1
  Scenario: Citizen pre-authorizes successfully a transaction already pre-authorized by himself
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen A pre-authorizes the transaction X
    Then the transaction X is identified

  @transaction
  @Scontoditipo1
  @MIL
  Scenario: Citizen pre-authorizes successfully a transaction, created through MIL, already pre-authorized by himself
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    When the citizen A pre-authorizes the transaction X
    Then the transaction X is identified
