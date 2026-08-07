# Spook van de machine

- **Tijdslimiet:** 10 minuten
- **Baseline-score:** 28.6
- **Omgeving:** één GPU (≈16 GB VRAM), geen internet
- **Oplossingsgrootte:** `solution.ipynb` ≤ 20 MB
- **Opslag:** 5 GB
- **Pretrained modellen:** alleen **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — een tekst-**encoder** (embeddingmodel).


## Opdracht

Jij bent een bibliothecaris. Voor de afgelopen 20 jaar, was het leven rustig. Dat veranderde, wanneer ClosedAI ging aanvallen. Iedereen dacht dat de energiesystemen en backsoftware de eersten zouden zijn die ongemerkt gehackt zouden worden. Dit bleek echter niet waar te zijn. 

Een hackgroep uit het Noord-Brabantse Best is het nationaal archief van Kazachstan binnengedrongen! In plaats van dat ze alleen maar boeken kapot maken om ze sneller te scannen, veranderen ze de verhalen met AI! Natuurlijk zijn de Beste hackers heel erg slim, maar jij bent (als goede IOAI deelnemer) natuurlijk nog slimmer. 
![Spook](../ghost.jpg)

Een passage begint als door een mens geschreven tekst en schakelt op een bepaald moment over
op een vervolg dat door een taalmodel is gegenereerd. Als geheel gelezen lijkt het
één samenhangend stuk — maar ergens in het midden verandert de auteur van een mens
in een machine. Jouw taak is om **die overgang te vinden: de tekenindex waar het
menselijke deel eindigt en het machinedeel begint**.

Elk sample is één enkele string `text`. Er is precies één grens. Alles
ervoor is door een mens geschreven; alles vanaf die grens is door een machine gegenereerd.

## Dataset

Engelstalige passages in platte tekst, elk met één grens.

- **Deel A** (vóór de grens): een fragment van door een mens geschreven tekst.
- **Deel B** (vanaf de grens): een door een taalmodel geproduceerd vervolg,
  geconditioneerd op Deel A.
- Elke zijde telt ten minste 180 woorden; de totale lengte is ~500–800 woorden.
- De **`boundary_char_index`** is de tekenoffset waar Deel A eindigt:
  `text[:boundary_char_index]` is het menselijke deel en
  `text[boundary_char_index:].lstrip()` is het machinedeel.

#### Wat je krijgt

Je ontvangt **twee mappen**:

| Map | Samples | `answers.jsonl`? | Gebruik deze om |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ inbegrepen | je methode te trainen / finetunen |
| `dataset/test_public/`  | 380   | ✅ inbegrepen (ontwikkelkopie) | je pipeline uit te voeren en lokaal je eigen score te berekenen |

Op het **beoordelingsmoment** wordt je map `dataset/test_public/`  **vervangen door een verborgen
evaluatieset**. Deze heeft hetzelfde formaat, maar **zonder `answers.jsonl`**. Je
notebook wordt er opnieuw op uitgevoerd en de geproduceerde `answers.jsonl` wordt beoordeeld.

- Het openbare leaderboard gebruikt een verborgen **test_leaderboard_a**-set (380 samples).

- De eindrangschikking gebruikt een verborgen **test_leaderboard_b**-set (380 samples).

Alle drie de evaluatie-
sets hebben dezelfde grootte en zijn afkomstig uit dezelfde verdeling als `train`, waardoor je lokale
`dataset/test_public/`-score een redelijke schatting is van je leaderboard-score.

#### Formaat op schijf

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- ID's in `answers.jsonl` komen overeen met ID's in `data.jsonl`.
- `dataset/train/` (met antwoorden) is beschikbaar wanneer je traint of finetunet.

## Uitvoer (inzendingsformaat)

Je dient **één notebook in, die de naam `solution.ipynb` moet hebben**. Deze exacte bestandsnaam is vereist. Al het andere wordt afgewezen zonder te worden uitgevoerd.

Je notebook moet **`dataset/test_public/data.jsonl` lezen** en één bestand
**`answers.jsonl`** in de hoofdmap van de repository schrijven — één JSON-object per regel, dat
elk sample-ID koppelt aan je voorspelde tekenindex van de grens:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` moet een **integer in `[0, len(text)]`** zijn.
- Elk ID in `dataset/test_public/data.jsonl` moet precies één keer voorkomen. Een sample dat ontbreekt
  in `answers.jsonl` (of een niet-integerwaarde / waarde buiten het bereik heeft), krijgt een score van 0
  voor dat sample.

## Scoring

Laat voor elk sample `p` je voorspelde index zijn en `t` de werkelijke grens. De score per sample neemt exponentieel af met de afstand in tekens:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Dit leidt tot het volgende gedrag van de score:
- **=1.0** — exact het grensteken;
- **≈0.78** — 25 tekens ernaast; - **≈0.61** — 50 tekens ernaast;
- **≈0.37** — 100 tekens ernaast;
- **≈0.01** — 500 tekens ernaast.

De **eindscore is het gemiddelde** van de scores per sample over alle samples in de split
(gerapporteerd op een schaal van 0–100). De metriek beloont *dichtbij komen*, niet alleen exact zijn.

## Beperkingen

- **Omgeving:** één GPU (≈16 GB VRAM), geen internet op het beoordelingsmoment — het toegestane
  model (hieronder) is al beschikbaar gesteld. **Wandklokbudget: 10 minuten** voor de
  volledige uitvoering — dit moet alle training / fine-tuning die je op het beoordelingsmoment uitvoert
  **plus** inferentie op de evaluatieset omvatten.
- **Toegestaan pretrained model** — deze lijst is uitputtend; er mogen geen andere pretrained gewichten
  worden gebruikt. Het is **vooraf beschikbaar gesteld in de omgeving** (laad het op de gebruikelijke manier, bijvoorbeeld
  `from_pretrained`; er is geen internet op het beoordelingsmoment):
  - **bge-base-en-v1.5** — een tekst-**encoder** met 110M parameters (embeddingmodel). Deze
    produceert embeddings van zinnen/passages; het is geen generatief taalmodel. Je
    mag het **as-is gebruiken (frozen features) of finetunen op de `train`-split**
    (volledige fine-tuning past binnen het budget van 16 GB / 10 minuten).
- Klassieke / statistische hulpmiddelen zijn onbeperkt: je mag elk op features gebaseerd
  model bouwen (bijvoorbeeld classifiers of regressors van scikit-learn) boven op embeddingfeatures die je
  zelf berekent. *Pretrained deep-learninggewichten* zijn uitsluitend beperkt tot de bovenstaande lijst.
