@whitelist
@suspension
Feature: A citizen can be suspended from a whitelist initiative

  Scenario Outline: The Institution tries to suspend an invited citizen on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And citizens <citizens> are invited on this initiative
    When the institution tries to suspend the citizen A
    Then the latest suspension fails because the citizen is not onboarded yet

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  Scenario Outline: The Institution suspends a citizen on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And the citizen A onboards on whitelist initiative
    And the onboard of A is OK
    When the institution suspends the citizen A
    Then the citizen A is suspended

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |
