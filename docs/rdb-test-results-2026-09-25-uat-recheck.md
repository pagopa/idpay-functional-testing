# RDB ? rilancio mirato UAT del 25 settembre 2026

## Aggiornamento ? portalUrl nei test email

Il contratto aggiornato del backend aggiunge portalUrl ai valori dei template.
I test diretti al servizio email sono stati allineati usando l'URL dev/UAT in base
a TARGET_ENV. **Rilancio mirato UAT: 3 passati, 0 falliti, 9 step passati** (2,099 s);
tutte le risposte sono HTTP 204 con body vuoto. Il precedente problema email non
si riproduce dopo la modifica. Non sono stati acquisiti log interni: la specifica
eccezione FreeMarker dei precedenti 400 non ? confermata.

[Payload effettivi inviati, destinatario oscurato](../tests/reports/rdb-2026-09-25-uat-email-portal-url/email-payloads.json) ?
[JUnit](../tests/reports/rdb-2026-09-25-uat-email-portal-url/junit) ?
[Risultati](../tests/reports/rdb-2026-09-25-uat-email-portal-url/results.json).

Gli altri scenari non sono stati rilanciati: l'ultimo esito noto resta KO per
import vuoto, associazione disabilitata e consenso storico. Questa verifica non
costituisce un nuovo lancio completo della suite.


## Aggiornamento ? rilancio dei soli KO alle 13:41 UTC

Eseguiti esclusivamente i 7 casi falliti nella verifica precedente: **1 passato, 6 falliti**.
**Il token scaduto ora passa anche in UAT**, compresa la verifica HTTP 401. La precedente
indicazione di apply mancante descrive il run precedente e non ? pi? il risultato attuale.
Restano i tre HTTP 400 email, il 500 sull?import vuoto e i due prerequisiti mancanti.
Gli altri 91 scenari non sono stati rieseguiti. Nessuna modifica al codice dei test.

[Risultati e diagnostica](../tests/reports/rdb-2026-09-25-134118-uat-failed-only/summary.json) ?
[JUnit](../tests/reports/rdb-2026-09-25-134118-uat-failed-only/junit).


**9 scenari eseguiti: 2 passati, 7 falliti.** Escludendo il token scaduto, gi? noto in attesa di apply UAT: **8 scenari, 2 passati e 6 falliti**.

Questo ? il rilancio dei nove casi falliti nel JUnit UAT del 25 settembre alle 10:30?10:38 locali. Non ? una nuova esecuzione della suite completa: gli altri 89 casi RDB sono esclusi dalla selezione, non verificati in questo run.
Inizio UTC: 2026-09-25T10:18:31.936626+00:00; fine UTC: 2026-09-25T10:18:40.310764+00:00. Durata Behave: 4,685 s. Exit code Behave: 1. Conteggi JSON e JUnit verificati.

## Esiti dei singoli scenari

| Scenario | Esito | Diagnostica |
| --- | --- | --- |
| Reject an expired application token | failed | ASSERT FAILED: Test signer did not preserve the requested expiration; deploy the exp override from jwt_register_token_test.xml.tpl or configure application_tokens.expired |
| Accept a notification request for an RDB event -- @1.1 | failed | ASSERT FAILED: Expected email service HTTP 204, got 400 |
| Accept a notification request for an RDB event -- @1.2 | failed | ASSERT FAILED: Expected email service HTTP 204, got 400 |
| Accept a notification request for an RDB event -- @1.3 | failed | ASSERT FAILED: Expected email service HTTP 204, got 400 |
| Return exactly the initiatives visible to the current user -- @1.2 | failed | ASSERT FAILED: Missing secrets.asset_register.datasets.producer disabled association; see docs/rdb.md |
| Reject an empty association payload | failed | ASSERT FAILED: Expected HTTP 400, got 500 (POST /idpayassetregisterbackend/idpay/register/producers) |
| Do not request acceptance of an already accepted version | passed |  |
| Request acceptance after the terms and conditions change | failed | ASSERT FAILED: Missing secrets.asset_register.datasets.previous consent version; see docs/rdb.md |
| Reject acceptance of an outdated version | passed |  |

## Email: tre HTTP 400 riprodotti

**Riscontro certo:** tutti e tre i test ricevono 400 invece di 204. Tre ulteriori chiamate diagnostiche, separate dal conteggio degli scenari, restituiscono il codice it.gov.pagopa.email.notification.bad.request e il messaggio Could not prepare mail. Endpoint UAT; nessun mock.

**Analisi del codice locale:** in idpay-notification-email, NotificationServiceImpl.sendMessage cattura tutte le eccezioni di preparazione e invio, le avvolge in MailPreparationException e NotificationExceptionHandler le converte in 400. Quindi il 400 non prova un errore del payload. I placeholder inviati dai test corrispondono ai template locali.

**Intervento:** leggere la causa originale nei log del servizio agli orari delle chiamate salvati in http-diagnostics.json. Controllare prima il caricamento dei template: il codice concatena un backslash prima di index.html, da verificare nel container Linux e uniformare a un percorso classpath con slash. Se il template ? caricato, verificare il rendering e la risposta AWS SES (identit? mittente, eventuali restrizioni sandbox sul destinatario di test, autorizzazioni e connettivit?). Questi sono controlli diagnostici, non cause gi? accertate.

Migliorare NotificationServiceImpl registrando la causa completa senza payload/destinatari e distinguere in NotificationExceptionHandler i veri errori del chiamante dagli errori interni o delle dipendenze. Conservare nei test l?attesa 204; non usare 400 come esito accettabile.

