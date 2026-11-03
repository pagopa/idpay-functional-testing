@family_initiative
@family
@cancellation
Feature: A transaction can be cancelled by the merchant on initiative for family

    Background:
        Given the initiative is "family_initiative"
        And the random merchant 1 is onboard
        And citizens A B C have fiscal code random
        And citizens A B C are in the same family
        And citizens A B C have ISEE 19999 of type "ordinario"
        And the first citizen of A B C onboards
        And the onboard of A is OK

    @bar_code
    Scenario: After a cancellation of a transaction by Bar Code the family member budget is updated
      Given the demanded family member B onboards
      And the citizen A creates the transaction X by Bar Code
      When the merchant 1 authorizes the transaction X by Bar Code of amount 17000 cents
      Then the family member A is rewarded with 170 euros
      And the family members A B have budget of 130 euros left
      When the merchant 1 cancels the transaction X
      Then the family member A is rewarded with 0 euros
      And the family members A B have budget of 300 euros left

    @idpay_code
    Scenario: After a cancellation of a transaction by IDPay Code the family member budget is updated
        Given the demanded family member B onboards
        And the citizen A enrolls correctly a new IDPay Code on the initiative
        And the merchant 1 generates the transaction X of amount 35000 cents to be paid by IDPay Code through MIL
        And the citizen A presents the ID card, reclaiming the transaction X
        And the payment by IDPay Code of transaction X is pre-authorized
        When the citizen A enters the IDPay Code correctly to pay the transaction X
        Then the family member A is rewarded with 300 euros
        And the family members A B have budget of 0 euros left
        When the merchant 1 cancels the transaction X
        Then the family member A is rewarded with 0 euros
        And the family members A B have budget of 300 euros left

    @qr_code
    Scenario: After a cancellation of a transaction by QR Code the family member budget is updated
        Given the demanded family member B onboards
        And the merchant 1 generates the transaction X of amount 20000 cents
        When the citizen A confirms the transaction X
        Then the citizen A is rewarded with 200 euros
        And the family members A B have budget of 100 euros left
        When the merchant 1 cancels the transaction X
        Then the citizen A is rewarded with 0 euros
        And the family members A B have budget of 300 euros left
