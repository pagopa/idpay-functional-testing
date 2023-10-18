@discount_idpay_code
@transaction
Feature: A citizen can pay with IDPay Code on a discount initiative

    Background:
        Given the initiative id is "652e886882b08d1934cd751c" ("discount_idpay_code")
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    Scenario: A citizen pays with IDPay Code by inserting the correct code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        Then the transaction X with IDPay Code is authorized

    Scenario: A citizen tries to pay with IDPay Code inserting the old code after regenerating it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A regenerates the IDPay Code
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code incorrectly inserted by citizen A
        Then the latest authorization by IDPay Code fails because it is incorrect

    Scenario: A citizen tries to pay with IDPay Code inserting the new code after regenerating it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A regenerates the IDPay Code
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        Then the transaction X with IDPay Code is authorized

    Scenario: A citizen tries to pay with IDPay Code without having enabled the code on initiative
        Given the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 tries to pre-authorize the transaction X with IDPay Code
        Then the transaction X with IDPay Code is not authorized for IDPay Code not enabled

    Scenario: A citizen tries to pay with IDPay Code a transaction that already assigned to another citizen
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        And the citizen B has fiscal code random
        And the citizen B is onboard
        And the citizen B enrolls correctly a new IDPay Code on the initiative
        When the MinInt tries to associate the transaction X with the citizen B by IDPay Code
        Then the latest association by MinInt fails because the transaction X is already assigned

    @suspension
    Scenario: A suspended citizen tries to pay with IDPay Code
        Given the institution suspends correctly the citizen A
        And the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        When the MinInt tries to associate the transaction X with the citizen A by IDPay Code
        Then the latest association by MinInt fails because the citizen is suspended

    Scenario: A readmitted citizen pays with IDPay Code by inserting the correct code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the institution suspends correctly the citizen A
        And the institution readmits correctly the citizen A
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        Then the transaction X with IDPay Code is authorized

    @unsubscribe
    @skip
    Scenario: An unsubscribed citizen tries to pay with IDPay Code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A is unsubscribed
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        When the MinInt tries to associate the transaction X with the citizen A by IDPay Code
        Then the latest association by MinInt fails because the citizen is unsubscribed

    Scenario: A citizen tries to pay with IDPay Code but the transaction is not found
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the transaction X does not exists
        When the MinInt tries to associate the transaction X with the citizen A by IDPay Code
        Then the latest association by MinInt fails because the transaction X is not found

    Scenario: A citizen tries to pay with IDPay Code but the transaction is already rejected
        Given the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the merchant 1 tries to pre-authorize the transaction X with IDPay Code
        And the transaction X with IDPay Code is not authorized for IDPay Code not enabled
        And the citizen A enrolls correctly a new IDPay Code on the initiative
        When the MinInt tries to associate the transaction X with the citizen A by IDPay Code
        Then the latest association by MinInt fails because the transaction X is already rejected