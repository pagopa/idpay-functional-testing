@onboarding
@whitelist
Feature: A citizen onboards on initiative with whitelist

  Background:
    Given citizens A B C D E have fiscal code random
    And citizens A B C D E are included in the whitelist
    And a new whitelist initiative "discount_whitelist"

  Scenario: A citizen who was invited on initiative tries to onboard successfully
    Given citizens A B C D E are invited on this initiative
    When the citizen A onboards on whitelist initiative
    Then the onboard of A is OK

  Scenario: A citizen who was not invited on initiative tries to onboard unsuccessfully
    Given citizen F has fiscal code random
    When the citizen F tries to onboard on whitelist initiative
    Then the latest check of prerequisites failed because the citizen is not in whitelist
    And the onboard of F is KO
