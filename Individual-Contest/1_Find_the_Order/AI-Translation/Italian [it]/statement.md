# Trova l'ordine

- **Limite di tempo:** 10 minuti
- **Ambiente:** una GPU (≈16 GB VRAM), senza accesso a internet
- **Dimensione della soluzione:** `solution.ipynb` ≤ 1 MB
- **Spazio di archiviazione:** 5 GB 

## Problema

Ti vengono forniti dialoghi in inglese parlato tra due partecipanti, *Parlante A* e *Parlante B*. Ogni dialogo è segmentato in turni di parola, ciascuno dei quali contiene il parlato di un solo parlante. Ogni turno è memorizzato come file audio `.wav` separato, quindi un dialogo completo è rappresentato da un insieme di file `.wav`, uno per ogni turno. 

Sfortunatamente, i turni sono stati mescolati casualmente, quindi la conversazione non ha più senso. Nel nome file `chunk_{k}.wav`, `k` si riferisce al k-esimo frammento nell'insieme mescolato, non al k-esimo turno nel dialogo originale.

**‼️ Il tuo compito è ricostruire l'ordine cronologico originale della conversazione.**

![Trova l'ordine](../../find_the_order.jpg)

---

## Dataset

Ogni dialogo contiene file audio `n` denominati `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. I frammenti sono singoli turni. I nomi file corrispondono soltanto all'ordine mescolato. Non indicano dove vada collocato un frammento nella conversazione originale. Ogni dialogo contiene 7–20 frammenti, mono, 44.1 kHz (puoi
effettuare il ricampionamento).

**`prefix.json` contiene gli indici dei nomi file dei primi due frammenti di ciascun dialogo.** Questo identifica il vero inizio del dialogo ed elimina l'ambiguità tra la lettura della conversazione in avanti o all'indietro.

Ad esempio: `11: [7, 12]` significa che il primo e il secondo turno del dialogo 11 sono rispettivamente `chunk_7.wav` e `chunk_12.wav`.

### Cosa viene fornito

Ricevi **due cartelle in formato identico**:

| Cartella | Dialoghi | `answers.json`? | Utilizzala per |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ incluso | addestrare / effettuare il fine-tuning del tuo modello |
| `dataset/test_public/`  | 100   | ✅ incluso | eseguire la tua pipeline e calcolare localmente il tuo punteggio |

Durante la valutazione, la tua cartella `dataset/test_public/` viene sostituita in modo trasparente da
un `hidden evaluation set` (`test_leaderboard_a` per la classifica pubblica e `test_leaderboard_b` per la classifica finale): questi hanno la stessa dimensione e lo stesso formato di `dataset/test_public/`, ma senza `answers.json`.

Il tuo notebook viene eseguito nuovamente su tali dati e il file `answers.json` che produce viene utilizzato per il calcolo del punteggio. I dialoghi del test tenuti da parte provengono dalla stessa distribuzione di `train`, quindi il tuo punteggio `test_public` locale costituisce un'anteprima fedele.

### Struttura delle directory

```bash
dataset/train/
    prefix.json  # {dialogue_id: [first_idx, second_idx]} filename index 
    answers.json  # {dialogue_id: P}  ground-truth order (rank convention)
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav

dataset/test_public/
    prefix.json
    answers.json     # present only in the development copy
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav
```

---

## Output

Per ogni dialogo, determina l'ordine cronologico originale dei suoi frammenti audio. La tua predizione deve essere una permutazione `P` di `{0, 1, …, n−1}`, dove `P[i]` è la posizione cronologica predetta di `chunk_i.wav` (0 = primo).

Il tuo file di output `answers.json` deve associare ogni ID di dialogo alla relativa permutazione predetta:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Esempio

Un dialogo contiene 3 frammenti mescolati `chunk_0, chunk_1, chunk_2`:

| frammento mescolato | contenuto parlato | posizione reale (rango) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (ultimo) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (primo) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

L'ordine reale è **chunk_1 → chunk_2 → chunk_0**, quindi `P = [2, 0, 1]`, e `prefix.json` contiene `[1, 2]`.

⚠️ **P deve essere una vera permutazione:** lunghezza n, indicizzata a partire da 0, con ciascun valore presente esattamente una volta. Valori duplicati, valori mancanti o elementi fuori intervallo (ad esempio, indicizzati a partire da 1) comportano un punteggio pari a 0 per quel dialogo, così come un dialogo assente dal file. Un file malformato o non JSON viene rifiutato.

## Calcolo del punteggio

Il criterio di valutazione per questo compito è l'**accuratezza dell'ordinamento a coppie**. Esamina ogni coppia di frammenti e chiede: _quale dei due dovrebbe venire prima?_ Una coppia è corretta se la tua predizione fornisce la stessa risposta della verità di riferimento. Per un dialogo con `n` frammenti ci sono $$M = n(n-1)/2$$ coppie; sia `I` il numero di inversioni, ossia le coppie ordinate diversamente rispetto alla verità di riferimento:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Il punteggio finale è la media dei punteggi per dialogo su tutti i
dialoghi dello split.**

## Modelli consentiti

Puoi utilizzare esclusivamente i seguenti modelli preaddestrati per risolvere questo compito, sia durante l'addestramento sia durante la valutazione. Tutti questi modelli sono già stati scaricati e sono disponibili nell'ambiente. Puoi trovare esempi del loro utilizzo nel notebook baseline `solution.ipynb`. Tieni presente che non puoi utilizzare alcun altro modello e che il tuo programma non ha accesso a internet.

- **Rappresentazioni del parlato:** **wav2vec 2.0**. Anche l'**encoder Whisper** può essere utilizzato come estrattore di feature.
[Scheda del modello wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Riconoscimento automatico del parlato (ASR):** **OpenAI Whisper** (qualsiasi dimensione).
[Scheda del modello Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Modello linguistico:** **Qwen2.5-0.5B**, che può essere utilizzato in modalità zero-shot oppure sottoposto a fine-tuning sullo split `train` fornito.
[Scheda del modello Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Tieni presente che il limite di 10 minuti deve comprendere qualsiasi addestramento o fine-tuning che esegui in fase di valutazione, oltre all'inferenza sul set di valutazione.

## Come inviare la soluzione

- Apri `solution.ipynb` ed esegui tutte le celle. Verifica che scriva `answers.json` nella directory di lavoro, con una permutazione per ogni dialogo in `dataset/test_public/` (100 dialoghi). In fase di valutazione, il notebook viene eseguito nuovamente sul test set nascosto e il file `answers.json` che produce viene valutato.
- Migliora la soluzione, se vuoi, oppure no; la baseline da sola convalida la pipeline.
- Apri la scheda Git nella barra laterale sinistra di JupyterLab.
- Esegui lo **stage** di `solution.ipynb` (l'icona + accanto a esso).
- Inserisci un messaggio di commit e fai clic su **Commit**.
- Fai clic sull'icona della nuvola con la freccia verso l'alto per eseguire il push.
- Torna a questa pagina della competizione e fai clic su **Submit**.

Invia esattamente un file, denominato `solution.ipynb`.
