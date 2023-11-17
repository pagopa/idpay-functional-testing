@whitelist
@suspension
Feature: A citizen can be suspended from an initiative with whitelist

  Scenario Outline: The Institution tries to suspend an invited citizen on initiative with whitelist
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are selected for the initiative with whitelist
    And the initiative with whitelist "discount_whitelist" is published
    And citizens <citizens> are invited on the initiative with whitelist
    When the institution tries to suspend the citizen A
    Then the latest suspension fails because the citizen is not onboarded

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  Scenario Outline: The Institution suspends a citizen on initiative with whitelist
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are selected for the initiative with whitelist
    And the initiative with whitelist "discount_whitelist" is published
    And the citizen A onboards on initiative with whitelist
    And the onboard of A is OK
    When the institution suspends the citizen A
    Then the citizen A is suspended

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |
