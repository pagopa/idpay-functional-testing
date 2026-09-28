# Reward batch counter tests

Questa suite verifica i contatori attraverso un unico flusso end-to-end.

## Come leggere gli scenari Gherkin

- `Given` prepara il dato iniziale.
- `When` esegue l'azione da verificare.
- `Then` controlla il risultato osservabile.
- `And` continua il blocco precedente.

I controlli sono integrati negli scenari esistenti di `reward_batch.feature`
quando il flusso di business e gia coperto. Il file
`reward_batch_counters.feature` contiene soltanto i casi aggiuntivi. Le frasi
aggiunte sono implementate in `bdd/steps/reward_batch_counter_steps.py`.

## Cosa viene verificato

- In `CREATED` i contatori cambiano seguendo le transazioni correnti; uno storno
  rimuove quindi la transazione dai totali e il postpone sposta lo stesso
  contributo live al lotto del mese successivo.
- Al passaggio a `SENT`, `initialAmountCents` rimane lo snapshot acquisito al
  momento dell'invio.
- Da `APPROVING`, `suspendedAmountCents` rimane lo snapshot acquisito prima che
  le transazioni sospese vengano riassegnate.
- Numero e importo delle transazioni `REJECTED` restano live: non hanno uno
  snapshot dedicato.

## Esecuzione

Scenari end-to-end dei contatori:

```shell
behave --tags @reward_batch_counter
```

Come indicato nel README del repository, l'esecuzione end-to-end ufficiale va
lanciata dal workflow GitHub Actions `test-run`, scegliendo il tipo `bdd` e il
tag `reward_batch_counter`. Tutti i casi CREATED, SENT, EVALUATING e APPROVING
sono eseguiti insieme con questa singola opzione.
