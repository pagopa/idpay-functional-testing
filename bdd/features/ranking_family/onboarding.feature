@family_ranking_initiative
@ranking
@family
@onboarding
Feature: A family onboards an initiative with ranking

  Background:
    Given a new initiative "family_ranking_initiative"

    @test
    Scenario Outline: Families with different ISEE onboard to ranking initiative in the correct order, given by ISEE value
      Given citizens <citizens> have fiscal code random
      And citizens <citizens> are in the same family
      And citizens A,B,C have ISEE 32568 of type "ordinario"
      And citizens D,E,F have ISEE 19999 of type "ordinario"
      And the first citizen of <citizens> onboards and wait for ranking
      When the ranking period ends
      And the institution publishes the ranking
      Then A D are elected
      And the onboards of B C E F are demanded
      And D A are ranked in the correct order

      Examples: Family members
        | citizens  |
        | A,B,C     |
        | D,E,F     |
