@family_initiative
@family
@transaction
Feature: A family member can pay a transaction

    Background:
        Given the initiative is "family_initiative"
        And the random merchant 1 is onboard
        And citizens A B C have fiscal code random
        And citizens A B C are in the same family
        And citizens A B C have ISEE 19999 of type "ordinario"
        When the first citizen of A B C onboards
        Then the onboard of A is OK

    @bar_code
    Scenario: A demanded family member cannot create a transaction by Bar Code
        Given the onboard of B is demanded
        When the citizen B tries to create the transaction X by Bar Code
        Then the latest transaction creation by citizen fails because the citizen is not onboarded
        When the citizen A tries to create the transaction Y by Bar Code
        Then with Bar Code the transaction Y is created

    @bar_code
    Scenario: A family member onboarded after another family member pays a transaction by Bar Code
        Given the citizen A creates the transaction X by Bar Code
        And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        And with Bar Code the transaction X is authorized
        When the batch process confirms the transaction X
        Then the family member A is rewarded with 200 euros
        And the family member A has budget of 100 euros left
        When the demanded family member B onboards
        Then the family member B has budget of 100 euros left

    @idpay_code
    Scenario: A family member cannot pay a transaction by IDPay Code of another family member
        Given the demanded family member B onboards
        And the citizen A enrolls correctly a new IDPay Code on the initiative
        And the IDPay Code is not enabled for citizen B
        And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
        And the citizen B presents the ID card, reclaiming the transaction X
        When the payment by IDPay Code of transaction X is about to be pre-authorized
        Then the latest pre-authorization by IDPay Code fails because IDPay Code is not enabled

    @idpay_code
    Scenario: A demanded family member cannot enroll IDPay Code on initiative
        Given the onboard of B is demanded
        When the citizen B generates the IDPay Code
        Then the IDPay Code is enabled for citizen B
        When the citizen B tries to enroll a new IDPay Code on the initiative
        Then the latest IDPay Code enrollment fails because the citizen is not onboard

    @qr_code
    Scenario: A demanded family member cannot pay a transaction by QR Code
        Given the onboard of B is demanded
        And the merchant 1 generates the transaction X of amount 30000 cents
        When the citizen B tries to pre-authorize the transaction X
        Then the latest pre-authorization fails because the citizen is not onboard
        When the citizen A confirms the transaction X
        Then the transaction X is authorized

    @qr_code
    Scenario: A family member onboarded after another family member pays a transaction by QR Code
        Given the merchant 1 generates the transaction X of amount 10000 cents
        And the citizen A confirms the transaction X
        And the transaction X is authorized
        When the demanded family member B onboards
        Then the family member B has budget of 200 euros left
        And the family member A has budget of 200 euros left
