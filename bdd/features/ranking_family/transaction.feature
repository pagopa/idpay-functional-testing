@family_ranking_initiative
@ranking
@transaction
Feature: Transactions on an initiative for families with ranking

  Background:
    Given a new initiative "family_ranking_initiative"

  Scenario: A merchant cannot generate a transaction, to be paid by QR Code, during onboarding period on an initiative for families with ranking
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because it is out of valid period

  @transaction_idpay_code
  Scenario: A merchant cannot generate a transaction, to be paid by IDPay Code, during onboarding period on an initiative for families with ranking
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
    Then the latest transaction creation by merchant through MIL fails because is out of valid period

  Scenario: A merchant cannot generate a transaction, to be paid by QR Code, during grace period on an initiative for families with ranking
    Given the random merchant 1 is onboard
    And the ranking period ends
    And the ranking is produced
    When the merchant 1 tries to generate the transaction X of amount 30000 cents
    Then the transaction X is not created because it is out of valid period

  @transaction_idpay_code
  Scenario: A merchant cannot generate a transaction, to be paid by IDPay Code, during grace period on an initiative for families with ranking
    Given the random merchant 1 is onboard
    And the ranking period ends
    And the ranking is produced
    When the merchant 1 tries to generate the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
    Then the latest transaction creation by merchant through MIL fails because is out of valid period