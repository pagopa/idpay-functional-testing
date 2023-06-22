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
    And the merchant 1 generates the transaction X of amount 1 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo1
  Scenario: budget completely eroded with 10 trx
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generated 10 transactions of amount 3000 cents each
    When the citizen A confirms all the transactions
    Then the citizen A is rewarded accordingly

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
  Scenario: A transaction greater than the budget by 1 cent is authorized
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 30001 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded accordingly

  @transaction
  @Scontoditipo1
  Scenario: The transaction is not authorized before the expendable period
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the transaction is created before fruition period
    And the merchant 1 generates the transaction X of amount 30001 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is expired

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
  @skip
  Scenario: The transaction is not generated for an amount equal to 0 cents
    Given the merchant 1 is qualified
    When the merchant 1 tries to generate the transaction X of amount 0 cents
    Then the transaction X is not created

  @transaction
  @Scontoditipo1
  Scenario: A transaction of amount 0 cents is generated but cannot be confirmed by the citizen
    Given the merchant 1 is qualified
    And the merchant 1 generates the transaction X of amount 0 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized

  @transaction
    @Scontoditipo1
  Scenario Outline: The transaction expires if not authorized after 3 days by the citizen
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the transaction is created <days_back> days ago
    And the merchant 1 generates the transaction X of amount 19999 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is expired

    Examples: Days Back
      | days_back |
      | 3         |
      | 4         |
      | 5         |

  @transaction
    @Scontoditipo1
  Scenario Outline: The transaction does not expires if not authorized within 3 days by the citizen
    Given the merchant 1 is qualified
    And the citizen A is onboard
    And the transaction is created <days_back> days ago
    And the merchant 1 generates the transaction X of amount 19999 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is confirmed

    Examples: Days Back
      | days_back |
      | 0         |
      | 1         |
      | 2         |

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
    And the merchant 1 generates the transaction X of amount 15000 cents
    And the merchant 2 generates the transaction Y of amount 30000 cents
    And the citizen A confirms the transaction Y
    When the citizen A tries to confirm the transaction X
    Then the latest pre-authorization fails
    And the transaction X is cancelled

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
    Then the transaction X is already confirmed

  @transaction
  @Scontoditipo1
  Scenario: 2 transactions cannot be authorized by the same citizen if at least one seconds has not passed between authorizations.
    Given the merchant 1 is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the merchant 1 generates the transaction Z of amount 3000 cents
    And the citizen A confirms the transaction X
    And the citizen B confirms the transaction Y
    When the citizen B tries to confirm the transaction Z
    Then the transaction Z is exceeding rate limit

  @transaction
  @Scontoditipo1
  Scenario: 2 transactions are authorized correctly by the same citizen if authorizations are 1 second apart one from the other.
    Given the merchant 1 is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboard
    And the citizen B is 20 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 3000 cents
    And the merchant 1 generates the transaction Y of amount 3000 cents
    And the merchant 1 generates the transaction Z of amount 3000 cents
    And the citizen A confirms the transaction X
    And the citizen B confirms the transaction Y
    When 1 second/s pass
    And the citizen B tries to confirm the transaction Z
    Then the transaction Z is authorized

  @transaction
  @Scontoditipo1
  Scenario: Citizen A (with eroded budget) fails to authorize a transaction, citizen B fail authorizing the same transaction because it is already assigned
    Given the merchant 1 is qualified
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the citizen A's budget is eroded
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 200000 cents
    When the citizen A tries to confirm the transaction X
    Then the transaction X is not authorized for budget eroded
    When the citizen B tries to confirm the transaction X
    Then the transaction X is already confirmed

  @transaction
  @Scontoditipo1
  Scenario: If citizen A pre-authorizes the transactions X and Y, and the transaction X is authorized, A receives an error upon authorizing the transaction Y
    Given the merchant 1 is qualified
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the merchant 1 generates the transaction Y of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    And the citizen A confirms the transaction X
    When the citizen A tries to confirm the transaction Y
    Then the transaction X is authorized
    And the citizen A is rewarded accordingly
    And the transaction Y is not authorized for budget eroded

  @transaction
  @Scontoditipo1
  Scenario: If citizen A pre-authorizes the transactions X and Y, and the transaction X is authorized, Y remains identified
    Given the merchant 1 is qualified
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the merchant 1 generates the transaction Y of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A pre-authorizes the transaction Y
    When the citizen A confirms the transaction X
    Then the transaction Y is identified

  @transaction
  @Scontoditipo1
  Scenario: Citizen pre-authorize 2 times a transaction and it is still identified
    Given the merchant 1 is qualified
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen A tries to pre-authorize the transaction X
    Then the transaction X is identified

  @transaction
  @Scontoditipo1
  Scenario: Citizen tries to pre-authorize a transaction already pre-authorized by another citizen
    Given the merchant 1 is qualified
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the merchant 1 generates the transaction X of amount 300000 cents
    And the citizen A pre-authorizes the transaction X
    When the citizen B tries to pre-authorize the transaction X
    Then the latest pre-authorization fails
    And the transaction X is identified
