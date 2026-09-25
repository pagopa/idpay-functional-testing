# RDB - report completo DEV, 24 settembre 2026

**90 PASSATI | 8 FALLITI | 0 ERRORI | 0 SCENARI RDB SALTATI**

Suite completa RDB: 98 scenari. Exit code 1; durata 444.2 s.
Inizio UTC: 2026-09-24T20:24:49.0951357Z; fine UTC: 2026-09-24T20:32:13.2693782Z.
Step RDB: 542 passati, 8 falliti, 0 in errore, 7 saltati.
I conteggi JSON e JUnit coincidono; il CSV contiene tutti i 98 scenari. I 333 scenari saltati nel riepilogo generale Behave appartengono ad altre suite, escluse dal tag @rdb.

## Avvio da shell e correzioni

```powershell
$env:PARI_TARGET_ENV = "dev"
pipenv run behave --junit --junit-directory "tests/reports/behave" --tags "@rdb"
```

- Ambiente predefinito dev. Il caricamento verifica subito che il file secret contenga la sezione selezionata: prima una sezione assente diventava un dizionario vuoto, causando AttributeError nel before_feature. Gli hook ora accedono ai dizionari tramite chiavi.
- Payload JWT compatibile con email e orgVAT del signer dev; normalizzazione dei precedenti orgEmail e orgVat. Nessuna modifica manuale alla firma.
- RDB-026/027 avviano un vero upload EPREL da 100 righe in un worker e inviano il secondo durante la prima elaborazione. Lo stato della prima deve essere attivo sia prima sia dopo la seconda risposta. Nessun dataset upload in progress n? arresto del consumer.
- Iniziative abilitate, storico CSV e produttori sono preparati con import/upload reali e identificativi nuovi. Lo storico ha due upload attesi, un controllo di altra iniziativa e uno di altro produttore.
- SelfCare viene confrontato con la partita IVA attesa e una descrizione valorizzata; il nome arbitrario del JWT non ? una fonte autorevole della ragione sociale. Un override permette ancora il confronto esatto della descrizione.
- L?import usa l?ingress interno del backend e richiede la VPN. L?endpoint email locale ? stato allineato a dev.

Token scaduto RDB-006, concorrenza RDB-026/027 e tutti i 35 casi CSV sono passati nel presente lancio. Nessun HOOK-ERROR in before_feature.

## Esiti per feature

| Feature | Passati | Falliti | Errori | Saltati |
| --- | ---: | ---: | ---: | ---: |
| Access and authorization to RDB | 7 | 0 | 0 | 0 |
| Manage the product CSV lifecycle | 35 | 0 | 0 | 0 |
| Accept RDB notification payloads at the email service | 0 | 3 | 0 | 0 |
| List the initiatives available to an RDB organization | 5 | 1 | 0 | 0 |
| Preserve RDB processing when the operational email is missing | 2 | 0 | 0 | 0 |
| Manage producer associations and operational email | 10 | 1 | 0 | 0 |
| Change product status with role checks and atomic updates | 12 | 0 | 0 | 0 |
| Consult products, batches and producers in the RDB registry | 15 | 2 | 0 | 0 |
| Accept the current version of the RDB terms and conditions | 4 | 1 | 0 | 0 |

## Casi non passati

