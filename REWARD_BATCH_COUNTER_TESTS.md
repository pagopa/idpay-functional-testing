# Reward batch counter tests

Questa suite separa i controlli veloci sulle formule dai flussi end-to-end.

## Come leggere gli scenari Gherkin

- `Given` prepara il dato iniziale.
- `When` esegue l'azione da verificare.
- `Then` controlla il risultato osservabile.
- `And` continua il blocco precedente.

Il file `bdd/features/bonus_elettrodomestici/reward_batch_counters.feature`
descrive i casi di business senza contenere codice Python. Le frasi aggiunte sono
implementate in `bdd/steps/reward_batch_counter_steps.py`.

## Cosa viene verificato

- In `CREATED` i contatori cambiano seguendo le transazioni correnti; uno storno
  rimuove quindi la transazione dai totali.
- Al passaggio a `SENT`, `initialAmountCents` rimane lo snapshot acquisito al
  momento dell'invio.
- Da `APPROVING`, `suspendedAmountCents` rimane lo snapshot acquisito prima che
  le transazioni sospese vengano riassegnate.
- Numero e importo delle transazioni `REJECTED` restano live: non hanno uno
  snapshot dedicato.

I test in `tests/test_reward_batch_counters.py` verificano le stesse formule in
memoria, senza chiamate HTTP. Sono il controllo più rapido durante lo sviluppo.

## Esecuzione

Test veloci locali, in un ambiente con le dipendenze del progetto:

```shell
pytest tests/test_reward_batch_counters.py -q
```

Scenari end-to-end mirati:

```shell
behave --tags @reward_batch_counters
```

Come indicato nel README del repository, l'esecuzione end-to-end ufficiale va
lanciata dal workflow GitHub Actions `test-run`, scegliendo il tipo `bdd` e il
tag `reward_batch_counters`.