## Import vuoto: HTTP 500 anzich? 400

**Riscontro certo:** sia il test sia la chiamata diagnostica POST interna con producers=[] ricevono 500. Corpo diagnostico: code=GENERIC_ERROR, message=A generic error occurred.

**Analisi del codice locale:** ProducerImportService.importProducers converte la validazione fallita in ResponseStatusException(BAD_REQUEST). ErrorManager.handleException gestisce RuntimeException e riconosce solo ClientExceptionNoBody/ClientExceptionWithBody; il resto diventa 500. Questo percorso spiega il risultato osservato. Senza log/versione distribuita non ? confermato che sia esattamente il percorso eseguito in UAT.

**Intervento in idpay-asset-register-backend:** aggiungere il mapping esplicito di ResponseStatusException rispettandone lo status, oppure utilizzare la ClientExceptionWithBody del progetto per questa validazione. Verificare con un test HTTP controller+advice su producers=[]: un solo test del service non controlla la conversione finale in HTTP. Gli errori interni reali devono continuare a produrre 500.

## Prerequisiti: associazione disabilitata e consenso storico

Entrambi i casi falliscono nel Given, prima di verificare il comportamento applicativo. Mancano rispettivamente datasets.producer disabled association e datasets.previous consent version. Nessuna configurazione fittizia ? stata aggiunta.

La ricerca mostrata dall?utente non ha restituito documenti, ma non sono ancora disponibili le verifiche su esistenza/conteggi delle collection e ambiente del collegamento. Questo non viene trattato come prova definitiva dell?assenza dei dati in UAT.

**Intervento sui dati di test:** verificare database/collection e individuare identit? dedicate ai test. Per l?associazione servono un record producers_initiative con enabled=false e l?insieme delle associazioni ancora abilitate dello stesso produttore. Per il consenso serve un portal_consent con una versione precedente reale e la versione attualmente attiva. Solo dopo questi riscontri impostare profili e dataset nei secret locali.

Le API correnti non permettono di disabilitare un?associazione n? di salvare retroattivamente una versione del consenso. Se i dati non esistono, predisporre fixture controllate fuori dalle API attuali o una capacit? amministrativa limitata all?ambiente di test. Non cambiare la versione OneTrust condivisa soltanto per far passare il caso.

## Consensi: due precedenti HTTP 500 non riprodotti

**Entrambi passati:** Do not request acceptance of an already accepted version e Reject acceptance of an outdated version. Nel secondo caso il test raggiunge ora la POST con versione non corrente, verifica 400 e controlla che il consenso non sia stato salvato. Nessuna modifica ai test e nessun retry aggiunto.

Nel run precedente il primo falliva sulla GET dopo il salvataggio; il secondo sulla GET preliminare, prima della POST negativa. PortalConsentServiceImpl.get consulta repository e OneTrust a ogni chiamata. L?intermittenza ? osservata; attribuirla specificamente a OneTrust, al database o al gateway richiede ancora i log.

**Intervento:** correlare le GET fallite del 25 settembre tra le 10:38:39 e le 10:38:44 Europe/Rome (08:38:39?08:38:44 UTC, orari file JUnit indicativi) con le eccezioni del backend e le chiamate OneTrust. Controllare status delle dipendenze, timeout, throttling e autenticazione; estendere la finestra di ricerca se necessario. Non mascherare il problema con retry automatici della suite.

## Token scaduto e accesso ai log

Il token scaduto continua a fallire nel Given: il signer UAT non conserva exp. Il test non raggiunge la GET con un JWT realmente scaduto. Intervento gi? previsto: apply della policy signer in UAT e successiva verifica HTTP 401.

Il tentativo di lettura pod con il contesto cstar-u-itn-uat-aks continua a fallire con AzureCLICredential: Decryption failed / Key not valid for use in specified state. Sono stati utilizzati i permessi di esecuzione esterna al sandbox; non ? un diniego automatico di approvazione. Nessun log remoto ? stato letto e nessuna causa interna viene presentata come confermata dai log.

L?utente ha confermato che kubectl fallisce anche nella propria shell, nonostante il login al portale Azure da browser. Il login web non ripristina la cache di Azure CLI/kubelogin: serve ripristinare l?autenticazione della CLI prima di ritentare l?accesso ai log. Non sono stati cambiati il contesto Kubernetes predefinito n? risorse del cluster.

## Artefatti ed effetti

- [Risultati JSON](../tests/reports/rdb-2026-09-25-101831-uat-recheck/results.json).
- [JUnit](../tests/reports/rdb-2026-09-25-101831-uat-recheck/junit).
- [Riepilogo verificato con primo step fallito](../tests/reports/rdb-2026-09-25-101831-uat-recheck/summary.json).
- [Corpi HTTP diagnostici e orari UTC](../tests/reports/rdb-2026-09-25-101831-uat-recheck/http-diagnostics.json).
- [Metadati e nomi esatti selezionati](../tests/reports/rdb-2026-09-25-101831-uat-recheck/metadata.json).
- [Console](../tests/reports/rdb-2026-09-25-101831-uat-recheck/console.log).

I test usano servizi UAT reali: creano consensi per UID nuovi e invocano il servizio email con il destinatario di test configurato. Nessun nuovo cleanup o modifica diretta al database. Artefatti locali ignorati da Git; JWT/bearer oscurati.
