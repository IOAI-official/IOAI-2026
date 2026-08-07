# Dilemma del doppio agente

- **Limite di tempo:** 12 minuti.
- **Spazio di archiviazione:** 5 GB
- **Ambiente:** una GPU (≈16 GB VRAM), senza accesso a Internet
- **Dimensione della soluzione:** `solution.ipynb` ≤ 1 MB
- **Punteggio della baseline:** 0 
- **Punteggio del Comitato Scientifico:** 96.99 

Nel centro nazionale di IA di Astana, due modelli informatici — il Modello R (un ResNet-18) e il Modello V (un ViT-Tiny) —stanno analizzando fotografie. Al momento, entrambi i modelli svolgono un lavoro perfetto, ottenendo un'accuratezza del 100% e concordando su ogni singola immagine. Per verificare quanto siano realmente diversi i loro "cervelli" intelligenti, il responsabile scientifico vi propone una sfida: apportare a ciascuna fotografia piccole modifiche ai pixel, quasi invisibili, in modo che il Modello R e il Modello V siano completamente in disaccordo.

![immagine](../../dilemma.jpg)

## 1. Compito

Due classificatori di immagini preaddestrati esaminano la stessa immagine. Sulle immagini fornite in questo compito, entrambi i classificatori raggiungono un'accuratezza del 100%.

- **Modello R**: `torchvision.models.resnet18` (una CNN, ResNet18).
- **Modello V**: `timm` di `vit_tiny_patch16_224` (un Transformer, ViT-Tiny).

Il vostro compito è creare una piccola modifica ("perturbazione") per ciascuna immagine, in modo che i due modelli siano in disaccordo. Per ogni immagine, dovete creare **due perturbazioni diverse**:

- **Tipo A**: dopo averla aggiunta, il Modello R classifica ancora correttamente l'immagine, ma il Modello V la classifica erroneamente.
- **Tipo B**: dopo averla aggiunta, il Modello V classifica ancora correttamente l'immagine, ma il Modello R la classifica erroneamente.

Ogni perturbazione deve essere abbastanza *piccola* da risultare difficile da notare. Le perturbazioni più piccole ottengono punteggi più alti (si veda la Sezione 5). La perturbazione viene applicata direttamente all'immagine originale a livello dei pixel.

## 2. Dati pubblici

Con il compito viene fornito un insieme di immagini, organizzato in due split — `train` (100 immagini) e
`test_public` (100 immagini) — ciascuno contenente immagini con risoluzioni diverse. Tutte le immagini appartengono alle 1000 classi di ImageNet-1K e sia il Modello R sia il Modello V raggiungono un'accuratezza del 100% su entrambi gli split.

Sono forniti i seguenti file:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Durante la valutazione, la vostra cartella `dataset/test_public/` viene sostituita in modo trasparente da due insiemi nascosti di immagini (`test_leaderboard_a` e `test_leaderboard_b`) ai fini del punteggio ufficiale. Ciascuno di essi contiene **100 immagini** in formato PNG e un file delle etichette. 

**Nota: per questo compito, le etichette nei dataset di test sono accessibili.**

## 3. Formato di output

Per ogni immagine, dovete produrre due file:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), corrisponde al nome dell'immagine nei dataset.
- Ogni file contiene un singolo tensore salvato con `torch.save`. La sua forma deve essere`3 x H x W`, dove `H` e `W` corrispondono alla risoluzione **originale** dell'immagine (non `224 x 224`).
- Il codice deve produrre un solo file ZIP, `submission.zip`. Inserite tutti i file `.pt` al livello principale dell'archivio ZIP, senza cartelle contenitrici né sottodirectory. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Il notebook vi avviserà se c'è eventuali problemi con il formato di output.

## 4. Vincoli

- **Modelli:** dovete utilizzare `torchvision.models.resnet18(pretrained=True)` e `timm.create_model('vit_tiny_patch16_224', pretrained=True)`. Non sono consentiti altri modelli preaddestrati.
- **Pipeline di trasformazione (applicata durante la valutazione):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` per i dettagli. 
- **Risoluzione della perturbazione:** deve corrispondere alla risoluzione **originale** dell'immagine grezza (non 224×224). Il tensore viene
  aggiunto all'immagine grezza *prima* della pipeline di trasformazione.
- **Formato di output:** esclusivamente file `.pt` — niente PNG/JPG . I tensori vengono aggiunti all'immagine grezza e i valori dei pixel vengono limitati a `[0, 1]` prima del preprocessing.
- **Denominazione dei file:** elenco piatto, rigoroso formato `{index}_a.pt` / `{index}_b.pt`. Nessuna sottodirectory all'interno del file zip.
- **Librerie:** `torch`, `torchvision`, `timm`. 

## 5. Punteggio

Il punteggio finale viene calcolato come segue. Sia `M` il numero di immagini nello split, $Score_A$ il numero di perturbazioni di Tipo A riuscite e $Score_B$ il numero di perturbazioni di Tipo B riuscite:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF è una funzione progettata per penalizzare le perturbazioni con una norma elevata e per essere molto sensibile in prossimità del massimo delle prestazioni. Essa essa è limitata all'intervallo da 0.5 a 1. L'implementazione completa è disponibile nella Sezione  8 di `solution.ipynb`. 

![immagine](../../curves.jpeg)
Figura: la curva della funzione di penalità.

## 6. Verifica della submission

Il notebook contiene controlli che vi avvisano in caso di problemi di formattazione, nella Sezione 7 del notebook `solution.ipynb`.

## 7. Test locale

`solution.ipynb` contiene un esempio completo e funzionante. Carica i dati pubblici, entrambi i modelli e il valutatore ufficiale, e genera un file ZIP per la submission. Consultatelo prima di iniziare.

## 8. Come effettuare la submission

- Salvate le vostre modifiche in `solution.ipynb`.
- Aprite la scheda Git nella barra laterale sinistra di JupyterLab.
- Eseguite lo **Stage** di `solution.ipynb` (l'icona + accanto al file).
- Inserite un messaggio di commit e fate clic su **Commit**.
- Fate clic sull'icona della nuvola con la freccia verso l'alto per eseguire il push.
- Tornate a questa pagina del Contest e fate clic su **Submit**.

Inviate esattamente un file, denominato `solution.ipynb`.
