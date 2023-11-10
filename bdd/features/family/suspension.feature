@family_initiative
@family
@suspension
Feature: A family member can be suspended from an initiative

    Background:
        Given the initiative is "family_initiative"
        And the random merchant 1 is onboard
        And citizens A B C have fiscal code random
        And citizens A B C are in the same family
        And citizens A B C have ISEE 19999 of type "ordinario"
        When the first citizen of A B C onboards
        Then the onboard of A is OK

    @bar_code
    Scenario: A suspended family member cannot pay a transaction by Bar Code
        Given the demanded family member B onboards
        And the institution suspends correctly the citizen B
        And the citizen B creates the transaction X by Bar Code
        When the merchant 1 tries to authorize the transaction X by Bar Code of amount 15000 cents
        Then the latest authorization by merchant fails because the citizen is suspended

    @bar_code
    Scenario: A family member pays a transaction by Bar Code, although another member is suspended
        Given the demanded family member B onboards
        And the institution suspends correctly the citizen B
        And the citizen A creates the transaction X by Bar Code
        When the the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        Then with Bar Code the transaction X is authorized
        And the family member A is rewarded with 200 euros
        And the family members A B have budget of 100 euros left

    @idpay_code
    Scenario: A suspended family member cannot pay a transaction by IDPay Code
        Given the demanded family member B onboards
        And the citizen B enrolls correctly a new IDPay Code on the initiative
        And the institution suspends correctly the citizen B
        And the merchant 1 generates the transaction X of amount 5000 cents to be paid by IDPay Code through MIL
        When the citizen B presents the ID card, trying to reclaim the transaction X
        Then the latest citizen reclaim fails because the citizen is suspended

    @idpay_code
    Scenario: A family member pays a transaction by IDPay Code, although another member is suspended
        Given the demanded family member B onboards
        And the institution suspends correctly the citizen B
        And the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 20000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        Then with IDPay Code the transaction X is authorized
        And the family member A is rewarded with 200 euros
        And the family members A B have budget of 100 euros left

    @qr_code
    Scenario: A suspended family member cannot pay a transaction by QR Code
        Given the demanded family member B onboards
        And the institution suspends correctly the citizen B
        And the merchant 1 generates the transaction X of amount 10000 cents
        When the citizen B tries to pre-authorize the transaction X
        Then the latest pre-authorization fails because the user is suspended

    @qr_code
    Scenario: A family member pays a transaction by QR Code, although another member is suspended
        Given the demanded family member B onboards
        And the institution suspends correctly the citizen B
        And the merchant 1 generates the transaction X of amount 10000 cents
        When the citizen A confirms the transaction X
        Then the transaction X is authorized
        And the family member A is rewarded with 100 euros
        And the family members A B have budget of 200 euros left
