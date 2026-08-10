# Campo IOAI

- **Limite di tempo:** 5 minuti
- **Spazio di archiviazione:** 5 GB
- **Dimensione della soluzione:** `solution.ipynb`, `custom_model.py` ≤ 1 MB complessivamente
- **Modelli preaddestrati:** nessuno — training da zero, nessun accesso a Internet durante la valutazione
- **Punteggio della baseline**: 31.2187
- **Punteggio del Comitato Scientifico:** 63.53


## Compito

Il sindaco di Astana vuole decorare la città con loghi IOAI stilizzati. In quanto statistico, considera ogni cosa — incluso il logo — come una funzione spaziale $F(x, y, \overline{W})$, dove $x, y \in [0, 1]$ rappresentano le coordinate su un piano 2D e $\overline{W}$ è un insieme di parametri nascosti che definiscono attributi stilistici quali i colori e le inclinazioni delle lettere.

Poiché $F$ è troppo complessa per essere espressa come un'equazione matematica esplicita, il vostro compito è addestrare una rete neurale per approssimarla. La rete produrrà un valore del **campo IOAI** per qualsiasi coppia di coordinate $(x, y)$, generando una visualizzazione heatmap completa del logo sul piano. Ecco un esempio di visualizzazione heatmap di $F$ con alcuni specifici parametri nascosti $\overline{W}$.

![f1](../../ioai1.png)

Da cosa è composto il campo IOAI? Quattro lettere e lo sfondo.

- I valori all'interno della prima lettera `I` sono molto grandi (1e+10 e oltre), con un gradiente lineare
- I valori nella lettera `O` presentano un pattern a spirale
- Il valore all'interno della lettera `A` è sempre -1
- I valori all'interno dell'ultima lettera `I` devono essere valori casuali appartenenti all'intervallo $[-2026,2026]$, anche se vengono valutati due volte nello stesso punto
- All'esterno delle lettere il valore è sempre zero

La funzione ha parametri nascosti $\overline{W}$, che influenzano la scala e l'inclinazione delle lettere, insieme all'intervallo dei valori all'interno della prima lettera `I`. Tuttavia, le lettere non si intersecheranno. Ecco alcuni esempi illustrativi dell'aspetto del campo IOAI con diversi $\overline{W}$:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Cosa vi viene fornito:**

Questo problema NON contiene dataset. Vi viene invece fornita la funzione generatrice, configurata dal file di configurazione JSON in `data/train_config/field_config.json`. 

La configurazione di test è nascosta, ma è di natura simile. Il vostro compito è effettuare il fit sul generatore fornito usando tutti i dati che desiderate. Le vostre distribuzioni di "train" e "test" sono generate dallo stesso generatore: semplicemente non sapete su quali punti $(x_i, y_i)$ sarete valutati.

La vostra submission deve essere composta da:
- la classe del modello di training salvata come `custom_model.py`. Questo modello deve ereditare dalla classe `torch.nn.Module` e utilizzare esclusivamente gli import di `torch`. Deve contenere la classe `CustomModel` utilizzata nel notebook `solution.ipynb`. 
- il notebook `solution.ipynb`, che produrrà i pesi `model.pt`


## Valutazione

Per ogni regione, il punteggio minimo è 0 e il punteggio massimo è 1. Il punteggio finale è calcolato come media sulle cinque regioni (quattro, una per ciascuna lettera, e lo sfondo) e moltiplicato per 100. È prevista una **penalità per il numero di parametri:**

**Se il vostro modello ha più di 20260 parametri, il punteggio viene dimezzato.**

Il numero di parametri viene misurato mediante `sum(p.numel() for p in model.parameters())`. Ci aspettiamo che il vostro modello operi anche in modalità stocastica, con il `nn.Dropout` di PyTorch come parte del modello.

### Per le regioni standard

Per ogni regione $R$ (prima lettera `I`, `O`, `A`, `Background`), valutiamo il modello su $N_R = 512$ punti di test $(x_i, y_i)$ con valori reali $v_i$ e predizioni $\hat{v}_i$. Utilizziamo l'errore assoluto medio (MAE) normalizzato come metrica principale. Il MAE è definito come:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

E la normalizzazione viene eseguita come 

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

dove $s_R > 0$ è una costante di scala.


### Per la regione dell'ultima lettera `I`

In questa regione, **il dropout è abilitato durante la valutazione**. Per ogni punto di test $j$:

1. Eseguiamo il modello $K = 10$ volte per ottenere $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Se un qualsiasi output è esterno all'intervallo $[-2026, 2026]$, allora $\mathrm{pointScore}(j) = 0$.
3. Altrimenti, calcoliamo la deviazione standard $\sigma_j$ dei $K$ output e la convertiamo in un punteggio:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

dove $s_E > 0$ è una costante di scala fissa.

Il punteggio della regione è la media su tutti i punti della regione:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

dove $N_E = K * N_R$. 

In termini semplici, maggiore è la diversità, maggiore sarà il vostro punteggio per questa regione. **Non potete usare la casualità in forma pura, incluse le funzioni `rand*` e `_uniform` di PyTorch; la casualità deve provenire dall'inferenza con il dropout abilitato.**

## Come effettuare la submission

1. Aprite `solution.ipynb` ed eseguite tutte le celle.
2. Migliorate il modello `CustomModel` in `custom_model.py`
3. Assicuratevi che l'ultima cella salvi il vostro modello nel file `model.pt`.
4. Nella scheda Git di JupyterLab, eseguite lo stage, inserite un commento ed effettuate il commit di `solution.ipynb` e `custom_model.py`, quindi eseguite il push.
5. Tornate alla pagina della competizione e fate clic su **Submit**. Il commento della submission deve essere lo stesso commento del passaggio precedente.
