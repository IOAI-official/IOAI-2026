# Inseguimento di robot

- **Limite di tempo:** 5 minuti
- **Ambiente:** una GPU (≈16 GB VRAM), senza internet
- **Dimensione della soluzione:** `solution.ipynb` ≤ 1 MB
- **Spazio di archiviazione:** 5 GB 

## Compito

Ci sono sei robot. Ogni robot opera in una piccola stanza rappresentata da una griglia. Ogni stanza ha un'area giocabile `6×6` circondata da pareti, pertanto l'array `image` completo ha dimensione `8×8` (area giocabile + pareti).

Ogni robot riceve un'istruzione in inglese che descrive un compito. L'istantanea può essere acquisita in qualsiasi momento mentre il robot lo sta eseguendo. Il vostro obiettivo è prevedere l'azione successiva del robot.

I robot non seguono sempre il percorso più breve. Il Robot 0 può comportarsi diversamente dal Robot 1, ma ciascun robot segue un proprio schema coerente. Utilizzate gli esempi di training, che includono le azioni successive corrette, per apprendere questi schemi.

![Robot](../robot.jpg)

Esistono tre tipi di missioni:

- **andare verso** un oggetto, per esempio `"approach the red ball"`;
- **raccogliere** un oggetto, per esempio `"grab the blue key"`;
- **mettere un oggetto accanto a un altro**, per esempio
  `"place the red box beside the green ball"`.

La stessa istruzione può essere formulata in diversi modi. Il test set può contenere nuove combinazioni di espressioni, colori e tipi di oggetti già noti. Tuttavia, ogni parola, schema di espressione, colore, tipo di oggetto e tipo di missione utilizzato nel test set compare anche nel training set.

Ogni campione contiene i seguenti campi:

| Campo | Significato |
|---|---|
| `robot_id` | quale dei 6 robot è (`0`–`5`) |
| `image` | la stanza, un array di interi `8×8×2` in cui il canale 0 contiene l'object_idx categorico (per esempio, 1=cella vuota, 2=parete, 10=robot) e il canale 1 contiene il colour_idx categorico (0–5). |
| `direction` | la direzione verso cui è attualmente rivolto il robot |
| `mission` | l'istruzione visibile in linguaggio naturale |
| `carrying` | `null` o `[object_idx, colour_idx]` per l'oggetto trasportato |

Le righe sono istantanee indipendenti disposte in ordine casuale. Non formano episodi e, al momento della valutazione, non è disponibile alcuna osservazione o azione precedente.

Il file `visualize_dataset.ipynb` fornito consente di esaminare le osservazioni disponibili al modello in diverse situazioni.

## Codifica della griglia

`image[row][column] = [object_idx, colour_idx]`. Il primo indice è la riga, dall'alto verso il basso, e il secondo è la colonna, da sinistra verso destra. L'array include il bordo esterno di pareti, pertanto l'interno navigabile è `6×6`.

ID degli oggetti:

| id | oggetto |
|---:|---|
| 1 | cella vuota |
| 2 | parete |
| 5 | chiave |
| 6 | palla |
| 7 | scatola |
| 10 | robot |
| 11 | token |

I token possono comparire nella stanza, ma non vengono mai menzionati nelle missioni.

Gli ID dei colori sono `0` rosso, `1` verde, `2` blu, `3` viola, `4` giallo e `5` grigio. Il canale del colore non ha significato per le celle vuote e le pareti.

L'immagine contiene soltanto i due canali descritti sopra. La direzione del robot è fornita una sola volta, nel campo `direction` di livello superiore; non è duplicata all'interno di `image`.

## Azioni

Per i codici `0`–`3`, le azioni di movimento utilizzano la seguente corrispondenza assoluta:

| azione | significato |
|---:|---|
| 0 | spostarsi verso l'alto |
| 1 | spostarsi verso il basso |
| 2 | spostarsi verso sinistra |
| 3 | spostarsi verso destra |
| 4 | raccogliere |
| 5 | depositare |


Il campo `direction` indica l'orientamento attuale utilizzando: 0 = Alto (row - 1), 1 = Basso (row + 1), 2 = Sinistra (col - 1), 3 = Destra (col + 1).

Un'azione di movimento fa prima ruotare il robot verso tale direzione assoluta e poi tenta di spostarlo di una cella. Una parete o un oggetto può bloccare il movimento, ma la direzione cambia comunque. `pick up` e `drop` agiscono esclusivamente sulla cella bersaglio adiacente definita dalla direzione (per esempio, se direction=0, l'azione viene eseguita su (row - 1, col)).

## Dataset

Riceverete due cartelle:

| Cartella | Righe | `labels.json`? | Utilizzatela per |
|---|---:|---|---|
| `dataset/train/` | 60,000 | incluso | addestrare il vostro modello |
| `dataset/test_public/` | 3,600 | incluso nella copia di sviluppo | eseguire e valutare autonomamente la vostra pipeline |

Ogni cartella contiene `observations.json`, una lista JSON dei campioni descritti
sopra. `labels.json` è una lista JSON allineata di azioni (`0`–`5`).

Il training set contiene esattamente 10,000 righe per robot e 20,000 righe per ciascuna
famiglia di compiti. Il test pubblico contiene 600 righe per robot. Racchiudete `image` con
`numpy.asarray(...)` se vi occorre un array.

Al momento della valutazione, `dataset/test_public/` viene sostituito in modo trasparente da un set nascosto di
3,600 osservazioni nello stesso formato, ma senza `labels.json`. La classifica
pubblica utilizza `test_leaderboard_a`; la classifica finale utilizza
`test_leaderboard_b`. Un notebook che legge incondizionatamente le etichette del test non funzionerà.
Leggete le etichette soltanto da `dataset/train/`.

## Output

Scrivete `predictions.json` nella directory di lavoro del notebook. Deve essere una lista
JSON contenente un'azione intera (`0`–`5`) per ogni riga di
`dataset/test_public/observations.json`, nello stesso ordine. Per un ipotetico test set contenente sei campioni, un output valido sarebbe:

```json
[0, 3, 2, 2, 5, 4]
```

Un file JSON mancante o non valido, un numero errato di predizioni, un valore non intero
o un'azione al di fuori di `{0,1,2,3,4,5}` vengono rifiutati senza assegnare un punteggio.

## Valutazione

Il punteggio è l'**accuratezza media per robot** su una scala `0`–`100`. L'accuratezza viene prima
calcolata indipendentemente per ciascun robot, quindi mediata sui sei robot. Ogni
robot ha pertanto lo stesso peso.

## Come inviare

1. Aprite `solution.ipynb` ed eseguite tutte le celle.
2. Verificate che generi `predictions.json` con 3,600 predizioni per il test set
   pubblico.
3. Se lo desiderate, migliorate il modello; il baseline fornito si limita a mostrare il
   formato di input e output richiesto.
4. Nella scheda Git di JupyterLab, aggiungete all'area di staging ed eseguite il commit di `solution.ipynb`, quindi effettuate il push.
5. Tornate alla pagina della competizione e fate clic su **Invia**.

Inviate esattamente un file denominato `solution.ipynb`.
