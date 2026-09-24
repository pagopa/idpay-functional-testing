# Test funzionali RDB

La suite `bdd/features/bonus_elettrodomestici/rdb` contiene 98 scenari indipendenti.
Gli step usano le API dell'ambiente selezionato; i dataset generati non simulano le risposte.
Gli esiti dei run sono riportati nel [report UAT](rdb-test-results-2026-09-23-remediation.md).

## Esecuzione

Nel workflow `test-run` scegliere ambiente `dev`/`uat`, tipo `bdd`, tag `rdb`.
`PARI_TARGET_ENV` seleziona l'ambiente e `PARI_SECRET_PATH` il JSON recuperato da
Key Vault. Le dipendenze sono bloccate in `Pipfile.lock` e installate con `pipenv sync`.
Il comando usato dal runner è:

```console
pipenv run behave bdd/features/bonus_elettrodomestici/rdb --junit --junit-directory tests/reports/behave
```

Per controllare esclusivamente la corrispondenza feature/step, aggiungere `--dry-run`.
Non equivale a un test UAT. `@rdb_fixture` descrive i prerequisiti e non salta i casi.
I tag `@csv_flow_success`, `@csv_flow_formal_errors`, `@csv_flow_initiative_isolation`,
`@csv_flow_eprel`, `@csv_flow_duplicates`, `@csv_flow_reload` e `@csv_flow_history`
permettono di selezionare i flussi CSV.

## Configurazione e secret

Configurare in `asset_register` del JSON dell'ambiente:

| Campo | Uso e riservatezza |
| --- | --- |
| `token_payload.operatore`, `.l1`, `.l2` | Profili esistenti riusati dai builder; dati personali/organizzativi da mantenere fuori da Git |
| `profiles` | Profili aggiuntivi con gli stessi campi, inclusi `orgRole`, `orgId`, `orgEmail`, `uid` |
| `initiatives.A`, `.B` | Override degli ID; in assenza si usano `initiatives.bonus_elettrodomestici.id` e `initiatives.bonus_decoder.id` dell'ambiente |
| `base_path.IDPAY.internal` (fuori da `asset_register`) | Host interno già usato dalla suite; deve essere raggiungibile per `POST /idpayassetregisterbackend/idpay/register/producers`. Non serve una chiave Data Factory |
| `application_tokens.expired` | JWT scaduto firmato, opzionale; trattare comunque come credenziale |
| `email_service.headers` | Secret se contiene bearer token o subscription key |
| `poll_timeout`, `poll_interval` | Polling API, default 120 e 2 secondi; non sono secret |

A e B devono essere configurate per RDB, con template e associazioni compatibili.
Usare produttori di test dedicati, senza scritture concorrenti di altri processi.
ID iniziativa, URL, nomi dei template, soglie energetiche e codici EPREL pubblici non
sono credenziali: non richiedono un secret solo perché sono configurabili.
`conf/rdb/eprel.json` contiene fixture pubbliche; `asset_register.eprel` ne consente l'override.

`conf/pari-feature-secrets.json`, `secrets/` e `tests/reports/`
sono ignorati da Git. Non copiare JWT, URI con password, chiavi, destinatari reali
nei report pubblici.

## Scritture dei test

La suite usa le API UAT reali. Upload e validazioni CSV possono creare prodotti,
record di storico e report; import, aggiornamenti email, consensi e dataset
Invitalia modificano associazioni o creano nuove bozze.
Gli hook generici gestiscono soltanto le iniziative registrate in
`secrets.newly_created`, secondo le opzioni `KEEP_INITIATIVES_*`.
I dati RDB non vengono cancellati automaticamente dopo il run.

## Dataset e prerequisiti residui

`asset_register.datasets` contiene eventuali override con i nomi usati dalle feature.
`profile` seleziona il profilo e `initiative` l'alias A/B. Per i test che scrivono,
le attese derivano dagli input o dalle scritture confermate.

I builder generano CSV, GTIN e utenti unici; preparano filtri, storico, report di un
altro produttore/iniziativa e bozze Invitalia. Il produttore configurato viene
riusato per le letture delle iniziative A/B e per i CSV con GTIN nuovi.

