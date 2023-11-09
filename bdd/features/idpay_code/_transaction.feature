@discount_idpay_code
@transaction
@idpay_code
Feature: A citizen can pay by IDPay Code on a discount initiative

    Background:
        Given the initiative is "discount_idpay_code"
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    Scenario: A citizen pays by IDPay Code by entering the correct code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        Then with IDPay Code the transaction X is authorized

    Scenario: A citizen tries to pay by IDPay Code entering the old code after regenerating it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A regenerates the IDPay Code
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        When the citizen A enters the IDPay Code incorrectly to pay the transaction X
        Then the latest authorization by IDPay Code fails because the pin is incorrect

    Scenario: A citizen tries to pay by IDPay Code inserting the new code after regenerating it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A regenerates the IDPay Code
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        Then with IDPay Code the transaction X is authorized

    Scenario: A citizen tries to pay by IDPay Code without having enabled the code on initiative
        Given the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        When the payment by IDPay Code of transaction X is about to be pre-authorized
        Then the latest pre-authorization by IDPay Code fails because IDPay Code is not enabled

    Scenario: A citizen tries to pay by IDPay Code a transaction that already assigned to another citizen
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the citizen B has fiscal code random
        And the citizen B is onboard
        And the citizen B enrolls correctly a new IDPay Code on the initiative
        When the citizen B presents the ID card, trying to reclaim the transaction X
        Then the latest citizen reclaim fails because the transaction X is already assigned

    @suspension
    Scenario: A suspended citizen tries to pay by IDPay Code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the institution suspends correctly the citizen A
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        When the citizen A presents the ID card, trying to reclaim the transaction X
        Then the latest citizen reclaim fails because the citizen is suspended

    Scenario: A readmitted citizen pays by IDPay Code by inserting the correct code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the institution suspends correctly the citizen A
        And the institution readmits correctly the citizen A
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        Then with IDPay Code the transaction X is authorized

    @unsubscribe
    Scenario: An unsubscribed citizen tries to pay by IDPay Code
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the citizen A is unsubscribed
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        When the citizen A presents the ID card, trying to reclaim the transaction X
        Then the latest citizen reclaim fails because the citizen is unsubscribed

    Scenario: A citizen tries to pay by IDPay Code but the transaction is not found
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the transaction X does not exists
        When the citizen A presents the ID card, trying to reclaim the transaction X
        Then the latest citizen reclaim fails because the transaction X is not found

    Scenario: A citizen tries to pay by IDPay Code but the transaction is rejected
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        And the citizen A enters the IDPay Code correctly to pay the transaction X
        And with IDPay Code the transaction X is authorized
        And the merchant 1 generates the transaction Y of amount 10000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction Y
        When the payment by IDPay Code of transaction Y is about to be pre-authorized
        Then the latest pre-authorization by IDPay Code fails because the budget is exhausted
        When the citizen A presents the ID card, trying to reclaim the transaction Y
        Then the latest citizen reclaim fails because the transaction Y is rejected

    Scenario: A not onboarded merchant tries to generate a transaction to be paid by IDPay Code
        Given the merchant 2 is not qualified
        When the merchant 2 tries to generate the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        Then the latest transaction creation through MIL fails because the merchant is not qualified

    Scenario: A merchant tries to pre-authorize a transaction, to be paid by IDPay Code, generated by another merchant
        Given the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the random merchant 2 is onboard
        When the payment by IDPay Code of transaction X is about to be pre-authorized by merchant 2
        Then the latest pre-authorization by IDPay Code fails because the merchant is not allowed to operate on this transaction
