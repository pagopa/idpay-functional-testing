# Analisi dei fallimenti UAT rispetto alla bonifica

Data: 30 ottobre 2026. Repository: `idpay-functional-testing`.
Baseline: `5d44f94ee86284af81fff94b8f2b1bbb425c56da` (`feat: LPBD-41 Tests for citizens onboarding (#116)`).
Confronto fra questa revisione di main, priva della bonifica locale, e il working tree attuale.

## Conclusione

**Non emergono evidenze che gli 11 fallimenti osservati il 29 ottobre siano stati introdotti
dalla bonifica.** I sei scenari unici interessati e il codice dei percorsi esaminati sono già presenti
con lo stesso comportamento nella baseline main. Le simulazioni delle risposte UAT producono
gli stessi fallimenti anche eseguendo il codice estratto da main.

Per nota ufficiale e Canone TV la carenza è direttamente verificabile nel codice di main.
Per riadesione e generazione CSV, oltre all'identità del codice, è stata verificata l'identità dei retry
e delle chiamate a parità di risposte. **Non è stata però eseguita una nuova suite UAT sulla baseline**:
non è quindi una prova A/B completa del comportamento del backend, dei dati o dei tempi dell'ambiente.

Questa verifica è offline: nessuna chiamata UAT, nessuna modifica a test, asserzioni, timeout o secret.

## Fallimenti esaminati

| Scenario | Esecuzioni fallite | Evidenza osservata in UAT | Confronto con main | Attribuzione |
|---|---:|---|---|---|
| An unsubscribed citizen onboards the same initiative again successfully | 2 | ON_EVALUATION dopo i retry, invece di ONBOARDING_OK | Scenario, disiscrizione, API, builder e polling invariati; stessa riproduzione offline con 62 risposte pendenti | Nessuna regressione di bonifica individuata; causa remota da approfondire |
| L2 Operator reject one transaction of reward batch and then approve the reward batch | 2 | HTTP 400 OFFICIAL_NOTE_FIELD_IS_MANDATORY | Il modello e il builder già non producono la nota ufficiale richiesta dal servizio | Carenza già presente in main rispetto al contratto UAT osservato |
| Suspending a transaction updates the live suspended amount while the reward batch is EVALUATING | 2 | HTTP 400 OFFICIAL_NOTE_FIELD_IS_MANDATORY | Stesso payload di sospensione in main e nel codice bonificato | Carenza già presente in main rispetto al contratto UAT osservato |
| An approved reward batch keeps its suspended amount after removing suspended transactions | 2 | HTTP 400 OFFICIAL_NOTE_FIELD_IS_MANDATORY | Usa lo stesso helper di sospensione, invariato | Carenza già presente in main rispetto al contratto UAT osservato |
| Operator downloads the approved reward batch report | 2 | HTTP 400 REWARD_BATCH_CSV_NOT_GENERATED | Già in main: attesa fissa di 30 secondi e una sola GET, senza polling della disponibilità | Nessun retry eliminato dalla bonifica in questo percorso; timing/generazione remota da approfondire |
| Citizen who has not paid Canone TV tries to onboard unsuccessfully | 1 | ASSERT FAILED: to be implemented | Lo step contiene già assert False in main | Placeholder preesistente, indipendente dalla bonifica |

Totale: **11 esecuzioni fallite, sei scenari unici**, perché cinque casi comuni falliscono su entrambi i Bonus.
Le 275 esecuzioni superate del 29 ottobre non vengono rieseguite in questa verifica.

## Come è stato verificato

### 1. Confronto strutturale del codice

Sono stati confrontati gli AST Python, ignorando numeri di riga e differenze puramente testuali.
Nei 16 moduli elencati nell'appendice risultano **189 definizioni conservate identiche**
(funzioni/classi, corpi, firme e decorator). Le funzioni legacy eliminate sono distinte dalle definizioni
conservate; la verifica non sostiene che i file completi siano identici.

I tre file Gherkin che contengono tutti i fallimenti sono identici a main:

- `bdd/features/common_bonus_features/onboarding.feature`
- `bdd/features/common_bonus_features/portale_enti/reward_batch.feature`
- `bdd/features/bonus_decoder/onboarding.feature`

Tutti i valori delle impostazioni rimaste in `settings.yaml` corrispondono ai valori di main.
Non risultano cambi di URL, stato atteso, percorso wallet o timeout fra quelli conservati.
I secret effettivi sono ignorati da Git: non esiste un loro confronto storico con main;
questa analisi non li modifica né ne riproduce i valori.

### 2. Prove differenziali offline

Le stesse funzioni sono state estratte e compilate separatamente dalle due versioni.
Le dipendenze HTTP e le attese sono state sostituite con mock; un guard blocca le connessioni socket.
Queste prove isolano i percorsi selezionati: non sostituiscono l'esecuzione completa dei due programmi
con tutti i moduli e un backend reale.

| Prova | Risultato in main | Risultato dopo bonifica |
|---|---|---|
| Rifiuto transazione con risposta HTTP 400 osservata | Stesso URL/payload, stessa asserzione fallita | Identico |
| Sospensione transazione con risposta HTTP 400 osservata | Stesso URL/payload, stessa asserzione fallita | Identico |
| Download lotto con CSV non generato | Una GET dopo sleep(30), stessa asserzione fallita | Identico |
| Onboarding sempre ON_EVALUATION | 62 richieste, 62 attese simulate di 5 secondi, stessa asserzione | Identico |
| Helper disiscrizione con risposta HTTP 204 | Stessi argomenti di disiscrizione e controlli wallet/timeline | Identico |
| Step Canone TV | AssertionError: to be implemented | Identico |
| Payload adesione Elettrodomestici | Stesso JSON, incluse autodichiarazioni | Identico |
| Payload adesione Decoder | Stesso JSON, incluse autodichiarazioni | Identico |

