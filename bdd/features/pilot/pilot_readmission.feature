@Scontoditipo1
@Scontoditipo1_not_started
@readmission
Feature: Readmission

  Scenario: The Institution tries to readmit a suspended citizen during the fruition period and receives an OK result
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the institution suspends correctly the citizen A
    When the institution tries to readmit the citizen A
    Then the citizen A is readmitted

  Scenario: The Institution tries to readmit a citizen not registered in the initiative and receives a KO
    Given the initiative is "Scontoditipo1"
    And the citizen A is 25 years old at most
    When the institution tries to readmit the citizen A
    Then the latest readmission fails not finding the citizen

  Scenario: A readmitted citizen confirms successfully a transaction and is rewarded
    Given the initiative is "Scontoditipo1"
    And the random merchant 1 is onboard
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    And the institution suspends correctly the citizen A
    And the institution readmits correctly the citizen A
    And the merchant 1 generates the transaction X of amount 2001 cents
    When the citizen A confirms the transaction X
    Then the transaction X is authorized
    And the citizen A is rewarded with 20.01 euros
