# Test funzionali RDB

La suite `bdd/features/bonus_elettrodomestici/rdb` contiene 98 scenari indipendenti.
Gli step usano le API dell'ambiente selezionato; i dataset generati non simulano le risposte.
Ultimo lancio completo: [UAT, 25 settembre 2026](rdb-test-results-2026-09-25-uat-full.md).

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
| `email_service` | `notify_url` dell'ambiente, `test_recipient` dedicato, eventuali `headers`; `authentication: "portal"` genera il token dai profili configurati |
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
I dati RDB non vengono cancellati automaticamente dopo il run.

## Dataset e prerequisiti residui

`asset_register.datasets` contiene eventuali override con i nomi usati dalle feature.
`profile` seleziona il profilo e `initiative` l'alias A/B. Per i test che scrivono,
le attese derivano dagli input o dalle scritture confermate.

La suite prepara tramite API CSV, prodotti, storico, report, associazioni e bozze.
Quattro test di lettura prodotti/batch riusano dati esistenti: servono prodotti
del produttore configurato e di un'altra organizzazione in A, oltre a prodotti in B.
Verificano coerenza e isolamento, non la completezza indipendente dell'inventario.
I casi SelfCare richiedono un'istituzione esistente con partita IVA nota.

| Dataset da predisporre esternamente | Campi/prerequisiti |
| --- | --- |
| `producer disabled association` | `profile`, `initiative_ids` delle sole associazioni abilitate; esiste anche un'associazione disabilitata |
| `previous consent version` | `profile`, `previous_version`, `current_version`; UID con una versione salvata a DB diversa da quella corrente |

Per il mismatch del consenso basta una versione salvata diversa, anche sintetica:
inserirla nei secret non modifica il DB. Non occorre cambiare OneTrust. Le API
attuali non consentono questa preparazione o la disabilitazione di associazioni.
Opzioni e pro/contro sono nel [documento di discussione](rdb-team-discussion.md).

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
