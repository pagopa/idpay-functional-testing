@Scontoditipo1
@Scontoditipo1_enrollment_cie
Feature: A citizen can enroll a electronic identity card (CIE) to an initiative

    Background:
        Given the initiative is "Scontoditipo1_enrollment_cie"
        And the citizen A is 25 years old at most
        And the citizen A is onboard

    Scenario: An onboarded citizen enrolls the CIE for the first time on this initiative
        Given the idpay_code is not enabled for citizen A
        When the citizen A enrolls the CIE
        Then the instrument CIE is in active status for citizen A on initiative

    Scenario: An onboarded citizen enables the CIE on this initiative having already generated the idpay code
        Given the citizen A generates the idpay code
        And the idpay_code is enabled for citizen A
        When the citizen A enables the CIE
        Then the instrument CIE is in active status for citizen A on initiative

    Scenario: An onboarded citizen tries to enable the CIE on this initiative not having already generated the idpay code
        Given the idpay_code is not enabled for citizen A
        When the citizen A tries to enable the CIE
        Then the latest CIE enabling fails because the code is missing
        And the instrument CIE is in rejected add status for citizen A on initiative

    Scenario: A citizen not onboarded on this initiative tries to enroll the CIE
        Given the citizen B is 30 years old at most
        And the citizen B is not onboard
        When the citizen B tries to enroll the CIE
        Then the latest CIE enrollment fails because the citizen is not onboard

    Scenario: An unsubscribed citizen on this initiative tries to enroll the CIE
        Given the citizen A is unsubscribed
        When the citizen A tries to enroll the CIE
        Then the latest CIE enrollment fails because the citizen is unsubscribed

    Scenario: An onboarded citizen tries to disable the CIE, after enabling it
        Given the citizen A enrolls the CIE
        When the citizen A disables the CIE
        Then the instrument CIE is in deleted status for citizen A on initiative

    Scenario: An onboarded citizen tries to enroll again the CIE, after disabling it
        Given the citizen A enrolls the CIE
        And the citizen A disables the CIE
        And the instrument CIE is in deleted status for citizen A on initiative
        When the citizen A tries to enable the CIE
        Then the instrument CIE is in active again status for citizen A on initiative

    #@skip @not_testable
    #Scenario: An onboarded citizen tries to disable the CIE, without enabling it
    #    When the citizen A tries to disable the CIE
    #    Then the latest CIE deactivation fails because the instrument is not active
    #    And the instrument CIE is in rejected delete status for citizen A on initiative
