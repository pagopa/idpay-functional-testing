@bonus_elettrodomestici @rdb @notification @rdb_email_contract
Feature: Accept RDB notification payloads at the email service
  The test invokes POST /idpay/email-notification/notify directly.
  HTTP 204 is the acceptance criterion; no telemetry or proxy is required.
  This contract does not verify the automatic RDB trigger, grouping or mailbox delivery.
  The configured recipient must be a dedicated test address.

  Scenario Outline: Accept a notification request for an RDB event
    Given an RDB email service request of type "<kind>"
    When the test invokes the RDB email notification service
    Then the RDB email notification service responds with HTTP 204

    Examples:
      | kind     |
      | ok       |
      | partial  |
      | rejected |
