# Ranking e ranking family: archivio per Bonus Valore

Queste suite sono conservate per una futura riattivazione, come richiesto il
2 novembre 2026. Non sono suite attive né test già adattati o validati per Bonus Valore.

## Contenuto e provenienza

- `features/ranking/`: 4 feature su graduatorie individuali.
- `features/ranking_family/`: 4 feature su graduatorie familiari.
- Totale: **31 scenari espansi**, inclusi i casi storicamente marcati `@skip`.
- `reference/ranking_steps.py.txt`: copia integrale degli step specifici di graduatoria,
  salvata come testo per non registrare step o importare dipendenze obsolete.
- `manifest.json`: commit di provenienza, percorsi originali, hash SHA-256, elenco
  dei 39 step di riferimento e degli step senza corrispondenza nella baseline.

Le otto feature e il file degli step sono copie esatte del commit
`5d44f94ee86284af81fff94b8f2b1bbb425c56da`, precedente alla bonifica.
Il percorso esterno a `bdd/` li esclude dalla discovery ordinaria, dalla matrice
Bonus e dalla documentazione generata da `bdd/features`. Non aggiungere questo
archivio ai percorsi di esecuzione senza completare la riattivazione.

## Dipendenze di riferimento

La conservazione non reinstalla le dipendenze legacy nell'ambiente attivo.
Il manifest identifica i vecchi step necessari; le versioni complete di utility,
API e configurazioni restano recuperabili dal commit sorgente. I file ancora
presenti nel repository potrebbero aver perso alcune funzioni durante la bonifica.

| Modulo originale | Step richiamati dagli scenari archiviati |
|---|---|
| `bdd/steps/dataset_steps.py` | `step_citizen_fc_exact_or_random`, `step_citizens_fc_exact_or_random`, `step_set_citizen_isee`, `step_set_citizens_isee` |
| `bdd/steps/discount_transaction_steps.py` | `step_check_latest_pre_authorization_failed_citizen_not_onboard`, `step_check_named_transaction_status`, `step_when_merchant_generated_a_named_transaction`, `step_when_merchant_tries_to_create_a_transaction`, `step_when_onboard_citizen_confirms_transaction` |
| `bdd/steps/family_steps.py` | `step_check_absence_in_ranking_families`, `step_given_same_family_id` |
| `bdd/steps/idpay_code_steps.py` | `step_check_latest_trx_creation_through_mil`, `step_merchant_tries_to_generate_a_transaction_mil` |
| `bdd/steps/initiative_steps.py` | `step_create_new_initiative`, `step_given_initiative_name`, `step_initiative_has_a_rank`, `step_initiative_in_grace_period` |
| `bdd/steps/onboarding_steps.py` | `step_check_citizens_correct_election`, `step_check_onboarding_citizens_status`, `step_check_onboarding_status`, `step_citizen_accepts_tos`, `step_citizen_tries_to_onboard`, `step_citizens_join_ranking`, `step_family_member_onboards_ranking`, `step_merchant_random_onboard`, `step_named_citizen_joins_ranking`, `step_named_citizen_suspension`, `step_save_pdnd_consent_not_correctly` |
| `bdd/steps/ranking_steps.py` | `step_check_absence_in_ranking`, `step_check_citizen_ranking_status`, `step_check_ranking_order`, `step_end_ranking`, `step_force_ranking`, `step_publish_ranking_` |
| `bdd/steps/rewards_step.py` | `step_check_rewards_of_citizen` |
| `bdd/steps/suspension_readmission_steps.py` | `step_check_latest_suspension`, `step_institution_tries_citizen_suspension` |
| `bdd/steps/unsubscribe_steps.py` | `step_check_latest_cancellation_failed`, `step_citizen_tries_to_unsubscribe` |

Gli step di graduatoria dipendevano inoltre da:

- `api/idpay.py`: `force_ranking`, `get_ranking_file`, `put_publish_ranking`,
  `put_ranking_end_date`.
- `util/utility.py`: `check_ranking_status_institution_portal`, `get_selfcare_token`.
- `util/encrypt_utilities.py`: `verify_and_clear_p7m_file`, con il relativo ambiente
  di verifica/estrazione P7M; `pandas` era usato per leggere i CSV delle graduatorie.
- Configurazioni `settings.initiatives.ranking_initiative` e
  `settings.initiatives.family_ranking_initiative`, relativi endpoint e stati.
- I vecchi flussi transazione QR, sospensione/riammissione e IDPay Code/MIL,
  inclusi i loro helper e le rispettive dipendenze. Alcuni scenari QR richiamavano
  indirettamente `put_authorize_payment`: la sua rimozione rimane corretta per le
  suite attive, ma va riconsiderata se si riattivano quegli scenari storici.

Per consultare la versione originale senza modificare il working tree:

```bash
git show 5d44f94ee86284af81fff94b8f2b1bbb425c56da:bdd/steps/discount_transaction_steps.py
git show 5d44f94ee86284af81fff94b8f2b1bbb425c56da:util/encrypt_utilities.py
git show 5d44f94ee86284af81fff94b8f2b1bbb425c56da:settings.yaml
git show 5d44f94ee86284af81fff94b8f2b1bbb425c56da:Pipfile
```

Non ripristinare in blocco secret, configurazioni di ambiente o il vecchio lockfile.
Valutare le sole dipendenze necessarie e mantenere le credenziali in file ignorati.

## Lavoro necessario per riattivare

1. Confermare con le regole di Bonus Valore i criteri ISEE, ordinamento, budget,
   nucleo familiare, pubblicazione e periodi di adesione/fruizione.
2. Adattare le configurazioni e il lifecycle alle iniziative di test correnti,
   ripristinando soltanto API, utility e librerie effettivamente richieste.
3. Decidere quali casi QR/IDPay Code siano ancora pertinenti e quali debbano usare
   i nuovi canali di pagamento. Non considerarli equivalenti al Barcode.
4. Risolvere lo step storico senza corrispondenza nella baseline:
   `the transaction X is not created because it is out of valid period`.
   La verifica statica non certifica quindi che la vecchia suite fosse già eseguibile.
5. Risolvere gli eventuali conflitti di step, controllare i casi `@skip`, effettuare
   dry run e verifiche offline, poi eseguire i test in un ambiente autorizzato.
6. Solo dopo questa verifica reinserire i percorsi in `bdd/`, nei runner e nella
   documentazione attiva. Il semplice spostamento dei file non completa la riattivazione.
