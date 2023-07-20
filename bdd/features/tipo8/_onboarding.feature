Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo8"

  @onboarding
  @Scontoditipo8
  Scenario: User over the maximum age tries onboarding
    Given the citizen A is 35 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is KO

  @onboarding
  @Scontoditipo8
  Scenario: User just 30 tries onboarding
    Given the citizen A is 30 years old exactly
    When the citizen A tries to onboard
    Then the onboard of A is OK

  @onboarding
  @Scontoditipo8
  Scenario: User under the maximum age tries onboarding
    Given the citizen A is 25 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is OK
