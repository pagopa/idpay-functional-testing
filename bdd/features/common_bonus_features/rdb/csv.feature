@rdb @csv @bonus_decoder @bonus_elettrodomestici
Feature: Isolate CSV upload history across organizations and initiatives
  The history request targets appliances initiative A.
  Uploads on decoder initiative B provide an initiative isolation control.

  @csv_flow_history @csv_history @rdb_fixture
  Scenario: List only uploads belonging to the organization and initiative
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"
    And the RDB dataset is "CSV history"
    When the producer requests the RDB CSV history
    Then the RDB CSV history includes known uploads and excludes foreign uploads
    And the RDB uploads are ordered by date descending
