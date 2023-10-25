@family
@family_allocated
@onboarding
Feature: A family onboards an initiative

  Scenario: One member of a family onboards an initiative
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    When the first citizen of A B C onboards
    Then the onboard of A is OK
    And the onboard of B is demanded
    And the onboard of C is demanded


  Scenario: One member of a family tries to onboard an initiative with ISEE greater than allowed
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 20001 of type "ordinario"
    When the first citizen of A B C onboards
    Then the onboard of A is KO
    And the onboard of B is KO
    And the onboard of C is KO


  Scenario: One member of a family tries to onboard an initiative with ISEE equal to the allowable limit
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 20000 of type "ordinario"
    When the first citizen of A B C onboards
    Then the onboard of A is KO
    And the onboard of B is KO
    And the onboard of C is KO
    

  Scenario: Only a few family are eligible for the initiative because of the budget
    Given the initiative is "family_allocated"
    And citizens A B have fiscal code random
    And citizens A B are in the same family
    And citizens A B have ISEE 19999 of type "ordinario"
    When the first citizen of A B onboards
    Then the onboard of A is OK
    And the onboard of B is demanded
    Given citizens C D have fiscal code random
    And citizens C D are in the same family
    And citizens C D have ISEE 19999 of type "ordinario"
    When the first citizen of C D onboards
    Then the onboard of C is OK
    And the onboard of D is demanded
    Given citizens E F have fiscal code random
    And citizens E F are in the same family
    And citizens E F have ISEE 19999 of type "ordinario"
    When the citizen E tries to accept terms and conditions
    Then the latest accept terms and conditions failed for budget terminated
    

  Scenario: One member of a family with self-declared incorrect criteria tries onboarding unsuccessfully
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the citizen A accepts terms and conditions
    When the citizen A insert self-declared criteria not correctly
    Then the onboard of A is KO
    And the onboard of B is KO
    And the onboard of C is KO


  Scenario: One member of a family onboards when demanded by another member on initiative
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the first citizen of A B C onboards
    And the onboard of A is OK
    And the onboard of B is demanded
    And the onboard of C is demanded
    When the demanded family member B onboards
    Then the onboard of B is OK after demanded

  @suspension
  Scenario: One member of a family is suspended from an initiative
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the first citizen of A B C onboards
    And the onboard of A is OK
    And the demanded family member B onboards
    And the onboard of C is demanded
    When the institution suspends the citizen A
    Then the onboard of A is suspended
    And the onboard of B is OK after demanded
    And the onboard of C is demanded

  @readmission
  Scenario: One member of a family is readmitted from an initiative
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the first citizen of A B C onboards
    And the onboard of A is OK
    And the demanded family member B onboards
    And the onboard of C is demanded
    And the institution suspends correctly the citizen A
    When the institution tries to readmit the citizen A
    Then the onboard of A is readmitted
    And the onboard of B is OK after demanded
    And the onboard of C is demanded

  @unsubscribe
  Scenario: One member of a family unsubscribes from an initiative
    Given the initiative is "family"
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    And the first citizen of A B C onboards
    And the onboard of A is OK
    And the demanded family member B onboards
    And the onboard of C is demanded
    When the citizen A tries to unsubscribe
    Then the onboard of A is unsubscribed
    And the onboard of B is OK after demanded
    And the onboard of C is demanded
