@Scontoditipo1
@Scontoditipo1_not_started
@unsubscribe
Feature: A citizen can unsubscribe from an initiative

  Background:
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  Scenario: A citizen onboard tries to unsubscribe and receives OK
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is OK
    And the onboard of A is unsubscribed

  @IDP-1710
  Scenario: An unsubscribed citizen tries to unsubscribe again and receives OK
    Given the citizen A is unsubscribed
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is OK

  Scenario: An unsubscribed citizen tries to onboard and fails
    Given the citizen A is unsubscribed
    When the citizen A tries to accept terms and conditions
    Then the latest accept terms and conditions failed for user unsubscribed
    And the onboard of A is unsubscribed

  Scenario: An unsubscribed citizen tries to authorize a transaction
    Given the citizen A is unsubscribed
    And the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 15000 cents
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is unsubscribed
    And the transaction X is still not identified

  Scenario: An unsubscribed citizen tries to onboard another initiative
    Given the citizen A is unsubscribed
    When the citizen A tries to onboard the initiative Scontoditipo1_not_started
    Then the onboard of A is OK

  @refund
  Scenario: The transaction made before unsubscribing is present in the rewards file
    Given the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 20001 cents
    And the citizen A confirms the transaction X
    And the batch process confirms the transaction X
    And the citizen A is unsubscribed
    When the institution refunds the merchant 1 of 200.01 euros successfully
    Then the merchant 1 is refunded 200.01 euros

  Scenario: A suspended citizen can unsubscribe
    Given the institution suspends the citizen A
    And the citizen A is suspended
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is OK
    And the onboard of A is unsubscribed
