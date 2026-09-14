@bonus_elettrodomestici @rdb @producer
Feature: Manage producer associations and operational email

  Background:
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"

  @rdb_import
  Scenario: Import valid producer associations
    Given the RDB producer association payload is "valid"
    When the RDB producer associations are imported
    Then the RDB import counts are 1 received, 1 imported and 0 failed
    And the RDB producer association is stored once

  @rdb_import
  Scenario: Reject an empty association payload
    Given the RDB producer association payload is "empty"
    When the RDB producer associations are imported
    Then the RDB response has HTTP status 400

  @rdb_import
  Scenario Outline: Count an association missing a mandatory field as failed
    Given the RDB producer association payload is "missing <field>"
    When the RDB producer associations are imported
    Then the RDB import counts are 1 received, 0 imported and 1 failed

    Examples:
      | field        |
      | initiativeId |
      | producerId   |
      | producerName |

  @rdb_import
  Scenario Outline: Normalize the producer email during import
    Given the RDB producer association payload has email "<email>"
    When the RDB producer associations are imported
    Then the RDB import counts are 1 received, 1 imported and 0 failed
    And the RDB operational email is "<stored>"

    Examples:
      | email          | stored         |
      | rdb@example.it | rdb@example.it |
      | invalid-email  | null           |

  @rdb_import
  Scenario: Reimport an association without creating duplicates
    Given the RDB producer association payload is "valid"
    And the RDB producer association has already been imported
    When the RDB producer associations are imported
    Then the RDB import counts are 1 received, 1 imported and 0 failed
    And the RDB producer association is stored once

  Scenario: Replace the previous operational email
    Given the producer is enabled for the RDB initiative
    And the RDB operational email was set to "old@example.it"
    When the producer sets the RDB operational email to "new@example.it"
    Then the RDB operation has outcome "OK"
    And the RDB operational email is "new@example.it"

  Scenario: Reject an invalid operational email
    Given the producer is enabled for the RDB initiative
    When the producer sets the RDB operational email to "invalid-email"
    Then the RDB request is rejected

  @rdb_fixture
  Scenario: Reject an email update for an unrelated initiative
    Given the RDB dataset is "unassociated initiative"
    When the producer sets the RDB operational email to "new@example.it"
    Then the RDB operation fails with error "update.email.invalid.initiative"
