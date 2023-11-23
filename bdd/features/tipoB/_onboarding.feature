@ScontoditipoB
@onboarding
Feature: A citizen onboards the pilot initiative with ISEE criteria

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

  Scenario: Citizen over the minimum ISEE ORDINARIO tries onboarding successfully
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 20001 of type "ordinario"
    When the citizen A tries to onboard
    Then the onboard of A is OK

  Scenario: Citizen over the minimum ISEE but the wrong type tries onboarding unsuccessfully
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 20001 of type "minorenne"
    When the citizen A tries to onboard
    Then the onboard of A is KO

  Scenario: Citizen under the minimum ISEE tries to onboard again after being already KO for unsatisfied requirements
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 19999.99 of type "ordinario"
    And the citizen A tries to onboard
    And the onboard of A is KO
    When the citizen A tries to accept terms and conditions again
    Then the latest accept terms and conditions failed for unsatisfied requirements
