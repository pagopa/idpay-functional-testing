Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo3"

  @Onboarding
  @Scontoditipo3
  Scenario: The citizen tries to onboard when the budget of the initiative is totally allocated
    Given the initiative's budget is totally allocated
    When the citizen A tries to onboard
    Then the onboard of A is KO
  