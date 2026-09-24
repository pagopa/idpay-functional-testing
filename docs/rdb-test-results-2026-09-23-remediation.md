# RDB - report completo UAT, 24 settembre 2026

**92 PASSATI | 6 FALLITI | 0 ERRORI | 0 SCENARI SALTATI**

Suite completa: **98 scenari**, senza filtri o esclusioni durante il lancio. Exit code 1.
Durata complessiva 450.3 s; timeout HTTP 30 s.
Inizio UTC: 2026-09-24T11:23:57.9392550Z; fine UTC: 2026-09-24T11:31:28.2758650Z.

Step: **533 passati, 6 falliti, 0 in errore, 19 saltati**.
I conteggi di scenari JSON, JUnit e CSV coincidono. Gli step saltati seguono un fallimento nello scenario.

## Modifiche e confronto

- Import e preparazione del produttore senza email usano ora la POST interna del backend, sul base_path.IDPAY.internal già configurato. Eliminati api/data_factory.py e il requisito producer_import_api_key.
- Elenco produttori: le GET di iniziative e prodotti forniscono associazioni note da verificare nella GET /producers, insieme a paginazione, campi obbligatori e assenza di duplicati. Gli override producer_ids mantengono il confronto esatto; senza override non si certifica la completezza delle associazioni senza prodotti.
- Conservata la correzione dei cinque test di lettura prodotti/storico/batch, verificata nel run mirato precedente.
- Rimossi i due scenari di indisponibilità email/OneTrust (RDB-061 e RDB-107) e il supporto WireMock. Non sono conteggiati come passati o saltati.
- I test con KO imposto restano utili come test di resilienza quando verificano il comportamento del backend, in un ambiente con dipendenze controllate. Non appartengono al presente run UAT contro servizi reali.

Rispetto al run completo del 23 settembre (77 passati, 23 falliti su 100): **15 casi recuperati, 0 regressioni, 2 scenari rimossi**.
Rispetto alle cinque correzioni di lettura già verificate: **10 ulteriori casi recuperati**.
Casi recuperati rispetto al precedente run completo: RDB-043, RDB-059, RDB-060, RDB-062, RDB-064, RDB-065, RDB-066, RDB-067, RDB-068, RDB-069, RDB-085, RDB-086, RDB-097, RDB-098, RDB-099.

## Esiti per feature

| Feature | Passati | Falliti | Errori | Saltati |
| --- | ---: | ---: | ---: | ---: |
| Access and authorization to RDB | 6 | 1 | 0 | 0 |
| Manage the product CSV lifecycle | 33 | 2 | 0 | 0 |
| Accept RDB notification payloads at the email service | 3 | 0 | 0 | 0 |
| List the initiatives available to an RDB organization | 5 | 1 | 0 | 0 |
| Preserve RDB processing when the operational email is missing | 2 | 0 | 0 | 0 |
| Manage producer associations and operational email | 10 | 1 | 0 | 0 |
| Change product status with role checks and atomic updates | 12 | 0 | 0 | 0 |
| Consult products, batches and producers in the RDB registry | 17 | 0 | 0 | 0 |
| Accept the current version of the RDB terms and conditions | 4 | 1 | 0 | 0 |

## Fallimenti residui

| ID | Scenario | Gruppo | Diagnostica |
| --- | --- | --- | --- |
| RDB-006 | Reject an expired application token | Prerequisito signer | Test signer did not preserve the requested expiration; deploy the exp override from jwt_register_token_test.xml.tpl or configure application_tokens.expired |
| RDB-026 | Reject concurrent uploads for the same initiative and organization | Prerequisito concorrenza | Missing secrets.asset_register.datasets.upload in progress; see docs/rdb.md |
| RDB-027 | Allow an upload on another initiative | Prerequisito concorrenza | Missing secrets.asset_register.datasets.upload in progress; see docs/rdb.md |
| RDB-049 | Return exactly the initiatives visible to the current user -- @1.2 | Prerequisito associazione | Missing secrets.asset_register.datasets.producer disabled association; see docs/rdb.md |
| RDB-063 | Reject an empty association payload | Difetto HTTP backend | Expected HTTP 400, got 500 (POST /idpayassetregisterbackend/idpay/register/producers) |
| RDB-104 | Request acceptance after the terms and conditions change | Prerequisito versione consenso | Missing secrets.asset_register.datasets.previous consent version; see docs/rdb.md |

