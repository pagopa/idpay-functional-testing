# RDB UAT - suite completa con pulizia per scenario

Esito: **96 scenari e 549 step passati**, 9 feature; nessun fallimento o errore.
Exit code: **0**. Durata degli step: **9 minuti e 40,663 secondi**.
I 337 scenari delle altre suite sono esclusi dal tag `@rdb`.

| Feature | Scenari passati |
| --- | ---: |
| `authorization` | 7 |
| `csv` | 35 |
| `email_service` | 3 |
| `initiatives` | 5 |
| `notification` | 2 |
| `producer` | 11 |
| `product_status` | 12 |
| `read_registry` | 17 |
| `terms_and_conditions` | 4 |

## Pulizia

I report JUnit registrano **96 completamenti della pulizia**, uno per
scenario, senza errori degli hook. Gli upload vengono eliminati tramite API e
l'assenza del relativo record viene verificata; le associazioni dedicate vengono
eliminate e verificate assenti. Consensi e bozze portal vengono rimossi attraverso
le rispettive API. Non sono state eseguite query dirette al database o verifiche
sullo storage.

Import, reimport e aggiornamenti email usano identità dedicate: non modificano
l'associazione del produttore condiviso. Il tracciamento resta in memoria per
scenario; l'hook finale ritenta soltanto le pulizie incomplete. Non esiste recupero
da crash o interruzioni forzate.

## Limiti del risultato

Resta TD-RDB-001: in questo lancio il caso CSV oltre 2 MB ha restituito HTTP 500,
accettato dalla tolleranza temporanea del test.
Il passaggio di questo scenario non certifica la correzione del backend.
I tre casi email verificano HTTP 204, senza certificare la consegna in casella.

## Artefatti

Log, JSON completo, progresso e JUnit: `tests/reports/rdb-uat-scenario-cleanup-full/`.
Comando: `PARI_TARGET_ENV=uat pipenv run behave --tags @rdb --junit`.