Esito: **otto confronti differenziali superati**, eseguiti su entrambe le versioni con dati sintetici.
Non sono state usate risposte UAT contenenti token o identità reali nelle simulazioni.

## Dettagli che escludono le rimozioni sospette

### Nota ufficiale

`TransactionActionRequest.to_dict()` emette transactionIds, reason e checksError; il relativo
modello non è stato modificato dalla bonifica. Il builder di rifiuto/sospensione e le API POST
serializzano la medesima struttura in main e nel working tree. Non è stata cancellata dalla bonifica
una proprietà della nota ufficiale in questo percorso: la richiesta era già così nella baseline.
La risposta UAT dimostra che il servizio richiede una nota; la forma da aggiungere deve essere
allineata al contratto effettivo, senza assumere che reason e nota ufficiale siano equivalenti.

### Riadesione

La disiscrizione è stata ripristinata nel riesame del 28 ottobre perché ora usata dai nuovi scenari.
L'helper ripristinato è identico a main, comprese le verifiche wallet e timeline; non è stato
semplificato o sostituito con una variante che salta i controlli. Sono invariati anche i payload
di adesione e il polling dello stato. La risposta ON_EVALUATION proviene dal servizio:
gli elementi disponibili non distinguono fra comportamento della riadesione, stato/dati UAT
e ritardo nell'elaborazione. Limitarsi ad aumentare il timeout non proverebbe la correttezza.

### CSV del lotto approvato

La feature chiede già in main un download dopo 30 secondi. `get_approved_reward_batch_download`
esegue già in main uno sleep e una sola GET: non c'è un ciclo di attesa della generazione che sia
stato eliminato nella bonifica. Non va confuso con il polling degli export CSV generici del portale enti,
che usa un altro percorso ed è passato nella run UAT.

### Canone TV

Il fallimento è deterministico e viene sollevato direttamente da `assert False, 'to be implemented'`.
Non dipende da una utility rimossa, da una credenziale bonificata o dalla connettività.

## Distinzione dai problemi trovati dopo il merge

Il riesame del 28 ottobre aveva effettivamente individuato incompatibilità fra bonifica e nuovi sviluppi:
conflitto su unsubscribe_steps, selettore esplicito dell'iniziativa rimosso, dipendenze della disiscrizione
e payload dei casi negativi da conservare. Questi problemi sono stati corretti prima della run UAT
del 29 ottobre. Non vengono nascosti o negati: sono diversi dagli 11 fallimenti oggetto di questa analisi.
La run con VPN attiva ha inoltre concluso tutte e tre le selezioni senza errori di import o degli hook.

## Appendice: definizioni conservate confrontate

| Modulo | Definizioni conservate | Definizioni conservate modificate |
|---|---:|---:|
| `api/idpay.py` | 31 | 0 |
| `api/onboarding_io.py` | 2 | 0 |
| `api/token_io.py` | 1 | 0 |
| `api/transaction.py` | 14 | 0 |
| `api/keycloak.py` | 1 | 0 |
| `api/merchant.py` | 5 | 0 |
| `model/transaction_model.py` | 5 | 0 |
| `util/onboarding_utilities.py` | 7 | 0 |
| `util/transaction_utilities.py` | 20 | 0 |
| `util/utility.py` | 17 | 0 |
| `bdd/environment.py` | 8 | 0 |
| `bdd/steps/onboarding_steps.py` | 18 | 0 |
| `bdd/steps/unsubscribe_steps.py` | 1 | 0 |
| `bdd/steps/initiative_steps.py` | 5 | 0 |
| `bdd/steps/reward_batch_steps.py` | 38 | 0 |
| `bdd/steps/bar_code_steps.py` | 16 | 0 |

## Riferimenti puntuali nel codice corrente e nella baseline

| Simbolo | Riga main | Riga corrente |
|---|---:|---:|
| `model/transaction_model.py::TransactionActionRequest` | 92 | 92 |
| `util/transaction_utilities.py::perform_reward_batch_transaction_action` | 219 | 208 |
| `api/transaction.py::post_reject_transactions` | 150 | 150 |
| `api/transaction.py::post_suspend_transactions` | 170 | 170 |
| `api/transaction.py::get_approved_reward_batch_download` | 117 | 117 |
| `util/utility.py::citizen_unsubscribe_from_initiative` | 901 | 474 |
| `api/idpay.py::unsubscribe` | 47 | 464 |
| `util/onboarding_utilities.py::retry_io_onboarding` | 35 | 12 |
| `bdd/steps/onboarding_steps.py::step_check_onboarding_status` | 319 | 202 |
| `bdd/steps/onboarding_steps.py::step_citizen_has_not_payed_canone_tv` | 713 | 499 |

## Artefatti

- Report UAT di riferimento: `docs/report-test-funzionali-uat-2026-10-29-connessione-attiva.md`.
- Risultati e JUnit originari: `tests/reports/uat-full-2026-10-29-connected/` (ignorati da Git).
- Evidenze delle prove offline, con soli input sintetici: `.cache/attribution-failures-2026-10-30.json`.
- Script riproducibile dell'analisi: `.cache/attribute_failures_20261030.py` (ignorato da Git).

Non è stata effettuata in questo turno alcuna correzione dei problemi funzionali: la richiesta
era attribuirne la causa rispetto alla bonifica, non cambiare il comportamento dei test.
