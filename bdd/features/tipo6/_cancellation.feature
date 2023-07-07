Feature: A transaction can be cancelled by the merchant 1

  Background:
    Given the initiative is "Scontoditipo6"
    And the merchant 1 is qualified
    And the citizen A is 20 years old at most
    And the citizen A is onboarded

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: After a cancellation request the transaction X is cancelled
    Given the merchant 1 generates a transaction X of amount 1000 cents
    When the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: After a cancellation request the transaction X is cancelled
    Given the merchant 1 generates a transaction X of amount 1050 cents
    And the citizen A confirms the transaction X
    When the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: After a cancellation request the transaction X is cancelled
    Given the merchant 1 generates a transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to authorize the transaction X
    Then the latest authorization fails

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: After a cancellation by merchant of transaction X before pre-authorisation, if the citizen tries to confirm receives error
    Given the merchant 1 generates a transaction X of amount 1000 cents
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: After a cancellation by merchant of transaction X before authorisation, if the citizen tries to cancel receives error
    Given the merchant 1 generates a transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to cancel the transaction X
    Then the latest cancellation by citizen fails

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: After 7 days of authorization, the merchant 1 cannot cancel the transaction
    Given the merchant 1 generates a transaction X of amount 1250 cents
    And the citizen A confirms the transaction X
    When the merchant 1 tries to cancel the transaction X after 7 days
    Then the latest cancellation fails

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: An authorized and cancelled transaction cannot be pre-authorized
    Given the merchant 1 generates a transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails

  @transaction
  @Scontoditipo6
  @skip
  Scenario: If citizen A pre-authorizes and then cancels the transaction, B if he tries to pre-authorize receives OK
    Given the citizen B is 20 years old at most
    And the citizen B is onboarded
    And the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A cancels the transaction X
    When the citizen B confirms the transaction X
    Then the transaction X is authorized

  @transaction
  @Scontoditipo6
  @skip
  Scenario: If a citizen cancels the pre-authorisation, can after authorizing the trx
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the citizen A cancels the transaction X
    When the citizen A confirms the transaction X
    Then the transaction is authorized

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: If the merchant 1 cancels the last transaction the citizen can make another transaction
    Given the merchant 1 generates the transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the merchant 1 generates a transaction Y of amount 1000 cents
    And the citizen A confirms the transaction Y
    Then the transaction Y is authorized
