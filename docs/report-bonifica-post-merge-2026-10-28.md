# Riesame della bonifica dopo aggiornamento da main

Data: 28 ottobre 2026. Repository: `idpay-functional-testing`.
Branch: `LPBD-151-refactoring-e-bonifica-del-repository-idpay-functional-test`.
Riferimento locale `HEAD`, `main` e `origin/main`: `5d44f94ee86284af81fff94b8f2b1bbb425c56da`.
Commit esaminato: `feat: LPBD-41 Tests for citizens onboarding (#116)`.
Non è stato eseguito un fetch: il confronto riguarda i riferimenti già disponibili localmente.

## Esito

La bonifica precedente **richiedeva correzioni dopo il merge**. La nuova copertura riutilizza
selezione esplicita dell’iniziativa, disiscrizione e payload per casi negativi che prima non erano
raggiungibili dalle suite attive. Questi elementi sono stati ripristinati o conservati.
Le rimozioni dei flussi legacy indipendenti restano appropriate rispetto al perimetro CI corrente.

All’inizio del riesame era presente un conflitto `UD` nell’indice su
`bdd/steps/unsubscribe_steps.py`. Il caricamento BDD si fermava con
`ImportError: cannot import name 'get_initiative_info' from 'api.idpay'`.
Non si trattava di una prova che occorresse ripristinare tutta l’API storica:
il suo import apparteneva a handler legacy riapparsi con il merge e non usati dai nuovi scenari.
Sono stati rimossi gli handler e gli import inutilizzati, ripristinando invece la catena realmente necessaria.

Il conflitto è stato risolto e registrato con `git add` sul solo `unsubscribe_steps.py`.
È stata poi registrata la sola pulizia whitespace di `util/onboarding_utilities.py`, verificando prima che il file non avesse modifiche unstaged.
Non è stato creato un commit e non sono stati ricreati o resettati gli altri contenuti dell’indice.
Gli altri aggiornamenti di questo riesame restano nel working tree, insieme allo stato preesistente.

## Vincolo operativo: nessun test UAT

**Non è stata eseguita la suite UAT, né sono stati effettuati login, provisioning,
richieste HTTP applicative o cleanup su UAT.** Non sono stati usati o modificati i file locali dei secret UAT.
I controlli runtime sono stati eseguiti con il template di placeholder, `PARI_TARGET_ENV=<ENV>`
e un guard locale che blocca apertura di connessioni socket nei processi di verifica.
Gli HTTP dei test unitari sono simulati tramite mock.
I risultati UAT del 27 ottobre restano storici e non sono presentati come risultati del nuovo codice.

## Cosa cambia rispetto al riesame precedente

| Aspetto | 27 ottobre | Dopo il merge e le correzioni |
|---|---|---|
| Scenari BDD nelle directory attive | 147 | 162 |
| Funzioni step risolte dal registro effettivo | 175 | 182 |
| Test unitari eseguiti | 27 | 32, inclusi 5 nuovi casi di regressione offline |
| Payload di iniziativa mantenuti | Due Bonus | Due Bonus, not_started e budget_exhausted |
| Disiscrizione | Rimossa perché senza consumatori attivi | Ripristinata per lo scenario di riadesione |
| Conflitti nell’indice | — | Nessuno al termine del riesame |

## Interventi di questo riesame, file per file

