@onboarding
@whitelist
Feature: A citizen onboards on initiative with whitelist

  Scenario:
    Given citizens A B C D E have fiscal code random
    And citizens A B C D E are included in the whitelist
    When a new whitelist initiative "discount_whitelist" is published
    Then citizens A B C D E are invited on this initiative

  Scenario:
    Given the initiative is "discount_whitelist"
    When the citizen A onboards on whitelist initiative
    Then the onboard of A is OK

  Scenario:
    Given the initiative is "discount_whitelist"
    And citizen F has fiscal code random
    When the citizen F tries to onboard on whitelist initiative
    Then the latest check of prerequisites failed because the citizen is not in whitelist
    And the onboard of F is KO
