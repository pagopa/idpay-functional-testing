@bonus_elettrodomestici @rdb @authorization
Feature: Access and authorization to RDB

  @rdb_fixture
  Scenario: Exchange a valid SelfCare identity token
    Given the RDB identity token fixture is "valid"
    When the user exchanges the SelfCare token for an RDB token
    Then the RDB response has HTTP status 200
    And the returned RDB token identifies the expected role and organization

  @rdb_fixture
  Scenario Outline: Reject a SelfCare token with invalid claims or signature
    Given the RDB identity token fixture is "<condition>"
    When the user exchanges the SelfCare token for an RDB token
    Then the RDB response has HTTP status 401

    Examples:
      | condition         |
      | invalid signature |
      | invalid issuer    |
      | invalid audience  |

  Scenario: Reject a request without an authentication token
    Given the RDB user has no application token
    When the RDB user requests the initiatives
    Then the RDB response has HTTP status 401

  @rdb_fixture
  Scenario: Reject an expired application token
    Given the RDB application token fixture is "expired"
    When the RDB user requests the initiatives
    Then the RDB response has HTTP status 401

  Scenario: A producer cannot approve a product
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"
    And RDB product "X" has initial status "WAIT_APPROVED"
    When the RDB user changes products "X" from "WAIT_APPROVED" to "APPROVED"
    Then the RDB response has HTTP status 403
    And RDB product "X" is unchanged
