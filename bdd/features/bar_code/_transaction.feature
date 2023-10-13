@discount_bar_code
@transaction
Feature: A citizen can pay with Bar Code on a discount initiative

    Background:
        Given the initiative is "discount_bar_code"
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    Scenario: An onboarded citizen generates a transaction by Bar Code and merchant authorizes it
        Given the citizen A creates the transaction X by Bar Code
        When the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        Then the payment of transaction X is authorized

    Scenario: The merchant authorizes a transaction that does not exist
        Given the transaction X does not exists
        When the merchant 1 tries to authorize the transaction X by Bar Code of amount 20000 cents
        Then the latest authorization by merchant fails because the transaction X is not found

    Scenario: The merchant authorizes a transaction already authorized
        Given the citizen A creates the transaction X by Bar Code
        And the merchant 1 authorizes the transaction X by Bar Code
        And the payment of transaction X is authorized
        When the merchant 1 tries to authorize the transaction X by Bar Code of amount 20000 cents
        Then the latest authorization by merchant fails because the transaction X is already authorized

    @suspension
    Scenario: A suspended citizen generates a transaction by Bar Code and merchant cannot authorize it
        Given the citizen A creates the transaction X by Bar Code
        And the institution suspends correctly the citizen A
        When the merchant 1 tries to authorize the transaction X by Bar Code of amount 20000 cents
        Then the latest authorization by merchant fails because the citizen A is suspended

    @unsubscribe
    Scenario: An unsubscribed citizen tries to generate a transaction by Bar Code
        Given the citizen A creates the transaction X by Bar Code
        And the institution suspends correctly the citizen A
        When the merchant 1 tries to authorize the transaction X by Bar Code of amount 20000 cents
        Then the latest authorization by merchant fails because the citizen A is unsubscribed

    Scenario: A readmitted citizen generates a transaction by Bar Code and merchant authorizes it
        Given the citizen A creates the transaction X by Bar Code
        And the institution suspends correctly the citizen A
        And the institution readmits correctly the citizen A
        When the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        Then the payment of transaction X is authorized

    Scenario: An onboarded citizen generates a transaction by Bar Code but the budget is exhausted
        Given the citizen A creates the transaction X by Bar Code
        And the merchant 1 authorizes the transaction X by Bar Code of amount 30000 cents
        And the payment of transaction X is authorized
        And the citizen A creates the transaction Y by Bar Code
        When the merchant 1 tries to authorize the transaction Y by Bar Code of amount 20000 cents
        Then the latest authorization by merchant fails because the budget is exhausted
