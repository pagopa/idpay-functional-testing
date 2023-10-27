@discount_bar_code
@cancellation
Feature: A transaction by Bar Code can be cancelled by the merchant

    Background:
        Given the initiative is "discount_bar_code"
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    Scenario: The merchant cancels a transaction after authorizing it
        Given the citizen A creates the transaction X by Bar Code
        And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        And with Bar Code the transaction X is authorized
        And 2 second/s pass
        When the merchant 1 cancels the transaction X
        Then with Bar Code the transaction X is cancelled

    Scenario: The merchant tries to cancel a transaction after it has been confirmed
        Given the citizen A creates the transaction X by Bar Code
        And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        And with Bar Code the transaction X is authorized
        And the batch process confirms the transaction X
        When the merchant 1 tries to cancel the transaction X
        Then the latest cancellation by merchant fails because the transaction is not found
