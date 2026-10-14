@bonus_elettrodomestici @rdb @authorization
Feature: Access and authorization to RDB

  # Application tokens are issued by /idpay-itn/register/token/test.
  # This flow does not exercise the real SelfCare identity-token exchange.
  Scenario: Access RDB with a generated application token
    Given the RDB user is authenticated as "producer"
    When the RDB user requests the initiatives
    Then the RDB response has HTTP status 200
    And the generated RDB token identifies the authenticated role and organization

  Scenario Outline: Reject an application token with invalid claims or signature
    Given an RDB application token with "<condition>" is generated
    When the RDB user requests the initiatives
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
  # Use a configured expired JWT or ask the test signer to preserve an expired exp.
  # Fail during preparation if the deployed signer still forces an 8-hour lifetime.
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
