@bonus_elettrodomestici
@bonus_decoder
@portale_enti
@report_csv
Feature: Export Transactions (Report CSV)
  Background:
    Given the initiative is active
    And the merchant 1 is qualified

  Scenario Outline: Operator requests the CSV report export correctly
    Given the operator with role <role> selects merchant 1 and a date range of 30 days
    When the operator tries to request the CSV report export
    Then the report request is inserted

    Examples:
      | role |
      | l1   |
      | l2   |
      | l3   |

  Scenario Outline: Operator requests the CSV report export with a range exceeding the maximum allowed
    Given the operator with role <role> selects merchant 1 and a date range of 92 days
    When the operator tries to request the CSV report export
    Then the report request is rejected because the range exceeds 90 days

    Examples:
      | role |
      | l1   |
      | l2   |
      | l3   |

  # Run generation polling once; the other roles only check download authorization.
  Scenario: Operator downloads the generated CSV report correctly
    Given the operator with role l1 selects merchant 1 and a date range of 30 days
    And the operator requests the CSV report export
    And the report request is inserted
    When the operator tries to download the generated CSV report within 600 seconds
    Then the CSV report is downloaded correctly

  Scenario Outline: Operator is authorized to download the CSV report
    Given the operator with role <role> selects merchant 1 and a date range of 30 days
    And the operator requests the CSV report export
    And the report request is inserted
    When the operator checks access to the CSV report download without waiting for generation
    Then the operator is authorized to download the CSV report

    Examples:
      | role |
      | l2   |
      | l3   |
