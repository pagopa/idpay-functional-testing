# RDB - run UAT dopo rimozione del teardown, 23 settembre 2026

**77 PASSATI | 23 FALLITI | 0 ERRORI | 0 SCENARI SALTATI**

Suite completa: **100 scenari**, senza esclusioni. Durata complessiva 8 min 28.8 s, timeout HTTP 30 s, exit code 1.
Inizio UTC: 2026-09-23T15:34:28.1572709Z; fine UTC: 2026-09-23T15:42:56.9301136Z.

Step: **486 passati, 23 falliti, 0 in errore, 66 saltati**.
I conteggi JSON, CSV e JUnit sono stati verificati e coincidono. Gli step saltati seguono il primo fallimento dello scenario.

Confronto con il precedente run completo (77 passati, 23 falliti): **0 regressioni, 0 casi recuperati**.

## Ripristino

Rimossi il modulo rdb_cleanup, i relativi test, gli hook, il tracciamento delle scritture e le modifiche al workflow. Pipfile, Pipfile.lock e requirements.txt sono tornati alla versione precedente al teardown. Le chiamate tornano direttamente alle API.
Ripristinato anche deepcopy, ancora necessario ai filtri: un primo tentativo aveva rilevato 9 NameError. I conteggi sopra appartengono esclusivamente al successivo run completo.
Il riordino della documentazione e le correzioni funzionali precedenti sono mantenuti.

## Esiti per feature

| Feature | Passati | Falliti | Errori | Saltati |
| --- | ---: | ---: | ---: | ---: |
| Access and authorization to RDB | 6 | 1 | 0 | 0 |
| Manage the product CSV lifecycle | 32 | 3 | 0 | 0 |
| Accept RDB notification payloads at the email service | 3 | 0 | 0 | 0 |
| List the initiatives available to an RDB organization | 5 | 1 | 0 | 0 |
| Preserve RDB processing when email is missing or unavailable | 0 | 3 | 0 | 0 |
| Manage producer associations and operational email | 3 | 8 | 0 | 0 |
| Change product status with role checks and atomic updates | 12 | 0 | 0 | 0 |
| Consult products, batches and producers in the RDB registry | 12 | 5 | 0 | 0 |
| Accept the current version of the RDB terms and conditions | 4 | 2 | 0 | 0 |

## Cause dei fallimenti

| Gruppo | Casi | Intervento necessario |
| --- | ---: | --- |
| G1a - Accesso Data Factory | 15 | Configurare asset_register.producer_import_api_key con la subscription Data Factory valida. |
| G1b - Dataset controllati | 5 | Predisporre il dataset indicato: upload in corso, associazione disabilitata, elenco produttori noto o consenso precedente. |
| G3b - Guasti email / OneTrust | 2 | Collegare il backend a dipendenze isolate e configurare asset_register.dependencies. |
| G4 - Token applicativo scaduto | 1 | Distribuire la policy che rispetta exp oppure configurare un JWT RDB firmato e realmente scaduto. |

### G1a - Accesso Data Factory

