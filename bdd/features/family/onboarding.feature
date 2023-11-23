@family_initiative
@family_allocated_initiative
@family
@onboarding
Feature: A family onboards on discount initiative

  Scenario Outline: One member of a family onboards an initiative
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 19999 of type "ordinario"
    When the first citizen of <family members> onboards
    Then the onboard of A is OK
    And the onboards of <demanded citizens> are demanded

    Examples: Family members
      | family members | demanded citizens |
      | A B C          | B C               |

  Scenario Outline: One member of a family tries to onboard an initiative with ISEE greater than allowed
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 20001 of type "ordinario"
    When the first citizen of <family members> onboards
    Then the onboards of <family members> are KO

    Examples: Family members
      | family members |
      | A B C          |

  Scenario Outline: One member of a family tries to onboard an initiative with ISEE equal to the not allowable limit
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 20000 of type "ordinario"
    When the first citizen of <family members> onboards
    Then the onboards of <family members> are KO

    Examples: Family members
      | family members |
      | A B C          |

  Scenario Outline: Only a few family are eligible for the initiative because of the budget
    Given the initiative is "family_allocated_initiative"
    And citizens <family members 1> have fiscal code random
    And citizens <family members 1> are in the same family
    And citizens <family members 1> have ISEE 19999 of type "ordinario"
    When the first citizen of <family members 1> onboards
    Then the onboard of A is OK
    And the onboard of B is demanded
    Given citizens <family members 2> have fiscal code random
    And citizens <family members 2> are in the same family
    And citizens <family members 2> have ISEE 19999 of type "ordinario"
    When the first citizen of <family members 2> onboards
    Then the onboard of C is OK
    And the onboard of D is demanded
    Given citizens <family members 3> have fiscal code random
    And citizens <family members 3> are in the same family
    And citizens <family members 3> have ISEE 19999 of type "ordinario"
    When the citizen E tries to accept terms and conditions
    Then the latest accept terms and conditions failed for budget terminated

    Examples: Family members
      | family members 1 | family members 2 | family members 3 |
      | A B              | C D              | E F              |

  Scenario Outline: One member of a family who denied PDND consent tries onboarding unsuccessfully
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 19999 of type "ordinario"
    And the citizen A accepts terms and conditions
    When the citizen A tries to save PDND consent not correctly
    Then the latest saving of consent failed because the consent was denied by the citizen
    And the onboard of A is KO

    Examples: Family members
      | family members |
      | A B C          |

  Scenario Outline: One member of a family onboards when demanded by another member on initiative
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 19999 of type "ordinario"
    And the first citizen of <family members> onboards
    And the onboard of A is OK
    And the onboards of <demanded citizens> are demanded
    When the demanded family member B onboards
    Then the onboard of B is OK after demanded

    Examples: Family members
      | family members | demanded citizens |
      | A B C          | B C               |

  @suspension
  Scenario Outline: One member of a family is suspended from an initiative
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 19999 of type "ordinario"
    And the first citizen of <family members> onboards
    And the onboard of A is OK
    And the demanded family member B onboards
    And the onboard of C is demanded
    When the institution suspends the citizen A
    Then the onboard of A is suspended
    And the onboard of B is OK after demanded
    And the onboard of C is demanded

    Examples: Family members
      | family members |
      | A B C          |

  @readmission
  Scenario Outline: One member of a family is readmitted from an initiative
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 19999 of type "ordinario"
    And the first citizen of <family members> onboards
    And the onboard of A is OK
    And the demanded family member B onboards
    And the onboard of C is demanded
    And the institution suspends correctly the citizen A
    When the institution tries to readmit the citizen A
    Then the onboard of A is readmitted
    And the onboard of B is OK after demanded
    And the onboard of C is demanded

    Examples: Family members
      | family members |
      | A B C          |

  @unsubscribe
  Scenario Outline: One member of a family unsubscribes from an initiative
    Given the initiative is "family_initiative"
    And citizens <family members> have fiscal code random
    And citizens <family members> are in the same family
    And citizens <family members> have ISEE 19999 of type "ordinario"
    And the first citizen of <family members> onboards
    And the onboard of A is OK
    And the demanded family member B onboards
    And the onboard of C is demanded
    When the citizen A tries to unsubscribe
    Then the onboard of A is unsubscribed
    And the onboard of B is OK after demanded
    And the onboard of C is demanded

    Examples: Family members
      | family members |
      | A B C          |