| File | Decisione e motivazione |
|---|---|
| `api/idpay.py` | Ripristinata la sola API unsubscribe: il nuovo scenario di riadesione richiama la disiscrizione. Le API issuer, MIL, RTD e gli altri flussi storici restano rimossi. |
| `util/utility.py` | Ripristinato citizen_unsubscribe_from_initiative e i suoi import: disiscrive il cittadino, verifica HTTP 204 e attende aggiornamento wallet/timeline. Conservate le modifiche di main a polling, statistiche e cleanup. |
| `bdd/steps/unsubscribe_steps.py` | Risolto il conflitto modifica/cancellazione conservando lo step citizen_unsubscribes, con i due decorator Given/When aggiornati da main. Rimossi gli altri tre handler storici non usati; ripristinato e registrato nell’indice solo questo file. |
| `bdd/steps/initiative_steps.py` | Ripristinato step_given_initiative_name, ora usato dalle feature specifiche dei due Bonus. Conservati i nuovi step di creazione delle iniziative negative e ripristinato get_selfcare_token. Eliminati nove handler legacy riapparsi nel merge e gli import a funzioni rimosse, fra cui get_initiative_info e get_ranking_page. |
| `bdd/steps/onboarding_steps.py` | Conservati tutti gli sviluppi onboarding di main (wallet, famiglia, email, nuovi codici e retry); rimosso step_family_member_onboards, che non è più richiamato dalle feature correnti. |
| `settings.yaml` | Conservati i Bonus e i payload not_started/budget_exhausted, ora usati da scenari negativi attivi. Ripristinata wallet.unsubscribe. Rimossi nuovamente 22 payload storici riapparsi nel merge, senza rimuovere endpoint o payload richiesti dai nuovi test. |
| `util/onboarding_utilities.py` | Conservati i nuovi builder decoder/budget_exhausted e il polling aggiornato da main. Rimossi soltanto spazi di fine riga; corpi delle funzioni invariati. Normalizzazione registrata nell’indice dopo avere verificato l’assenza di modifiche unstaged al file. |
| `tests/unit/test_postmerge_compatibility.py` | Aggiunti cinque test offline: URL/header della DELETE di disiscrizione; attesa di wallet/timeline dopo successo; arresto dopo errore; selezione dell’iniziativa nominata; registrazione delle nuove iniziative per il cleanup. |
| `docs/report-bonifica-post-merge-2026-10-28.md` | Nuovo report di riesame; il report del 27 ottobre resta invariato come documento storico. |

### Definizioni ripristinate dalla versione main

- `api/idpay.py`: `unsubscribe`.
- `bdd/steps/initiative_steps.py`: `step_given_initiative_name`.
- `util/utility.py`: `citizen_unsubscribe_from_initiative`.

Lo step `step_citizen_unsubscribes` è stato conservato dal file in conflitto, che era presente
nel working tree ma non risolto nell’indice. Non è stato necessario ripristinare pytest,
issuer/MIL/RTD, crittografia PGP o le iniziative di ranking per supportarlo.

### Definizioni non più necessarie dopo il merge

- `bdd/steps/initiative_steps.py`: `step_given_initiative_id`, `step_check_initiative_statistics_updated`, `step_allocate_initiative_budget`, `step_create_new_initiative`, `step_create_new_initiative_with_whitelist`, `step_initiative_in_grace_period`, `step_initiative_in_grace_period`, `step_initiative_has_a_rank`, `step_initiative_published`.
- `bdd/steps/onboarding_steps.py`: `step_family_member_onboards`.
- `bdd/steps/unsubscribe_steps.py`: `step_citizen_tries_to_unsubscribe`, `step_citizen_tries_to_unsubscribe`, `step_check_latest_cancellation_failed`.

Due handler di periodo avevano lo stesso nome Python ma decorator diversi: sono elencati entrambi.
La decisione è basata sul matching delle feature attive e sui richiami agli helper,
non soltanto sul nome del file o sulla presenza della funzione nell’ultimo commit.

### Configurazioni

Conservati i payload `bonus_elettrodomestici`, `bonus_decoder`, `not_started`, `budget_exhausted`.
La selezione `NOT_STARTED` è stata verificata anche con l’accesso dinamico case-insensitive di Dynaconf.
`not_started` era stato rimosso insieme alla vecchia suite pytest; ora è riutilizzato da uno scenario BDD
e deve restare, senza ripristinare la suite pytest o credenziali statiche per quella iniziativa.

Rimossi nuovamente i seguenti payload ricomparsi nel merge:

`Discount_whitelist_closed`, `Ranking_fruition_open`, `Ranking_in_grace_period`, `Scontoditipo1`, `Scontoditipo1_allocated`, `Scontoditipo1_not_started`, `Scontoditipo3`, `Scontoditipo4`, `Scontoditipo5`, `Scontoditipo6`, `Scontoditipo8`, `ScontoditipoB`, `cashback_like`, `complex`, `discount_bar_code`, `discount_idpay_code`, `discount_whitelist`, `family_allocated_initiative`, `family_initiative`, `family_ranking_initiative`, `ranking_initiative`, `timeframes`.

## Inventario completo della bonifica, riconfermato rispetto a main

