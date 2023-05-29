Feature: A Citizen onboards the pilot initiative

  Background:
    Given the initiative is "pilot"

  @onboarding
  @pilot
  Scenario: User under the minimum age tries onboarding
    Given the citizen is 17 years old at most
    When the citizen tries to onboard
    Then the onboard is KO

  @onboarding
  @pilot
  @need_fix
  Scenario: User just 18 tries onboarding
    Given the citizen is 18 years old exactly
    When the citizen tries to onboard
    Then the onboard is OK

  @onboarding
  @pilot
  Scenario: User over the maximum age tries onboarding
    Given the citizen is 36 years old at most
    When the citizen tries to onboard
    Then the onboard is KO

  @onboarding
  @pilot
  @need_fix
  Scenario: User over the maximum age tries onboarding
    Given the citizen is 36 years old tomorrow
    When the citizen tries to onboard
    Then the onboard is OK

  @onboarding
  @pilot
  @need_fix
  Scenario: User with self-declared incorrect criteria tries onboarding
    Given the citizen is 23 years old at most
    And the citizen accepts terms and condition
    When the citizen insert self-declared criteria not correctly
    Then the onboard is KO

  @onboarding
  @pilot
  @need_fix
  Scenario: User under minimum age and with incorrect self-declared criteria tries onboarding
    Given the citizen is 17 years old at most
    And the citizen accepts terms and condition
    When the citizen insert self-declared criteria not correctly
    Then the onboard is KO

  @onboarding
  @pilot
  Scenario: User over the maximum age and with incorrect self-declared criteria tries onboarding
    Given the citizen is 36 years old at most
    And the citizen accepts terms and condition
    When the citizen insert self-declared criteria not correctly
    Then the onboard is pending

  @onboarding
  @pilot
  @need_fix
  Scenario: user onboarded tries to onboard again
    Given the citizen is 23 years old at most
    And the citizen onboarded
    When the citizen tries to onboard
    Then the onboard is KO
