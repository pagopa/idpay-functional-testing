@discount_idpay_code
@transaction
Feature: A citizen can pay with IDPay Code on a discount initiative

    Background:
        Given the initiative is "discount_idpay_code"
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    Scenario: A citizen pays with IDPay Code by inserting the correct code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        Then the transaction X is being authorized

    Scenario: A citizen tries to pay with IDPay Code inserting the old code after regenerating it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A regenerates the IDPay Code
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code incorrectly inserted by citizen A
        Then the latest authorization fails because the IDPay Code is incorrect

    Scenario: A citizen tries to pay with IDPay Code inserting the new code after regenerating it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A regenerates the IDPay Code
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        Then the transaction X is being authorized

    Scenario: A citizen tries to pay with IDPay Code without having enabled the code on initiative
        Given the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 tries to pre-authorize the transaction X with IDPay Code
        Then the transaction X is being not authorized for ##########

    Scenario: A citizen tries to pay with IDPay Code a transaction that already authorized by another citizen
        Given the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        And the citizen B has fiscal code random
        And the citizen B is onboard
        When the MinInt tries to associate the transaction X with the citizen B by IDPay Code
        Then the latest association by MinInt fails because the transaction X is already authorized

    @suspension
    Scenario: A suspended citizen tries to pay with IDPay Code
        Given the institution suspends correctly the citizen A
        And the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        When the MinInt tries to associate the transaction X with the citizen A by IDPay Code
        Then the latest association by MinInt fails because citizen A is suspended

    Scenario: A readmitted citizen pays with IDPay Code by inserting the correct code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the institution suspends correctly the citizen A
        And the institution readmits correctly the citizen A
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        Then the transaction X is being authorized

    @unsubscribed
    Scenario: An unsubscribed citizen tries to pay with IDPay Code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A is unsubscribed
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        When the MinInt tries to associate the transaction X with the citizen A by IDPay Code
        Then the latest association by MinInt fails because citizen A is unsubscribed

    Scenario: A citizen tries to pay with IDPay Code but the transaction is expired
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the transaction X does not exists
        When the MinInt tries to associate the transaction X with the citizen A by IDPay Code
        Then the latest association by MinInt fails because the transaction X is expired

    Scenario: A citizen tries to pay with IDPay Code having exhausted the budget on the initiative
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the citizen A pre-authorizes and authorizes the transaction X with IDPay Code correctly
        And the transaction X is being authorized
        And the merchant 1 generates the transaction Y of amount 10000 cents through MIL (new)
        And the MinInt associates the transaction Y with the citizen A by IDPay Code
        When the merchant 1 tries to pre-authorize the transaction Y with IDPay Code
        Then the transaction Y is being not authorized for budget eroded

    Scenario: A citizen tries to pay with IDPay Code a second transaction by exhausting the budget
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 20000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the citizen A pre-authorizes and authorizes the transaction X with IDPay Code correctly
        And the transaction X is being authorized
        And the merchant 1 generates the transaction Y of amount 20000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 tries to pre-authorize the transaction Y with IDPay Code
        Then the transaction Y is being authorized
