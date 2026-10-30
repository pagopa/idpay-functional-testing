# Report di bonifica — idpay-functional-testing

Data: 27 ottobre 2026. Confronto: working tree corrente rispetto a `HEAD`.
Il report descrive le differenze presenti, senza includere valori di credenziali o dati dei log UAT.

## Criterio usato per decidere le eliminazioni

Il workflow `.github/workflows/test-run-bdd.yaml` esegue le directory
`common_bonus_features`, `bonus_elettrodomestici` e `bonus_decoder`.
Il workflow pytest era disabilitato nel chiamante. Questo è stato il criterio operativo
per identificare il perimetro legacy: l'esclusione dal workflow è evidenza di mancato utilizzo
nella CI corrente, non dimostra da sola che ogni vecchia regola di business sia stata formalmente dismessa.

Gli step ancora necessari sono stati individuati attraverso il registro Behave sugli scenari attivi.
Sono stati conservati gli helper e le API richiamati dagli step, dagli hook e dai test unitari.
Il confronto offline conserva esattamente l'inventario di 147 scenari attivi e non trova step indefiniti.
Questa verifica non sostituisce l'esecuzione UAT.

I file locali dei secret già ignorati non sono stati cancellati. La bonifica dei file tracciati
non ha rilevato credenziali concrete con i controlli effettuati; sono stati rimossi i placeholder
non più necessari e rafforzate le protezioni. Non è stata riscritta la storia Git.

## Motivazione per ciascun file

File con differenze di contenuto: 110. Definizioni Python eliminate rispetto a HEAD: 342.

