@Scontoditipo3
@onboarding
Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo3"
    And the initiative's budget is totally allocated

  Scenario: The citizen tries to onboard when the budget of the initiative is totally allocated
    Given the citizen A is 35 years old at most
    When the citizen A tries to accept terms and conditions
    Then the latest accept terms and conditions failed for budget terminated
    And the onboard of A is KO
