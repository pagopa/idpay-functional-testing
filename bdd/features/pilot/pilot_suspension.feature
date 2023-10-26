@Scontoditipo1
@Scontoditipo1_not_started
@Scontoditipo1_allocated
@suspension
Feature: Suspension

  Scenario: The Institution tries to suspend an onboard citizen during the fruition period and receives an OK result
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    When the institution suspends the citizen A
    Then the citizen A is suspended

  Scenario: The Institution tries to suspend a citizen not registered in the initiative and receives a KO
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen

  Scenario: A suspended citizen who tries to onboard remains in the "suspended" state
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the institution suspends correctly the citizen A
    When the citizen A tries to onboard
    Then the citizen A is suspended

  Scenario: A suspended citizen who tries to pre-authorize a transaction receives a KO result
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the institution suspends correctly the citizen A
    And the merchant 1 generates the transaction X of amount 20001 cents
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the user is suspended

  Scenario: A citizen who tries to authorize a transaction, being suspended after pre-authorization, receives a KO result
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 20001 cents
    And the citizen A pre-authorizes the transaction X
    And the institution suspends correctly the citizen A
    When the citizen A tries to authorize the transaction X
    Then the latest authorization fails because the user is suspended

  @refund
  Scenario: A citizen is correctly awarded for a transaction confirmed before its suspension
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 1001 cents
    And the citizen A confirms the transaction X
    And the institution suspends correctly the citizen A
    When the batch process confirms the transaction X
    Then the citizen A is rewarded with 10.01 euros

  @refund
  Scenario: If a transaction is correctly authorized by the citizen, if the latter is suspended, the payment mandate is correctly generated
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the merchant 1 generates the transaction X of amount 1001 cents
    And the citizen A confirms the transaction X
    And the institution suspends correctly the citizen A
    And the batch process confirms the transaction X
    When the institution refunds the merchant 1 of 10.01 euros successfully
    Then the merchant 1 is refunded 10.01 euros

  Scenario: Suspending a citizen does not free up the budget of an initiative with a fully allocated budget
    Given the initiative is "Scontoditipo1_allocated"
    And the initiative's budget is almost allocated
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the citizen B is 25 years old at most
    And the institution suspends correctly the citizen A
    When the citizen B tries to accept terms and conditions
    Then the latest accept terms and conditions failed for budget terminated
    And the onboard of B is KO

  Scenario: A transaction can still be authorized even if a suspended citizen tried to pre-authorize it
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the citizen B is 25 years old at most
    And the citizen B is onboard
    And the institution suspends correctly the citizen A
    And the merchant 1 generates the transaction X of amount 100 cents
    And the citizen A tries to pre-authorize the transaction X
    When the citizen B confirms the transaction X
    Then the transaction X is authorized
    And the citizen B is rewarded with 1 euros
