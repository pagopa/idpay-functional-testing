@whitelist
@transaction
Feature: Transactions on a whitelist initiative

  @qr_code
  Scenario Outline: An invited citizen tries to confirm a transaction by QR Code on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 10000 cents
    When the citizen A tries to pre-authorize the transaction X
    Then the latest pre-authorization fails because the citizen is not onboard

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  @bar_code
  Scenario Outline: An invited citizen tries to create a transaction by Bar Code on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    When the citizen A tries to create the transaction X by Bar Code
    Then the latest transaction creation by citizen fails because the citizen is not onboarded

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  @idpay_code
  Scenario Outline: An invited citizen tries to enable the IDPay Code on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    When the citizen A tries to enroll a new IDPay Code on the initiative
    Then the latest IDPay Code enrollment fails because the citizen is not onboard

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |

  @idpay_code
  Scenario Outline: An invited citizen tries to pay a transaction by IDPay Code on whitelist initiative
    Given citizens <citizens> have fiscal code random
    And citizens <citizens> are included in the whitelist
    And a new whitelist initiative "discount_whitelist"
    And the random merchant 1 is onboard
    And the merchant 1 generates the transaction X of amount 10000 cents to be paid by IDPay Code through MIL
    When the citizen A presents the ID card, trying to reclaim the transaction X
    Then the latest citizen reclaim fails because the citizen is not onboarded

    Examples: Citizens in whitelist
      | citizens  |
      | A B C D E |