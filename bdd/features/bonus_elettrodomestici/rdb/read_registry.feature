@bonus_elettrodomestici @rdb @read_registry
Feature: Consult products, batches and producers in the RDB registry

  Background:
    Given the RDB initiative is "A"

  @rdb_fixture
  Scenario Outline: Restrict product visibility to the selected organization
    Given the RDB dataset is "<dataset>"
    When the RDB user requests the dataset products
    Then the returned RDB product GTINs match the dataset
    And the returned RDB products belong to the expected organization and initiative

    Examples:
      | dataset            |
      | producer registry  |
      | Invitalia registry |

  @rdb_fixture
  Scenario Outline: Filter products by a supported field
    Given the RDB dataset is "product filters"
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

  @rdb_fixture
  Scenario Outline: Restrict batches to the selected organization
    Given the RDB dataset is "<dataset>"
    When the RDB user requests the CSV batches
    Then the returned RDB batch IDs match the dataset

    Examples:
      | dataset                  |
      | organization CSV batches |
      | foreign CSV batches      |

  @rdb_fixture
  Scenario: List the producers associated with the initiative
    Given the RDB dataset is "initiative producers"
    When the RDB user requests the producers
    Then the returned RDB producer IDs match the dataset

  @rdb_fixture
  Scenario: Retrieve a producer registered in SelfCare
    Given the RDB dataset is "SelfCare producer"
    When the RDB user requests the producer details
    Then the RDB producer details identify the requested institution

  @rdb_fixture
  Scenario: Reject an unauthorized request for producer information
    Given the RDB dataset is "unauthorized producer details"
    When the RDB user requests the producer details
    Then the RDB response has HTTP status 403
