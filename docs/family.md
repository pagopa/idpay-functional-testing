# Famiglie nei Bonus Elettrodomestici e Decoder

Le feature attive sono in `bdd/features/common_bonus_features/family/`, con tag
`@family`, `@bonus_elettrodomestici` e `@bonus_decoder`. La matrice CI dei due Bonus
le include automaticamente: non è necessario aggiungere un nuovo percorso al runner.

## Regole e preparazione

La regola ripresa dai casi già presenti nei due Bonus è **un solo beneficiario per
nucleo familiare**. Il primo richiedente completa l'onboarding; gli altri ricevono
`ONBOARDING_FAMILY_UNIT_ALREADY_JOINED`. Non si usa il vecchio stato `DEMANDED` e
non si prevede un budget condiviso da spendere tra più familiari.

La famiglia viene preparata con `put_mocked_family` e verificata tramite gli user ID
nel mock. Gli scenari selezionano ISEE ordinario 19.999 euro e dichiarazione
`under_25000` per Elettrodomestici; il builder Decoder usa il proprio payload vuoto,
come nel flusso corrente. Il wallet iniziale atteso proviene da
`context.initiative_settings.budget_per_citizen`: 200 euro per Elettrodomestici nella
fascia scelta, 70 euro per Decoder. Il prodotto GTIN e le credenziali POS restano
quelli selezionati dalla configurazione del Bonus.

## Copertura attiva

| Feature | Scenari espansi | Verifica |
|---|---:|---|
| `onboarding.feature` | 3 | Due ordini di adesione nella stessa famiglia; indipendenza tra due nuclei; rifiuto degli altri membri e integrità del budget del beneficiario. |
| `transaction.feature` | 1 | Il beneficiario può autorizzare un Barcode dopo il rifiuto degli altri membri. |
| `cancellation.feature` | 1 | Il POS può cancellare il Barcode autorizzato del beneficiario. |
| `refund.feature` | 1 | Il pagamento del beneficiario può essere acquisito, fatturato e stornato. |
| `unsubscribe.feature` | 1 | Il beneficiario può rinunciare dopo il rifiuto delle altre domande familiari. |

I sette scenari sono selezionati per entrambi i Bonus: **14 esecuzioni** nella
matrice completa. I due precedenti casi familiari presenti nei file onboarding
specifici sono confluiti nel nuovo Scenario Outline, che aggiunge la verifica del
primo beneficiario e del budget e rimuove la duplicazione.

Il rimborso è adattato allo **storno del pagamento Barcode fatturato** già supportato
dai test correnti: non equivale al vecchio rimborso massivo dell'ente al merchant.
Non viene asserito che il voucher possa essere riutilizzato dopo storno o rinuncia,
né che un familiare escluso possa subentrare: queste regole richiedono una verifica
funzionale separata. La copertura corrente del budget riguarda la fascia under 25k;
non è una nuova copertura familiare delle altre fasce ISEE.

## Casi storici conservati

Le sei feature originali (37 scenari) sono conservate nel repository in `archive/family/` (vedere il relativo README).
Rimangono come riferimento i vecchi casi su soglia ISEE 20.000 euro, esaurimento del
budget dell'iniziativa dedicata, budget condiviso, QR/IDPay Code/MIL e sospensione/
riammissione dei familiari. Non vengono automaticamente dichiarati validi per i
Bonus: in particolare la gestione della sospensione e l'eventuale subentro non sono
specificati dai casi correnti e non sono stati inventati in questa riattivazione.

## Esecuzione

Con credenziali e connettività dell'ambiente autorizzato:

```bash
pipenv run behave bdd/features/common_bonus_features/family --tags "bonus_elettrodomestici and family"
pipenv run behave bdd/features/common_bonus_features/family --tags "bonus_decoder and family"
```

I tag CLI selezionano il Bonus per gli hook. Il solo filtro `family` usa invece il
default Elettrodomestici; non implica una doppia esecuzione.

Per verificare esclusivamente risoluzione degli step, senza chiamate remote:

```bash
PARI_SECRET_PATH=conf/pari-feature-secrets-template.json PARI_TARGET_ENV='<ENV>' pipenv run behave bdd/features/common_bonus_features/family --dry-run
```

In PowerShell impostare le corrispondenti variabili `$env:` prima del comando.
L'esito offline non certifica gli scenari sul backend UAT.