| ID | Scenario | Diagnostica | Intervento |
| --- | --- | --- | --- |
| EMAIL-001 | Accept a notification request for an RDB event -- @1.1 | ASSERT FAILED: Expected email service HTTP 204, got 400 | HTTP 204 resta obbligatorio. Il servizio restituisce 400; una chiamata diagnostica ha riportato Could not prepare mail. Verificare i log del servizio, template/configurazione e invio SES: il messaggio esterno non identifica la causa. |
| EMAIL-002 | Accept a notification request for an RDB event -- @1.2 | ASSERT FAILED: Expected email service HTTP 204, got 400 | HTTP 204 resta obbligatorio. Il servizio restituisce 400; una chiamata diagnostica ha riportato Could not prepare mail. Verificare i log del servizio, template/configurazione e invio SES: il messaggio esterno non identifica la causa. |
| EMAIL-003 | Accept a notification request for an RDB event -- @1.3 | ASSERT FAILED: Expected email service HTTP 204, got 400 | HTTP 204 resta obbligatorio. Il servizio restituisce 400; una chiamata diagnostica ha riportato Could not prepare mail. Verificare i log del servizio, template/configurazione e invio SES: il messaggio esterno non identifica la causa. |
| RDB-049 | Return exactly the initiatives visible to the current user -- @1.2 | ASSERT FAILED: Missing secrets.asset_register.datasets.producer disabled association; see docs/rdb.md | Import e reimport impostano enabled=true. Non esiste una API applicativa per creare o disabilitare questa associazione: serve un dato predisposto o una nuova API. |
| RDB-063 | Reject an empty association payload | ASSERT FAILED: Expected HTTP 400, got 500 (POST /idpayassetregisterbackend/idpay/register/producers) | Il payload producers vuoto deve restituire 400. Verificare la gestione di ResponseStatusException nel backend: il catch generico di RuntimeException pu? trasformarlo in 500. |
| RDB-100 | Retrieve a producer registered in SelfCare | ASSERT FAILED: Expected HTTP 200, got 500 (GET /idpay-itn/register/institutions/72c2c5f8-1c71-4614-a4b3-95e3aee71c3d) | GET institutions restituisce 500. Verificare backend/dipendenza SelfCare. Nel caso non autorizzato fallisce il controllo preliminare autorizzato: il rifiuto al produttore non viene raggiunto. |
| RDB-101 | Reject an unauthorized request for producer information | ASSERT FAILED: Expected HTTP 200, got 500 (GET /idpay-itn/register/institutions/72c2c5f8-1c71-4614-a4b3-95e3aee71c3d) | GET institutions restituisce 500. Verificare backend/dipendenza SelfCare. Nel caso non autorizzato fallisce il controllo preliminare autorizzato: il rifiuto al produttore non viene raggiunto. |
| RDB-104 | Request acceptance after the terms and conditions change | ASSERT FAILED: Missing secrets.asset_register.datasets.previous consent version; see docs/rdb.md | La POST accetta solo la versione corrente. Serve un consenso precedente realmente salvato e un cambio versione controllato; un ID inventato non verifica il caso. |

## Interpretazione e confronto

- Il primo lancio completo dev aveva 86 passati e 12 falliti. Dopo la correzione delle fixture, un lancio intermedio ha avuto 40 passati e 58 falliti: 53 di questi erano risposte HTTP 502/503, comparse a partire dalla paginazione dello storico. La causa infrastrutturale precisa non ? accertata.
- Prima del presente rilancio la GET delle iniziative ? tornata HTTP 200. I risultati di questa pagina provengono tutti dal nuovo lancio completo; non sono un insieme dei migliori risultati di prove diverse.
- I tre test email richiedono HTTP 204 e body vuoto. Il messaggio Could not prepare mail ? generico: nel codice locale NotificationServiceImpl cattura eccezioni sia della preparazione sia dell?invio AWS SES. Non dimostra da solo che il template manchi.
- Per il payload import vuoto, il codice locale ProducerImportService solleva BAD_REQUEST, mentre ErrorManager gestisce genericamente RuntimeException. ? una possibile spiegazione del 500, da confermare con i log del servizio.
- In questo lancio anche le due verifiche SelfCare ricevono HTTP 500 sulla GET institutions. Nel caso negativo fallisce il controllo preliminare autorizzato che prova l?esistenza del dato. Le stesse verifiche erano passate nelle prove precedenti: la causa del nuovo 500 richiede diagnostica del servizio, non ? dimostrata una regressione dei test.
- Per associazione disabilitata e consenso storico non sono state trovate API per predisporre gli stati necessari. I casi restano falliti esplicitamente per prerequisito mancante; non vengono simulati n? dichiarati passati.

## Perimetro ed effetti

- Rimossi i due scenari con indisponibilit? email/OneTrust imposta via mock: non sono contati come passati o saltati. Restano 98 scenari.
- EPREL e soglie energetiche seguono il perimetro concordato nella guida. Il download verificato ? il report degli errori, non il CSV originale.
- Rimane la tolleranza temporanea HTTP 500 per CSV oltre 2 MB, documentata come TD-RDB-001: un passaggio non certifica la correzione backend.
- Le API reali possono creare prodotti, upload, associazioni, consensi e bozze, aggiornare stati e inviare notifiche. Come richiesto, rdb_cleanup non ? stato reintrodotto: i dati non vengono eliminati automaticamente.
- Token e bearer nei report sono oscurati; file di secret e relativi backup sono ignorati da Git. Gli artefatti sotto tests/reports sono locali e ignorati da Git.

## Verifica dopo ottimizzazione del codice