| File | Operazione | Motivazione |
|---|---|---|
| `.github/PULL_REQUEST_TEMPLATE.md` | Modificato | Corretti i riferimenti al template dei secret e alla configurazione Key Vault: i precedenti nomi non corrispondevano alla gestione attuale. |
| `.github/copilot-instructions.md` | Modificato | Rimosse istruzioni per le suite pytest ritirate; documentati suite BDD mantenute, configurazione sicura, verifiche offline e cleanup. |
| `.github/workflows/test-run-bdd.yaml` | Modificato | Aggiunto umask 077 al recupero del secret e cancellazione del file temporaneo anche in caso di errore: evita credenziali residue sul runner self-hosted. |
| `.github/workflows/test-run-functional-test.yaml` | Eliminato | Workflow pytest già disabilitato nel chiamante; rimosso insieme ai test di integrazione legacy che eseguiva. |
| `.github/workflows/test-run.yaml` | Modificato | Eliminato il blocco commentato del workflow pytest e aggiunto un job offline per compilazione Python, test unitari e caricamento BDD senza credenziali. |
| `.gitignore` | Modificato | Estesa protezione a varianti dei secret, file .env, contenitori di credenziali/certificati, cache, report e file temporanei. Eccezione esplicita per il template privo di credenziali. |
| `Pipfile` | Modificato | Eliminate nove dipendenze dirette dei flussi ritirati; dichiarate esplicitamente cucumber-tag-expressions, pytz e requests, importate dalla suite attiva. |
| `Pipfile.lock` | Modificato | Rigenerato con Pipenv: 16 pacchetti risolti, hash coerente con Pipfile. Le dipendenze transitive sono state nuovamente risolte: non è una semplice eliminazione di righe. |
| `README.md` | Modificato | Aggiornati perimetro mantenuto, comandi offline, prerequisiti UAT, build della documentazione e comportamento dei trigger CI. |
| `api/asset_register.py` | Modificato | Rimosse 3 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `api/data_vault.py` | Modificato | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `api/idpay.py` | Modificato | Rimosse 32 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `api/issuer.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `api/mil.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `api/mock.py` | Modificato | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `api/onboarding_io.py` | Modificato | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `api/rtd.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `api/token_io.py` | Modificato | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `api/transaction.py` | Modificato | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/features/bar_code/_cancellation.feature` | Eliminato | Feature del gruppo storico `bar_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/bar_code/_refund.feature` | Eliminato | Feature del gruppo storico `bar_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/bar_code/_transaction.feature` | Eliminato | Feature del gruppo storico `bar_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/cancellation.feature` | Eliminato | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/onboarding.feature` | Eliminato | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/refund.feature` | Eliminato | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/suspension.feature` | Eliminato | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/transaction.feature` | Eliminato | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/family/unsubscribe.feature` | Eliminato | Feature del gruppo storico `family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_cancellation.feature` | Eliminato | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_enrollment.feature` | Eliminato | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_generation.feature` | Eliminato | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_refund.feature` | Eliminato | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/idpay_code/_transaction.feature` | Eliminato | Feature del gruppo storico `idpay_code`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_cancellation.feature` | Eliminato | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_onboarding.feature` | Eliminato | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_readmission.feature` | Eliminato | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_refund.feature` | Eliminato | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_suspension.feature` | Eliminato | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_transaction.feature` | Eliminato | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/pilot/pilot_unsubscription.feature` | Eliminato | Feature del gruppo storico `pilot`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/onboarding.feature` | Eliminato | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/suspension.feature` | Eliminato | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/transaction.feature` | Eliminato | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking/unsubscribe.feature` | Eliminato | Feature del gruppo storico `ranking`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/onboarding.feature` | Eliminato | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/suspension.feature` | Eliminato | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/transaction.feature` | Eliminato | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/ranking_family/unsubscription.feature` | Eliminato | Feature del gruppo storico `ranking_family`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo3/_onboarding.feature` | Eliminato | Feature del gruppo storico `tipo3`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo3/_transaction.feature` | Eliminato | Feature del gruppo storico `tipo3`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo4/_onboarding.feature` | Eliminato | Feature del gruppo storico `tipo4`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo4/_transaction.feature` | Eliminato | Feature del gruppo storico `tipo4`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo5/_onboarding.feature` | Eliminato | Feature del gruppo storico `tipo5`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo5/_transaction.feature` | Eliminato | Feature del gruppo storico `tipo5`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_cancellation.feature` | Eliminato | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_onboarding.feature` | Eliminato | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_refund.feature` | Eliminato | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo6/_transaction.feature` | Eliminato | Feature del gruppo storico `tipo6`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_onboarding.feature` | Eliminato | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_refund.feature` | Eliminato | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_returnflow.feature` | Eliminato | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipo8/_transaction.feature` | Eliminato | Feature del gruppo storico `tipo8`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/tipoB/_onboarding.feature` | Eliminato | Feature del gruppo storico `tipoB`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/onboarding.feature` | Eliminato | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/suspension.feature` | Eliminato | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/transaction.feature` | Eliminato | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/features/whitelist/unsubscribe.feature` | Eliminato | Feature del gruppo storico `whitelist`, esterno alle tre directory eseguite dal workflow BDD attivo. Rimossa per allineare la repository al perimetro Bonus/RDB mantenuto. |
| `bdd/steps/bar_code_steps.py` | Modificato | Rimosse 6 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/dataset_steps.py` | Modificato | Rimosse 4 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/discount_transaction_steps.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/family_steps.py` | Modificato | Rimosse 6 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/idpay_code_steps.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/initiative_steps.py` | Modificato | Rimosse 8 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/onboarding_steps.py` | Modificato | Rimosse 18 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/ranking_steps.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/report_steps.py` | Modificato | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `bdd/steps/reward_batch_steps.py` | Modificato | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `bdd/steps/rewards_step.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/suspension_readmission_steps.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `bdd/steps/unsubscribe_steps.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `conf/conftest.py` | Eliminato | Eliminato il lifecycle pytest che creava le iniziative cashback_like, not_started, complex e timeframes, non più usate dalle suite mantenute. |
| `conf/pari-feature-secrets-template.json` | Modificato | Rimossi placeholder dei flussi ritirati: iniziative storiche, mTLS, PM, issuer/MIL/RTD, IDPay code e whitelist. Conservati i campi necessari alle API attive; non sono state eliminate credenziali concrete da questo template. |
| `docs/rdb.md` | Modificato | Convertiti in testo due link a documenti assenti dalla repository, che facevano fallire la build MkDocs strict. Conservata la descrizione della copertura RDB. |
| `mkdocs.yaml` | Eliminato | Eliminata la configurazione statica obsoleta con collegamenti a feature legacy e Azure DevOps. Il generatore produce mkdocs.yml per i workflow correnti. |
| `model/visura_impresa.py` | Modificato | Ripuliti import non usati e formattazione; nessuna funzione rimossa. |
| `pytest.ini` | Eliminato | Eliminati marker e configurazione delle suite pytest di integrazione ritirate. I test unitari RDB sono unittest e non richiedono questi marker. |
| `requirements.txt` | Modificato | Allineato alle sei dipendenze dirette ancora usate, coerentemente con Pipfile. |
| `scenario_parser.py` | Modificato | Eliminati report pytest/FUNCTIONAL obsoleti e cartelle senza feature. Conservati percorsi distinti per feature con lo stesso nome in directory diverse, evitando sovrascritture delle pagine attive; aggiunta guida RDB alla navigazione. |
| `settings.yaml` | Modificato | Conservate le due iniziative Bonus attive; rimossi payload delle iniziative storiche ed endpoint senza consumatori. Preservati i sottoalberi letti tramite alias, inclusi asset_register e reward_batch. |
| `tests/test_cashback_like/__init__.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_cashback_like.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_enrollment_iban.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_enrollment_issuer.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_cashback_like/test_onboarding_io.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_complex_initiative.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/__init__.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/test_fail_onboard_api_issuer.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/test_fail_onboard_io.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_not_started/test_login_io.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `tests/test_timeframes_initiative.py` | Eliminato | Test o package della suite pytest legacy (cashback/enrollment/onboarding storico, complex, timeframes o not_started); il relativo workflow era disabilitato. I test unitari RDB in tests/unit sono conservati. |
| `util/certs_loader.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/data_vault_utilities.py` | Modificato | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `util/dataset_utility.py` | Modificato | Rimosse 14 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `util/encrypt_utilities.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/onboarding_utilities.py` | Modificato | Rimosse 2 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `util/sanitize-allure-results.py` | Modificato | Solo normalizzazione di formattazione/terminatori o commenti: nessun cambiamento alla logica Python. |
| `util/text_formatter.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/transaction_upload.py` | Eliminato | Modulo non più necessario dopo la rimozione dei flussi legacy; nessun import attivo richiede il file. La verifica del caricamento BDD non segnala step indefiniti. |
| `util/transaction_utilities.py` | Modificato | Rimosse 1 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |
| `util/utility.py` | Modificato | Rimosse 25 definizioni non raggiungibili dagli scenari mantenuti o dai loro helper; ripuliti gli import collegati. Le implementazioni ancora richiamate sono conservate. |

## Dettaglio delle definizioni eliminate

### `api/asset_register.py`

Definizioni eliminate: `update_products_status_approved`, `update_products_status_rejected`, `update_products_status_supervised`.

### `api/idpay.py`

Definizioni eliminate: `delete_payment_citizen`, `delete_payment_merchant`, `enroll_iban`, `force_ranking`, `force_reward`, `get_iban_info`, `get_iban_list`, `get_idpay_code_status`, `get_initiative_info`, `get_merchant_list`, `get_merchant_unprocessed_transactions`, `get_onboardings_list`, `get_payment_dispositions_export_content`, `get_payment_instruments`, `get_ranking_file`, `get_ranking_page`, `get_reward_content`, `post_idpay_code_generate`, `post_merchant_create_transaction_acquirer`, `put_authorize_payment`, `put_citizen_readmission`, `put_citizen_suspension`, `put_code_instrument`, `put_merchant_confirms_payment`, `put_minint_associate_user_and_payment`, `put_payment_results`, `put_pre_authorize_payment`, `put_publish_ranking`, `put_ranking_end_date`, `remove_payment_instrument`, `unsubscribe`, `upload_merchant_csv`.

### `api/issuer.py`

Definizioni eliminate: `enroll`.

### `api/mil.py`

Definizioni eliminate: `delete_transaction_mil`, `get_initiative_list_mil`, `get_public_key`, `get_transaction_detail_mil`, `post_merchant_create_transaction_mil`, `put_merchant_authorize_transaction_mil`, `put_merchant_pre_authorize_transaction_mil`.

### `api/rtd.py`

Definizioni eliminate: `pm_salt`, `public_key`, `sas_token`, `upload_file`.

### `api/token_io.py`

Definizioni eliminate: `introspect`.

### `api/transaction.py`

Definizioni eliminate: `get_reward_batches`.

### `bdd/steps/bar_code_steps.py`

Definizioni eliminate: `step_check_latest_citizen_creation_bar_code`, `step_check_latest_merchant_authorized_bar_code`, `step_citizen_try_create_bar_code`, `step_merchant_authorize_bar_code`, `step_merchant_try_to_authorize_bar_code`, `step_point_of_sale_update_invoice_bar_code`.

### `bdd/steps/dataset_steps.py`

Definizioni eliminate: `step_citizens_in_whitelist`, `step_trx_before_fruition_period`, `step_trx_date_days_ago`, `step_trx_does_not_exists`.

### `bdd/steps/discount_transaction_steps.py`

Definizioni eliminate: `complete_transaction_confirmation`, `step_check_every_transaction_status`, `step_check_latest_authorization_failed`, `step_check_latest_cancellation_by_citizen_failed`, `step_check_latest_cancellation_by_merchant`, `step_check_latest_cancellation_by_merchant_through_mil`, `step_check_latest_cancellation_failed`, `step_check_latest_pre_authorization_failed`, `step_check_latest_pre_authorization_failed_citizen_not_onboard`, `step_check_latest_pre_authorization_failed_missing_pre_auth`, `step_check_latest_pre_authorization_failed_not_found`, `step_check_latest_pre_authorization_failed_user_suspended`, `step_check_named_transaction_status`, `step_citizen_cancels_a_transaction`, `step_citizen_only_pre_authorize_transaction`, `step_citizen_tries_pre_authorize_transaction`, `step_citizen_tries_to_cancel_a_transaction`, `step_erode_budget`, `step_given_amount_cents`, `step_merchant_cancels_a_transaction`, `step_merchant_cancels_a_transaction_mil`, `step_merchant_cancels_every_transaction`, `step_merchant_cancels_every_transaction_mil`, `step_merchant_tries_to_cancels_a_transaction`, `step_merchant_tries_to_cancels_a_transaction_and_fails`, `step_merchant_tries_to_cancels_a_transaction_and_fails_mil`, `step_merchant_tries_to_cancels_a_transaction_mil`, `step_when_citizen_authorizes_all_transactions`, `step_when_citizen_confirms_transaction`, `step_when_citizen_rapidly_confirms_the_transactions`, `step_when_merchant_creates_n_transaction_successfully`, `step_when_merchant_creates_n_transaction_successfully_mil`, `step_when_merchant_generated_a_named_transaction`, `step_when_merchant_generated_a_named_transaction_mil`, `step_when_merchant_tries_to_create_a_transaction`, `step_when_merchant_tries_to_create_a_transaction_mil`, `step_when_merchant_tries_to_create_a_transaction_with_wrong_acquirer_id`, `step_when_onboard_citizen_confirms_transaction`, `update_user_counters`.

### `bdd/steps/family_steps.py`

Definizioni eliminate: `step_check_absence_in_ranking_families`, `step_check_family_member_budget_left`, `step_check_family_members_budget_left`, `step_check_rewards_of_citizen`, `step_demanded_family_member_onboards`, `step_family_members_enrolls_idpay_code`.

### `bdd/steps/idpay_code_steps.py`

Definizioni eliminate: `step_authorize_trx_mil`, `step_check_idpay_code_status`, `step_check_latest_association_by_minint`, `step_check_latest_association_with_citizen_by_minint`, `step_check_latest_auth_fails`, `step_check_latest_idpay_code_enabling_failed`, `step_check_latest_idpay_code_enrollment_failed`, `step_check_latest_pre_auth_fails`, `step_check_latest_response_idpay_code_deactivation`, `step_check_latest_trx_creation_through_mil`, `step_check_status_instrument_idpay_code`, `step_check_transaction_status`, `step_citizen_disable_idpay_code`, `step_citizen_enable_idpay_code`, `step_citizen_enroll_correctly_idpay_code`, `step_citizen_enroll_idpay_code`, `step_citizen_try_disable_idpay_code`, `step_citizen_try_enable_idpay_code`, `step_citizen_try_enroll_idpay_code`, `step_create_authorize_request_trx_request_by_pos`, `step_idpay_code_generate`, `step_idpay_code_regenerate`, `step_merchant_generates_a_transaction_mil`, `step_merchant_tries_to_generate_a_transaction_mil`, `step_minint_associates_trx_with_citizen`, `step_minint_tries_to_associate_trx_with_citizen`, `step_pre_authorize_transaction_mil`, `step_tries_to_authorize_trx_mil`, `step_tries_to_pre_authorize_transaction_mil`, `step_tries_to_pre_authorize_transaction_mil_another_merchant`, `step_try_to_authorize_trx_mil`.

### `bdd/steps/initiative_steps.py`

Definizioni eliminate: `step_allocate_initiative_budget`, `step_check_initiative_statistics_updated`, `step_create_new_initiative`, `step_create_new_initiative_with_whitelist`, `step_given_initiative_id`, `step_given_initiative_name`, `step_initiative_has_a_rank`, `step_initiative_in_grace_period`.

### `bdd/steps/onboarding_steps.py`

Definizioni eliminate: `step_card_enroll`, `step_check_citizens_correct_election`, `step_check_citizens_invited_whitelist_initiative`, `step_check_latest_prerequisites_failed`, `step_check_onboard_not_found`, `step_citizen_not_onboard`, `step_citizen_tries_to_accept_terms_and_conditions`, `step_citizen_tries_to_onboard_whitelist`, `step_citizens_join_ranking`, `step_family_member_onboards_ranking`, `step_iban_enroll`, `step_insert_self_declared_criteria`, `step_invited_citizen_tries_to_onboard`, `step_merchant_random_onboard`, `step_named_citizen_joins_ranking`, `step_named_citizen_onboard`, `step_named_citizen_suspension`, `step_save_pdnd_consent_not_correctly`.

### `bdd/steps/ranking_steps.py`

Definizioni eliminate: `step_check_absence_in_ranking`, `step_check_citizen_ranking_status`, `step_check_ranking_order`, `step_end_ranking`, `step_force_ranking`, `step_publish_ranking_`.

### `bdd/steps/report_steps.py`

Definizioni eliminate: `step_operator_selects_report_parameters_without_merchant`.

### `bdd/steps/rewards_step.py`

Definizioni eliminate: `assert_merchant_confirmation`, `step_check_missing_refund_of_merchant`, `step_check_refund_of_merchant`, `step_check_rewards_of_citizen`, `step_check_rewards_on_wallet`, `step_check_transaction_cancellation_on_citizen`, `step_institution_refunds_merchant`, `step_merchant_confirms_a_transactions`, `step_merchant_confirms_all_transactions`, `step_set_expected_accrued`, `step_set_expected_amount_left`.

### `bdd/steps/suspension_readmission_steps.py`

Definizioni eliminate: `step_check_latest_readmission`, `step_check_latest_suspension`, `step_institution_suspends_citizen`, `step_institution_suspends_correctly_citizen`, `step_institution_tries_citizen_readmission`, `step_institution_tries_citizen_suspension`.

### `bdd/steps/unsubscribe_steps.py`

Definizioni eliminate: `step_check_latest_cancellation_failed`, `step_citizen_tries_to_unsubscribe`, `step_citizen_unsubscribes`.

### `conf/conftest.py`

Definizioni eliminate: `create_test_initiatives`, `pytest_collection_modifyitems`, `pytest_configure`, `pytest_sessionfinish`.

### `tests/test_cashback_like/test_cashback_like.py`

Definizioni eliminate: `test_award_again_after_reversal`, `test_award_correct_amount_after_partial_reversal`, `test_correct_statistic_of_onboard_citizen`, `test_get_pending_reward_after_unsubscribe`, `test_homocode_onboarding`, `test_ko_iban_enroll`, `test_no_reward_after_complete_reversal`, `test_no_reward_transaction_1sec_before_card_enrollment`, `test_not_award_after_budget_erosion`, `test_onboarding_after_unsubscribe`, `test_remove_card_and_enroll_again`, `test_reward_transaction_after_complete_reversal`, `test_reward_transaction_after_partial_reversal`, `test_send_50_transaction_erode_budget_max_award`, `test_send_minimum_awardable_amount`, `test_send_single_200e_transaction_erode_budget_max_award`, `test_send_single_transaction`, `test_send_transaction_after_fruition_period`, `test_send_transaction_after_unsubscribe`, `test_send_transaction_ko_card_enroll`, `test_small_amount_no_award`.

### `tests/test_cashback_like/test_enrollment_iban.py`

Definizioni eliminate: `test_enroll_iban_more_times`, `test_enroll_same_iban_on_different_citizens`, `test_enrollment_iban`, `test_fail_enrollment_iban_citizen_not_onboard`.

### `tests/test_cashback_like/test_enrollment_issuer.py`

Definizioni eliminate: `test_abnormal_of_card_enroll`, `test_cannot_enroll_same_payment_instrument_of_another_citizen_that_removed_it`, `test_cannot_enroll_same_payment_instrument_of_another_unsubscribed_citizen`, `test_enroll_alphabetic_characters_pan`, `test_enroll_blank_pan`, `test_enroll_incorrect_length_pan_too_long`, `test_enroll_incorrect_length_pan_too_short`, `test_enroll_same_payment_instrument_of_another_citizen`, `test_enrollment_api_issuer`, `test_fail_enrollment_card_expired`, `test_fail_enrollment_issuer_not_onboard`, `test_ok_card_enroll_already_associated_to_another_initiative_same_citizen`, `test_remove_payment_instrument_of_another_citizen`.

### `tests/test_cashback_like/test_onboarding_io.py`

Definizioni eliminate: `test_onboard_blank_fc`, `test_onboard_io`, `test_onboard_io_temporary_fc`, `test_onboard_long_fc`, `test_onboard_space_fc`, `test_onboard_too_long_fc`, `test_onboard_two_times`, `test_onboard_unicode`, `test_timeline_without_ever_onboard`.

### `tests/test_complex_initiative.py`

Definizioni eliminate: `test_award_max_budget`, `test_award_new_transaction_after_reversal_on_awarded_transaction`, `test_award_transactions_done_with_two_payment_methods`, `test_erode_budget_with_one_transaction`, `test_no_award_insufficient_amount`, `test_no_award_insufficient_amount_and_transactions`, `test_no_award_new_transaction_after_reversal_on_first_transaction`, `test_no_award_wrong_mcc`, `test_no_award_wrong_mcc_on_first_transaction`, `test_no_reward_exceed_max_trx_amount`, `test_no_reward_on_first_transaction_insufficient_amount`, `test_no_reward_on_reverted_not_awarded_transaction`, `test_no_reward_one_cent`, `test_no_reward_zero_cent`, `test_not_award_transactions_after_unsubscribe`, `test_partial_reversal_on_first_transaction`, `test_partial_reversal_on_first_transaction_making_it_unacceptable`, `test_send_five_transactions_award_decimal`, `test_send_five_transactions_award_second_and_third`, `test_send_five_transactions_award_second_and_third_not_erode`, `test_send_one_transactions_no_award`, `test_unsubscribe_after_first_transaction`, `test_update_reward_on_reverted_awarded_transaction`, `test_wrong_reward_reverting_first_transaction`.

### `tests/test_not_started/test_fail_onboard_api_issuer.py`

Definizioni eliminate: `test_fail_onboarding_issuer_citizen_not_onboard`, `test_fail_onboarding_issuer_malformed_pgp`.

### `tests/test_not_started/test_fail_onboard_io.py`

Definizioni eliminate: `test_fail_onboarding`, `test_fail_onboarding_wrong_token`.

### `tests/test_not_started/test_login_io.py`

Definizioni eliminate: `test_login_io`.

### `tests/test_timeframes_initiative.py`

Definizioni eliminate: `Timeframe`, `test_award_transaction`, `test_award_transaction_1_sec_before_timeframe_end`, `test_award_transaction_exact_timeframe_end`, `test_award_transaction_exact_timeframe_start`, `test_enroll_same_iban_1`, `test_enroll_same_iban_2`, `test_erode_budget`, `test_ko_card_enroll_already_associated_to_another_initiative`, `test_ko_card_enroll_already_associated_to_the_same_initiative`, `test_no_award_transaction_after_card_removal`, `test_not_award_exceeds_max_amount`, `test_not_award_insufficient_amount`, `test_not_award_out_of_amount_range`, `test_not_award_transaction_1_sec_after_timeframe_start`, `test_not_award_transaction_1_sec_before_timeframe_start`, `test_not_award_transaction_1ms_after_timeframe`, `test_not_award_transaction_1ms_before_timeframe`, `test_not_award_transaction_after_allowed_timeframe`, `test_not_award_transaction_exceeds_max_amount`, `test_not_award_transaction_insufficient_amount`, `test_not_award_transaction_wrong_day`, `test_not_award_transaction_wrong_day_sunday`.

### `util/certs_loader.py`

Definizioni eliminate: `load_certificates`, `load_pm_public_key`.

### `util/data_vault_utilities.py`

Definizioni eliminate: `detokenize_to_fc`.

### `util/dataset_utility.py`

Definizioni eliminate: `fake_iban`, `fake_merchant_file`, `fake_pan`, `fake_temporary_fc`, `fake_vat`, `get_random_time`, `get_random_unicode`, `get_seconds`, `hash_pan`, `merchantInfo`, `reward`, `serialize`, `tomorrow_date`, `yesterday_date`.

### `util/encrypt_utilities.py`

Definizioni eliminate: `pgp_file_routine`, `pgp_string_routine`, `verify_and_clear_p7m_file`.

### `util/onboarding_utilities.py`

Definizioni eliminate: `build_bonus_decoder_self_declaration_list_payload`, `onboard_io`.

### `util/text_formatter.py`

Definizioni eliminate: `TextFormat`.

### `util/transaction_upload.py`

Definizioni eliminate: `encrypt_and_upload`, `input_trx_name_formatter`.

### `util/transaction_utilities.py`

Definizioni eliminate: `get_institutions_access_token`.

### `util/utility.py`

Definizioni eliminate: `card_enroll`, `card_removal`, `check_merchant_statistics`, `check_processed_transactions`, `check_ranking_status_institution_portal`, `check_rewards`, `check_unprocessed_transactions`, `citizen_unsubscribe_from_initiative`, `clean_trx_files`, `custom_transaction`, `force_rewards`, `generate_payment_results`, `get_payment_disposition_unique_ids`, `get_refund_exported_content`, `iban_enroll`, `merchant_id_from_fc`, `onboard_one_random_merchant`, `readmit_citizen_to_initiative`, `retry_iban_info`, `retry_merchant_statistics`, `retry_payment_instrument`, `retry_reward_batch_lifecycle`, `suspend_citizen_from_initiative`, `transactions_hash`, `upload_payment_results`.

## Verifiche già completate

- 27 test unitari RDB superati con HTTP simulato, anche nel virtualenv isolato con i soli 16 pacchetti del lockfile.
- Inventario degli scenari attivi identico a quello precedente alla pulizia; 175 funzioni step risolte, nessuno step indefinito.
- Compilazione Python, validazione JSON/YAML e controllo pre-commit delle chiavi private superati.
- `pipenv verify`: lockfile coerente con Pipfile.
- Build MkDocs `--strict` superata; `git diff --check` superato.
- Verificata la protezione gitignore per secret, report e file temporanei, mantenendo tracciabile il template.

Il dry run di Behave 1.3.3 riporta anche alcune feature come “failed” con step “untested”;
lo stesso risultato era presente prima della pulizia e il comando termina con codice 0.
Non viene conteggiato come esecuzione funzionale superata.

## Esecuzione UAT richiesta il 27 ottobre 2026

Esecuzioni sequenziali con gli stessi tag della matrice CI: `bonus_elettrodomestici`, poi `bonus_decoder`.
Ambiente `PARI_TARGET_ENV=uat`, configurazione locale ignorata `conf/pari-feature-secrets.json`,
cleanup dei reward batch abilitato. I log e i report dettagliati restano sotto `tests/reports/`, ignorato da Git.

Il primo tentativo nel sandbox è terminato per errori di connessione; è stato avviato
un nuovo tentativo con accesso alla rete UAT. Stato del tentativo con rete:

| Tag | Stato | Inizio UTC | Fine UTC | Exit code |
|---|---|---|---|---|
| `bonus_elettrodomestici` | failed | 2026-10-27T09:18:25.871510+00:00 | 2026-10-27T09:19:52.964330+00:00 | 1 |
| `bonus_decoder` | failed | 2026-10-27T09:19:52.966331+00:00 | 2026-10-27T09:21:25.474202+00:00 | 1 |

### Risultati osservati

| Tag | Scenari superati | Falliti | In errore | Esclusi dal tag |
|---|---:|---:|---:|---:|
| `bonus_elettrodomestici` | 12 | 0 | 117 | 18 |
| `bonus_decoder` | 9 | 1 | 114 | 23 |

“In errore” indica un errore di setup o di esecuzione; “fallito” indica un'asserzione non soddisfatta.
Gli scenari esclusi dal tag sono attesi nella selezione della matrice CI e non sono test superati.

### Cause rilevate

1. **Configurazione UAT locale incompleta.** Entrambe le iniziative sono presenti,
   ma mancano i valori `uat.initiatives.bonus_elettrodomestici.organization_id` e
   `uat.initiatives.bonus_decoder.organization_id`. L'errore ricorrente è
   `KeyError: 'organization_id'`. Il campo è già richiesto dal codice in `HEAD`
   e resta nel template tracciato: non è stato eliminato dalla bonifica.
   La classificazione come problema di configurazione deriva dal controllo delle sole
   chiavi presenti nel file locale; non sono stati riportati i relativi valori.
2. **Concorrenza CSV decoder non dimostrata.** Un'asserzione segnala:
   “The first CSV finished before overlap could be proved; concurrency result is inconclusive”.
   Il primo caricamento termina prima che sia verificabile la sovrapposizione con il secondo.
   Questo risultato non permette di concludere che il comportamento concorrente sia corretto o errato.

Non sono stati inventati organization ID né modificati i secret locali per aggirare gli errori.
Non sono stati attenuati controlli o asserzioni per ottenere un risultato verde.
Per completare la validazione occorre valorizzare i due organization ID usando la configurazione UAT
autorevole, ripetere le due suite e rivalutare il caso concorrente.

### Esito rispetto agli acceptance criteria

La bonifica e le verifiche offline sono completate. Le esecuzioni UAT sono state effettuate
ma **non sono passate**: l'AC “suite attive eseguite con successo senza regressioni”
non è soddisfatto. Non è quindi possibile certificare l'assenza di regressioni funzionali.
La presenza dei problemi descritti non costituisce da sola una prova di regressione introdotta
dalla rimozione dei file.
