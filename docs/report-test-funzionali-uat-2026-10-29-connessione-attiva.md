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
| `bonus_elettrodomestici` | failed | 133 | 5 | 0 | 0 | 2026-10-29T16:16:39.899241+00:00 | 2026-10-29T16:57:11.616326+00:00 | 1 |
| `bonus_decoder` | failed | 127 | 6 | 0 | 0 | 2026-10-29T16:57:11.618021+00:00 | 2026-10-29T17:37:24.772569+00:00 | 1 |
| `common_without_bonus_tag` | passed | 15 | 0 | 0 | 0 | 2026-10-29T17:37:25.064153+00:00 | 2026-10-29T17:37:54.687013+00:00 | 0 |

Le celle senza conteggio indicano che il report JSON è ancora in scrittura oppure che il processo è terminato prima di completarlo.

## bonus_elettrodomestici

Report JUnit leggibili: 16; conteggi JUnit: `{'cases': 138, 'passed': 133, 'failed': 5}`.


### Dettagli disponibili dai report JUnit

| Scenario | Diagnosi senza dati sensibili |
|---|---|
| An unsubscribed citizen onboards the same initiative again successfully | Onboarding ancora ON_EVALUATION; atteso ONBOARDING_OK dopo i retry. |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| An approved reward batch keeps its suspended amount after removing suspended transactions | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| Operator downloads the approved reward batch report | HTTP 400: CSV del lotto non ancora generato al momento del download. |

### Scenari falliti o in errore

| Scenario | Stato |
|---|---|
| An unsubscribed citizen onboards the same initiative again successfully | failed |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | failed |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | failed |
| An approved reward batch keeps its suspended amount after removing suspended transactions | failed |
| Operator downloads the approved reward batch report | failed |

## bonus_decoder

Report JUnit leggibili: 15; conteggi JUnit: `{'cases': 133, 'passed': 127, 'failed': 6}`.

- Step Canone TV non implementato: assert False già presente in main.

### Dettagli disponibili dai report JUnit

| Scenario | Diagnosi senza dati sensibili |
|---|---|
| Citizen who has not paid Canone TV tries to onboard unsuccessfully | Step non implementato in main. |
| An unsubscribed citizen onboards the same initiative again successfully | Onboarding ancora ON_EVALUATION; atteso ONBOARDING_OK dopo i retry. |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| An approved reward batch keeps its suspended amount after removing suspended transactions | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| Operator downloads the approved reward batch report | HTTP 400: CSV del lotto non ancora generato al momento del download. |

### Scenari falliti o in errore

| Scenario | Stato |
|---|---|
| An unsubscribed citizen onboards the same initiative again successfully | failed |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | failed |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | failed |
| An approved reward batch keeps its suspended amount after removing suspended transactions | failed |
| Operator downloads the approved reward batch report | failed |
| Citizen who has not paid Canone TV tries to onboard unsuccessfully | failed |

## common_without_bonus_tag

Report JUnit leggibili: 4; conteggi JUnit: `{'cases': 15, 'passed': 15}`.


## Esito complessivo

**Esecuzione conclusa con errori/fallimenti: validazione funzionale non superata.**

Totali delle esecuzioni (inclusi i casi comuni ripetuti sui due Bonus): failed=11, passed=275.

Durata complessiva: 1 h 21 min 14 s.

### Sintesi delle cause osservate

| Causa | Esecuzioni fallite |
|---|---:|
| Onboarding ancora ON_EVALUATION; atteso ONBOARDING_OK dopo i retry. | 2 |
| HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. | 6 |
| HTTP 400: CSV del lotto non ancora generato al momento del download. | 2 |
| Step non implementato in main. | 1 |

### Verifiche da approfondire prima di certificare la suite

- Riadesione: lo stato resta ON_EVALUATION oltre i retry; verificare il comportamento del backend e il criterio atteso dal test.
- Rifiuto/sospensione delle transazioni: allineare le richieste alla nota ufficiale ora richiesta dal servizio.
- CSV del lotto approvato: gestire/verificare il completamento della generazione prima del download.
- Canone TV: implementare lo step ancora lasciato con assert False in main.

Nessuno di questi esiti è stato aggirato modificando asserzioni, timeout o secret durante l'esecuzione.
La run con connessione attiva non presenta errori DNS né scenari in hook_error.
Nei log disponibili non sono segnalati errori del cleanup; questa osservazione non è una verifica autonoma dell'assenza di ogni residuo remoto.

## Artefatti locali

Per ogni iniziativa: `tests/reports/uat-full-2026-10-29-connected/<tag>/results.json`, `junit/`,
`runner.log` e `scenarios.log`. Stato e timestamp: `execution.json` nella cartella della run.
I log completi restano ignorati da Git perché possono contenere dati generati e risposte applicative.
Questo report registra conteggi, nomi di scenario e classificazioni degli errori senza riprodurre credenziali.

Copertura effettiva della selezione: **162 scenari unici**, includendo i casi senza tag Bonus. Questo conteggio indica i casi selezionati, non i test superati.