I cinque test di consultazione di prodotti, storico e batch riusano dati esistenti
tramite `GET /idpay-itn/register/initiatives/{initiativeId}/products`, senza import
produttori o upload. La lista completa letta come Invitalia viene filtrata in Python
per costruire l'attesa delle letture per organizzazione e ruolo. Servono prodotti
del produttore configurato e di un'altra organizzazione in A, oltre a prodotti in B.
Questi confronti verificano coerenza e isolamento; non certificano autonomamente
la completezza dell'inventario di partenza.

I riferimenti CSV contenuti nel `batchName` dei prodotti sono confrontati con la GET
`/product-files/batch-list`. Per la GET `/product-files`, lo storico deve includere
i caricamenti noti del produttore in A ed escludere quelli noti di altre organizzazioni
o di B. Può includere altri caricamenti senza prodotti accettati: il confronto esatto
dell'intero storico resta disponibile tramite override `upload_ids` indipendente.
Le due GET hanno lo stesso prefisso `/idpay-itn/register/initiatives/{initiativeId}`.

Il test dell'elenco produttori usa le GET di iniziative e prodotti per ottenere
associazioni note, che devono comparire nella GET `/producers`. Verifica anche
paginazione, identità valorizzate e assenza di duplicati. Non confronta l'intero
elenco con un'attesa ricavata dalla stessa GET: produttori senza prodotti possono
essere presenti. L'override `producer_ids` mantiene il confronto esatto.

I test di import e i due casi senza email usano `ProducerImportController` attraverso
l'host interno già configurato. Il secondo gruppo crea un produttore dedicato con
email assente; la PUT email del portale richiede invece un indirizzo non vuoto.

| Dataset da predisporre esternamente | Campi/prerequisiti |
| --- | --- |
| `producer disabled association` | `profile`, `initiative_ids` delle sole associazioni abilitate; esiste anche un'associazione disabilitata |
| `upload in progress` | `profile`, `initiative`, `product_file_id` in UPLOADED/IN_PROCESS con consumer controllato in ambiente isolato |
| `previous consent version` | `profile`, `previous_version`, `current_version`; UID con consenso precedente reale e cambio versione controllato |

Non risultano API applicative per disabilitare associazioni, trattenere un CSV in
elaborazione o salvare un consenso a una versione precedente. L'import abilita
sempre l'associazione e la POST consenso accetta solo la versione corrente.
I casi restano espliciti nella suite: non si simula il loro prerequisito con ID fittizi.

Override di lettura: registry richiede `organization_id` e `product_gtins`; storico
`upload_ids` (attesa completa), oppure `known_upload_ids` e `foreign_upload_ids`
(inclusione/esclusione); batch `organization_id` e `batch_ids`; report `product_file_id`.
`product filters` richiede `filters` e `filter_product_gtins` per categoria, upload,
EPREL, GTIN, nome prodotto, marca, modello, stato e combinazione categoria/marca/modello/stato.
I casi SelfCare usano `institution_id` e `institution_expected.vatNumber/description`.
Non passare prodotti preesistenti ai test che modificano lo stato.

## Autenticazione, EPREL e notifiche

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
La fixture negativa usa EPREL 703757, lavatrice classe F, verificata nel run conservato.
Il portale permette il download del report degli errori, non del CSV originale di history.

I tre test email invocano direttamente `email_service.notify_url` e richiedono
**HTTP 204 con body vuoto**, senza telemetria. Configurare `test_recipient` con un
indirizzo di test; `authentication: "portal"` genera un token Welfare fresco dai
profili esistenti. Non certificano consegna in casella né trigger automatico RDB.
I due casi di indisponibilità email/OneTrust sono rimossi dalla suite UAT, insieme
al supporto WireMock. Imporre un KO ha senso in un test di resilienza che verifica
la successiva reazione di RDB, con dipendenze controllate in un ambiente isolato.
Non certifica l'indisponibilità del servizio reale. Nel backend esiste già
`ProductServiceTest.updateStatuses_rejected_oneEmailFails_returnsOK` per l'errore
email; la mancata persistenza del consenso in caso di errore OneTrust resta una
copertura da verificare nei test del backend, non dichiarata passata qui.

## TD-RDB-001

La validazione di un CSV oltre 2 MB tollera temporaneamente HTTP 500 nel solo caso
`@rdb_td_001`. Il risultato corretto è HTTP 200, `status: KO`,
`errorKey: product.invalid.file.maxsize`. Un passaggio con 500 non certifica la
correzione del backend. Rimuovere deroga e tag dopo la verifica della correzione in UAT.
