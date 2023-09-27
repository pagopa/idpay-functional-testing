@IdpayCode
Feature: A citizen can generate the idpay code

  Background:
    Given the citizen A is 25 years old at most

  Scenario: A citizen can generate the idpay code
    Given the idpay_code is not enabled for citizen A
    When the citizen A generates the idpay code
    Then the idpay_code is enabled for citizen A

  Scenario: A citizen can regenerate the idpay code
    Given the citizen A generates the idpay code
    And the idpay_code is enabled for citizen A
    When the citizen A regenerates the idpay code
    Then the idpay_code is enabled for citizen A