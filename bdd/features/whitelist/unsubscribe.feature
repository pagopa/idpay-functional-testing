@whitelist
@unsubscribe
Feature: A citizen can unsubscribe from a whitelist initiative

  Scenario Outline: The Institution tries to suspend an invited citizen on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    When the institution tries to suspend the citizen A
    Then the latest suspension fails not finding the citizen

    Examples: Citizens in whitelist
      | citizens    |
      | A B C D E F |

  Scenario Outline: The Institution suspends a citizen on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And the citizen A onboards on whitelist initiative
    When the institution suspends the citizen A
    Then the citizen A is suspended

    Examples: Citizens in whitelist
      | citizens    |
      | A B C D E F |
