@Scontoditipo4
@onboarding
Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo4"

  Scenario: Transaction X is not generated on a closed initiative
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate a transaction X of amount 1000 cents
    Then the transaction X is not generated
