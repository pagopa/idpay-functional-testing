Feature: A transaction can be cancelled by the merchant

  Background:
    Given the initiative is "Scontoditipo1"
    And the merchant 1 is qualified
    And the citizen A is 25 years old at most
    And the citizen A is onboard

  @cancellation
  @Scontoditipo1
  Scenario: After a cancellation request the transaction X is cancelled
    Given the merchant 1 generates the transaction X of amount 15000 cents
    When the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  @cancellation
  @Scontoditipo1
  Scenario: After a cancellation request the trasaction X is cancelled
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms the transaction X
    Then the citizen A is rewarded accordingly
    When 1 second/s pass
    And the merchant 1 cancels the transaction X
    Then the transaction X is cancelled
    And the citizen A has its transaction cancelled

  @cancellation
  @Scontoditipo1
  Scenario: The transaction cancellation fails if done shortly after the confirmation
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms the transaction X
    When the merchant 1 tries to cancel the transaction X
    Then the latest cancellation fails

  @cancellation
  @Scontoditipo1
  Scenario: The transaction cancellation fails if done shortly after the confirmation but can be cancelled later
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms the transaction X
    And the merchant 1 fails cancelling the transaction X
    When 1 second/s pass
    And the merchant 1 cancels the transaction X
    Then the transaction X is cancelled

  @cancellation
  @Scontoditipo1
  Scenario: An authorized and cancelled transaction X cannot be pre-authorised
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the merchant 1 cancels the transaction X
    When the citizen A tries to confirm the transaction X
    Then the transaction X is cancelled

  @cancellation
  @Scontoditipo1
  Scenario: After the eroded budget, if the merchant cancels the last transaction the citizen can make another transaction
    Given the merchant 1 generates the transaction X of amount 30000 cents
    And the citizen A confirms the transaction X
    And 1 second/s pass
    And the merchant 1 cancels the transaction X
    And the merchant 1 generates the transaction Y of amount 15000 cents
    When the citizen A confirms the transaction Y
    Then the transaction Y is authorized

  @cancellation
  @Scontoditipo1
  Scenario: the merchant requests cancellation for 10 transactions of amount 1500 cents each
    Given the merchant 1 generated 10 transactions of amount 1500 cents each
    And the citizen A confirms each transaction
    And 1 second/s pass
    When the merchant 1 cancels every transaction
    Then every transaction is cancelled
