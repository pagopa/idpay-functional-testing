@discount_idpay_code
@transaction
Feature: A citizen can pay by IDPay Code on a discount initiative

    Background:
        Given the initiative id is "652e886882b08d1934cd751c" ("discount_idpay_code")
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    Scenario: A citizen tries to pay by IDPay Code having exhausted the budget on the initiative
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the merchant 1 pre-authorizes and authorizes the transaction X by IDPay Code correctly inserted by citizen A
        And with IDPay Code the transaction X is authorized
        And the citizen A is rewarded with 300 euros
        And the merchant 1 generates the transaction Y of amount 10000 cents to be paid by IDPay Code through MIL
        And the MinInt associates the transaction Y with the citizen A by IDPay Code
        When the merchant 1 tries to pre-authorize the transaction Y by IDPay Code
        Then the latest pre-authorization by IDPay Code fails because the budget is exhausted
        Given the batch process confirms the transaction X
        When the institution refunds the merchant 1 of 300 euros successfully
        Then the merchant 1 is refunded 300 euros

    Scenario: A citizen tries to pay by IDPay Code a second transaction by exhausting the budget
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 20000 cents to be paid by IDPay Code through MIL
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the merchant 1 pre-authorizes and authorizes the transaction X by IDPay Code correctly inserted by citizen A
        And with IDPay Code the transaction X is authorized
        And the citizen A is rewarded with 200 euros
        And the merchant 1 generates the transaction Y of amount 20000 cents to be paid by IDPay Code through MIL
        And the MinInt associates the transaction Y with the citizen A by IDPay Code
        When the merchant 1 pre-authorizes and authorizes the transaction Y by IDPay Code correctly inserted by citizen A
        Then with IDPay Code the transaction Y is authorized
        And the citizen A is rewarded with 300 euros
        Given the batch process confirms the transaction X
        And the batch process confirms the transaction Y
        When the institution refunds the merchant 1 of 300 euros successfully
        Then the merchant 1 is refunded 300 euros
