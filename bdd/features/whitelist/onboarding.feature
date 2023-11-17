@whitelist
@onboarding
Feature: A citizen onboards on initiative with whitelist

  Scenario Outline: An invited citizen tries to onboard successfully on initiative with whitelist
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are selected for the initiative with whitelist
    And the initiative with whitelist "discount_whitelist" is published
    And citizens <citizens> are invited on the initiative with whitelist
    When the citizen A onboards on initiative with whitelist
    Then the onboard of A is OK

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  Scenario Outline: An uninvited citizen tries to onboard unsuccessfully on initiative with whitelist
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are selected for the initiative with whitelist
    And the initiative with whitelist "discount_whitelist" is published
    And the citizen G has fiscal code random
    When the citizen G tries to onboard on initiative with whitelist
    Then the latest check of prerequisites failed because the citizen is not in whitelist
    And the onboard of G is KO

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  #@Discount_whitelist_closed
  #Scenario: An invited citizen tries to onboard when the adhesion period ended on initiative with whitelist
  #  Given the initiative is "Discount_whitelist_closed"
  #  When the invited citizen tries to onboard on initiative with whitelist
  #  Then the latest accept terms and conditions failed for onboarding period ended
