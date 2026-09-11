@bonus_elettrodomestici @rdb @initiatives @rdb_fixture
Feature: List the initiatives available to an RDB organization

  Scenario Outline: Return exactly the initiatives visible to the current user
    Given the RDB dataset is "<dataset>"
    When the RDB user requests the initiatives
    Then the returned RDB initiative IDs match the dataset
    And the RDB initiatives are enabled

    Examples:
      | dataset                            |
      | producer enabled initiatives       |
      | producer disabled association      |
      | producer without initiatives       |
      | Invitalia organization initiatives |
      | Invitalia foreign initiative       |

  Scenario: Sort the producer initiatives by name
    Given the RDB dataset is "producer enabled initiatives"
    When the RDB user requests the initiatives
    Then the returned RDB initiative IDs match the dataset
    And the RDB initiatives are ordered by name
