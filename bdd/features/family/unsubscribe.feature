@family_initiative
@family
@unsubscribe
Feature: A family member can unsubscribe from an initiative

    Background:
        Given the initiative is "family_initiative"
        And the random merchant 1 is onboard
        And citizens A B C have fiscal code random
        And citizens A B C are in the same family
        And citizens A B C have ISEE 19999 of type "ordinario"
        When the first citizen of A B C onboards
        Then the onboard of A is OK

    @bar_code
    Scenario: A family member pays a transaction by Bar Code, although another member has unsubscribed
        Given the demanded family member B onboards
        And the citizen B is unsubscribed
        And the citizen A creates the transaction X by Bar Code
        When the the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
        Then with Bar Code the transaction X is authorized
        When the citizen B tries to create the transaction Y by Bar Code
        Then the latest transaction creation by citizen fails because the citizen is unsubscribed

    @idpay_code
    Scenario: An unsubscribed family member cannot pay a transaction by IDPay Code
        Given the demanded family member B onboards
        And the citizen B enrolls correctly a new IDPay Code on the initiative
        And the citizen B is unsubscribed
        And the merchant 1 generates the transaction X of amount 11000 cents to be paid by IDPay Code through MIL
        When the citizen B presents the ID card, trying to reclaim the transaction X
        Then the latest citizen reclaim fails because the citizen is unsubscribed

    @qr_code
    Scenario: A family member pays a transaction by QR Code, although another member has unsubscribed
        Given the demanded family member B onboards
        And the citizen B is unsubscribed
        And the merchant 1 generates the transaction X of amount 10000 cents
        When the citizen A confirms the transaction X
        Then the transaction X is authorized
        Given the merchant 1 generates the transaction Y of amount 20000 cents
        When the citizen B tries to pre-authorize the transaction Y
        Then the latest pre-authorization fails because the user is unsubscribed
