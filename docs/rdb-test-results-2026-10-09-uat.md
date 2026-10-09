# RDB UAT - 9 ottobre 2026

Suite completa con pulizia semplificata: **95 scenari passati, 1 fallito**.
**546 step passati, 1 fallito**, 2 step RDB successivi al fallimento non eseguiti.
Gli altri 337 scenari sono esclusi dal tag `@rdb`.
Durata degli step: **9 minuti e 33,726 secondi**. Exit code: **1**.

| Feature | Passati | Falliti |
| --- | ---: | ---: |
| `authorization` | 7 | 0 |
| `csv` | 34 | 1 |
| `email_service` | 3 | 0 |
| `initiatives` | 5 | 0 |
| `notification` | 2 | 0 |
| `producer` | 11 | 0 |
| `product_status` | 12 | 0 |
| `read_registry` | 17 | 0 |
| `terms_and_conditions` | 4 | 0 |

## Caso fallito e riscontro

`csv.feature:123` - **Allow an upload on another initiative**.
Il passo fallito è la verifica che il primo CSV fosse ancora in elaborazione sia
prima sia dopo la seconda richiesta di upload. Il messaggio è:

> The first CSV finished before overlap could be proved; concurrency result is inconclusive

Il caso è stato rilanciato isolatamente: **stesso fallimento**, dopo 11,381 secondi.
Questo risultato non dimostra un rifiuto dell'upload su B: il fallimento riguarda
la prova della sovrapposizione temporale. Il run non certifica quindi il requisito
concorrente previsto dallo scenario.

Intervento: rivedere la preparazione del primo upload e la finestra di osservazione,
affinche la sovrapposizione sia dimostrabile nell'ambiente UAT attuale. Mantenere
l'asserzione sulla concorrenza; non considerare passato un caso in cui il primo
upload ha già terminato. Nessuna modifica al test effettuata in questo rilancio.

## Correzione successiva e verifica

I controlli preliminari della pulizia eseguivano chiamate HTTP nella finestra
misurata dal test. Ora vengono completati per entrambi i file prima di iniziare
il primo upload; i decoratori riusano il tracciamento senza ripetere i controlli.
Il CSV resta di 100 righe, il massimo previsto dal validatore backend.
Le asserzioni sugli stati prima e dopo la seconda richiesta restano invariate.

Verifica UAT: i due casi concorrenti sono passati in due lanci consecutivi
(**4 esecuzioni riuscite**, con sovrapposizione confermata e pulizia completata
in tutti i casi). Durate: 21,556 e 21,659 secondi. **27 test unitari passati**.
La suite completa non è stata rilanciata dopo questa correzione; il risultato
95/96 sopra documenta il lancio precedente.
Report: `tests/reports/rdb-concurrency-fix-2026-10-09/first/` e `repeat/`.

## Pulizia

**96 completamenti della pulizia** nel lancio completo e **1 nel rilancio isolato**.
Nessun errore degli hook. Anche i dati dello scenario fallito sono stati puliti.
Le verifiche degli hook usano le API: nessuna query diretta al database o controllo
sullo storage. Import e modifica email utilizzano associazioni dedicate.

## Limiti noti

Il caso CSV oltre 2 MB ha restituito **HTTP 500**, accettato dalla deroga temporanea
TD-RDB-001; il suo passaggio non certifica la correzione backend.
I tre casi email sono passati con HTTP 204, senza verifica della consegna in casella.

## Artefatti

- Lancio completo: `tests/reports/rdb-cleanup-simplified-2026-10-09-full/`.
- Rilancio isolato: `tests/reports/rdb-cleanup-simplified-2026-10-09-retry/`.

Entrambe le cartelle contengono JSON, JUnit, progresso e log del lancio.
