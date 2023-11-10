@discount_idpay_code
@refunds
@idpay_code
Feature: A citizen can be rewarded and the merchant can be refunded about a transaction by IDPay Code

    Background:
        Given the initiative is "discount_idpay_code"
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard
        And the citizen A enrolls correctly a new IDPay Code on the initiative

    @budget
    Scenario: A citizen tries to pay by IDPay Code having exhausted the budget on the initiative
        Given the citizen A's budget is eroded
        And the batch process confirms the transaction that eroded the budget
        And the merchant 1 generates the transaction Y of amount 10000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction Y
        When the payment by IDPay Code of transaction Y is about to be pre-authorized
        Then the latest pre-authorization by IDPay Code fails because the budget is exhausted
        When the institution refunds the merchant 1 of 300 euros successfully
        Then the merchant 1 is refunded 300 euros

    Scenario: A citizen tries to pay by IDPay Code a second transaction by exhausting the budget
        Given the merchant 1 generates the transaction X of amount 20000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        And the citizen A enters the IDPay Code correctly to pay the transaction X
        And with IDPay Code the transaction X is authorized
        And the citizen A is rewarded with 200 euros
        And the merchant 1 generates the transaction Y of amount 20000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction Y
        And the payment by IDPay Code of transaction Y is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction Y
        Then with IDPay Code the transaction Y is authorized
        And the citizen A is rewarded with 300 euros
        Given the batch process confirms the transaction X
        And the batch process confirms the transaction Y
        When the institution refunds the merchant 1 of 300 euros successfully
        Then the merchant 1 is refunded 300 euros
