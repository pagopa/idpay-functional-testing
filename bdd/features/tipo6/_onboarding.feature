Feature: A citizen A onboards the pilot initiative

  Background:
    Given the initiative is "Scontoditipo6"
    And the merchant 1 is qualified

  @onboarding
  @Scontoditipo6
  Scenario: User under the minimum age tries onboarding unsuccessfully
    Given the citizen A is 18 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is KO

  @onboarding
  @Scontoditipo6
  Scenario: User just 19 tries onboarding unsuccessfully
    Given the citizen A is 19 years old exactly
    When the citizen A tries to onboard
    Then the onboard of A is KO

  @onboarding
  @Scontoditipo6
  Scenario: User over the maximum age tries onboarding successfully
    Given the citizen A is 20 years old at most
    When the citizen A tries to onboard
    Then the onboard of A is OK
