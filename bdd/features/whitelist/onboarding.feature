@whitelist
@onboarding
Feature: A citizen onboards on initiative with whitelist

  Scenario Outline: An invited citizen tries to onboard successfully on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And citizens <citizens> are invited on this initiative
    When the citizen A onboards on whitelist initiative
    Then the onboard of A is OK

    Examples: Citizens in whitelist
      | citizens    |
      | A B C D E F |

  Scenario Outline: An uninvited citizen tries to onboard unsuccessfully on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And the citizen G has fiscal code random
    When the citizen G tries to onboard on whitelist initiative
    Then the latest check of prerequisites failed because the citizen is not in whitelist
    And the onboard of G is KO

    Examples: Citizens in whitelist
      | citizens    |
      | A B C D E F |

  Scenario Outline: An invited citizen tries to onboard when the budget is exhausted on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And the citizen A onboards on whitelist initiative
    And the citizen B onboards on whitelist initiative
    And the citizen C onboards on whitelist initiative
    And the citizen D onboards on whitelist initiative
    And the citizen E onboards on whitelist initiative
    When the citizen F tries to accept terms and conditions
    Then the latest accept terms and conditions failed for budget terminated
    And the onboard of F is KO

    Examples: Citizens in whitelist
      | citizens    |
      | A B C D E F |

  #@discount_whitelist_closed
  #Scenario: An invited citizen tries to onboard when the adhesion period ended on whitelist initiative
  #  Given the initiative is "discount_whitelist_closed"
  #  When the invited citizen tries to onboard on whitelist initiative
  #  Then the latest accept terms and conditions failed for onboarding period ended
