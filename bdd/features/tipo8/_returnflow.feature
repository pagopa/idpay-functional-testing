Feature: For a refund, there is a return flow 

Background:
    Given the initiative is "Scontoditipo8"
    And the citizen A is 25 years old at most
    And the citizen A is onboard
    Then the transaction is OK

  @Returnflow
  @Scontoditipo8
  @skip
  Scenario: Against a payment order, the return flow is ok

  @Returnflow
  @Scontoditipo8
  @skip
  Scenario: Against a payment order, the return flow is ko