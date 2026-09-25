# RDB ? suite completa UAT, 25 settembre 2026

**98 scenari: 95 passati, 3 falliti, 0 errori, 0 saltati.**

Inizio UTC: 2026-09-25T14:58:17.3990117Z; fine UTC: 2026-09-25T15:06:40.6951071Z. Durata totale 503.3 s; exit code 1.
Intera suite RDB selezionata con @rdb, senza esclusioni di casi RDB. I 333 scenari di altre suite esclusi dal tag non rientrano nei 98.
Step RDB: 549 passati, 3 falliti, 0 errori, 5 saltati. Conteggi JSON/JUnit verificati.

## Risultati per feature

| Feature | OK | KO | Errori | Saltati |
| --- | ---: | ---: | ---: | ---: |
| Access and authorization to RDB | 7 | 0 | 0 | 0 |
| Manage the product CSV lifecycle | 35 | 0 | 0 | 0 |
| Accept RDB notification payloads at the email service | 3 | 0 | 0 | 0 |
| List the initiatives available to an RDB organization | 5 | 1 | 0 | 0 |
| Preserve RDB processing when the operational email is missing | 2 | 0 | 0 | 0 |
| Manage producer associations and operational email | 10 | 1 | 0 | 0 |
| Change product status with role checks and atomic updates | 12 | 0 | 0 | 0 |
| Consult products, batches and producers in the RDB registry | 17 | 0 | 0 | 0 |
| Accept the current version of the RDB terms and conditions | 4 | 1 | 0 | 0 |

## Problemi e interventi

| Scenario | Primo step fallito / riscontro | Intervento |
| --- | --- | --- |
| Return exactly the initiatives visible to the current user -- @1.2 | Giventhe RDB dataset is "producer disabled association": ASSERT FAILED: Missing secrets.asset_register.datasets.producer disabled association; see docs/rdb.md | Predisporre una vera associazione disabilitata per un produttore di test e configurare il dataset. L?import imposta enabled=true e la GET nasconde i disabilitati. |
| Reject an empty association payload | Thenthe RDB response has HTTP status 400: ASSERT FAILED: Expected HTTP 400, got 500 (POST /idpayassetregisterbackend/idpay/register/producers) | Correggere il mapping delle eccezioni in asset-register-backend: ProducerImportService solleva ResponseStatusException(400), mentre ErrorManager tratta le RuntimeException non ClientException come 500. Verificare controller+advice con un test HTTP. |
| Request acceptance after the terms and conditions change | Giventhe RDB dataset is "previous consent version": ASSERT FAILED: Missing secrets.asset_register.datasets.previous consent version; see docs/rdb.md | Predisporre un consenso storico reale per un UID di test e configurare versione precedente/corrente. La POST accetta soltanto la versione corrente. |

## Controlli rilevanti

- Reject an expired application token: **passed**.
- Reject concurrent uploads for the same initiative and organization: **passed**.
- Allow an upload on another initiative: **passed**.
- Accept a notification request for an RDB event -- @1.1: **passed**.
- Accept a notification request for an RDB event -- @1.2: **passed**.
- Accept a notification request for an RDB event -- @1.3: **passed**.
- Do not request acceptance of an already accepted version: **passed**.
- Reject acceptance of an outdated version: **passed**.

## Perimetro e limiti

- I test email includono portalUrl UAT tramite TARGET_ENV e RDB_EMAIL_PORTAL_URLS. Verificano HTTP 204 con body vuoto, non la consegna in casella. Il JUnit contiene i payload con destinatario oscurato.
- Tutti gli esiti riportati provengono da questo unico lancio completo; non sono aggregati da esecuzioni precedenti.
- Nessun log Azure/AKS ? stato acquisito in questo lancio. Le spiegazioni ricavate dal codice locale non certificano la versione o lo stack trace distribuiti.
- Rimane la deroga TD-RDB-001 per CSV oltre 2 MB: un passaggio che tollera 500 non certifica la correzione backend. Il perimetro EPREL e i due scenari di indisponibilit? rimossi restano invariati.
- La suite usa API UAT reali e pu? creare prodotti, upload, associazioni, bozze e consensi e invocare notifiche. rdb_cleanup non ? stato reintrodotto; i dati RDB non sono cancellati automaticamente.
- Gli artefatti sono locali e ignorati da Git; JWT/bearer oscurati.

## Artefatti

- [Riepilogo completo dei 98 casi](../tests/reports/rdb-2026-09-25-145817-uat-full/summary.json).
- [Risultati JSON](../tests/reports/rdb-2026-09-25-145817-uat-full/results.json).
- [JUnit](../tests/reports/rdb-2026-09-25-145817-uat-full/junit).
- [Metadati](../tests/reports/rdb-2026-09-25-145817-uat-full/metadata.json).
- [Console](../tests/reports/rdb-2026-09-25-145817-uat-full/console.log).
- [Progress](../tests/reports/rdb-2026-09-25-145817-uat-full/progress.log).

[Verifiche mirate precedenti](rdb-test-results-2026-09-25-uat-recheck.md).
