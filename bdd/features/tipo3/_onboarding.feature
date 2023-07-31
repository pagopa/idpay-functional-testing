Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo3"

  @Onboarding
  @Scontoditipo3
  @to_remove
  Scenario: Onboarding of 4 person
    Given the citizen A is 25 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is OK
    Given the citizen B is 25 years old at most
    When the citizen B tries to onboard
    Then the onboard of B is OK
    Given the citizen C is 25 years old at most
    When the citizen C tries to onboard
    Then the onboard of C is OK
    Given the citizen D is 25 years old at most
    When the citizen D tries to onboard
    Then the onboard of D is OK


  @Onboarding
  @Scontoditipo3
  Scenario: The citizen tries to onboard when the budget of the initiative is totally allocated
    Given the initiative's budget is totally allocated
    When the citizen A tries to onboard
    Then the onboard of A is KO
  