@family
@transaction
Feature: A family member can pay a transaction by Bar Code

    Background:
      Given the initiative is "family"
      And the random merchant 1 is onboard
      And citizens A B C have fiscal code random
      And citizens A B C are in the same family
      And citizens A B C have ISEE 19999 of type "ordinario"
      When the first citizen of A B C onboards
      Then the onboard of A is OK

    Scenario: A demanded family member cannot create a transaction by Bar Code
      Given the onboard of B is demanded
      When the citizen B tries to create the transaction X by Bar Code
      Then the latest transaction creation by citizen fails because the citizen is not onboarded
      When the citizen B tries to create the transaction X by Bar Code
      Then the transaction X is created

    @suspension
    Scenario: A family member pays a transaction by Bar Code, although another member is suspended
      Given the demanded family member B onboards
      And the institution suspends correctly the citizen B
      And the citizen A creates the transaction X by Bar Code
      When the the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
      Then with Bar Code the transaction X is authorized
      Given the citizen B creates the transaction Y by Bar Code
      When the merchant 1 tries to authorize the transaction Y by Bar Code of amount 15000 cents
      Then the latest authorization by merchant fails because the citizen is suspended

    @unsubscribe
    Scenario: A family member pays a transaction by Bar Code, although another member has unsubscribed
      Given the demanded family member B onboards
      And the citizen B is unsubscribed
      And the citizen A creates the transaction X by Bar Code
      When the the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
      Then with Bar Code the transaction X is authorized
      When the citizen B tries to create the transaction Y by Bar Code
      Then the latest transaction creation by citizen fails because the citizen is unsubscribed

    Scenario: A family member onboarded after another family member pays a transaction by Bar Code
      Given the citizen A creates the transaction X by Bar Code
      And the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
      And with Bar Code the transaction X is authorized
      When the batch process confirms the transaction X
      And the family member A has budget of 100 euros left
      Then the family member A is rewarded with 200 euros
      When the demanded family member B onboards
      Then the family member B has budget of 100 euros left

    @refund
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
      When the institution refunds the merchant 1 of 225.50 euros successfully
      Then the merchant 1 is refunded 225.50 euros

    @refund
    Scenario: Two family members pay a transaction by Bar Code and the second one exhausts the budget
      Given the demanded family member B onboards
      And the citizen A creates the transaction X by Bar Code
      And the citizen B creates the transaction Y by Bar Code
      When the merchant 1 authorizes the transaction X by Bar Code of amount 20000 cents
      Then the family member A is rewarded with 100 euros
      And the family members A B have budget of 200 euros left
      When the merchant 1 authorizes the transaction Y by Bar Code of amount 15000 cents
      Then the family member B is rewarded with 100 euros
      And the family members A B have budget of 0 euros left
      Given the batch process confirms the transaction X
      And the batch process confirms the transaction Y
      When the institution refunds the merchant 1 of 300 euros successfully
      Then the merchant 1 is refunded 300 euros

    @refund
    Scenario: Two family members pay a transaction by Bar Code but the first one exhausted the budget
      Given the demanded family member B onboards
      And the citizen A creates the transaction X by Bar Code
      And the citizen B creates the transaction Y by Bar Code
      When the merchant 1 authorizes the transaction X by Bar Code of amount 35000 cents
      Then the family member A is rewarded with 300 euros
      And the family members A B have budget of 0 euros left
      When the merchant 1 tries to authorize the transaction X by Bar Code of amount 17000 cents
      Then the latest authorization by merchant fails because the budget is exhausted

    @cancellation
    Scenario: After a cancellation of a transaction by Bar Code the family member budget is updated
      Given the demanded family member B onboards
      And the citizen A creates the transaction X by Bar Code
      When the merchant 1 authorizes the transaction X by Bar Code of amount 17000 cents
      Then the family member A is rewarded with 170 euros
      And the family members A B have budget of 130 euros left
      When the merchant 1 cancels the transaction X
      Then the family member A is rewarded with 0 euros
      And the family members A B have budget of 300 euros left
