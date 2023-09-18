@ranking_initiative
@ranking
Feature: A citizen onboards an initiative with ranking

  Background:
    Given the initiative is "ranking_initiative"

  @test
  Scenario Outline: Citizens onboard to ranking initiative
    Given the citizen A has fiscal code random
    And the citizen A has ISEE 39999 of type "ordinario"
    And the citizen B has fiscal code random
    And the citizen B has ISEE 29999 of type "ordinario"
    And the citizen C has fiscal code random
    And the citizen C has ISEE 19999 of type "ordinario"
    When <citizens> onboard and wait for ranking
    And the ranking period ends and the institution publishes the ranking
    Then <citizens> are elected
    And <ordered citizens> are ranked in the correct order

    Examples: Those citizens onboard and are ranked in the correct order based on the ISEE
      | citizens        | ordered citizens |
      | ["A", "B", "C"] | ["C", "B", "A"]  |
