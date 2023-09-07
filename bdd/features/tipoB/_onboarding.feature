@ScontoditipoB
@onboarding
Feature: A citizen A onboards the pilot initiative with ISEE criteria

  Background:
    Given the initiative is "ScontoditipoB"

  Scenario: Citizen under the minimum ISEE ORDINARIO tries onboarding and fails
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 19999.99 of type "ordinario"
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: The citizen with an ISEE ORDINARIO equal to the threshold tries onboarding and fails
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 20000 of type "ordinario"
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: Citizen under the minimum ISEE ORDINARIO tries onboarding successfully
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 20001 of type "ordinario"
    When the citizen A tries to onboard
    Then the onboard of A is OK
