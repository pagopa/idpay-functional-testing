@Scontoditipo5
@onboarding
Feature: Transaction on an adhesion-closed initiative

  Background:
    Given the initiative is "Scontoditipo5"

  Scenario: A transaction can be generated after the end of the onboarding period
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 1000 cents
    Then the transaction X is created
