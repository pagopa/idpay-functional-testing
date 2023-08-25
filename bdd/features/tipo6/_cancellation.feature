@Scontoditipo6
@cancellation
Feature: A transaction can be cancelled by the merchant 1

  Background:
    Given the initiative is "Scontoditipo6"
    And the random merchant 1 is onboard
    And the citizen A is 20 years old at most
    And the citizen A is onboarded

  Scenario: After a cancellation request the transaction is cancelled
    Given the merchant 1 generates the transaction X of amount 1000 cents
    When the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  Scenario: After a cancellation request the transaction is cancelled even if the transaction is confirmed
    Given the merchant 1 generates the transaction X of amount 1050 cents
    And the citizen A confirms the transaction X
    When the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  Scenario: After a cancellation of a pre-authorized transaction is cancelled and cannot be authorized
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to authorize the transaction X
    Then the latest authorization fails because the transaction no longer exists

  Scenario: After a cancellation by merchant a transaction before pre-authorization, if the citizen tries to confirm receives error
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the transaction no longer exists

  Scenario: After a cancellation by merchant of a transaction before authorization, if the citizen tries to cancel receives error
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to cancel the transaction X
    Then the latest cancellation by citizen fails because the transaction no longer exists

  @skip
  Scenario: After 7 days of authorization, the merchant cannot cancel the transaction
    Given the merchant 1 generates the transaction X of amount 1250 cents
    And the citizen A confirms the transaction X
    When the merchant 1 tries to cancel the transaction X after 7 days
    Then the latest cancellation fails

  Scenario: An authorized and cancelled transaction cannot be pre-authorized
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the transaction no longer exists

  Scenario: If a citizen pre-authorizes and then cancels the transaction, another citizen receives an error if he tries to pre-authorize
    Given the citizen B is 20 years old at most
    And the citizen B is onboarded
    And the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A cancels the transaction X
    When the citizen B confirms the transaction X
    Then the transaction X is authorized

  Scenario: If a citizen cancels a pre-authorized transaction, can after authorizing the trx
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A cancels the transaction X
    When the citizen A confirms the transaction X
    Then the transaction X is authorized

  Scenario: If the merchant cancels the last transaction the citizen can make another transaction
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the merchant 1 generates the transaction Y of amount 1000 cents
    And the citizen A confirms the transaction Y
    Then the transaction Y is authorized
