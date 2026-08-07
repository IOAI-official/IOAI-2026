# Il fantasma della macchina

- **Limite di tempo:** 10 minuti
- **Punteggio baseline:** 28.6
- **Punteggio del Comitato Scientifico:** 93.41
- **Ambiente:** una GPU (≈16 GB VRAM), senza internet
- **Dimensione della soluzione:** `solution.ipynb` ≤ 20 MB
- **Spazio di archiviazione:** 5 GB
- **Modelli preaddestrati:** solo **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — un **encoder** di testo (modello di embedding).


## Compito

Strani eventi stanno accadendo all'Archivio Nazionale del Kazakistan. I bibliotecari affermano che alcuni libri un tempo terminassero diversamente, ma nessuno può dimostrarlo: ogni copia è uguale e ogni storia continua ad avere senso. Siete invitati, in qualità di ricercatori di IA, a individuare le modifiche.
![Fantasma](../../ghost.jpg)

Un brano inizia come testo scritto da un essere umano e, a un certo punto, passa senza alcun segnale
a una continuazione generata da un modello linguistico. Letto nel suo insieme, appare come
un unico testo coerente, ma da qualche parte nel mezzo l'autore cambia da una persona
a una macchina. Il vostro compito è **individuare quel passaggio: l'indice del carattere in cui
termina la parte umana e inizia quella della macchina**.

Ogni campione è una singola stringa `text`. Esiste esattamente un confine. Tutto ciò che
lo precede è umano; tutto ciò che si trova a partire da esso è generato da una macchina.

## Dataset

Brani in inglese in testo semplice, ciascuno con un confine.

- **Parte A** (prima del confine): un estratto di testo scritto da un essere umano.
- **Parte B** (dal confine in poi): una continuazione prodotta da un modello linguistico,
  condizionata sulla Parte A.
- Ciascuna parte contiene almeno 180 parole; la lunghezza totale è di ~500–800 parole.
- Il **`boundary_char_index`** è l'offset in caratteri in cui termina la Parte A:
  `text[:boundary_char_index]` è la parte umana e
  `text[boundary_char_index:].lstrip()` è la parte della macchina.

#### Materiale fornito

Ricevete **due cartelle**:

| Cartella | Campioni | `answers.jsonl`? | Utilizzo |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ incluso | addestrare / effettuare il fine-tuning del vostro metodo |
| `dataset/test_public/`  | 380   | ✅ incluso (copia di sviluppo) | eseguire la vostra pipeline e calcolare localmente il vostro punteggio |

Al **momento della valutazione**, la vostra cartella `dataset/test_public/` viene **sostituita da un
set di valutazione nascosto**. Ha lo stesso formato, ma **senza `answers.jsonl`**. Il vostro
notebook viene eseguito nuovamente su di esso e il file `answers.jsonl` che produce viene valutato.

- La classifica pubblica utilizza un set nascosto **test_leaderboard_a** (380 campioni).

- La classifica finale utilizza un set nascosto **test_leaderboard_b** (380 campioni).

Tutti e tre i set di valutazione
hanno la stessa dimensione e sono estratti dalla stessa distribuzione di `train`, pertanto il vostro punteggio
`dataset/test_public/` locale costituisce una stima ragionevole del vostro punteggio in classifica.

#### Formato su disco

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- Gli id in `answers.jsonl` corrispondono agli id in `data.jsonl`.
- `dataset/train/` (con le risposte) è disponibile ogni volta che effettuate l'addestramento o il fine-tuning.

## Output (formato di consegna)

Dovete consegnare **un singolo notebook, che deve essere denominato `solution.ipynb`**. È richiesto esattamente questo nome di file. Qualsiasi altro file viene rifiutato senza essere eseguito.

Il vostro notebook deve **leggere `dataset/test_public/data.jsonl`** e scrivere un singolo file
**`answers.jsonl`** nella directory principale del repository — un oggetto JSON per riga, che associa
ciascun id di campione all'indice del carattere del confine previsto:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` deve essere un **intero in `[0, len(text)]`**.
- Ogni id in `dataset/test_public/data.jsonl` deve comparire esattamente una volta. Un campione mancante
  da `answers.jsonl` (o con un valore non intero / fuori intervallo) ottiene 0
  punti per quel campione.

## Valutazione

Per ogni campione, siano `p` l'indice previsto e `t` il confine reale. Il punteggio per campione decresce esponenzialmente con la distanza in caratteri:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Ciò determina il seguente comportamento del punteggio:
- **=1.0** — carattere esatto del confine;
- **≈0.78** — errore di 25 caratteri; - **≈0.61** — errore di 50 caratteri;
- **≈0.37** — errore di 100 caratteri;
- **≈0.01** — errore di 500 caratteri.

Il **punteggio finale è la media** dei punteggi per campione su tutti i campioni dello split
(riportata su una scala da 0–100). La metrica premia la vicinanza, non soltanto l'esattezza.

## Vincoli

- **Ambiente:** una GPU (≈16 GB VRAM), senza internet al momento della valutazione — il modello
  consentito (indicato sotto) è già fornito. **Budget di tempo effettivo: 10 minuti** per l'intera
  esecuzione — deve includere qualsiasi addestramento / fine-tuning eseguito al momento della valutazione
  **più** l'inferenza sul set di valutazione.
- **Modello preaddestrato consentito** — l'elenco è esaustivo; non è possibile utilizzare altri pesi
  preaddestrati. Il modello è **già fornito nell'ambiente** (caricatelo normalmente, ad es.
  `from_pretrained`; non è disponibile internet al momento della valutazione):
  - **bge-base-en-v1.5** — un **encoder** di testo da 110M parametri (modello di embedding). Produce
    embedding di frasi/brani; non è un modello linguistico generativo. Potete
    utilizzarlo **così com'è (feature congelate) oppure effettuarne il fine-tuning sullo split `train`**
    (il fine-tuning completo rientra nel budget di 16 GB / 10 minuti).
- Gli strumenti classici / statistici non sono soggetti a restrizioni: potete costruire qualsiasi modello
  basato su feature (ad es. classificatori o regressori scikit-learn) sopra le feature di embedding che
  calcolate autonomamente. Le restrizioni sui *pesi di deep learning preaddestrati* si applicano esclusivamente all'elenco sopra.

## Baseline

Il file `solution.ipynb` fornito è un riferimento elementare: stima una singola
«frazione media del confine» da `dataset/train/` e prevede quella stessa frazione della
lunghezza per ogni brano di test. Ottiene un punteggio di **28.6** sullo split nascosto
**test_leaderboard_a** ed è presente esclusivamente come modello eseguibile per il ciclo
lettura di `dataset/test_public/` → scrittura di `answers.jsonl`.

Il **punteggio del Comitato Scientifico di 93.41**, misurato sullo stesso split e con lo stesso
budget di 10 minuti, è ottenuto effettuando il fine-tuning dell'encoder consentito su `train` e individuando
il passaggio come punto di cambiamento tra le frasi. Non costituisce un limite superiore — il massimo
per questa metrica è 100.
