@discount_idpay_code
@transaction
Feature: A citizen can pay with IDPay Code on a discount initiative

    Background:
        Given the initiative id is "652e886882b08d1934cd751c" ("discount_idpay_code")
        And the citizen A has fiscal code random
        And the citizen A is onboard
        And the random merchant 1 is onboard

    @need_fix
    Scenario: A citizen tries to pay with IDPay Code having exhausted the budget on the initiative
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 30000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        And the transaction X with IDPay Code is authorized
        And the citizen A is rewarded with 300 euros
        And the merchant 1 generates the transaction Y of amount 10000 cents through MIL (new)
        And the MinInt associates the transaction Y with the citizen A by IDPay Code
        When the merchant 1 tries to pre-authorize the transaction Y with IDPay Code
        Then the transaction Y with IDPay Code is not authorized for budget exhausted
        When the batch process confirms all the transactions
        Then the merchant 1 is refunded 300 euros

    @need_fix
    Scenario: A citizen tries to pay with IDPay Code a second transaction by exhausting the budget
        Given the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 20000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        And the merchant 1 pre-authorizes and authorizes the transaction X with IDPay Code correctly inserted by citizen A
        And the transaction X with IDPay Code is authorized
        And the citizen A is rewarded with 200 euros
        And the merchant 1 generates the transaction Y of amount 20000 cents through MIL (new)
        And the MinInt associates the transaction X with the citizen A by IDPay Code
        When the merchant 1 tries to pre-authorize the transaction Y with IDPay Code
        Then the transaction Y with IDPay Code is authorized
        And the citizen A is rewarded with 300 euros
        When the batch process confirms all the transactions
        Then the merchant 1 is refunded 300 euros
