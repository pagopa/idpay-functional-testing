@family_ranking_initiative
@ranking
@transaction
Feature: Transactions on an initiative for families with ranking

  Scenario: A merchant cannot generate a transaction by QR Code during onboarding period on an initiative for families with ranking
    Given a new initiative "family_ranking_initiative"
    And the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because it is out of valid period

  Scenario: A merchant cannot generate a transaction by IDPay Code during onboarding period on an initiative for families with ranking
    Given a new initiative "family_ranking_initiative"
    And the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
    Then the latest transaction creation by merchant through MIL fails because is out of valid period

  @skip
  Scenario: A merchant cannot generate a transaction by QR Code during grace period on an initiative for families with ranking
    Given a new initiative "family_ranking_in_grace_period"
    And the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because it is out of valid period

  @skip
  Scenario: A merchant cannot generate a transaction by IDPay Code during grace period on an initiative for families with ranking
    Given a new initiative "family_ranking_in_grace_period"
    And the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
    Then the latest transaction creation by merchant through MIL fails because is out of valid period