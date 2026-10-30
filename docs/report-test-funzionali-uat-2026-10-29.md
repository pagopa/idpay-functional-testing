# Esecuzione completa dei test funzionali — 29 ottobre 2026

Ambiente: **UAT**. Esecuzione autorizzata dall'utente il 29 ottobre 2026.
Eseguita sul working tree corrente, che include la bonifica e il riesame dopo il merge da main.
I risultati dei giorni precedenti non sono riutilizzati come esito di questa esecuzione.

## Perimetro e modalità

- Tutte le directory BDD attive: `common_bonus_features`, `bonus_elettrodomestici`, `bonus_decoder`.
- Due esecuzioni sequenziali, con tag `bonus_elettrodomestici` e `bonus_decoder`, come la matrice CI.
- Terza esecuzione con `not (bonus_elettrodomestici or bonus_decoder)` per includere i 15 casi senza tag Bonus esclusi dalla matrice CI; selezione iniziativa predefinita Elettrodomestici per gli hook.
- I casi comuni vengono eseguiti per entrambe le iniziative; i conteggi delle due righe non rappresentano scenari unici.
- Configurazione UAT locale ignorata da Git; cleanup dei reward batch e lifecycle degli hook abilitati.
- Nessuna modifica ai secret, agli scenari o alle asserzioni per ottenere esiti positivi.
- Test unitari offline: **32 superati**, eseguiti separatamente con HTTP simulato.

## Esecuzioni

| Tag | Stato processo | Superati | Falliti | Errori scenario | Errori hook | Inizio UTC | Fine UTC | Exit code |
|---|---|---:|---:|---:|---:|---|---|---:|
| `bonus_elettrodomestici` | failed | 0 | 0 | 59 | 79 | 2026-10-29T16:10:57.845560+00:00 | 2026-10-29T16:11:11.044183+00:00 | 1 |
| `bonus_decoder` | failed | 0 | 0 | 56 | 77 | 2026-10-29T16:11:11.081719+00:00 | 2026-10-29T16:11:16.835083+00:00 | 1 |
| `common_without_bonus_tag` | failed | 1 | 0 | 0 | 14 | 2026-10-29T16:15:10.768864+00:00 | 2026-10-29T16:15:13.464809+00:00 | 1 |

Le celle senza conteggio indicano che il report JSON è ancora in scrittura oppure che il processo è terminato prima di completarlo.

## bonus_elettrodomestici

Report JUnit leggibili: 16; conteggi JUnit: `{'cases': 138, 'error': 138}`.

Classi di errore rilevate nei log: `ConnectionError`, `MaxRetryError`, `NameResolutionError`.

- DNS UAT non disponibile: impossibile risolvere l’host interno (getaddrinfo 11001). Bloccate statistiche iniziativa e verifica capabilities del cleanup RDB; non è un’asserzione funzionale fallita.
- Sono presenti errori negli hook; verificare i log locali prima di dichiarare completato il cleanup.

### Scenari falliti o in errore

