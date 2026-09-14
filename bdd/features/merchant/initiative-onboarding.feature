@merchant
Feature: Merchant onboards an initiative

  #TODO: set ateco code on initiative
  #TODO: which initiative to use?
  #TODO: test token policy

  Background:
    Given the initiative is "bonus_elettrodomestici"

  Scenario: Eligible merchant tries to onboard successfully
    Given merchant A login through Self-Care
    And merchant A isn't onboarded on bonus_elettrodomestici
    And merchant A has ATECO code 11.11.11
    When merchant A tries to onboard the initiative bonus_elettrodomestici
    Then the onboarding attempt of merchant A is successfull

  Scenario: Merchant without eligible ATECO tries to onboard unsuccessfully
    Given merchant A login through Self-Care
    And merchant A isn't onboarded on bonus_elettrodomestici
    And merchant A has ATECO code 22.22.22
    When merchant A tries to onboard the initiative bonus_elettrodomestici
    Then the onboarding attempt of merchant A fails because not eligible

  Scenario: Eligible merchant already onboarded tries to onboard unsuccessfully
    Given merchant A login through Self-Care
    And merchant A isn't onboarded on bonus_elettrodomestici
    And merchant A has ATECO code 11.11.11
    And merchant A has onboarded initiative bonus_elettrodomestici
    When merchant A tries to onboard the initiative bonus_elettrodomestici
    Then the onboarding attempt of merchant A fails because already onboarded
