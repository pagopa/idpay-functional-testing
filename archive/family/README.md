# Feature family originali

Riferimento storico conservato il 2 novembre 2026 prima dell'adattamento ai Bonus
Elettrodomestici e Decoder. Le sei feature in `features/` contengono **37 scenari**
espansi e sono copie esatte del commit
`5d44f94ee86284af81fff94b8f2b1bbb425c56da`; `manifest.json` registra percorsi e hash.

La copertura attiva adattata è in `bdd/features/common_bonus_features/family/`;
vedere [regole, copertura e comandi](../../docs/family.md).

Le feature originali richiedevano `family_initiative`/`family_allocated_initiative`,
ISEE inferiore a 20.000 euro, stato `DEMANDED`, più beneficiari con budget condiviso
da 300 euro e vecchi canali QR/IDPay Code/MIL. Queste assunzioni non sono state
reintrodotte nei Bonus. Il contenuto storico non viene eseguito da Behave né incluso
nella documentazione generata per le suite attive.

Gli step e le configurazioni originali restano consultabili con `git show` usando
il commit sopra, ad esempio:

```bash
git show 5d44f94ee86284af81fff94b8f2b1bbb425c56da:bdd/steps/family_steps.py
git show 5d44f94ee86284af81fff94b8f2b1bbb425c56da:bdd/steps/suspension_readmission_steps.py
git show 5d44f94ee86284af81fff94b8f2b1bbb425c56da:settings.yaml
```

Non ripristinare in blocco queste dipendenze o vecchi secret per riattivare i test.
