@bonus_elettrodomestici @rdb @product_status
Feature: Change product status with role checks and atomic updates

  Background:
    Given the RDB initiative is "A"

  Scenario Outline: Perform an allowed product status transition
    Given the RDB user is authenticated as "<role>"
    And RDB product "X" has initial status "<current>"
    When the RDB user changes products "X" from "<current>" to "<target>"
    Then the RDB operation has outcome "OK"
    And RDB product "X" has status "<target>"
    And RDB product "X" records the requested status change

    Examples:
      | role            | current       | target        |
      | Invitalia       | UPLOADED      | SUPERVISED    |
      | Invitalia       | UPLOADED      | WAIT_APPROVED |
      | Invitalia       | SUPERVISED    | WAIT_APPROVED |
      | Invitalia       | UPLOADED      | REJECTED      |
      | Invitalia       | SUPERVISED    | REJECTED      |
      | Invitalia Admin | WAIT_APPROVED | APPROVED      |
      | Invitalia Admin | WAIT_APPROVED | UPLOADED      |

  Scenario: An Invitalia operator cannot approve a product
    Given the RDB user is authenticated as "Invitalia"
    And RDB product "X" has initial status "WAIT_APPROVED"
    When the RDB user changes products "X" from "WAIT_APPROVED" to "APPROVED"
    Then the RDB response has HTTP status 403
    And RDB product "X" is unchanged

  Scenario: Reject an incorrect declared current status
    Given the RDB user is authenticated as "Invitalia"
    And RDB product "X" has initial status "UPLOADED"
    When the RDB user changes products "X" from "SUPERVISED" to "WAIT_APPROVED"
    Then the RDB request is rejected
    And RDB product "X" is unchanged

  Scenario: Reject a batch containing different current statuses
    Given the RDB user is authenticated as "Invitalia"
    And RDB product "X" has initial status "UPLOADED"
    And RDB product "Y" has initial status "SUPERVISED"
    When the RDB user changes products "X, Y" from "UPLOADED" to "REJECTED"
    Then the RDB request is rejected
    And RDB product "X" is unchanged
    And RDB product "Y" is unchanged

  Scenario: Reject the entire batch when one product does not exist
    Given the RDB user is authenticated as "Invitalia"
    And RDB product "X" has initial status "UPLOADED"
    And RDB product "Y" does not exist
    When the RDB user changes products "X, Y" from "UPLOADED" to "REJECTED"
    Then the RDB request is rejected
    And RDB product "X" is unchanged
    And RDB product "Y" remains absent

  @rdb_fixture
  Scenario: Do not update a product through another initiative
    Given the RDB user is authenticated as "Invitalia"
    And RDB product "X" has initial status "UPLOADED"
    And the RDB initiative is "B"
    When the RDB user changes products "X" from "UPLOADED" to "REJECTED"
    Then the RDB request is rejected
    And RDB product "X" is unchanged
