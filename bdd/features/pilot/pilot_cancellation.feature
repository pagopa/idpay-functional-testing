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

  @cancellation
  @Scontoditipo1
  @skip
  Scenario: The transaction cancellation fails if done shortly after the confirmation
    Given the merchant 1 generates the transaction X of amount 15000 cents
    And the citizen A confirms the transaction X
    When the merchant 1 cancels the transaction X
    Then the transaction X is cancelled
