@bonus_elettrodomestici @rdb @read_registry
Feature: Consult products, batches and producers in the RDB registry

  Background:
    Given the RDB initiative is "A"

  @rdb_fixture
  Scenario Outline: Filter products by a supported field
    Given RDB products are prepared for filter "<filter>"
    When the RDB user filters products by "<filter>"
    Then only RDB products matching the selected filters are returned

    Examples:
      | filter       |
      | category     |
      | CSV upload   |
      | EPREL code   |
      | GTIN         |
      | product name |
      | brand        |
      | model        |
      | status       |

  @rdb_fixture
  Scenario: Combine product filters
    Given the RDB dataset is "product filters"
    When the RDB user filters products by "category, brand, model, status"
    Then only RDB products matching the selected filters are returned

  Scenario: Return an empty result for a nonexistent GTIN
    Given the RDB user is authenticated as "producer"
    And RDB product "X" does not exist
    When the RDB user searches for product "X"
    Then the RDB product list is empty
