@discount_idpay_code
@cancellation
@idpay_code
Feature: A transaction paid by IDPay Code can be cancelled by the merchant

    Background:
        Given the initiative is "discount_idpay_code"
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    Scenario: The merchant cancels a transaction paid by IDPay Code after authorizing it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        And the citizen A enters the IDPay Code correctly to pay the transaction X
        And with IDPay Code the transaction X is authorized
        And the citizen A is rewarded with 300 euros
        And 1 second/s pass
        When the merchant 1 cancels the transaction X through MIL
        Then with IDPay Code the transaction X is cancelled
        And the citizen A is rewarded with 0 euros

    Scenario: The merchant tries to cancel a transaction paid by IDPay Code after it has been confirmed
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        And the citizen A enters the IDPay Code correctly to pay the transaction X
        And with IDPay Code the transaction X is authorized
        And the batch process confirms the transaction X
        When the merchant 1 tries to cancel the transaction X through MIL
        Then the latest cancellation by merchant through MIL fails because the transaction is not found

    Scenario: The merchant cancels a transaction paid by IDPay Code after pre-authorizing it
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        When the merchant 1 cancels the transaction X through MIL
        Then with IDPay Code the transaction X is cancelled