@family_initiative
@family
@refunds
Feature: A merchant is refunded and a family member is rewarded for a transaction on initiative for family

    Background:
        Given the initiative is "family_initiative"
        And the random merchant 1 is onboard
        And citizens A B C have fiscal code random
        And citizens A B C are in the same family
        And citizens A B C have ISEE 19999 of type "ordinario"
        And the first citizen of A B C onboards
        And the onboard of A is OK

    @bar_code
    Scenario: All family members pay a transaction by Bar Code and they are rewarded individually, sharing the budget
        Given the demanded family member B onboards
        And the demanded family member C onboards
        And the citizen A creates the transaction X by Bar Code
        And the citizen B creates the transaction Y by Bar Code
        And the citizen C creates the transaction Z by Bar Code
        When the merchant 1 authorizes the transaction X by Bar Code of amount 10000 cents
        Then the family member A is rewarded with 100 euros
        And the family members A B C have budget of 200 euros left
        When the merchant 1 authorizes the transaction Y by Bar Code of amount 5000 cents
        Then the family member B is rewarded with 50 euros
        And the family members A B C have budget of 150 euros left
        When the merchant 1 authorizes the transaction Z by Bar Code of amount 7550 cents
        Then the family member C is rewarded with 75.50 euros
        And the family members A B C have budget of 74.50 euros left
        Given the batch process confirms the transaction X
        And the batch process confirms the transaction Y
        And the batch process confirms the transaction Z
        And 1 second/s pass
        When the institution refunds the merchant 1 of 225.50 euros successfully
        Then the merchant 1 is refunded 225.50 euros

    @bar_code
    Scenario: Two family members pay a transaction by Bar Code and the second one exhausts the budget
        Given the demanded family member B onboards
        And the citizen A creates the transaction X by Bar Code
        And the citizen B creates the transaction Y by Bar Code
        When the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        Then the family member A is rewarded with 200 euros
        And the family members A B have budget of 100 euros left
        When the merchant 1 authorizes the transaction Y by Bar Code of amount 15000 cents
        Then the family member B is rewarded with 100 euros
        And the family members A B have budget of 0 euros left
        Given the batch process confirms the transaction X
        And the batch process confirms the transaction Y
        And 1 second/s pass
        When the institution refunds the merchant 1 of 300 euros successfully
        Then the merchant 1 is refunded 300 euros

    @bar_code
    Scenario: Two family members pay a transaction by Bar Code but the first one exhausted the budget
        Given the demanded family member B onboards
        And the citizen A creates the transaction X by Bar Code
        And the citizen B creates the transaction Y by Bar Code
        When the merchant 1 authorizes the transaction X by Bar Code of amount 35000 cents
        Then the family member A is rewarded with 300 euros
        And the family members A B have budget of 0 euros left
        When the merchant 1 tries to authorize the transaction Y by Bar Code of amount 17000 cents
        Then the latest authorization by merchant fails because the budget is exhausted

    @idpay_code
    Scenario: All family members pay a transaction by IDPay Code and they are rewarded individually, sharing the budget
        Given the demanded family member B onboards
        And the demanded family member C onboards
        And the family members A B C enroll correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
        And the merchant 1 generates the transaction Y of amount 5000 cents to be paid by IDPay Code through MIL
        And the merchant 1 generates the transaction Z of amount 7550 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the citizen B presents the ID card, reclaiming the transaction Y
        And the citizen C presents the ID card, reclaiming the transaction Z
        And the payment by IDPay Code of transaction X is pre-authorized
        And the payment by IDPay Code of transaction Y is pre-authorized
        And the payment by IDPay Code of transaction Z is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        And 1 second/s pass
        And the batch process confirms the transaction X
        Then the family member A is rewarded with 100 euros
        And the family members A B C have budget of 200 euros left
        When the citizen B enters the IDPay Code correctly to pay the transaction Y
        And 1 second/s pass
        And the batch process confirms the transaction Y
        Then the family member B is rewarded with 50 euros
        And the family members A B C have budget of 150 euros left
        When the citizen C enters the IDPay Code correctly to pay the transaction Z
        And 1 second/s pass
        And the batch process confirms the transaction Z
        Then the family member C is rewarded with 75.50 euros
        And the family members A B C have budget of 74.50 euros left
        When the institution refunds the merchant 1 of 225.50 euros successfully
        Then the merchant 1 is refunded 225.50 euros

    @idpay_code
    Scenario: Two family members pay a transaction by IDPay Code and the second one exhausts the budget
        Given the demanded family member B onboards
        And the family members A B enroll correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
        And the merchant 1 generates the transaction Y of amount 25000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the citizen B presents the ID card, reclaiming the transaction Y
        And the payment by IDPay Code of transaction X is pre-authorized
        And the payment by IDPay Code of transaction Y is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        And 1 second/s pass
        And the batch process confirms the transaction X
        Then the family member A is rewarded with 100 euros
        And the family members A B have budget of 200 euros left
        When the citizen B enters the IDPay Code correctly to pay the transaction Y
        And 1 second/s pass
        And the batch process confirms the transaction Y
        Then the family member B is rewarded with 200 euros
        And the family members A B have budget of 0 euros left
        When the institution refunds the merchant 1 of 300 euros successfully
        Then the merchant 1 is refunded 300 euros

    @idpay_code
    Scenario: Two family members pay a transaction by IDPay Code but the second pre-authorization fails because the budget is exhausted
        Given the demanded family member B onboards
        And the family members A B enroll correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 35000 cents to be paid by IDPay Code through MIL
        And the merchant 1 generates the transaction Y of amount 17000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the citizen B presents the ID card, reclaiming the transaction Y
        And the payment by IDPay Code of transaction X is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        And 1 second/s pass
        And the batch process confirms the transaction X
        Then the family member A is rewarded with 300 euros
        And the family members A B have budget of 0 euros left
        When the payment by IDPay Code of transaction Y is about to be pre-authorized
        Then the latest pre-authorization by IDPay Code fails because the budget is exhausted

    @idpay_code
    Scenario: Two family members pay a transaction by IDPay Code but the second authorization fails because the budget is exhausted
        Given the demanded family member B onboards
        And the family members A B enroll correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 35000 cents to be paid by IDPay Code through MIL
        And the merchant 1 generates the transaction Y of amount 17000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the citizen B presents the ID card, reclaiming the transaction Y
        And the payment by IDPay Code of transaction X is pre-authorized
        And the payment by IDPay Code of transaction Y is pre-authorized
        And the citizen A enters the IDPay Code correctly to pay the transaction X
        And 1 second/s pass
        When the citizen B enters the correct IDPay Code trying to pay the transaction Y
        Then the latest authorization by IDPay Code fails because the budget is exhausted

    @qr_code
    Scenario: All family members pay a transaction by QR Code and they are rewarded individually, sharing the budget
        Given the demanded family member B onboards
        And the demanded family member C onboards
        And the merchant 1 generates the transaction X of amount 10000 cents
        And the merchant 1 generates the transaction Y of amount 5000 cents
        And the merchant 1 generates the transaction Z of amount 7550 cents
        When the citizen A confirms the transaction X
        Then the family member A is rewarded with 100 euros
        And the family members A B C have budget of 200 euros left
        When the citizen B confirms the transaction Y
        Then the family member B is rewarded with 50 euros
        And the family members A B C have budget of 150 euros left
        When the citizen C confirms the transaction Z
        Then the family member C is rewarded with 75.50 euros
        And the family members A B C have budget of 74.50 euros left
        Given the batch process confirms the transaction X
        And the batch process confirms the transaction Y
        And the batch process confirms the transaction Z
        And 1 second/s pass
        When the institution refunds the merchant 1 of 225.50 euros successfully
        Then the merchant 1 is refunded 225.50 euros

    @qr_code
    Scenario: Two family members pay a transaction by QR Code and the second one exhausts the budget
        Given the demanded family member B onboards
        And the merchant 1 generates the transaction X of amount 20000 cents
        And the merchant 1 generates the transaction Y of amount 15000 cents
        When the citizen A confirms the transaction X
        Then the family member A is rewarded with 200 euros
        And the family members A B have budget of 100 euros left
        When the citizen B confirms the transaction Y
        Then the family member B is rewarded with 100 euros
        And the family members A B have budget of 0 euros left
        Given the batch process confirms the transaction X
        And the batch process confirms the transaction Y
        When the institution refunds the merchant 1 of 300 euros successfully
        Then the merchant 1 is refunded 300 euros

    @qr_code
    Scenario: Two family members pay a transaction by QR Code but the first one exhausted the budget
        Given the demanded family member B onboards
        And the merchant 1 generates the transaction X of amount 35000 cents
        And the merchant 1 generates the transaction Y of amount 17000 cents
        When the citizen A confirms the transaction X
        Then the family member A is rewarded with 300 euros
        And the family members A B have budget of 0 euros left
        When the citizen B tries to pre-authorize the transaction Y
        Then the transaction Y is not authorized for budget eroded
