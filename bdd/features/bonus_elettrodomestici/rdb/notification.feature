@bonus_elettrodomestici @rdb @notification @rdb_fixture
Feature: Preserve RDB processing when email is missing or unavailable
  Email service HTTP 204 acceptance is checked in email_service.feature.
  These scenarios check RDB processing and persistence.
  The failure scenario requires an isolated dependency to reproduce an outage.

  Background:
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"

  Scenario: Process a CSV when the operational email is missing
    Given the RDB dataset is "producer without email"
    And the RDB operational email is initially absent
    And a valid RDB product CSV with 1 rows
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And all submitted RDB products have status "UPLOADED"

  Scenario: Reject a product when the operational email is missing
    Given the RDB dataset is "producer without email"
    And the RDB operational email is initially absent
    And RDB product "X" has initial status "UPLOADED"
    And the RDB user is authenticated as "Invitalia"
    When the RDB user changes products "X" from "UPLOADED" to "REJECTED"
    Then the RDB operation has outcome "OK"
    And RDB product "X" has status "REJECTED"

  @rdb_dependency_outage
  Scenario: Preserve the status change when the email service fails
    Given the RDB operational email was set to "rdb@example.it"
    And RDB product "X" has initial status "UPLOADED"
    And the RDB user is authenticated as "Invitalia"
    And the RDB dependency "email" is unavailable
    When the RDB user changes products "X" from "UPLOADED" to "REJECTED"
    Then the RDB operation has outcome "OK"
    And RDB product "X" has status "REJECTED"
    And RDB product "X" records the requested status change
    And the RDB backend received the email service failure
