@bonus_elettrodomestici
@bonus_decoder
@merchant_portal
@merchant_onboarding
Feature: Merchant onboards an initiative

  # Note: these tests don't perform the actual login flow (SelfCare + token exchange),
  # but emulate it by directly creating the merchant in DB

  Background:
    Given the initiative is active

  Scenario: Eligible merchant onboards successfully
    Given merchant A login through Self-Care
    And merchant A is not onboarded on the initiative
    And merchant A has ATECO code 47.11.10
    When merchant A tries to onboard the initiative
    Then the onboarding attempt of merchant A is successfull

  Scenario: Merchant without eligible ATECO fails to onboard
    Given merchant A login through Self-Care
    And merchant A is not onboarded on the initiative
    And merchant A has ATECO code 00.00.00
    When merchant A tries to onboard the initiative
    Then the onboarding attempt of merchant A fails because not eligible

  Scenario: Eligible merchant already onboarded fails to onboard
    Given merchant A login through Self-Care
    And merchant A has ATECO code 47.11.10
    And merchant A has onboarded the initiative
    When merchant A tries to onboard the initiative
    Then the onboarding attempt of merchant A fails because already onboarded