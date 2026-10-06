# Test funzionali RDB

La suite `bdd/features/bonus_elettrodomestici/rdb` contiene 96 scenari indipendenti.
Gli step usano le API dell'ambiente selezionato; i dataset generati non simulano le risposte.
Ultimo lancio completo con pulizia: [DEV, 6 ottobre 2026](rdb-test-results-2026-10-06-dev-full.md),
96 scenari passati e hook finale completato. La verifica della pulizia usa le API
per confermare l'assenza di upload e prodotti, senza controlli diretti dello storage.

## Esecuzione

Installare le dipendenze con `pipenv sync`. Il default in `settings.yaml` è `uat`.
Da PowerShell, selezionare esplicitamente l'ambiente:

```powershell
$env:PARI_TARGET_ENV = "uat"  # oppure "dev"
pipenv run behave --junit --junit-directory "tests/reports/behave" --tags "@rdb"
```

Nel workflow `test-run` scegliere ambiente, tipo `bdd` e tag `rdb`.
Per un solo scenario usare il percorso della feature e `--name "^Nome scenario$"`.

Il file indicato da `PARI_SECRET_PATH` (default `conf/pari-feature-secrets.json`)
deve contenere la sezione dell'ambiente scelto. Gli import richiedono accesso
all'host interno, tramite VPN quando necessaria.

`--dry-run` verifica la corrispondenza tra scenari e step senza eseguire le API.
`@rdb_fixture` segnala un prerequisito: non esclude il caso dal lancio.

## Configurazione e secret

Configurare in `asset_register` del JSON dell'ambiente:

| Campo | Uso e riservatezza |
| --- | --- |
| `token_payload.operatore`, `.l1`, `.l2` | Profili esistenti riusati dai builder; dati personali/organizzativi da mantenere fuori da Git |
| `profiles` | Profili aggiuntivi con gli stessi campi, inclusi `orgRole`, `orgId`, `email`, `uid` |
| `initiatives.A`, `.B` | Override degli ID; in assenza si usano `initiatives.bonus_elettrodomestici.id` e `initiatives.bonus_decoder.id` dell'ambiente |
| `base_path.IDPAY.internal` (fuori da `asset_register`) | Host interno già usato dalla suite; deve essere raggiungibile per `POST /idpayassetregisterbackend/idpay/register/producers`. Non serve una chiave Data Factory |
| `application_tokens.expired` | JWT scaduto firmato, opzionale; trattare comunque come credenziale |
| `email_service` (opzionale) | Eventuali `headers` aggiuntivi; il token viene generato dai profili configurati. Il destinatario fittizio viene da `RDB_EMAIL_TEST_RECIPIENT` nei settings. L'URL usa `base_path.IO`, `IDPAY.domain` e `IDPAY.endpoints.asset_register.notify_path` |
| `poll_timeout`, `poll_interval` | Polling API, default 120 e 2 secondi; non sono secret |

A e B devono essere configurate per RDB, con template e associazioni compatibili.
Usare produttori di test dedicati, senza scritture concorrenti di altri processi.
I profili usano `email` e `orgVAT`, con supporto agli alias `orgEmail` e `orgVat`.
Credenziali, JWT e dati personali restano fuori da Git. URL pubblici, ID iniziativa
e soglie energetiche non sono credenziali.

## Scritture dei test

La suite usa le API reali dell'ambiente selezionato. Upload e validazioni CSV possono creare prodotti,
record di storico e report; import, aggiornamenti email, consensi e dataset
Invitalia modificano associazioni o creano nuove bozze.
Gli hook generici gestiscono soltanto le iniziative registrate in
`secrets.newly_created`, secondo le opzioni `KEEP_INITIATIVES_*`.

La pulizia RDB viene eseguita da `after_all`, anche se alcuni scenari falliscono
e Behave arriva regolarmente all'hook finale. Il tracciamento è solo in memoria,
per il run corrente: non ci sono file di stato né recupero da run interrotti.

- CSV, report, record upload e prodotti vengono eliminati solo per i file creati
  dal run, identificati da organizzazione, iniziativa e nome esatto. Prima di una
  scrittura viene escluso che i GTIN appartengano a prodotti preesistenti.
- Le associazioni nuove vengono eliminate; quelle preesistenti vengono
  ripristinate integralmente, inclusi email e timestamp. Se lo stato osservato
  è cambiato nel frattempo, il backend risponde 409 e non lo sovrascrive.
- Vengono rimossi soltanto i consensi dei nuovi utenti generati dai test e le
  iniziative portal i cui ID provengono dalle creazioni confermate del run.

