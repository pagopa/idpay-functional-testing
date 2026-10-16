@bonus_decoder @rdb @csv
Feature: Manage the decoder product CSV lifecycle across initiatives
  These scenarios verify operations on the decoder initiative B.
  Products and uploads on the appliances initiative A provide isolation controls.
  Each scenario is independent and prepares its own preconditions.

  Background:
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"

  # Flow: Concurrent uploads and isolation between initiatives

  @csv_flow_initiative_isolation @upload_csv @rdb_fixture
  Scenario: Allow an upload on another initiative
    Given a new RDB CSV is prepared for concurrent processing on initiative A
    And the RDB initiative is "B"
    And the producer is enabled for the RDB initiative
    And a valid RDB product CSV with 1 rows
    And the RDB CSV uses the decoder template
    When the producer uploads the RDB product CSV during the first processing
    Then the first RDB CSV was processing before and after the second upload request
    And the RDB operation has outcome "OK"
    And the RDB CSV finishes with status "LOADED"

  @csv_flow_initiative_isolation @csv_processing @rdb_fixture
  Scenario: Manage the same GTIN independently across initiatives
    Given the producer is enabled for the RDB initiative
    And RDB product "X" has initial status "UPLOADED"
    And the RDB CSV updates product "X"
    And the RDB initiative is "B"
    And the producer is enabled for the RDB initiative
    And the RDB CSV uses the decoder template
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And the submitted RDB product belongs to the selected initiative
    And RDB product "X" is unchanged

  # Flow: Upload history, pagination and report access control

  @csv_flow_history @csv_history @rdb_fixture
  Scenario Outline: Reject access to an inaccessible report
    Given the RDB dataset is "<dataset>"
    When the producer downloads the dataset report
    Then the RDB response has HTTP status 404

    Examples:
      | dataset                        |
      | report from another initiative |
