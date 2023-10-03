@IDPayCode
Feature: A citizen can generate the IDPay Code

  Background:
    Given the citizen A is 25 years old at most

  Scenario: A citizen can generate the IDPay Code
    Given the IDPay Code is not enabled for citizen A
    When the citizen A generates the IDPay Code
    Then the IDPay Code is enabled for citizen A

  Scenario: A citizen can regenerate the IDPay Code
    Given the citizen A generates the IDPay Code
    And the IDPay Code is enabled for citizen A
    When the citizen A regenerates the IDPay Code
    Then the IDPay Code is enabled for citizen A