| Scenario | Stato |
|---|---|
| An onboarded citizen creates a barcode payment accepted by a merchant | error |
| A citizen's second barcode payment is rejected | error |
| A merchant captures an authorized barcode payment | error |
| A point of sale cancels an authorized barcode payment | error |
| A point of sale cannot cancel a captured barcode payment | error |
| A merchant invoices a captured barcode payment | error |
| A merchant invoices an already invoiced barcode payment | error |
| A merchant reverses an invoiced barcode payment | error |
| Citizen without email tries to onboard successfully | error |
| Citizen with mismatching email tries to onboard unsuccessfully | error |
| A citizen with self-declared incorrect criteria tries to onboard unsuccessfully | error |
| A citizen who has not accepted the Terms and Conditions tries to onboard unsuccessfully | error |
| A citizen who denied PDND consent tries to onboard unsuccessfully | error |
| A citizen tries to onboard a nonexistent initiative | error |
| A citizen tries to onboard a non published initiative | error |
| A citizen tries to onboard a non started initiative | error |
| A citizen tries to onboard an initiative with residual budget less than 100 euros | error |
| An unsubscribed citizen onboards the same initiative again successfully | error |
| Point of sale invoice updates are rejected while the reward batch is SENT or EVALUATING | error |
| Evaluating a sent reward batch rewards its invoiced transactions synchronously | error |
| A merchant updates an invoice while the reward batch is EVALUATING | error |
| An invoiced payment is associated with a reward batch | error |
| Reversing an invoiced payment removes it from its reward batch | error |
| A merchant sends an empty reward batch | error |
| A merchant postpones a transaction to the next reward batch | error |
| Eligible merchant onboards successfully | error |
| Merchant without eligible ATECO fails to onboard | error |
| Eligible merchant already onboarded fails to onboard | error |
| Operator requests the CSV report export correctly -- @1.1  | error |
| Operator requests the CSV report export correctly -- @1.2  | error |
| Operator requests the CSV report export correctly -- @1.3  | error |
| Operator requests the CSV report export with a range exceeding the maximum allowed -- @1.1  | error |
| Operator requests the CSV report export with a range exceeding the maximum allowed -- @1.2  | error |
| Operator requests the CSV report export with a range exceeding the maximum allowed -- @1.3  | error |
| Operator downloads the generated CSV report correctly -- @1.1  | error |
| Operator downloads the generated CSV report correctly -- @1.2  | error |
| Operator downloads the generated CSV report correctly -- @1.3  | error |
| Operator requests the USER_DETAILS CSV report export correctly -- @1.1  | error |
| Operator requests the USER_DETAILS CSV report export correctly -- @1.2  | error |
| Operator requests the USER_DETAILS CSV report export correctly -- @1.3  | error |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.1  | error |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.2  | error |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.3  | error |
| L1 operator tries to validate unsuccessfully a reward batch without performing checks on at least 15% of the transactions | error |
| L1 Operator tries to validate successfully a reward batch after performing checks on at least 15% of the transactions | error |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | error |
| L3 Operator approves the reward batch | error |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | error |
| An approved reward batch keeps its suspended amount after removing suspended transactions | error |
| Operator downloads the approved reward batch report | error |
| Validate a CSV compliant with the initiative template | hook_error |
| Accept a valid CSV for processing | hook_error |
| Store every valid product | hook_error |
| Process cooking hobs without requiring EPREL data | hook_error |
| Reject invalid CSV file constraints -- @1.1  | hook_error |
| Reject invalid CSV file constraints -- @1.2  | hook_error |
| Reject invalid CSV file constraints -- @1.3  | hook_error |
| Reject invalid CSV file constraints -- @1.4  | hook_error |
| Reject invalid CSV file constraints -- @1.5  | hook_error |
| Reject invalid CSV file constraints -- @1.6  | hook_error |
| Reject invalid CSV file constraints -- @1.7  | hook_error |
| Reject invalid CSV file constraints -- @1.8  | hook_error |
| Reject invalid CSV file constraints -- @1.9  | hook_error |
| Reject a CSV larger than 2 MB with temporary server error tolerance | hook_error |
| Report every formal error in the same row | hook_error |
| Do not process an invalid CSV | hook_error |
| Exclude a CSV with formal errors from history | hook_error |
| Download a formal validation report | hook_error |
| Reject concurrent uploads for the same initiative and organization | hook_error |
| Keep the first occurrence of a duplicated GTIN | hook_error |
| Download a processing report repeatedly | hook_error |
| Reload a product from an allowed status -- @1.1  | hook_error |
| Reload a product from an allowed status -- @1.2  | hook_error |
| Preserve a product that is already under review | hook_error |
| Paginate the CSV upload history | hook_error |
| Reject access to an inaccessible report -- @1.1  | hook_error |
| Reject access to an inaccessible report -- @1.2  | hook_error |
| List only uploads belonging to the organization and initiative | hook_error |
| Return exactly the initiatives visible to the current user -- @1.1  | hook_error |
| Return exactly the initiatives visible to the current user -- @1.2  | hook_error |
| Return exactly the initiatives visible to the current user -- @1.3  | hook_error |
| Return exactly the initiatives visible to the current user -- @1.4  | hook_error |
| Sort the producer initiatives by name | hook_error |
| Process a CSV when the operational email is missing | hook_error |
| Reject a product when the operational email is missing | hook_error |
| Import valid producer associations | hook_error |
| Reject an empty association payload | hook_error |
| Count an association missing a mandatory field as failed -- @1.1  | hook_error |
| Count an association missing a mandatory field as failed -- @1.2  | hook_error |
| Count an association missing a mandatory field as failed -- @1.3  | hook_error |
| Normalize the producer email during import -- @1.1  | hook_error |
| Normalize the producer email during import -- @1.2  | hook_error |
| Reimport an association without creating duplicates | hook_error |
| Replace the previous operational email | hook_error |
| Reject an invalid operational email | hook_error |
| Reject an email update for an unrelated initiative | hook_error |
| Perform an allowed product status transition -- @1.1  | hook_error |
| Perform an allowed product status transition -- @1.2  | hook_error |
| Perform an allowed product status transition -- @1.3  | hook_error |
| Perform an allowed product status transition -- @1.4  | hook_error |
| Perform an allowed product status transition -- @1.5  | hook_error |
| Perform an allowed product status transition -- @1.6  | hook_error |
| Perform an allowed product status transition -- @1.7  | hook_error |
| An Invitalia operator cannot approve a product | hook_error |
| Reject an incorrect declared current status | hook_error |
| Reject a batch containing different current statuses | hook_error |
| Reject the entire batch when one product does not exist | hook_error |
| Do not update a product through another initiative | hook_error |
| Filter products by a supported field -- @1.1  | hook_error |
| Filter products by a supported field -- @1.2  | hook_error |
| Filter products by a supported field -- @1.3  | hook_error |
| Filter products by a supported field -- @1.4  | hook_error |
| Filter products by a supported field -- @1.5  | hook_error |
| Filter products by a supported field -- @1.6  | hook_error |
| Filter products by a supported field -- @1.7  | hook_error |
| Combine product filters | hook_error |
| Return an empty result for a nonexistent GTIN | hook_error |
| Restrict product visibility to the selected organization -- @1.1  | hook_error |
| Restrict product visibility to the selected organization -- @1.2  | hook_error |
| Restrict batches to the selected organization -- @1.1  | hook_error |
| Restrict batches to the selected organization -- @1.2  | hook_error |
| List the producers associated with the initiative | hook_error |
| Retrieve a producer registered in SelfCare | hook_error |
| Reject an unauthorized request for producer information | hook_error |
| Citizen onboards successfully | error |
| Citizen with ISEE lower than 25k tries to onboard successfully | error |
| Onboarded citizen with ISEE lower than 25k has a wallet with correct budget | error |
| Citizen with ISEE equal or above 25k tries to onboard successfully | error |
| Onboarded citizen with ISEE equal or above 25k has a wallet with correct budget | error |
| Citizen with no declared ISEE tries to onboard successfully | error |
| Onboarded citizen with no declared ISEE has a wallet with correct budget | error |
| A citizen with self-declared incorrect criteria tries to onboard unsuccessfully | error |
| Family members join first family's onboarding | error |
| Accept a published and compliant EPREL product | hook_error |
| Discard products failing an EPREL check -- @1.1  | hook_error |
| Discard products failing an EPREL check -- @1.2  | hook_error |
| An invalid product does not prevent valid products from being stored | hook_error |
| Filter products by EPREL code | hook_error |

