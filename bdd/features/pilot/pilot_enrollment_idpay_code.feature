@enrollment_idpay_code
Feature: A citizen can enroll an IDPay Code to an initiative

    Background:
        Given the initiative is "enrollment_idpay_code"
        And the citizen A has fiscal code random
        And the citizen A is onboard

    Scenario: An onboarded citizen enrolls the IDPay Code for the first time on this initiative
        Given the IDPay Code is not enabled for citizen A
        When the citizen A enrolls the IDPay Code
        Then the instrument IDPay Code is in active status for citizen A on initiative

    Scenario: An onboarded citizen enables the IDPay Code on this initiative having already generated the IDPay Code
        Given the citizen A generates the IDPay Code
        And the IDPay Code is enabled for citizen A
        When the citizen A enables the IDPay Code
        Then the instrument IDPay Code is in active status for citizen A on initiative

    Scenario: An onboarded citizen tries to enable the IDPay Code on this initiative not having already generated the IDPay Code
        Given the IDPay Code is not enabled for citizen A
        When the citizen A tries to enable the IDPay Code
        Then the latest IDPay Code enabling fails because the code is missing
        And the instrument IDPay Code is in rejected add status for citizen A on initiative

    Scenario: A citizen not onboarded on this initiative tries to enroll the IDPay Code
        Given the citizen B has fiscal code random
        And the citizen B is not onboard
        When the citizen B tries to enroll the IDPay Code
        Then the latest IDPay Code enrollment fails because the citizen is not onboard

    Scenario: An unsubscribed citizen on this initiative tries to enroll the IDPay Code
        Given the citizen A is unsubscribed
        When the citizen A tries to enroll the IDPay Code
        Then the latest IDPay Code enrollment fails because the citizen is unsubscribed

    Scenario: An onboarded citizen tries to disable the IDPay Code, after enabling it
        Given the citizen A enrolls the IDPay Code
        When the citizen A disables the IDPay Code
        Then the instrument IDPay Code is in deleted status for citizen A on initiative

    Scenario: An onboarded citizen tries to enroll again the IDPay Code, after disabling it
        Given the citizen A enrolls the IDPay Code
        And the citizen A disables the IDPay Code
        And the instrument IDPay Code is in deleted status for citizen A on initiative
        When the citizen A tries to enable the IDPay Code
        Then the instrument IDPay Code is in active again status for citizen A on initiative

    #@skip @not_testable
    #Scenario: An onboarded citizen tries to disable the IDPay Code, without enabling it
    #    When the citizen A tries to disable the IDPay Code
    #    Then the latest IDPay Code deactivation fails because the instrument is not active
    #    And the instrument IDPay Code is in rejected delete status for citizen A on initiative