La tabella seguente comprende le differenze attuali fra `HEAD` e working tree/indice;
non attribuisce a questo turno modifiche già presenti all’avvio. Le sette revisioni specifiche di questo
turno sono distinte sopra. Le feature nuove di main non sono state alterate.

| File | Decisione finale | Motivazione |
|---|---|---|
| `.github/PULL_REQUEST_TEMPLATE.md` | Modifica mantenuta/rivista | Corretti i riferimenti al template dei secret e alla configurazione Key Vault: i precedenti nomi non corrispondevano alla gestione attuale. |
| `.github/copilot-instructions.md` | Modifica mantenuta/rivista | Rimosse istruzioni per le suite pytest ritirate; documentati suite BDD mantenute, configurazione sicura, verifiche offline e cleanup. |
| `.github/workflows/test-run-bdd.yaml` | Modifica mantenuta/rivista | Aggiunto umask 077 al recupero del secret e cancellazione del file temporaneo anche in caso di errore: evita credenziali residue sul runner self-hosted. |
| `.github/workflows/test-run-functional-test.yaml` | Eliminazione confermata | Workflow pytest già disabilitato nel chiamante; rimosso insieme ai test di integrazione legacy che eseguiva. |
| `.github/workflows/test-run.yaml` | Modifica mantenuta/rivista | Eliminato il blocco commentato del workflow pytest e aggiunto un job offline per compilazione Python, test unitari e caricamento BDD senza credenziali. |
| `.gitignore` | Modifica mantenuta/rivista | Estesa protezione a varianti dei secret, file .env, contenitori di credenziali/certificati, cache, report e file temporanei. Eccezione esplicita per il template privo di credenziali. |
| `Pipfile` | Modifica mantenuta/rivista | Eliminate nove dipendenze dirette dei flussi ritirati; dichiarate esplicitamente cucumber-tag-expressions, pytz e requests, importate dalla suite attiva. |
| `Pipfile.lock` | Modifica mantenuta/rivista | Rigenerato con Pipenv: 16 pacchetti risolti, hash coerente con Pipfile. Le dipendenze transitive sono state nuovamente risolte: non è una semplice eliminazione di righe. |
| `README.md` | Modifica mantenuta/rivista | Aggiornati perimetro mantenuto, comandi offline, prerequisiti UAT, build della documentazione e comportamento dei trigger CI. |
| `api/asset_register.py` | Modifica mantenuta/rivista | Rimosse 3 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `api/data_vault.py` | Modifica mantenuta/rivista | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `api/idpay.py` | Modifica mantenuta/rivista | Ripristinata la sola API unsubscribe: il nuovo scenario di riadesione richiama la disiscrizione. Le API issuer, MIL, RTD e gli altri flussi storici restano rimossi. |
| `api/issuer.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `api/mil.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `api/mock.py` | Modifica mantenuta/rivista | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `api/onboarding_io.py` | Modifica mantenuta/rivista | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `api/rtd.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `api/token_io.py` | Modifica mantenuta/rivista | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `api/transaction.py` | Modifica mantenuta/rivista | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/features/bar_code/_cancellation.feature` | Eliminazione confermata | Feature del gruppo storico `bar_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/bar_code/_refund.feature` | Eliminazione confermata | Feature del gruppo storico `bar_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/bar_code/_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `bar_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/cancellation.feature` | Eliminazione confermata | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/refund.feature` | Eliminazione confermata | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/suspension.feature` | Eliminazione confermata | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/transaction.feature` | Eliminazione confermata | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/unsubscribe.feature` | Eliminazione confermata | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_cancellation.feature` | Eliminazione confermata | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_enrollment.feature` | Eliminazione confermata | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_generation.feature` | Eliminazione confermata | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_refund.feature` | Eliminazione confermata | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_cancellation.feature` | Eliminazione confermata | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_readmission.feature` | Eliminazione confermata | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_refund.feature` | Eliminazione confermata | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_suspension.feature` | Eliminazione confermata | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_unsubscription.feature` | Eliminazione confermata | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/suspension.feature` | Eliminazione confermata | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/transaction.feature` | Eliminazione confermata | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/unsubscribe.feature` | Eliminazione confermata | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/suspension.feature` | Eliminazione confermata | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/transaction.feature` | Eliminazione confermata | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/unsubscription.feature` | Eliminazione confermata | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo3/_onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `tipo3`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo3/_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `tipo3`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo4/_onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `tipo4`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo4/_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `tipo4`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo5/_onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `tipo5`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo5/_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `tipo5`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_cancellation.feature` | Eliminazione confermata | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_refund.feature` | Eliminazione confermata | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_refund.feature` | Eliminazione confermata | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_returnflow.feature` | Eliminazione confermata | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_transaction.feature` | Eliminazione confermata | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipoB/_onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `tipoB`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/onboarding.feature` | Eliminazione confermata | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/suspension.feature` | Eliminazione confermata | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/transaction.feature` | Eliminazione confermata | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/unsubscribe.feature` | Eliminazione confermata | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/steps/bar_code_steps.py` | Modifica mantenuta/rivista | Rimosse 6 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/dataset_steps.py` | Modifica mantenuta/rivista | Rimosse 4 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/discount_transaction_steps.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/family_steps.py` | Modifica mantenuta/rivista | Rimosse 6 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/idpay_code_steps.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/initiative_steps.py` | Modifica mantenuta/rivista | Ripristinato step_given_initiative_name, ora usato dalle feature specifiche dei due Bonus. Conservati i nuovi step di creazione delle iniziative negative e ripristinato get_selfcare_token. Eliminati nove handler legacy riapparsi nel merge e gli import a funzioni rimosse, fra cui get_initiative_info e get_ranking_page. |
| `bdd/steps/onboarding_steps.py` | Modifica mantenuta/rivista | Conservati tutti gli sviluppi onboarding di main (wallet, famiglia, email, nuovi codici e retry); rimosso step_family_member_onboards, che non è più richiamato dalle feature correnti. |
| `bdd/steps/ranking_steps.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/report_steps.py` | Modifica mantenuta/rivista | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/reward_batch_steps.py` | Modifica mantenuta/rivista | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `bdd/steps/rewards_step.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/suspension_readmission_steps.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/unsubscribe_steps.py` | Modifica mantenuta/rivista | Risolto il conflitto modifica/cancellazione conservando lo step citizen_unsubscribes, con i due decorator Given/When aggiornati da main. Rimossi gli altri tre handler storici non usati; ripristinato e registrato nell’indice solo questo file. |
| `conf/conftest.py` | Eliminazione confermata | Eliminato il lifecycle pytest che creava le iniziative cashback_like, not_started, complex e timeframes, non più usate dalle suite mantenute. |
| `conf/pari-feature-secrets-template.json` | Modifica mantenuta/rivista | Rimossi placeholder dei flussi ritirati: iniziative storiche, mTLS, PM, issuer/MIL/RTD, IDPay code e whitelist. Conservati i campi necessari alle API attive; non sono state eliminate credenziali concrete da questo template. |
| `docs/rdb.md` | Modifica mantenuta/rivista | Convertiti in testo due link a documenti assenti dalla repository, che facevano fallire la build MkDocs strict. Conservata la descrizione della copertura RDB. |
| `mkdocs.yaml` | Eliminazione confermata | Eliminata la configurazione statica obsoleta con collegamenti a feature legacy e Azure DevOps. Il generatore produce mkdocs.yml per i workflow correnti. |
| `model/visura_impresa.py` | Modifica mantenuta/rivista | Ripuliti import non usati e formattazione; nessuna funzione rimossa. |
| `pytest.ini` | Eliminazione confermata | Eliminati marker e configurazione delle suite pytest di integrazione ritirate. I test unitari RDB sono unittest e non richiedono questi marker. |
| `requirements.txt` | Modifica mantenuta/rivista | Allineato alle sei dipendenze dirette ancora usate, coerentemente con Pipfile. |
| `scenario_parser.py` | Modifica mantenuta/rivista | Eliminati report pytest/FUNCTIONAL obsoleti e cartelle senza feature. Conservati percorsi distinti per feature con lo stesso nome in directory diverse, evitando sovrascritture delle pagine attive; aggiunta guida RDB alla navigazione. |
| `settings.yaml` | Modifica mantenuta/rivista | Conservati i Bonus e i payload not_started/budget_exhausted, ora usati da scenari negativi attivi. Ripristinata wallet.unsubscribe. Rimossi nuovamente 22 payload storici riapparsi nel merge, senza rimuovere endpoint o payload richiesti dai nuovi test. |
| `tests/test_cashback_like/__init__.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_cashback_like.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_enrollment_iban.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_enrollment_issuer.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_onboarding_io.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_complex_initiative.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/__init__.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/test_fail_onboard_api_issuer.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/test_fail_onboard_io.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/test_login_io.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_timeframes_initiative.py` | Eliminazione confermata | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `util/certs_loader.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/data_vault_utilities.py` | Modifica mantenuta/rivista | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `util/dataset_utility.py` | Modifica mantenuta/rivista | Rimosse 14 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `util/encrypt_utilities.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/onboarding_utilities.py` | Modifica mantenuta/rivista | Conservati i nuovi builder decoder/budget_exhausted e il polling aggiornato da main. Rimossi soltanto spazi di fine riga; corpi delle funzioni invariati. Normalizzazione registrata nell’indice dopo avere verificato l’assenza di modifiche unstaged al file. |
| `util/sanitize-allure-results.py` | Modifica mantenuta/rivista | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `util/text_formatter.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/transaction_upload.py` | Eliminazione confermata | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/transaction_utilities.py` | Modifica mantenuta/rivista | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `util/utility.py` | Modifica mantenuta/rivista | Ripristinato citizen_unsubscribe_from_initiative e i suoi import: disiscrive il cittadino, verifica HTTP 204 e attende aggiornamento wallet/timeline. Conservate le modifiche di main a polling, statistiche e cleanup. |

## Verifiche offline

| Controllo | Risultato |
|---|---|
| Import interni, inclusi simboli rimossi/ripristinati | Nessun riferimento a simboli locali mancanti |
| Riferimenti statici a settings e alias | Nessun percorso mancante individuato |
| Matching del registro reale Behave | 182 funzioni step, nessuno step indefinito |
| Inventario delle feature mantenute | 162 scenari; nuove feature di main conservate |
| Test unitari, con socket bloccati e HTTP simulato | 32 superati |
| Configurazioni dinamiche NOT_STARTED e budget_exhausted | Presenti e accessibili |
| Compilazione Python | Superata |
| Pipenv verify | Lockfile coerente, nessuna dipendenza diretta aggiuntiva necessaria |
| Build MkDocs strict | Superata |
| JSON/YAML, credenziali tracciate, whitespace e indice | Superati; nessuna credenziale rilevata dai pattern controllati e nessun conflitto residuo |

Il riepilogo `--dry-run` di Behave 1.3.3 classifica alcune feature come failed con step untested,
pur terminando con codice 0; il comportamento era già presente prima del merge.
Qui il dry run certifica il caricamento/matching degli scenari, **non** il comportamento del backend.

## Problemi provenienti dai nuovi sviluppi e limiti residui

1. In `bdd/steps/onboarding_steps.py`, lo step `step_citizen_has_not_payed_canone_tv`
   contiene `assert False, 'to be implemented'`. È già così nel commit main esaminato ed è richiamato
   da una nuova feature decoder. È stato conservato perché la richiesta è verificare la bonifica;
   inventare un mock Canone TV o sopprimere lo scenario altererebbe la copertura attesa.
   Quel caso richiede un’implementazione prima di poter ottenere una suite completamente verde.
2. La configurazione UAT dei due organization ID, risultata incompleta il 27 ottobre,
   non è stata rivalidata o modificata. Il fallback aggiunto da main in uno step onboarding è conservato;
   altri step di selezione dell’iniziativa richiedono ancora organization_id nella relativa configurazione.
3. Il problema di timing del test concorrente CSV osservato il 27 ottobre non è stato rieseguito.
4. I controlli di raggiungibilità e dei riferimenti settings sono conservativi e statici;
   non equivalgono a una prova del comportamento remoto. L’assenza di regressioni UAT resta da verificare
   quando l’ambiente sarà disponibile e l’esecuzione verrà autorizzata.

Le rimozioni legacy sono confermate rispetto ai consumatori e ai workflow correnti;
questo non costituisce una certificazione formale di dismissione delle vecchie regole di business.

Ulteriore verifica finale: tutte le 22 feature attive coincidono con main; i corpi delle funzioni/classi conservate e i quattro payload mantenuti non sono stati alterati rispetto all’avvio del riesame. Il controllo whitespace accetta i terminatori CRLF presenti nell’indice su Windows (`cr-at-eol`), senza normalizzare o riaggiungere in blocco i file già staged.