Verifica mirata su dev: **5 scenari passati, 0 falliti**, 32 step passati, durata Behave 41,403 s.
Copertura: RDB-006, RDB-026/027, isolamento dello storico CSV e ordinamento delle iniziative.
Il refactoring centralizza la registrazione dei profili e il completamento degli upload,
verifica gli alias delle iniziative prima delle scritture e conserva l'errore originale
se fallisce anche l'attesa finale del CSV concorrente. Verificati localmente anche i percorsi
di errore e la separazione dei payload; il dry-run riconosce tutti i 98 scenari.
Questa verifica mirata non sostituisce il lancio completo da 90 passati e 8 falliti riportato sopra.

[JSON della verifica mirata](../tests/reports/rdb-2026-09-24-dev-optimization/results.json) ?
[JUnit](../tests/reports/rdb-2026-09-24-dev-optimization/junit).

## Artefatti

- [CSV completo dei 98 casi](../tests/reports/rdb-2026-09-24-dev-rerun/scenarios.csv).
- [Risultati JSON](../tests/reports/rdb-2026-09-24-dev-rerun/results.json).
- [JUnit](../tests/reports/rdb-2026-09-24-dev-rerun/junit).
- [Riepilogo verificato](../tests/reports/rdb-2026-09-24-dev-rerun/summary.json).
- [Metadati del lancio](../tests/reports/rdb-2026-09-24-dev-rerun/run-metadata.json).
- [Console](../tests/reports/rdb-2026-09-24-dev-rerun/console.log).
- [Progress](../tests/reports/rdb-2026-09-24-dev-rerun/progress.log).

[Guida RDB](rdb.md). [Primo completo DEV](../tests/reports/rdb-2026-09-24-dev-full/results.json). [Lancio intermedio con 502/503](../tests/reports/rdb-2026-09-24-dev-final/results.json).

## Diagnostica UAT del 25 settembre

Questa verifica non sostituisce il lancio completo DEV descritto sopra.

- Email: tre chiamate riproducono HTTP 400 con codice it.gov.pagopa.email.notification.bad.request e messaggio Could not prepare mail. Il servizio raggruppa errori template e SES nella stessa MailPreparationException; il corpo non identifica la causa interna.
- Consensi: i tre profili di test configurati restituiscono 200 e oggetto vuoto (versione corrente gi? accettata). Tre letture di un UID nuovo restituiscono 200 e firstAcceptance=true. Nessun consenso storico individuato tra questi profili.
- Rilancio dei due casi precedentemente in 500: **2 passati, 0 falliti**, 9 step passati. Errori precedenti intermittenti; la dipendenza responsabile non ? stata identificata.
- Prerequisiti: nessun dataset o profilo aggiuntivo nei file locali UAT/dev. Le API nascondono le associazioni disabilitate e non espongono la versione del consenso gi? salvata. Nessun valore fittizio inserito nei secret.
- Accesso log: contesto Kubernetes UAT presente, ma AzureCLICredential fallisce con Decryption failed / Key not valid. Serve ripristinare l'autenticazione prima di consultare i log.
- Import vuoto: ProducerImportService solleva ResponseStatusException(BAD_REQUEST), ErrorManager tratta le RuntimeException non ClientException come 500. Correggere il mapping di ResponseStatusException oppure usare la ClientExceptionWithBody prevista dal progetto; verificare con un test HTTP controller/advice, non solo del service.
- Email: verificare il caricamento del template nel pacchetto Linux (il codice locale concatena un backslash prima di index.html), i placeholder e l'errore SES effettivo. Registrare la causa con stack trace senza payload o destinatari; distinguere errori del chiamante da errori interni/dipendenze nel NotificationExceptionHandler.
- Consensi: correlare i 500 alla GET consent e alla chiamata OneTrust, controllando eccezioni Feign, timeout, throttling, autenticazione e accesso repository. Non aggiungere retry ai test per mascherare il problema.

[Risposte diagnostiche](../tests/reports/rdb-2026-09-25-uat-diagnostics/responses.json),
[rilancio consensi](../tests/reports/rdb-2026-09-25-uat-diagnostics/consent-results.json),
[query di sola lettura per cercare i prerequisiti](../tests/reports/rdb-2026-09-25-uat-diagnostics/prerequisite-read-queries.json).
Le query sono preparate ma non eseguite; eventuali candidati vanno verificati come identit? dedicate ai test prima dell'utilizzo.
