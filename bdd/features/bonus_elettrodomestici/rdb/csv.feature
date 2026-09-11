@bonus_elettrodomestici @rdb @csv
Feature: Manage the product CSV lifecycle
  A producer validates and uploads product files, monitors processing,
  and retrieves the upload history and error reports.
  Scenarios sharing a csv_flow tag describe the same business flow.
  Each scenario is independent and prepares its own preconditions.

  Background:
    Given the RDB user is authenticated as "producer"
    And the RDB initiative is "A"

  # Flow: Successful validation, upload and product registration

  @csv_flow_success @csv_upload_and_validate
  Scenario: Validate a CSV compliant with the initiative template
    Given the producer is enabled for the RDB initiative
    And a valid RDB product CSV with 1 rows
    When the producer validates the RDB product CSV
    Then the RDB operation has outcome "OK"

  @csv_flow_success @upload_csv
  Scenario: Accept a valid CSV for processing
    Given the producer is enabled for the RDB initiative
    And a valid RDB product CSV with 1 rows
    When the producer uploads the RDB product CSV
    Then the RDB operation has outcome "OK"
    And the RDB CSV finishes with status "LOADED"

  @csv_flow_success @csv_processing
  Scenario: Store every valid product
    Given the producer is enabled for the RDB initiative
    And a valid RDB product CSV with 2 rows
    When the producer uploads the RDB product CSV
    Then the RDB operation has outcome "OK"
    And the RDB CSV finishes with status "LOADED"
    And all submitted RDB products have status "UPLOADED"

  @csv_flow_success @csv_processing
  Scenario: Process cooking hobs without requiring EPREL data
    Given the producer is enabled for the RDB initiative
    And a valid RDB product CSV with 1 rows
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And all submitted RDB products have status "UPLOADED"
    And the submitted RDB products have no EPREL code


  # Flow: Formal validation errors, rejected uploads and validation reports

  @csv_flow_formal_errors @csv_upload_and_validate
  Scenario Outline: Reject invalid CSV file constraints
    Given the producer is enabled for the RDB initiative
    And the RDB product CSV has defect "<defect>"
    When the producer validates the RDB product CSV
    Then the RDB operation fails with error "<error>"

    Examples:
      | defect                 | error                          |
      | not a CSV file         | product.invalid.file.extension |
      | empty                  | product.invalid.file.empty     |
      | header only            | product.invalid.file.empty     |
      | larger than 2 MB       | product.invalid.file.maxsize   |
      | more than 100 rows     | product.invalid.file.maxrow    |
      | missing headers        | product.invalid.file.header    |
      | additional headers     | product.invalid.file.header    |
      | headers in wrong order | product.invalid.file.header    |
      | unsupported category   | product.invalid.file.category  |
      | mismatching category   | product.invalid.file.report    |

  @csv_flow_formal_errors @csv_upload_and_validate
  Scenario: Report every formal error in the same row
    Given the producer is enabled for the RDB initiative
    And the RDB product CSV has defect "multiple row errors"
    When the producer validates the RDB product CSV
    Then the RDB operation fails with error "product.invalid.file.report"
    And the RDB formal report contains errors for "Codice GTIN/EAN, Marca, Modello"

  @csv_flow_formal_errors @upload_csv
  Scenario: Do not process an invalid CSV
    Given the producer is enabled for the RDB initiative
    And the RDB product CSV has defect "mismatching category"
    When the producer uploads the RDB product CSV
    Then the RDB operation fails with error "product.invalid.file.report"
    And the submitted RDB CSV is absent from upload history
    And none of the submitted RDB products are stored

  @csv_flow_formal_errors @csv_history
  Scenario: Exclude a CSV with formal errors from history
    Given the RDB product CSV has defect "multiple row errors"
    When the producer validates the RDB product CSV
    Then the RDB operation fails with error "product.invalid.file.report"
    And the submitted RDB CSV is absent from upload history

  @csv_flow_formal_errors @csv_history
  Scenario: Download a formal validation report
    Given the RDB product CSV has defect "multiple row errors"
    When the producer validates the RDB product CSV
    Then the RDB operation fails with error "product.invalid.file.report"
    And the RDB formal report contains errors for "Codice GTIN/EAN, Marca, Modello"


  # Flow: Concurrent uploads and isolation between initiatives

  @csv_flow_initiative_isolation @upload_csv @rdb_fixture
  Scenario: Reject concurrent uploads for the same initiative and organization
    Given the producer is enabled for the RDB initiative
    And the RDB dataset is "upload in progress"
    And an RDB CSV is already being processed
    And a valid RDB product CSV with 1 rows
    When the producer uploads the RDB product CSV
    Then the RDB operation fails with error "product.invalid.file.already_in_progress"

  @csv_flow_initiative_isolation @upload_csv @rdb_fixture
  Scenario: Allow an upload on another initiative
    Given the producer is enabled for the RDB initiative
    And the RDB dataset is "upload in progress"
    And an RDB CSV is already being processed
    And the RDB initiative is "B"
    And the producer is enabled for the RDB initiative
    And a valid RDB product CSV with 1 rows
    When the producer uploads the RDB product CSV
    Then the RDB operation has outcome "OK"
    And the RDB CSV finishes with status "LOADED"

  @csv_flow_initiative_isolation @csv_processing @rdb_fixture
  Scenario: Manage the same GTIN independently across initiatives
    Given the producer is enabled for the RDB initiative
    And RDB product "X" has initial status "UPLOADED"
    And the RDB CSV updates product "X"
    And the RDB initiative is "B"
    And the producer is enabled for the RDB initiative
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And the submitted RDB product belongs to the selected initiative
    And RDB product "X" is unchanged


  # Flow: EPREL validation and complete or partial product processing

  @csv_flow_eprel @csv_processing @rdb_fixture @eprel
  Scenario: Accept a published and compliant EPREL product
    Given the producer is enabled for the RDB initiative
    And the RDB EPREL CSV case is "valid"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And all submitted RDB products have status "UPLOADED"

  @csv_flow_eprel @csv_processing @rdb_fixture @eprel
  Scenario Outline: Discard products failing an EPREL check
    Given the producer is enabled for the RDB initiative
    And the RDB EPREL CSV case is "<condition>"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "PARTIAL"
    And none of the submitted RDB products are stored
    And the RDB processing report contains the expected EPREL error

    Examples:
      | condition                  |
      | product not found          |
      | product not published      |
      | product blocked            |
      | organization not verified  |
      | brand not verified         |
      | category mismatch          |
      | energy class below minimum |

  @csv_flow_eprel @csv_processing @rdb_fixture @eprel
  Scenario: An invalid product does not prevent valid products from being stored
    Given the producer is enabled for the RDB initiative
    And the RDB EPREL CSV case is "mixed"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "PARTIAL"
    And only the valid EPREL rows are stored
    And the RDB processing report contains the expected EPREL error


  # Flow: Duplicate GTIN handling and repeatable processing reports

  @csv_flow_duplicates @csv_processing
  Scenario: Keep the first occurrence of a duplicated GTIN
    Given the producer is enabled for the RDB initiative
    And the RDB CSV contains duplicate GTIN rows with different product codes
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "PARTIAL"
    And only the first occurrence of the RDB GTIN is stored
    And the RDB processing report contains "duplicato"

  @csv_flow_duplicates @csv_history
  Scenario: Download a processing report repeatedly
    Given the RDB CSV contains duplicate GTIN rows with different product codes
    And the RDB CSV has been uploaded and processed
    When the producer downloads the RDB processing report 2 times
    Then every RDB report download succeeds with identical content
    And the RDB processing report contains "duplicato"


  # Flow: Reload products according to their current status

  @csv_flow_reload @csv_processing
  Scenario Outline: Reload a product from an allowed status
    Given the producer is enabled for the RDB initiative
    And RDB product "X" has initial status "<status>"
    And the RDB CSV updates product "X"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "LOADED"
    And RDB product "X" contains the new CSV data and batch

    Examples:
      | status   |
      | UPLOADED |
      | REJECTED |

  @csv_flow_reload @csv_processing
  Scenario: Preserve a product that is already under review
    Given the producer is enabled for the RDB initiative
    And RDB product "X" has initial status "WAIT_APPROVED"
    And the RDB CSV updates product "X"
    When the producer uploads the RDB product CSV
    Then the RDB CSV finishes with status "PARTIAL"
    And RDB product "X" is unchanged


  # Flow: Upload history, pagination and report access control

  @csv_flow_history @csv_history @rdb_fixture
  Scenario: List only uploads belonging to the organization and initiative
    Given the RDB dataset is "CSV history"
    When the producer requests the RDB CSV history
    Then the returned RDB upload IDs match the dataset
    And the RDB uploads are ordered by date descending

  @csv_flow_history @csv_history @rdb_fixture
  Scenario: Paginate the CSV upload history
    Given the RDB dataset is "CSV history"
    And the RDB CSV history contains at least 3 uploads
    When the producer requests RDB CSV history page 1 with size 2
    Then the RDB CSV history page and metadata are correct

  @csv_flow_history @csv_history @rdb_fixture
  Scenario Outline: Reject access to an inaccessible report
    Given the RDB dataset is "<dataset>"
    When the producer downloads the dataset report
    Then the RDB response has HTTP status 404

    Examples:
      | dataset                        |
      | report from another producer   |
      | report from another initiative |
      | upload without report          |
