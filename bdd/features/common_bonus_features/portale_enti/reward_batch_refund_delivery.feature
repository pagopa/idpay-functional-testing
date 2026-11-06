@bonus_elettrodomestici
@bonus_decoder
@portale_enti
@reward_batch
@reward_batch_refund_delivery
Feature: Reward batch refund delivery and outcomes from APPROVED status
  Background:
    Given the initiative is active
    And the merchant 1 is qualified
    And an existing reward batch in status APPROVED for merchant 1 is selected as transaction X
    And the reward batch of transaction X is APPROVED

  Scenario: Approved reward batch moves to PENDING_REFUND after delivery
    When the approved reward batch of transaction X is sent for refund delivery
    Then the reward batch of transaction X becomes PENDING_REFUND within 60 seconds

  Scenario: Completed Invitalia outcome moves batch to REFUNDED
    Given the approved reward batch of transaction X is sent for refund delivery
    And the reward batch of transaction X becomes PENDING_REFUND within 60 seconds
    And the invitalia outcome status of reward batch of transaction X becomes COMPLETATA within 180 seconds
    When the refund outcomes are checked for reward batch of transaction X
    Then the reward batch of transaction X becomes REFUNDED within 60 seconds

  Scenario: Rejected Invitalia outcome moves batch to NOT_REFUNDED
    Given the approved reward batch of transaction X is sent for refund delivery
    And the reward batch of transaction X becomes PENDING_REFUND within 60 seconds
    And the invitalia outcome status of reward batch of transaction X becomes RIFIUTATA within 180 seconds
    When the refund outcomes are checked for reward batch of transaction X
    Then the reward batch of transaction X becomes NOT_REFUNDED within 60 seconds

  Scenario: In progress Invitalia outcome keeps batch in PENDING_REFUND
    Given the approved reward batch of transaction X is sent for refund delivery
    And the reward batch of transaction X becomes PENDING_REFUND within 60 seconds
    And the invitalia outcome status of reward batch of transaction X becomes IN_LAVORAZIONE within 180 seconds
    When the refund outcomes are checked for reward batch of transaction X
    Then the reward batch of transaction X becomes PENDING_REFUND within 60 seconds

