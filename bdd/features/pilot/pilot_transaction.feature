@Scontoditipo1
@transaction
Feature: A transaction is generated, authorized and confirmed

  Background:
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most

  Scenario: The merchant tries to generate the trx
    Given the random merchant 1 is onboard
    When the merchant 1 generates the transaction X of amount 30000 cents
    Then the transaction X is created

  @MIL
  Scenario: The merchant tries to generate a transaction through MIL
    Given the random merchant 1 is onboard
    When the merchant 1 generates the transaction X of amount 30000 cents through MIL
    Then the transaction X is created

  Scenario: The merchant not qualified tries to generate the trx
    Given the merchant 1 is not qualified
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because the merchant is not qualified

  @MIL
  Scenario: The merchant not qualified tries to generate the trx through MIL
    Given the merchant 1 is not qualified
    When the merchant 1 tries to generate the transaction X of amount 30000 cents through MIL
    Then the transaction X is not created because the merchant is not qualified

  @skip
  @need_fix
  Scenario: The merchant tries to generate the transaction with wrong acquirer ID
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 30000 cents with wrong acquirer ID
    Then the transaction X is not created

  @skip
  @MIL
  @need_fix
  Scenario: The merchant tries to generate the transaction with wrong acquirer ID through MIL
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 30000 cents with wrong acquirer ID
    Then the transaction X is not created

  Scenario: The budget is completely eroded with one trx
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

  @MIL
  Scenario: The budget is completely eroded with one trx through MIL
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

  Scenario: The second time a transaction is pre-authorized by the same citizen an error is returned
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A tries to pre-authorize the transaction X
    Then the transaction X is already authorized
    And the citizen A is rewarded with 300 euros

  @MIL
  Scenario: The second time a transaction, created through MIL, is pre-authorized by the same citizen an error is returned
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    When the citizen A confirms the transaction X
    And 1 second/s pass
    And the citizen A tries to pre-authorize the transaction X
    Then the transaction X is already authorized
    And the citizen A is rewarded with 300 euros

  Scenario: A transaction of 1 cent is authorized
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 1 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 0.01 euros

  @MIL
  Scenario: A transaction, created through MIL, of 1 cent is authorized
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 1 cents through MIL
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 0.01 euros

  Scenario: Citizen's budget is completely eroded with 10 trx
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generated 10 transactions of amount 3000 cents each
    When the citizen A confirms all the transactions
    Then the citizen A is rewarded with 300 euros

  @MIL
  Scenario: Citizen's budget is completely eroded with 10 trx, created through MIL
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generated 10 transactions of amount 3000 cents each through MIL
    When the citizen A confirms all the transactions
    Then the citizen A is rewarded with 300 euros

  Scenario: A transaction is not authorized if the budget is eroded
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the merchant 1 generates the transaction X of amount 200000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded

  @MIL
  Scenario: A transaction, created through MIL, is not authorized if the budget is eroded
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the merchant 1 generates the transaction X of amount 200000 cents through MIL
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded

  Scenario: A transaction greater than the budget by 1 cent is authorized
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30001 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

  @MIL
  Scenario: A transaction, created through MIL, greater than the budget by 1 cent is authorized
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30001 cents through MIL
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros

  Scenario: The transaction is not authorized for a citizen which got KO during onboarding
    Given the random merchant 1 is onboard
    And the citizen A is not onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard

  @MIL
  Scenario: The transaction, created through MIL, is not authorized for onboarding citizen KO
    Given the random merchant 1 is onboard
    And the citizen A is not onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard

  Scenario: The transaction is not authorized for ever registered citizen
    Given the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard

  @MIL
  Scenario: The transaction, created through MIL, is not authorized for ever registered citizen
    Given the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard

  Scenario: The transaction can still be authorized if an ever registered citizen tried to authorize it
    Given the random merchant 1 is onboard
    And the citizen A is not onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A tries to pre-authorize the transaction X
    When the citizen B confirms the transaction X
    Then the transaction X is authorized

  @MIL
  Scenario: The transaction, created through MIL, can still be authorized if an ever registered citizen tried to authorize it
    Given the random merchant 1 is onboard
    And the citizen A is not onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A tries to pre-authorize the transaction X
    When the citizen B confirms the transaction X
    Then the transaction X is authorized

  Scenario: The transaction is not generated for an amount equal to 0 cents
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 0 cents
    Then the transaction X is not created for invalid amount

  @MIL
  Scenario: The transaction is not generated for an amount equal to 0 cents through MIL
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 0 cents through MIL
    Then the transaction X is not created for invalid amount

  Scenario: The transaction is not generated for an amount equal to -1 cents
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount -1 cents
    Then the transaction X is not created for invalid amount

  @MIL
  Scenario: The transaction is not generated for an amount equal to -1 cents through MIL
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount -1 cents through MIL
    Then the transaction X is not created for invalid amount

  Scenario: With two transactions generated by two merchants for the citizen to the confirmation of a transaction that erodes the budget to the second authorization receives error
    Given the random merchant 1 is onboard
    And the random merchant 2 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 15000 cents
    And the merchant 2 generates the transaction Y of amount 30000 cents
    And the citizen A confirms the transaction Y
    When the citizen A tries to confirm the transaction X
    Then the latest pre-authorization fails
    And the transaction X is not authorized for budget eroded

  @MIL
  Scenario: With two transactions generated by two merchants through MIL for the citizen to the confirmation of a transaction that erodes the budget to the second authorization receives error
    Given the random merchant 1 is onboard
    And the random merchant 2 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the merchant 2 generates the transaction Y of amount 30000 cents through MIL
    And the citizen A confirms the transaction Y
    When the citizen A tries to confirm the transaction X
    Then the latest pre-authorization fails
    And the transaction X is not authorized for budget eroded

  Scenario: If a transaction is authorized by citizen A, B receives an error upon pre-authorizing the same transaction.
    Given the random merchant 1 is onboard
    And the citizen A is 20 years old at most
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A confirms the transaction X
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @MIL
  Scenario: If a transaction, created through MIL, is authorized by citizen A, B receives an error upon pre-authorizing the same transaction.
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A confirms the transaction X
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @skip
  Scenario: 2 transactions cannot be authorized by the same citizen if at least one second has not passed between authorizations.
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction Y is exceeding rate limit

  @skip
  @MIL
  Scenario: 2 transactions, created through MIL, cannot be authorized by the same citizen if at least one second has not passed between authorizations.
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 3000 cents through MIL
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction Y is exceeding rate limit

  Scenario: 2 transactions can be authorized by different citizens even if one second has not passed between authorizations.
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen B tries to confirm the transaction Y
    Then the transaction X is authorized
    And the transaction Y is authorized

  @MIL
  Scenario: 2 transactions, created through MIL, can be authorized by different citizens even if one second has not passed between authorizations.
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 3000 cents through MIL
    And the citizen A confirms, immediately before the next step, the transaction X
    When the citizen B tries to confirm the transaction Y
    Then the transaction X is authorized
    And the transaction Y is authorized

  @skip
  Scenario: One second after a rate limit failure the transaction can be authorized.
    Given the random merchant 1 is onboard
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

  @skip
  @MIL
  Scenario: One second after a rate limit failure the transaction, created through MIL, can be authorized.
    Given the random merchant 1 is onboard
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

  Scenario: 2 transactions are authorized correctly by the same citizen if authorizations are 1 second apart one from the other.
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the citizen A confirms the transaction X
    When 1 second/s pass
    And the citizen A tries to confirm the transaction Y
    Then the transaction Y is authorized

  @MIL
  Scenario: 2 transactions, created through MIL, are authorized correctly by the same citizen if authorizations are 1 second apart one from the other.
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 3000 cents through MIL
    And the citizen A confirms the transaction X
    When 1 second/s pass
    And the citizen A tries to confirm the transaction Y
    Then the transaction Y is authorized

  Scenario: Citizen A (with eroded budget) fails to authorize a transaction, citizen B fail authorizing the same transaction because it is already assigned
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 200000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  @MIL
  Scenario: Citizen A (with eroded budget) fails to authorize a transaction, created through MIL, citizen B fail authorizing the same transaction because it is already assigned
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 200000 cents through MIL
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already assigned

  Scenario: If citizen A pre-authorizes the transactions X and Y, and the transaction X is authorized eroding A's budget, A receives an error upon authorizing the transaction Y
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the merchant 1 generates the transaction Y of amount 30000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    And the citizen A confirms the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros
    And the transaction Y is not authorized for budget eroded

  @MIL
  Scenario: If citizen A pre-authorizes the transactions X and Y through MIL, and the transaction X is authorized eroding A's budget, A receives an error upon authorizing the transaction Y
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 30000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    And the citizen A confirms the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction X is authorized
    And the citizen A is rewarded with 300 euros
    And the transaction Y is not authorized for budget eroded

  Scenario: If citizen A pre-authorizes the transactions X and Y, and the transaction X is authorized eroding A's budget, Y remains identified
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the merchant 1 generates the transaction Y of amount 30000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    When the citizen A confirms the transaction X
    Then the transaction Y is identified

  @MIL
  Scenario: If citizen A pre-authorizes the transactions X and Y through MIL, and the transaction X is authorized eroding A's budget, Y remains identified
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the merchant 1 generates the transaction Y of amount 30000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    When the citizen A confirms the transaction X
    Then the transaction Y is identified

  Scenario: Citizen pre-authorize 2 times a transaction and it is still identified
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen A tries to pre-authorize the transaction X
    Then the transaction X is identified

  @MIL
  Scenario: Citizen pre-authorize 2 times a transaction through MIL and it is still identified
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    When the citizen A tries to pre-authorize the transaction X
    Then the transaction X is identified

  Scenario: Citizen tries to pre-authorize a transaction already pre-authorized by another citizen
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen B tries to pre-authorize the transaction X
    Then the latest pre-authorization fails
    And the transaction X is identified

  @MIL
  Scenario: Citizen tries to pre-authorize a transaction, created through MIL, already pre-authorized by another citizen
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    When the citizen B tries to pre-authorize the transaction X
    Then the latest pre-authorization fails
    And the transaction X is identified

  Scenario: Citizen pre-authorizes successfully a transaction already pre-authorized by himself
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen A pre-authorizes the transaction X
    Then the transaction X is identified

  Scenario: Citizen authorizes successfully a transaction already pre-authorized by himself
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen A confirms the transaction X
    Then the transaction X is authorized

  @MIL
  Scenario: Citizen pre-authorizes successfully a transaction, created through MIL, already pre-authorized by himself
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    When the citizen A pre-authorizes the transaction X
    Then the transaction X is identified

  Scenario: Citizen fails pre-authorizing a non-existing transaction code (chosen at random)
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the transaction X does not exists
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the transaction cannot be found

  Scenario: Citizen authorizes a transaction before pre-authorization
    Given the random merchant 1 is onboard
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30000 cents
    When the citizen A tries to authorize the transaction X
    Then the latest authorization fails because the user did not pre-authorize the transaction

  Scenario: Budget not completely eroded with one transaction X of amount 300 cents
    Given the citizen A is onboard
    And the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 300 cents
    When the citizen A confirms the transaction X
    Then the citizen A is rewarded with 3 euros
