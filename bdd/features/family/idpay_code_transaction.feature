@family_initiative
@family
@transaction
Feature: A family member can pay a transaction by IDPay Code

  Background:
    Given the initiative is "family_initiative"
    And the random merchant 1 is onboard
    And citizens A B C have fiscal code random
    And citizens A B C are in the same family
    And citizens A B C have ISEE 19999 of type "ordinario"
    When the first citizen of A B C onboards
    Then the onboard of A is OK

  Scenario: A family member cannot pay a transaction by IDPay Code of another family member
    Given the demanded family member B onboards
    And the citizen A enrolls correctly a new IDPay Code on the initiative
    And the IDPay Code is not enabled for citizen B
    And the merchant 1 generates the transaction X of amount 30000 cents to be paid by IDPay Code through MIL
    And the MinInt associates the transaction X with the citizen B by IDPay Code
    When the merchant 1 tries to pre-authorize the transaction X by IDPay Code
    Then the latest pre-authorization by IDPay Code fails because IDPay Code is not enabled

   Scenario: A demanded family member cannot enroll IDPay Code on initiative
    Given the onboard of B is demanded
    When the citizen B generates the IDPay Code
	Then the IDPay Code is enabled for citizen B
	When the citizen B tries to enroll a new IDPay Code on the initiative
    Then the latest IDPay Code enrollment fails because the citizen is not onboard

  @suspension
  Scenario: A suspended family member cannot pay a transaction by IDPay Code
    Given the demanded family member B onboards
	And the citizen B enrolls correctly a new IDPay Code on the initiative
    And the institution suspends correctly the citizen B
	And the merchant 1 generates the transaction X of amount 5000 cents to be paid by IDPay Code through MIL
	When the MinInt tries to associate the transaction X with the citizen B by IDPay Code
	Then the latest association by MinInt fails because the citizen is suspended

  @suspension
  Scenario: A family member pays a transaction by IDPay Code, although another member is suspended
    Given the demanded family member B onboards
    And the institution suspends correctly the citizen B
	And the citizen A enrolls correctly a new IDPay Code on the initiative
	And the merchant 1 generates the transaction X of amount 15000 cents to be paid by IDPay Code through MIL
	And the MinInt associates the transaction X with the citizen A by IDPay Code
    When the merchant 1 pre-authorizes and authorizes the transaction X by IDPay Code correctly inserted by citizen A
    Then with IDPay Code the transaction X is authorized

  @unsubscribe
  Scenario: An unsubscribed family member cannot pay a transaction by IDPay Code
    Given the demanded family member B onboards
	And the citizen B enrolls correctly a new IDPay Code on the initiative
	And the citizen B is unsubscribed
	And the merchant 1 generates the transaction X of amount 11000 cents to be paid by IDPay Code through MIL
	When the MinInt tries to associate the transaction X with the citizen B by IDPay Code
	Then the latest association by MinInt fails because the citizen is unsubscribed

  @refund
  Scenario: All family members pay a transaction by IDPay Code and they are rewarded individually, sharing the budget
    Given the demanded family member B onboards
    And the demanded family member C onboards
	And the family members A B C enrolls correctly a new IDPay Code on the initiative
	And the merchant 1 generates the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
	And the merchant 1 generates the transaction Y of amount 5000 cents to be paid by IDPay Code through MIL
	And the merchant 1 generates the transaction Z of amount 7550 cents to be paid by IDPay Code through MIL
	And the MinInt associates the transaction X with the citizen A by IDPay Code
	And the MinInt associates the transaction Y with the citizen B by IDPay Code
	And the MinInt associates the transaction Z with the citizen C by IDPay Code
    When the merchant 1 pre-authorizes and authorizes the transaction X by IDPay Code correctly inserted by citizen A
	And the batch process confirms the transaction X
	Then the family member A is rewarded with 100 euros
    And the family members A B C have budget of 200 euros left
	When the merchant 1 pre-authorizes and authorizes the transaction Y by IDPay Code correctly inserted by citizen B
	And the batch process confirms the transaction Y
	Then the family member B is rewarded with 50 euros
    And the family members A B C have budget of 150 euros left
	When the merchant 1 pre-authorizes and authorizes the transaction Z by IDPay Code correctly inserted by citizen C
	And the batch process confirms the transaction Z
	Then the family member C is rewarded with 75.50 euros
    And the family members A B C have budget of 74.50 euros left
	When the institution refunds the merchant 1 of 225.50 euros successfully
    Then the merchant 1 is refunded 225.50 euros

  @refund
  Scenario: Two family members pay a transaction by IDPay Code and the second one exhausts the budget
	Given the demanded family member B onboards
	And the family members A B enrolls correctly a new IDPay Code on the initiative
	And the merchant 1 generates the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
	And the merchant 1 generates the transaction Y of amount 25000 cents to be paid by IDPay Code through MIL
	And the MinInt associates the transaction X with the citizen A by IDPay Code
	And the MinInt associates the transaction Y with the citizen B by IDPay Code
	When the merchant 1 pre-authorizes and authorizes the transaction X by IDPay Code correctly inserted by citizen A
	And the batch process confirms the transaction X
	Then the family member A is rewarded with 100 euros
    And the family members A B C have budget of 200 euros left
	When the merchant 1 pre-authorizes and authorizes the transaction Y by IDPay Code correctly inserted by citizen B
	And the batch process confirms the transaction Y
	Then the family member B is rewarded with 200 euros
    And the family members A B have budget of 0 euros left
	When the institution refunds the merchant 1 of 300 euros successfully
    Then the merchant 1 is refunded 300 euros

  @refund
  Scenario: Two family members pay a transaction by IDPay Code but the second pre-auth fails because the budget is exhausted
	Given the demanded family member B onboards
	And the family members A B enrolls correctly a new IDPay Code on the initiative
	And the merchant 1 generates the transaction X of amount 35000 cents to be paid by IDPay Code through MIL
	And the merchant 1 generates the transaction Y of amount 17000 cents to be paid by IDPay Code through MIL
	And the MinInt associates the transaction X with the citizen A by IDPay Code
	And the MinInt associates the transaction Y with the citizen B by IDPay Code
	When the merchant 1 pre-authorizes and authorizes the transaction X by IDPay Code correctly inserted by citizen A
	And the batch process confirms the transaction X
	Then the family member A is rewarded with 300 euros
    And the family members A B have budget of 0 euros left
	When the merchant 1 tries to pre-authorize the transaction Y by IDPay Code
	Then the latest pre-authorization by IDPay Code fails because the budget is exhausted

  @refund
  Scenario: Two family members pay a transaction by IDPay Code but the second authorization fails because the budget is exhausted
	Given the demanded family member B onboards
	And the family members A B enrolls correctly a new IDPay Code on the initiative
	And the merchant 1 generates the transaction X of amount 35000 cents to be paid by IDPay Code through MIL
	And the merchant 1 generates the transaction Y of amount 17000 cents to be paid by IDPay Code through MIL
	And the MinInt associates the transaction X with the citizen A by IDPay Code
	And the MinInt associates the transaction Y with the citizen B by IDPay Code
	And the merchant 1 pre-authorizes the transaction X by IDPay Code
	And the merchant 1 pre-authorizes the transaction Y by IDPay Code
	And the merchant 1 authorizes the transaction X by IDPay Code
	When the merchant 1 tries to authorize the transaction Y by IDPay Code
	Then the latest authorization by IDPay Code fails because the budget is exhausted

  @cancellation
  Scenario: After a cancellation of a transaction by IDPay Code the family member budget is updated
	Given the demanded family member B onboards
	And the citizen A enrolls correctly a new IDPay Code on the initiative
    And the merchant 1 generates the transaction X of amount 35000 cents to be paid by IDPay Code through MIL
    And the MinInt associates the transaction X with the citizen A by IDPay Code
    When the merchant 1 pre-authorizes and authorizes the transaction X by IDPay Code correctly inserted by citizen A
    Then the family member A is rewarded with 300 euros
    And the family members A B have budget of 0 euros left
    When the merchant 1 cancels the transaction X
    Then the family member A is rewarded with 0 euros
    And the family members A B have budget of 300 euros left
