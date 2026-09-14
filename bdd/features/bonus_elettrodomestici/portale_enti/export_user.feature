@bonus_elettrodomestici
@portale_enti
@report_csv
Feature: Export User Details (Report CSV)
  Background:
    Given the initiative is "bonus_elettrodomestici"
    And the merchant 1 is qualified

  Scenario Outline: Operator requests the USER_DETAILS CSV report export correctly
    Given the operator with role <role> prepares report type USER_DETAILS for merchant 1 with a date range of 30 days
    When the operator tries to request the CSV report export
    Then the report request is inserted

    Examples:
      | role |
      | l1   |
      | l2   |
      | l3   |

  Scenario Outline: Operator downloads the generated USER_DETAILS CSV report correctly
    Given the operator with role <role> prepares report type USER_DETAILS for merchant 1 with a date range of 30 days
    And the operator requests the CSV report export
    And the report request is inserted
    When the operator tries to download the generated CSV report
    Then the CSV report is downloaded correctly

    Examples:
      | role |
      | l1   |
      | l2   |
      | l3   |
