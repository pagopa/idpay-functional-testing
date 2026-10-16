@bonus_elettrodomestici @rdb @read_registry
Feature: Filter appliance products by EPREL code

  Background:
     Given the RDB initiative is "A"

  @rdb_fixture @eprel
  Scenario: Filter products by EPREL code
    Given RDB products are prepared for filter "EPREL code"
    When the RDB user filters products by "EPREL code"
    Then only RDB products matching the selected filters are returned
