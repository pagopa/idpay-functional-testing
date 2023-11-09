@Scontoditipo4
@transaction
Feature: Transaction in a closed initiative

  Background:
    Given the initiative is "Scontoditipo4"

  Scenario: Transaction X is not generated on a closed initiative
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 1000 cents
    Then the transaction X is not created because it is out of valid period

  @bar_code
  Scenario: Transaction X to be paid by Bar Code is not generated on a closed initiative
    Given the citizen A has fiscal code random
    When the citizen A tries to create the transaction X by Bar Code
    Then the latest transaction creation by citizen fails because is out of valid period

  @idpay_code
  Scenario: Transaction X to be paid by IDPay Code is not generated on a closed initiative
    Given the random merchant 1 is onboard
    When the merchant 1 tries to generate the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
    Then the latest transaction creation through MIL fails because is out of valid period