| ID | Scenario | Primo step fallito | Diagnostica |
| --- | --- | --- | --- |
| RDB-043 | [List only uploads belonging to the organization and initiative](../bdd/features/bonus_elettrodomestici/rdb/csv.feature#L232) | [Given the RDB dataset is "CSV history"](../bdd/features/bonus_elettrodomestici/rdb/csv.feature#L233) | Missing secrets.asset_register.producer_import_api_key; isolated RDB datasets require POST /idpay-itn/df/producers |
| RDB-059 | [Process a CSV when the operational email is missing](../bdd/features/bonus_elettrodomestici/rdb/notification.feature#L11) | [Given the RDB dataset is "producer without email"](../bdd/features/bonus_elettrodomestici/rdb/notification.feature#L12) | Missing secrets.asset_register.producer_import_api_key; isolated RDB datasets require POST /idpay-itn/df/producers |
| RDB-060 | [Reject a product when the operational email is missing](../bdd/features/bonus_elettrodomestici/rdb/notification.feature#L19) | [Given the RDB dataset is "producer without email"](../bdd/features/bonus_elettrodomestici/rdb/notification.feature#L20) | Missing secrets.asset_register.producer_import_api_key; isolated RDB datasets require POST /idpay-itn/df/producers |
| RDB-062 | [Import valid producer associations](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L9) | [When the RDB producer associations are imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L11) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-063 | [Reject an empty association payload](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L16) | [When the RDB producer associations are imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L18) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-064 | [Count an association missing a mandatory field as failed -- @1.1](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L29) | [When the RDB producer associations are imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L24) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-065 | [Count an association missing a mandatory field as failed -- @1.2](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L30) | [When the RDB producer associations are imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L24) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-066 | [Count an association missing a mandatory field as failed -- @1.3](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L31) | [When the RDB producer associations are imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L24) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-067 | [Normalize the producer email during import -- @1.1](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L42) | [When the RDB producer associations are imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L36) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-068 | [Normalize the producer email during import -- @1.2](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L43) | [When the RDB producer associations are imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L36) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-069 | [Reimport an association without creating duplicates](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L46) | [And the RDB producer association has already been imported](../bdd/features/bonus_elettrodomestici/rdb/producer.feature#L48) | Missing secrets.asset_register.producer_import_api_key; POST /idpay-itn/df/producers requires the Data Factory subscription |
| RDB-085 | [Restrict product visibility to the selected organization -- @1.1](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L16) | [Given the RDB dataset is "producer registry"](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L9) | Missing secrets.asset_register.producer_import_api_key; isolated RDB datasets require POST /idpay-itn/df/producers |
| RDB-086 | [Restrict product visibility to the selected organization -- @1.2](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L17) | [Given the RDB dataset is "Invitalia registry"](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L9) | Missing secrets.asset_register.producer_import_api_key; isolated RDB datasets require POST /idpay-itn/df/producers |
| RDB-097 | [Restrict batches to the selected organization -- @1.1](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L56) | [Given the RDB dataset is "organization CSV batches"](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L50) | Missing secrets.asset_register.producer_import_api_key; isolated RDB datasets require POST /idpay-itn/df/producers |
| RDB-098 | [Restrict batches to the selected organization -- @1.2](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L57) | [Given the RDB dataset is "foreign CSV batches"](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L50) | Missing secrets.asset_register.producer_import_api_key; isolated RDB datasets require POST /idpay-itn/df/producers |

### G1b - Dataset controllati

| ID | Scenario | Primo step fallito | Diagnostica |
| --- | --- | --- | --- |
| RDB-026 | [Reject concurrent uploads for the same initiative and organization](../bdd/features/bonus_elettrodomestici/rdb/csv.feature#L114) | [And the RDB dataset is "upload in progress"](../bdd/features/bonus_elettrodomestici/rdb/csv.feature#L116) | Missing secrets.asset_register.datasets.upload in progress; see docs/rdb.md |
| RDB-027 | [Allow an upload on another initiative](../bdd/features/bonus_elettrodomestici/rdb/csv.feature#L123) | [And the RDB dataset is "upload in progress"](../bdd/features/bonus_elettrodomestici/rdb/csv.feature#L125) | Missing secrets.asset_register.datasets.upload in progress; see docs/rdb.md |
| RDB-049 | [Return exactly the initiatives visible to the current user -- @1.2](../bdd/features/bonus_elettrodomestici/rdb/initiatives.feature#L13) | [Given the RDB dataset is "producer disabled association"](../bdd/features/bonus_elettrodomestici/rdb/initiatives.feature#L5) | Missing secrets.asset_register.datasets.producer disabled association; see docs/rdb.md |
| RDB-099 | [List the producers associated with the initiative](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L60) | [Given the RDB dataset is "initiative producers"](../bdd/features/bonus_elettrodomestici/rdb/read_registry.feature#L61) | Missing secrets.asset_register.datasets.initiative producers; see docs/rdb.md |
| RDB-104 | [Request acceptance after the terms and conditions change](../bdd/features/bonus_elettrodomestici/rdb/terms_and_conditions.feature#L17) | [Given the RDB dataset is "previous consent version"](../bdd/features/bonus_elettrodomestici/rdb/terms_and_conditions.feature#L18) | Missing secrets.asset_register.datasets.previous consent version; see docs/rdb.md |

### G3b - Guasti email / OneTrust

| ID | Scenario | Primo step fallito | Diagnostica |
| --- | --- | --- | --- |
| RDB-061 | [Preserve the status change when the email service fails](../bdd/features/bonus_elettrodomestici/rdb/notification.feature#L29) | [And the RDB dependency "email" is unavailable](../bdd/features/bonus_elettrodomestici/rdb/notification.feature#L33) | Missing secrets.asset_register.dependencies; see docs/rdb.md |
| RDB-107 | [Do not store consent when OneTrust is unavailable](../bdd/features/bonus_elettrodomestici/rdb/terms_and_conditions.feature#L36) | [And the RDB dependency "OneTrust" is unavailable](../bdd/features/bonus_elettrodomestici/rdb/terms_and_conditions.feature#L38) | Missing secrets.asset_register.dependencies; see docs/rdb.md |

### G4 - Token applicativo scaduto

| ID | Scenario | Primo step fallito | Diagnostica |
| --- | --- | --- | --- |
| RDB-006 | [Reject an expired application token](../bdd/features/bonus_elettrodomestici/rdb/authorization.feature#L31) | [Given the RDB application token fixture is "expired"](../bdd/features/bonus_elettrodomestici/rdb/authorization.feature#L32) | Test signer did not preserve the requested expiration; deploy the exp override from jwt_register_token_test.xml.tpl or configure application_tokens.expired |

## Perimetro ed evidenze

- Servizio email: 3/3 passati. L'asserzione verifica HTTP 204 e body vuoto; non verifica la consegna in casella.
- Perimetro EPREL e soglie energetiche invariati. Gli stati esterni esclusi restano fuori dal conteggio.
- La tolleranza HTTP 500 per CSV oltre 2 MB resta il debito tecnico [TD-RDB-001](rdb.md#td-rdb-001).
- I test hanno usato API e dati UAT reali. Le risorse RDB create non vengono eliminate automaticamente dopo questo run.
- Non sono state aggiunte credenziali Data Factory, alterate versioni OneTrust o riconfigurate dipendenze condivise.

## Artefatti

- [Risultati JSON](../tests/reports/rdb-2026-09-23-uat-final/results.json).
- [CSV con tutti i 100 scenari](../tests/reports/rdb-2026-09-23-uat-final/scenarios.csv).
- [JUnit](../tests/reports/rdb-2026-09-23-uat-final/junit), [metadati verificati](../tests/reports/rdb-2026-09-23-uat-final/run-metadata.json).
- [Progress](../tests/reports/rdb-2026-09-23-uat-final/progress.log), [console](../tests/reports/rdb-2026-09-23-uat-final/console.log).

Gli artefatti sotto tests/reports sono locali e ignorati da Git. Il report Markdown e la [guida RDB](rdb.md) sono versionabili.
