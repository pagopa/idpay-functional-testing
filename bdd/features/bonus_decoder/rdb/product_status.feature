@bonus_decoder @rdb @product_status
Feature: Reject product status changes through the decoder initiative
  The product belongs to the appliances initiative A.
  The attempted update uses the decoder initiative B.

  Background:
    Given the RDB initiative is "A"

  @rdb_fixture
  Scenario: Do not update a product through another initiative
    Given the RDB user is authenticated as "Invitalia"
    And RDB product "X" has initial status "UPLOADED"
    And the RDB initiative is "B"
    When the RDB user changes products "X" from "UPLOADED" to "REJECTED"
    Then the RDB request is rejected
    And RDB product "X" is unchanged