Il backend deve esporre le API interne `/idpay/register/clean/fixtures`, con
`TEST_SUPPORT_ENABLED=true`, come in `idpay-transactions`. La proprietà applicativa
è `app.test-support.enabled`, con default `false`. I valori Helm DEV/UAT abilitano
la flag; produzione resta disabilitata per default. Gli endpoint non richiedono un token
dedicato. La suite verifica la disponibilità delle API prima degli scenari RDB.
Il controller di pulizia è escluso dalla documentazione Swagger e usa soltanto
l'ingress interno: non vengono aggiunte rotte APIM né modifiche Terraform.

La pulizia attende al massimo 120 secondi per upload ancora in elaborazione
e cancellazioni portal asincrone; il limite è definito nel codice. Una pulizia incompleta
produce un errore nell'hook finale, senza cancellare le associazioni collegate a
upload ancora presenti. Il dry-run non invoca queste API.

## Dataset

`asset_register.datasets` contiene eventuali override con i nomi usati dalle feature.
`profile` seleziona il profilo e `initiative` l'alias A/B. Per i test che scrivono,
le attese derivano dagli input o dalle scritture confermate.

La suite prepara tramite API CSV, prodotti, storico, report, associazioni e bozze.
Quattro test di lettura prodotti/batch riusano dati esistenti: servono prodotti
del produttore configurato e di un'altra organizzazione in A, oltre a prodotti in B.
Verificano coerenza e isolamento, non la completezza indipendente dell'inventario.
I casi SelfCare richiedono un'istituzione esistente con partita IVA nota.

Per decisione dello standup, i casi di riaccettazione dopo un cambio versione e di
associazione produttore disabilitata sono rimossi dalla suite Behave. La copertura
resta nei test JUnit del backend; una futura integrazione UAT è rinviata, senza
sviluppare ora API dedicate ai test. Non sono conteggiati come passati o saltati.
Dettagli nel [documento di decisione](rdb-team-discussion.md).
I report storici conservano il perimetro originale di 98 scenari.

I test concorrenti preparano un CSV EPREL da 100 righe e ne verificano lo stato
attivo prima e dopo il secondo upload. Non richiedono `datasets.upload in progress`.
Il produttore deve essere abilitato su A/B e non avere altri upload attivi; il test
attende il completamento del proprio CSV senza sospendere consumer condivisi.

## Perimetro funzionale

Il signer `/register/token/test` genera JWT applicativi; non è uno scambio reale
SelfCare. Il test del token scaduto richiede che la policy rispetti `exp`, oppure
un JWT firmato già scaduto in `application_tokens.expired`.

Le condizioni EPREL product not found/not published/blocked e organization/brand
not verified sono fuori dal perimetro concordato e non sono conteggiate come passate.
Restano categoria, elaborazione valida/mista e classe energetica minima:

| Categoria | Minimo |
| --- | --- |
| WASHINGMACHINES, WASHERDRIERS, OVENS | A |
| RANGEHOODS | B |
| DISHWASHERS, TUMBLEDRYERS | C |
| REFRIGERATINGAPPL | D |
| COOKINGHOBS | Nessun controllo EPREL |

Tutte usano `Codice GTIN/EAN`. Per le categorie EPREL il template è EPREL_STANDARD.
Fixture pubbliche in `conf/rdb/eprel.json`, con override tramite `asset_register.eprel`.
Il portale permette il download del report degli errori, non del CSV originale di history.

I due scenari di indisponibilità forzata email/OneTrust sono esclusi dalla suite.
La resilienza con dipendenze simulate va verificata nei test backend.

## Email e report

I tre test email invocano direttamente il servizio e richiedono **HTTP 204 con body
vuoto**. `templateValues.portalUrl` deriva da `TARGET_ENV` e dalla mappa
`RDB_EMAIL_PORTAL_URLS` in `settings.yaml`, con URL dev/UAT. Una voce assente blocca
l'invio. Il servizio costruisce l'HTML dai template; il test non certifica la
consegna in casella né il trigger automatico del backend RDB.

Il payload viene stampato con destinatario oscurato e senza token. In caso di KO
l'assertion include `code` e `message`. Con JUnit lo stdout finisce negli XML;
senza JUnit, `--no-capture` permette di visualizzarlo in console.

`tests/reports/` contiene risultati generati, ignorati da Git e ripulibili quando
non servono più. JUnit è il formato XML dei risultati, non un'altra suite.
I file `tests/test_*.py` appartengono invece alla suite pytest e non sono report.

## TD-RDB-001

La validazione di un CSV oltre 2 MB tollera temporaneamente HTTP 500 nel solo caso
`@rdb_td_001`. Il risultato corretto è HTTP 200, `status: KO`,
`errorKey: product.invalid.file.maxsize`. Un passaggio con 500 non certifica la
correzione del backend. Rimuovere deroga e tag dopo la verifica della correzione nell'ambiente selezionato.