- **RDB-006**: Il signer UAT non conserva exp. Serve distribuire la policy che rispetta la scadenza richiesta o fornire un JWT firmato già scaduto. Il controllo 401 su token scaduto non viene raggiunto.
- **RDB-026**: Nessuna API applicativa per mantenere un CSV in UPLOADED/IN_PROCESS. Un upload ordinario non garantisce che resti in corso durante la seconda richiesta. Serve un consumer controllato in ambiente isolato.
- **RDB-027**: Stesso prerequisito di RDB-026: la prima elaborazione deve essere ancora attiva mentre si carica il CSV sulla seconda iniziativa.
- **RDB-049**: Nessuna API applicativa per disabilitare associazioni. Import e reimport impostano enabled=true; la GET delle iniziative nasconde quelle disabilitate.
- **RDB-063**: POST interna /idpay/register/producers con {"producers":[]} restituisce 500 GENERIC_ERROR invece di 400. Correggere la gestione HTTP delle eccezioni nel backend; attesa del test invariata.
- **RDB-104**: La POST consenso accetta solo la versione corrente e la GET non espone quella precedentemente salvata. Serve un utente con consenso storico e un cambio versione controllato, non un ID inventato.

## Evidenze dal backend

- Import: [ProducerImportController](../../idpay-asset-register-backend/src/main/java/it/gov/pagopa/register/controller/operation/ProducerImportController.java) espone POST /idpay/register/producers. Sul runner si usa /idpayassetregisterbackend/idpay/register/producers tramite ingress interno.
- Payload vuoto: [ProducerImportService](../../idpay-asset-register-backend/src/main/java/it/gov/pagopa/register/service/operation/ProducerImportService.java) solleva ResponseStatusException con BAD_REQUEST; il suo test importProducers_shouldRejectEmptyPayload richiede 400. Causa probabile del 500 osservato: [ErrorManager](../../idpay-asset-register-backend/src/main/java/it/gov/pagopa/common/web/exception/ErrorManager.java) intercetta RuntimeException e tratta ResponseStatusException come errore generico. Questa è una deduzione dal codice, senza log del servizio.
- Associazioni: lo stesso import imposta sempre enabled=true. Non sono esposte API applicative di disabilitazione.
- Concorrenza: [ProductFileController](../../idpay-asset-register-backend/src/main/java/it/gov/pagopa/register/controller/operation/ProductFileController.java) espone upload/verifica/lettura, non un comando per mantenere il consumer fermo. Non vengono sospesi consumer condivisi per preparare i test.
- Consenso: [PortalConsentServiceImpl](../../idpay-asset-register-backend/src/main/java/it/gov/pagopa/register/service/role/PortalConsentServiceImpl.java) rifiuta versioni diverse dalla corrente; non permette di creare un consenso storico tramite POST.
- Email in errore: nel backend esiste ProductServiceTest.updateStatuses_rejected_oneEmailFails_returnsOK. La mancata persistenza su errore OneTrust resta una copertura da verificare nei test del backend, non dichiarata passata da questa suite.

## Perimetro ed effetti del run

- I tre test email controllano la risposta reale HTTP 204 con body vuoto, non la consegna in casella.
- Perimetro EPREL e soglie energetiche invariati; gli stati esterni precedentemente esclusi restano fuori dal conteggio.
- Resta la tolleranza temporanea HTTP 500 sul CSV oltre 2 MB, documentata in [TD-RDB-001](rdb.md#td-rdb-001). Il passaggio di quel caso non certifica la correzione del backend.
- La suite usa API UAT reali: upload, import, email operative, consensi e bozze possono scrivere dati. Il modulo rdb_cleanup non è stato reintrodotto; i dati RDB non vengono eliminati automaticamente.
- Nessun nuovo secret aggiunto; nessuna modifica alla versione OneTrust o alle dipendenze condivise.

## Artefatti

- [CSV di tutti i 98 scenari](../tests/reports/rdb-2026-09-24-uat-full/scenarios.csv).
- [Risultati JSON](../tests/reports/rdb-2026-09-24-uat-full/results.json).
- [JUnit](../tests/reports/rdb-2026-09-24-uat-full/junit).
- [Riepilogo verificato](../tests/reports/rdb-2026-09-24-uat-full/summary.json).
- [Metadati](../tests/reports/rdb-2026-09-24-uat-full/run-metadata.json).
- [Console](../tests/reports/rdb-2026-09-24-uat-full/console.log).
- [Progress](../tests/reports/rdb-2026-09-24-uat-full/progress.log).

Confronti storici: [run completo del 23 settembre](../tests/reports/rdb-2026-09-23-uat-final/scenarios.csv) e [verifica mirata delle cinque letture](../tests/reports/rdb-2026-09-24-read-api/scenarios.csv).
Gli artefatti sotto tests/reports sono locali e ignorati da Git; JWT e bearer sono oscurati. La [guida RDB](rdb.md) descrive i prerequisiti residui.
