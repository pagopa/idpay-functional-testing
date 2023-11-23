@whitelist
@unsubscribe
Feature: A citizen can unsubscribe from an initiative with whitelist

  Scenario Outline: An invited citizen tries to unsubscribe from initiative with whitelist
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are selected for the initiative with whitelist
    And the initiative with whitelist "discount_whitelist" is published
    And citizens <citizens> are invited on the initiative with whitelist
    When the citizen A tries to unsubscribe
    Then the latest unsubscribe is KO because the citizen is not onboarded

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  Scenario Outline: An onboarded citizen unsubscribes from initiative with whitelist
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are selected for the initiative with whitelist
    And the initiative with whitelist "discount_whitelist" is published
    And the citizen A onboards on initiative with whitelist
    And the onboard of A is OK
    When the citizen A unsubscribes
    Then the onboard of A is unsubscribed

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |
