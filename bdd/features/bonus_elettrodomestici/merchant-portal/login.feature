@merchant
@login
Feature: Merchant login through Self-Care

  Scenario: Merchant successfully logs in Merchant Portal
    Given merchant successfully logged in SelfCare
    When merchant access Merchant Portal
    Then merchant has been successfully logged in Merchant Portal
