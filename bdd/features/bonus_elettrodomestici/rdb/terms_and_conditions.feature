@bonus_elettrodomestici @rdb @terms_and_conditions @term_and_conditions
Feature: Accept the current version of the RDB terms and conditions

  Background:
    Given a new RDB user authenticated as "producer"

  Scenario: Request consent for a user who has never accepted
    When the RDB user requests the consent status
    Then the RDB consent requires first acceptance of the current version

  Scenario: Do not request acceptance of an already accepted version
    Given the RDB user has accepted the current consent version
    When the RDB user requests the consent status
    Then no RDB consent acceptance is required

  @rdb_fixture
  Scenario: Request acceptance after the terms and conditions change
    Given the RDB dataset is "previous consent version"
    When the RDB user requests the consent status
    Then the RDB consent requires renewed acceptance of the current version

  Scenario: Store acceptance of the current terms and conditions
    Given the RDB user knows the current consent version
    When the RDB user accepts the current consent version
    Then the RDB response has HTTP status 200
    And no RDB consent acceptance is required after reading it again

  Scenario: Reject acceptance of an outdated version
    Given the RDB user knows the current consent version
    When the RDB user accepts an outdated consent version
    Then the RDB response has HTTP status 400
    And the RDB consent still requires first acceptance

  @rdb_fixture
  Scenario: Do not store consent when OneTrust is unavailable
    Given the RDB user knows the current consent version
    And the RDB dependency "OneTrust" is unavailable
    When the RDB user accepts the current consent version
    Then the RDB consent request fails because OneTrust is unavailable
    And the RDB consent still requires first acceptance after OneTrust recovers
