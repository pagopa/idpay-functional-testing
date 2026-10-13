@bonus_elettrodomestici @rdb @authorization
Feature: Access and authorization to RDB

    Scenario: A producer cannot approve a product
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"
    And RDB product "X" has initial status "WAIT_APPROVED"
    When the RDB user changes products "X" from "WAIT_APPROVED" to "APPROVED"
    Then the RDB response has HTTP status 403
    And RDB product "X" is unchanged