## bonus_decoder

Report JUnit leggibili: 15; conteggi JUnit: `{'cases': 133, 'error': 133}`.

Classi di errore rilevate nei log: `ConnectionError`, `MaxRetryError`, `NameResolutionError`.

- DNS UAT non disponibile: impossibile risolvere l’host interno (getaddrinfo 11001). Bloccate statistiche iniziativa e verifica capabilities del cleanup RDB; non è un’asserzione funzionale fallita.
- Sono presenti errori negli hook; verificare i log locali prima di dichiarare completato il cleanup.

### Scenari falliti o in errore

| Scenario | Stato |
|---|---|
| An onboarded citizen creates a barcode payment accepted by a merchant | error |
| A citizen's second barcode payment is rejected | error |
| A merchant captures an authorized barcode payment | error |
| A point of sale cancels an authorized barcode payment | error |
| A point of sale cannot cancel a captured barcode payment | error |
| A merchant invoices a captured barcode payment | error |
| A merchant invoices an already invoiced barcode payment | error |
| A merchant reverses an invoiced barcode payment | error |
| Citizen without email tries to onboard successfully | error |
| Citizen with mismatching email tries to onboard unsuccessfully | error |
| A citizen with self-declared incorrect criteria tries to onboard unsuccessfully | error |
| A citizen who has not accepted the Terms and Conditions tries to onboard unsuccessfully | error |
| A citizen who denied PDND consent tries to onboard unsuccessfully | error |
| A citizen tries to onboard a nonexistent initiative | error |
| A citizen tries to onboard a non published initiative | error |
| A citizen tries to onboard a non started initiative | error |
| A citizen tries to onboard an initiative with residual budget less than 100 euros | error |
| An unsubscribed citizen onboards the same initiative again successfully | error |
| Point of sale invoice updates are rejected while the reward batch is SENT or EVALUATING | error |
| Evaluating a sent reward batch rewards its invoiced transactions synchronously | error |
| A merchant updates an invoice while the reward batch is EVALUATING | error |
| An invoiced payment is associated with a reward batch | error |
| Reversing an invoiced payment removes it from its reward batch | error |
| A merchant sends an empty reward batch | error |
| A merchant postpones a transaction to the next reward batch | error |
| Eligible merchant onboards successfully | error |
| Merchant without eligible ATECO fails to onboard | error |
| Eligible merchant already onboarded fails to onboard | error |
| Operator requests the CSV report export correctly -- @1.1  | error |
| Operator requests the CSV report export correctly -- @1.2  | error |
| Operator requests the CSV report export correctly -- @1.3  | error |
| Operator requests the CSV report export with a range exceeding the maximum allowed -- @1.1  | error |
| Operator requests the CSV report export with a range exceeding the maximum allowed -- @1.2  | error |
| Operator requests the CSV report export with a range exceeding the maximum allowed -- @1.3  | error |
| Operator downloads the generated CSV report correctly -- @1.1  | error |
| Operator downloads the generated CSV report correctly -- @1.2  | error |
| Operator downloads the generated CSV report correctly -- @1.3  | error |
| Operator requests the USER_DETAILS CSV report export correctly -- @1.1  | error |
| Operator requests the USER_DETAILS CSV report export correctly -- @1.2  | error |
| Operator requests the USER_DETAILS CSV report export correctly -- @1.3  | error |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.1  | error |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.2  | error |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.3  | error |
| L1 operator tries to validate unsuccessfully a reward batch without performing checks on at least 15% of the transactions | error |
| L1 Operator tries to validate successfully a reward batch after performing checks on at least 15% of the transactions | error |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | error |
| L3 Operator approves the reward batch | error |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | error |
| An approved reward batch keeps its suspended amount after removing suspended transactions | error |
| Operator downloads the approved reward batch report | error |
| Validate a CSV compliant with the initiative template | hook_error |
| Accept a valid CSV for processing | hook_error |
| Store every valid product | hook_error |
| Process cooking hobs without requiring EPREL data | hook_error |
| Reject invalid CSV file constraints -- @1.1  | hook_error |
| Reject invalid CSV file constraints -- @1.2  | hook_error |
| Reject invalid CSV file constraints -- @1.3  | hook_error |
| Reject invalid CSV file constraints -- @1.4  | hook_error |
| Reject invalid CSV file constraints -- @1.5  | hook_error |
| Reject invalid CSV file constraints -- @1.6  | hook_error |
| Reject invalid CSV file constraints -- @1.7  | hook_error |
| Reject invalid CSV file constraints -- @1.8  | hook_error |
| Reject invalid CSV file constraints -- @1.9  | hook_error |
| Reject a CSV larger than 2 MB with temporary server error tolerance | hook_error |
| Report every formal error in the same row | hook_error |
| Do not process an invalid CSV | hook_error |
| Exclude a CSV with formal errors from history | hook_error |
| Download a formal validation report | hook_error |
| Reject concurrent uploads for the same initiative and organization | hook_error |
| Keep the first occurrence of a duplicated GTIN | hook_error |
| Download a processing report repeatedly | hook_error |
| Reload a product from an allowed status -- @1.1  | hook_error |
| Reload a product from an allowed status -- @1.2  | hook_error |
| Preserve a product that is already under review | hook_error |
| Paginate the CSV upload history | hook_error |
| Reject access to an inaccessible report -- @1.1  | hook_error |
| Reject access to an inaccessible report -- @1.2  | hook_error |
| List only uploads belonging to the organization and initiative | hook_error |
| Return exactly the initiatives visible to the current user -- @1.1  | hook_error |
| Return exactly the initiatives visible to the current user -- @1.2  | hook_error |
| Return exactly the initiatives visible to the current user -- @1.3  | hook_error |
| Return exactly the initiatives visible to the current user -- @1.4  | hook_error |
| Sort the producer initiatives by name | hook_error |
| Process a CSV when the operational email is missing | hook_error |
| Reject a product when the operational email is missing | hook_error |
| Import valid producer associations | hook_error |
| Reject an empty association payload | hook_error |
| Count an association missing a mandatory field as failed -- @1.1  | hook_error |
| Count an association missing a mandatory field as failed -- @1.2  | hook_error |
| Count an association missing a mandatory field as failed -- @1.3  | hook_error |
| Normalize the producer email during import -- @1.1  | hook_error |
| Normalize the producer email during import -- @1.2  | hook_error |
| Reimport an association without creating duplicates | hook_error |
| Replace the previous operational email | hook_error |
| Reject an invalid operational email | hook_error |
| Reject an email update for an unrelated initiative | hook_error |
| Perform an allowed product status transition -- @1.1  | hook_error |
| Perform an allowed product status transition -- @1.2  | hook_error |
| Perform an allowed product status transition -- @1.3  | hook_error |
| Perform an allowed product status transition -- @1.4  | hook_error |
| Perform an allowed product status transition -- @1.5  | hook_error |
| Perform an allowed product status transition -- @1.6  | hook_error |
| Perform an allowed product status transition -- @1.7  | hook_error |
| An Invitalia operator cannot approve a product | hook_error |
| Reject an incorrect declared current status | hook_error |
| Reject a batch containing different current statuses | hook_error |
| Reject the entire batch when one product does not exist | hook_error |
| Do not update a product through another initiative | hook_error |
| Filter products by a supported field -- @1.1  | hook_error |
| Filter products by a supported field -- @1.2  | hook_error |
| Filter products by a supported field -- @1.3  | hook_error |
| Filter products by a supported field -- @1.4  | hook_error |
| Filter products by a supported field -- @1.5  | hook_error |
| Filter products by a supported field -- @1.6  | hook_error |
| Filter products by a supported field -- @1.7  | hook_error |
| Combine product filters | hook_error |
| Return an empty result for a nonexistent GTIN | hook_error |
| Restrict product visibility to the selected organization -- @1.1  | hook_error |
| Restrict product visibility to the selected organization -- @1.2  | hook_error |
| Restrict batches to the selected organization -- @1.1  | hook_error |
| Restrict batches to the selected organization -- @1.2  | hook_error |
| List the producers associated with the initiative | hook_error |
| Retrieve a producer registered in SelfCare | hook_error |
| Reject an unauthorized request for producer information | hook_error |
| Citizen onboards successfully | error |
| Citizen onboarding allocate correct budget for initiative | error |
| Citizen who has not paid Canone TV tries to onboard unsuccessfully | error |
| Citizen without email tries to onboard successfully | error |
| A citizen with self-declared incorrect criteria tries to onboard unsuccessfully | error |
| Family members join first family's onboarding | error |
| Allow an upload on another initiative | hook_error |
| Manage the same GTIN independently across initiatives | hook_error |
| Reject access to an inaccessible report -- @1.1  | hook_error |

