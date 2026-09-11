@bonus_elettrodomestici @rdb @notification @rdb_fixture
Feature: Notify producers about CSV processing and rejected products

  Background:
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"
    And RDB notifications are observed

  Scenario: Notify a producer after successful CSV processing
    Given the RDB operational email was set to "rdb@example.it"
    And a valid RDB product CSV with 1 rows
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And an RDB "ok" notification is sent to "rdb@example.it" for the uploaded CSV
    And the RDB notification contains the initiative name

  @eprel
  Scenario: Notify a producer after partial CSV processing
    Given the RDB operational email was set to "rdb@example.it"
    And the RDB EPREL CSV case is "mixed"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "PARTIAL"
    And an RDB "partial" notification is sent to "rdb@example.it" for the uploaded CSV

  Scenario Outline: Group rejected products in one notification per producer
    Given the RDB operational email was set to "rdb@example.it"
    And RDB product "X" has initial status "UPLOADED"
    And RDB product "Y" has initial status "UPLOADED"
    And the RDB user is authenticated as "Invitalia"
    When the RDB user changes products "<products>" from "UPLOADED" to "REJECTED"
    Then the RDB operation has outcome "OK"
    And one RDB rejection notification for products "<products>" is sent to "rdb@example.it"

    Examples:
      | products |
      | X        |
      | X, Y     |

  Scenario: Send separate rejection notifications to different producers
    Given the RDB dataset is "products from different producers"
    And the dataset RDB products have status "UPLOADED"
    When the RDB user changes products "X, Y" from "UPLOADED" to "REJECTED"
    Then the RDB operation has outcome "OK"
    And each dataset producer receives its RDB rejection notification

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

  Scenario: Preserve the status change when the email service fails
    Given the RDB operational email was set to "rdb@example.it"
    And RDB product "X" has initial status "UPLOADED"
    And the RDB user is authenticated as "Invitalia"
    And the RDB dependency "email" is unavailable
    When the RDB user changes products "X" from "UPLOADED" to "REJECTED"
    Then the RDB operation has outcome "OK"
    And RDB product "X" has status "REJECTED"
    And RDB product "X" records the requested status change
