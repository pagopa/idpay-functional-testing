@Scontoditipo1
@cancellation
Feature: A transaction can be cancelled by the merchant

  Background:
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  Scenario: After a cancellation request the transaction X is cancelled
    Given the merchant 1 generates the transaction X of amount 15000 cents
    When the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  @MIL
  Scenario: After a cancellation request the transaction X is cancelled through MIL
    Given the merchant 1 generates the transaction X of amount 15000 cents through MIL
    When the merchant 1 cancels the transaction X through MIL
    Then the transaction X is cancelled

  Scenario: After a cancellation request the transaction X is cancelled after being confirmed by the citizen
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms the transaction X
    Then the citizen A is rewarded with 150 euros
    When 1 second/s pass
    And the merchant 1 cancels the transaction X
    Then the transaction X is cancelled
    And the citizen A has its transaction cancelled

  @MIL
  Scenario: After a cancellation request the transaction X is cancelled through MIL after being confirmed by the citizen
    Given the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the citizen A confirms the transaction X
    Then the citizen A is rewarded with 150 euros
    When 1 second/s pass
    And the merchant 1 cancels the transaction X through MIL
    Then the transaction X is cancelled
    And the citizen A has its transaction cancelled

  @skip
  Scenario: The transaction cancellation fails if done shortly after the confirmation
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms, immediately before the next step, the transaction X
    When the merchant 1 tries to cancel the transaction X
    Then the latest cancellation fails exceeding rate limit

  @skip
  @MIL
  Scenario: The transaction cancellation through MIL fails if done shortly after the confirmation
    Given the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the citizen A confirms, immediately before the next step, the transaction X
    When the merchant 1 tries to cancel the transaction X through MIL
    Then the latest cancellation fails exceeding rate limit

  @skip
  Scenario: The transaction cancellation fails if done shortly after the confirmation but can be cancelled later
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms, immediately before the next step, the transaction X
    And the merchant 1 fails cancelling the transaction X
    When 1 second/s pass
    And the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  @skip
  @MIL
  Scenario: The transaction cancellation through MIL fails if done shortly after the confirmation but can be cancelled later
    Given the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the citizen A confirms, immediately before the next step, the transaction X
    And the merchant 1 fails cancelling the transaction X through MIL
    When 1 second/s pass
    And the merchant 1 cancels the transaction X through MIL
    Then the transaction X is cancelled

  Scenario: An authorized and cancelled transaction X cannot be pre-authorized
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the merchant 1 cancels the transaction X
    When the citizen A tries to confirm the transaction X
    Then the transaction X is cancelled

  @cancellation
  @MIL
  Scenario: An authorized and cancelled transaction X cannot be pre-authorized through MIL
    Given the random merchant 1 is onboard
    Given the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the merchant 1 cancels the transaction X through MIL
    When the citizen A tries to confirm the transaction X
    Then the transaction X is cancelled

  Scenario: After the eroded budget, if the merchant cancels the last transaction the citizen can make another transaction
    Given the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the merchant 1 cancels the transaction X
    And the merchant 1 generates the transaction Y of amount 15000 cents
    When the citizen A confirms the transaction Y
    Then the transaction Y is authorized

  @MIL
  Scenario: After the eroded budget, if the merchant through MIL cancels the last transaction the citizen can make another transaction
    Given the merchant 1 generates the transaction X of amount 30000 cents through MIL
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the merchant 1 cancels the transaction X through MIL
    And the merchant 1 generates the transaction Y of amount 15000 cents through MIL
    When the citizen A confirms the transaction Y
    Then the transaction Y is authorized

  Scenario: The merchant requests cancellation for 10 transactions of amount 1500 cents each
    Given the merchant 1 generated 10 transactions of amount 1500 cents each
    And the citizen A confirms each transaction
    And 1 second/s pass
    When the merchant 1 cancels every transaction
    Then every transaction is cancelled

  @MIL
  Scenario: The merchant through MIL requests cancellation for 10 transactions of amount 1500 cents each
    Given the merchant 1 generated 10 transactions of amount 1500 cents each through MIL
    And the citizen A confirms each transaction
    And 1 second/s pass
    When the merchant 1 cancels every transaction through MIL
    Then every transaction is cancelled

  Scenario: Before pre-authorization, after a cancellation request the transaction is cancelled and cannot be pre-authorized
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the merchant 1 cancels the transaction X
    And the transaction X is cancelled
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the transaction cannot be found

  @MIL
  Scenario: Before pre-authorization, after a cancellation request the transaction, created through MIL, is cancelled and cannot be pre-authorized
    Given the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the merchant 1 cancels the transaction X through MIL
    And the transaction X is cancelled
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the transaction cannot be found

  Scenario: Transaction cancelled before the citizen’s authorization
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A pre-authorizes the transaction X
    And the merchant 1 cancels the transaction X
    When the citizen A tries to authorize the transaction X
    Then the transaction X is cancelled

  @MIL
  Scenario: Transaction, created through MIL, cancelled before the citizen’s authorization
    Given the merchant 1 generates the transaction X of amount 15000 cents through MIL
    And the citizen A pre-authorizes the transaction X
    And the merchant 1 cancels the transaction X through MIL
    When the citizen A tries to authorize the transaction X
    Then the transaction X is cancelled