## common_without_bonus_tag

Report JUnit leggibili: 4; conteggi JUnit: `{'cases': 15, 'passed': 1, 'error': 14}`.

Classi di errore rilevate nei log: `ConnectionError`, `NameResolutionError`.

- DNS UAT non disponibile: impossibile risolvere l’host interno (getaddrinfo 11001). Bloccate statistiche iniziativa e verifica capabilities del cleanup RDB; non è un’asserzione funzionale fallita.
- Sono presenti errori negli hook; verificare i log locali prima di dichiarare completato il cleanup.

### Scenari falliti o in errore

| Scenario | Stato |
|---|---|
| Access RDB with a generated application token | hook_error |
| Reject an application token with invalid claims or signature -- @1.1  | hook_error |
| Reject an application token with invalid claims or signature -- @1.2  | hook_error |
| Reject an application token with invalid claims or signature -- @1.3  | hook_error |
| Reject a request without an authentication token | hook_error |
| Reject an expired application token | hook_error |
| A producer cannot approve a product | hook_error |
| Accept a notification request for an RDB event -- @1.1  | hook_error |
| Accept a notification request for an RDB event -- @1.2  | hook_error |
| Accept a notification request for an RDB event -- @1.3  | hook_error |
| Request consent for a user who has never accepted | hook_error |
| Do not request acceptance of an already accepted version | hook_error |
| Store acceptance of the current terms and conditions | hook_error |
| Reject acceptance of an outdated version | hook_error |

## Esito complessivo

**Esecuzione conclusa con errori/fallimenti: validazione funzionale non superata.**

## Artefatti locali

Per ogni iniziativa: `tests/reports/uat-full-2026-10-29/<tag>/results.json`, `junit/`,
`runner.log` e `scenarios.log`. Stato e timestamp: `execution.json` nella cartella della run.
I log completi restano ignorati da Git perché possono contenere dati generati e risposte applicative.
Questo report registra conteggi, nomi di scenario e classificazioni degli errori senza riprodurre credenziali.

Copertura effettiva della selezione: **162 scenari unici**, includendo i casi senza tag Bonus. Questo conteggio indica i casi selezionati, non i test superati.
