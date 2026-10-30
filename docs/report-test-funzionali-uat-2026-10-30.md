# Esecuzione completa dei test funzionali — 30 ottobre 2026

Ambiente: **UAT**. Esecuzione autorizzata dall'utente il 30 ottobre 2026.
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
| `bonus_elettrodomestici` | failed | 133 | 5 | 0 | 0 | 2026-10-30T08:57:14.417435+00:00 | 2026-10-30T09:42:22.572033+00:00 | 1 |
| `bonus_decoder` | failed | 126 | 7 | 0 | 0 | 2026-10-30T09:42:22.573155+00:00 | 2026-10-30T10:26:10.261662+00:00 | 1 |
| `common_without_bonus_tag` | passed | 15 | 0 | 0 | 0 | 2026-10-30T10:26:10.544783+00:00 | 2026-10-30T10:26:38.005917+00:00 | 0 |

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

Report JUnit leggibili: 15; conteggi JUnit: `{'cases': 133, 'passed': 126, 'failed': 7}`.

- Step Canone TV non implementato: assert False già presente in main.

### Dettagli disponibili dai report JUnit

| Scenario | Diagnosi senza dati sensibili |
|---|---|
| Citizen who has not paid Canone TV tries to onboard unsuccessfully | Step non implementato in main. |
| An unsubscribed citizen onboards the same initiative again successfully | Onboarding ancora ON_EVALUATION; atteso ONBOARDING_OK dopo i retry. |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.3  | CSV USER_DETAILS ancora IN_PROGRESS dopo i 10 tentativi di download. |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| An approved reward batch keeps its suspended amount after removing suspended transactions | HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. |
| Operator downloads the approved reward batch report | HTTP 400: CSV del lotto non ancora generato al momento del download. |

### Scenari falliti o in errore

| Scenario | Stato |
|---|---|
| An unsubscribed citizen onboards the same initiative again successfully | failed |
| Operator downloads the generated USER_DETAILS CSV report correctly -- @1.3  | failed |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | failed |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | failed |
| An approved reward batch keeps its suspended amount after removing suspended transactions | failed |
| Operator downloads the approved reward batch report | failed |
| Citizen who has not paid Canone TV tries to onboard unsuccessfully | failed |

## common_without_bonus_tag

Report JUnit leggibili: 4; conteggi JUnit: `{'cases': 15, 'passed': 15}`.


## Esito complessivo

**Esecuzione conclusa con errori/fallimenti: validazione funzionale non superata.**

Totali delle esecuzioni (inclusi i casi comuni ripetuti sui due Bonus): failed=12, passed=274.

Durata complessiva: 1 h 29 min 23 s.

### Sintesi delle cause osservate

| Causa | Esecuzioni fallite |
|---|---:|
| Onboarding ancora ON_EVALUATION; atteso ONBOARDING_OK dopo i retry. | 2 |
| HTTP 400: manca la nota ufficiale obbligatoria nel rifiuto/sospensione della transazione. | 6 |
| HTTP 400: CSV del lotto non ancora generato al momento del download. | 2 |
| Step non implementato in main. | 1 |
| CSV USER_DETAILS ancora IN_PROGRESS dopo i 10 tentativi di download. | 1 |

### Verifiche da approfondire prima di certificare la suite

- Riadesione: verificare lo stato remoto ancora pendente oltre i retry e il criterio atteso dal test.
- Rifiuto/sospensione: allineare le richieste alla nota ufficiale richiesta dal servizio.
- CSV del lotto approvato: verificare il completamento della generazione prima del download.
- Canone TV: implementare lo step ancora lasciato con assert False in main.

Nessuno di questi esiti è stato aggirato modificando asserzioni, timeout o secret durante l’esecuzione.

Nessun errore DNS rilevato in questa run.

Nessuno scenario in hook_error.

## Artefatti locali

Per ogni iniziativa: `tests/reports/uat-full-2026-10-30/<tag>/results.json`, `junit/`,
`runner.log` e `scenarios.log`. Stato e timestamp: `execution.json` nella cartella della run.
I log completi restano ignorati da Git perché possono contenere dati generati e risposte applicative.
Questo report registra conteggi, nomi di scenario e classificazioni degli errori senza riprodurre credenziali.

Copertura effettiva della selezione: **162 scenari unici**, includendo i casi senza tag Bonus. Questo conteggio indica i casi selezionati, non i test superati.

## Confronto con la run del 29 ottobre e relazione con la bonifica

| Gruppo | Superati / falliti il 29 ottobre | Superati / falliti il 30 ottobre |
|---|---:|---:|
| Bonus Elettrodomestici | 133 / 5 | 133 / 5 |
| Bonus Decoder | 127 / 6 | 126 / 7 |
| Casi senza tag Bonus | 15 / 0 | 15 / 0 |
| Totale esecuzioni | 275 / 11 | 274 / 12 |

Gli 11 fallimenti precedenti si ripresentano con le stesse diagnosi. Si aggiunge un solo caso: `Operator downloads the generated USER_DETAILS CSV report correctly -- @1.3`, Bonus Decoder, ruolo **L3**. Il report remoto risulta ancora **IN_PROGRESS** all'esaurimento dei 10 tentativi, intervallati da 30 secondi (9 attese, 270 secondi complessivi oltre al tempo delle richieste). Il caso era superato il 29 ottobre.

La funzione `retry_generated_report_download` in `bdd/steps/report_steps.py` ? identica a main `5d44f94` nel confronto AST; anche la feature `bdd/features/common_bonus_features/portale_enti/export_user.feature` ? invariata rispetto a main. L'esito indica un mancato completamento della generazione entro la finestra osservata: non dimostra da solo se si tratti di lentezza temporanea o di un problema del servizio. Occorre verificare la lavorazione del report in UAT; non sono stati estesi i timeout n? modificati i test.

Il controllo SHA-256 dei **78 file** registrati in `source-metadata.json` non rileva variazioni tra avvio e fine della run. Non emergono nuove evidenze che attribuiscano i fallimenti alla bonifica. Per gli 11 fallimenti gi? noti restano valide le verifiche differenziali e i limiti descritti nel [report di attribuzione](report-attribuzione-fallimenti-bonifica-2026-10-30.md): questa riesecuzione non costituisce un confronto A/B dal vivo con main.

## Integrit? dell'esecuzione e cleanup

- Copertura: **286 esecuzioni**, **162 scenari unici**; 124 esecuzioni ripetono scenari comuni per le due iniziative.
- Fallimenti: **12 esecuzioni**, corrispondenti a **7 scenari distinti**.
- Nessuna occorrenza di `HOOK-ERROR`, `Failed to delete initiative` o `RDB fixture cleanup failed` nei file `runner.log` e `scenarios.log` delle tre esecuzioni.
- Il cleanup era abilitato e non ha segnalato errori nei log esaminati; questo controllo non certifica autonomamente l'assenza di ogni residuo remoto.
- In questa ripresa sono stati aggiornati soltanto il report e strumenti diagnostici locali ignorati da Git. Nessun file applicativo, configurazione o credenziale ? stato modificato per correggere l'esito.

La suite funzionale UAT resta **non superata**. I 32 test unitari offline risultano invece superati.
