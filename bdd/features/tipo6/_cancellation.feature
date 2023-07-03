Feature: A transaction can be cancelled by the merchant

  Background:
    Given the initiative is "Scontoditipo6"
    And the citizen A is onboarded
    And the citizen B is onboarded
    And the user can only authorize one transaction

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: after a cancellation request the transaction X is cancelled
    Given the merchant generates a transaction X of amount 1000 cents
    When the merchant cancels the transaction X
    Then the cancellation is OK

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: after a cancellation request the transaction X is cancelled
    Given the merchant generates a transaction X of amount 1050 cents
    And the citizen A confirms the transaction X
    When the merchant cancels the transaction X
    Then the cancellation is OK

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: after a cancellation request the transaction X is cancelled
    Given the merchant generates a transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the merchant cancels the transaction X
    And the cancellation is OK
    When the citizen A tries to authorize the transaction X
    Then the transaction X is not authorized

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: after a cancellation by merchant of transaction X before pre-authorisation, if the citizen tries to confirm receives error
    Given the merchant generates a transaction X of amount 1000 cents
    And the citizen A does not pre-authorize the transaction X
    And the merchant cancels the transaction X
    And the cancellation is OK
    When the citizen A tries to pre-authorize the transaction X
    Then the transaction X is not present

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: after a cancellation by merchant of transaction X before authorisation, if the citizen tries to cancel receives error
    Given the merchant generates a transaction X of amount 1000 cents
    And the citizen A pre-authorizes the transaction X
    And the merchant cancels the transaction X
    And the cancellation is OK
    When the citizen A tries to cancel the transaction X
    Then the transaction X is not present

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: after 7 days of authorization, the merchant cannot cancel the transaction
    Given the merchant generates a transaction X of amount 1250 cents
    And the citizen A confirms the transaction X
    When the merchant tries to cancel the transaction X after 7 days
    Then the cancellation is KO

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: an authorized and cancelled transaction cannot be pre-authorized
    Given the merchant generates a transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    And the merchant cancels the transaction X
    And the cancellation is OK
    When the citizen A tries to pre-authorize the transaction X
    Then the transaction X is not present

  @transaction
  @Scontoditipo6
  @skip
  Scenario: if citizen A pre-authorizes and then cancels the transaction, B if he tries to pre-authorize receives OK
    Given the merchant generates the transaction X of amount 1000 cents
    And the citizen A does not confirm the transaction X
    When the citizen B confirms the transaction X
    Then the transaction X is authorized

  @transaction
  @Scontoditipo6
  @skip
  Scenario: if a citizen cancels the pre-authorisation, can after authorizing the trx
    Given the merchant generates the transaction X of amount 1000 cents
    And the citizen A does not confirm the transaction X
    When the citizen A confirms the transaction X
    Then the transaction is authorized

  @cancellation
  @Scontoditipo6
  @skip
  Scenario: if the merchant cancels the last transaction the citizen can make another transaction
    Given the merchant generates the transaction X of amount 1000 cents
    And the citizen A confirms the transaction X
    And the merchant cancels the transaction X
    And the cancellation is OK
    When the merchant generates a transaction Y of amount 1000 cents
    And the citizen A confirms the transaction Y
    Then the transaction Y is authorized
