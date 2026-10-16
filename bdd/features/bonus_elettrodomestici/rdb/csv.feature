@bonus_elettrodomestici @rdb @csv
Feature: Manage the product CSV lifecycle
  A producer validates and uploads product files, monitors processing,
  and views the upload history and downloads error reports for individual uploads.
  The portal offers an Excel error report, not an export of the CSV upload history.
  These API tests read the backend report data used by the portal.
  Scenarios sharing a csv_flow tag describe the same business flow.
  Each scenario is independent and prepares its own preconditions.

  Background:
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"

  # Flow: EPREL validation and complete or partial product processing

  @csv_flow_eprel @csv_processing @rdb_fixture @eprel
  Scenario: Accept a published and compliant EPREL product
    Given the producer is enabled for the RDB initiative
    And the RDB EPREL CSV case is "valid"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And all submitted RDB products have status "UPLOADED"

  @csv_flow_eprel @csv_processing @rdb_fixture @eprel
  Scenario Outline: Discard products failing an EPREL check
    Given the producer is enabled for the RDB initiative
    And the RDB EPREL CSV case is "<condition>"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "PARTIAL"
    And none of the submitted RDB products are stored
    And the RDB processing report contains the expected EPREL error

    Examples:
      | condition                  |
      | category mismatch          |
      | energy class below minimum |

  @csv_flow_eprel @csv_processing @rdb_fixture @eprel
  Scenario: An invalid product does not prevent valid products from being stored
    Given the producer is enabled for the RDB initiative
    And the RDB EPREL CSV case is "mixed"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "PARTIAL"
    And only the valid EPREL rows are stored
    And the RDB processing report contains the expected EPREL error
