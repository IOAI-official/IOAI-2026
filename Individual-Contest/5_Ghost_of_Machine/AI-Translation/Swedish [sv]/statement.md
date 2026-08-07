# Maskinens spöke

- **Tidsgräns:** 10 minuter
- **Baseline-poäng:** 28.6
- **Vetenskapliga kommitténs poäng:** 93.41
- **Miljö:** en GPU (≈16 GB VRAM), ingen internetuppkoppling
- **Lösningens storlek:** `solution.ipynb` ≤ 20 MB
- **Lagring:** 5 GB
- **Förtränade modeller:** endast **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — en text**encoder** (embedding-modell).


## Uppgift

Märkliga saker händer på Kazakstans nationalarkiv. Bibliotekarierna säger att vissa böcker förr slutade annorlunda, men ingen kan bevisa det — varje exemplar är likadant, och varje berättelse är fortfarande begriplig. Du bjuds in som AI-forskare för att lokalisera ändringarna.
![Spöke](../../ghost.jpg)

Ett textstycke börjar som människoskriven text och övergår vid någon punkt tyst
till en fortsättning genererad av en språkmodell. Läst som helhet ser den ut som
ett sammanhängande stycke — men någonstans i mitten byts författaren från en person
till en maskin. Din uppgift är att **hitta detta byte: teckenindexet där
den mänskliga delen slutar och maskindelen börjar**.

Varje sample är en enda sträng `text`. Det finns exakt en gräns. Allt
före den är mänskligt; allt från den och framåt är maskingenererat.

## Dataset

Engelska textstycken i ren text, med en gräns var.

- **Del A** (före gränsen): ett utdrag av människoskriven text.
- **Del B** (från gränsen och framåt): en fortsättning producerad av en språkmodell,
  betingad på del A.
- Varje sida är minst 180 ord; total längd är ~500–800 ord.
- **`boundary_char_index`** är teckenoffseten där del A slutar:
  `text[:boundary_char_index]` är den mänskliga delen och
  `text[boundary_char_index:].lstrip()` är maskindelen.

#### Vad du får

Du får **två mappar**:

| Mapp | Samples | `answers.jsonl`? | Använd den till att |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ ingår | träna / finjustera din metod |
| `dataset/test_public/`  | 380   | ✅ ingår (dev-kopia) | köra din pipeline och poängsätta dig själv lokalt |

Vid **rättningstillfället** ersätts din mapp `dataset/test_public/` av ett **dolt
utvärderingsset**. Det har samma format men **utan `answers.jsonl`**. Din
notebook körs om på det, och den `answers.jsonl` den producerar poängsätts.

- Den publika leaderboarden använder ett dolt **test_leaderboard_a**-set (380 samples).

- Den slutliga rankningen använder ett dolt **test_leaderboard_b**-set (380 samples).

Alla tre utvärderingsset
är lika stora och dragna från samma fördelning som `train`, så din lokala
`dataset/test_public/`-poäng är en rimlig uppskattning av din leaderboard-poäng.

#### Format på disk

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- Id:n i `answers.jsonl` matchar id:n i `data.jsonl`.
- `dataset/train/` (med svar) är tillgänglig närhelst du tränar eller finjusterar.

## Utdata (inlämningsformat)

Du lämnar in **en enda notebook, som måste heta `solution.ipynb`**. Exakt detta filnamn krävs. Allt annat avvisas utan att köras.

Din notebook måste **läsa `dataset/test_public/data.jsonl`** och skriva en enda fil
**`answers.jsonl`** i repositoryts rot — ett JSON-objekt per rad, som mappar
varje sample-id till ditt predikterade teckenindex för gränsen:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` måste vara ett **heltal i `[0, len(text)]`**.
- Varje id i `dataset/test_public/data.jsonl` bör förekomma exakt en gång. Ett sample som saknas
  i `answers.jsonl` (eller har ett icke-heltalsvärde / värde utanför intervallet) ger 0 poäng
  för det samplet.

## Poängsättning

För varje sample, låt `p` vara ditt predikterade index och `t` vara den sanna gränsen. Poängen per sample avtar exponentiellt med teckenavståndet:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Detta leder till följande beteende hos poängen:
- **=1.0** — exakt gränstecken;
- **≈0.78** — 25 tecken fel; - **≈0.61** — 50 tecken fel;
- **≈0.37** — 100 tecken fel;
- **≈0.01** — 500 tecken fel.

Den **slutliga poängen är medelvärdet** av poängen per sample över alla samples i uppdelningen
(rapporterad på en skala 0–100). Måttet belönar att komma *nära*, inte bara att träffa exakt.

## Begränsningar

- **Miljö:** en GPU (≈16 GB VRAM), ingen internetuppkoppling vid rättningstillfället — den tillåtna
  modellen (nedan) är redan tillhandahållen. **Budget i realtid (wall-clock): 10 minuter** för
  hela körningen — detta måste täcka all träning / finjustering du gör vid rättningstillfället
  **plus** inferens på utvärderingssetet.
- **Tillåten förtränad modell** — denna lista är uttömmande; inga andra förtränade vikter
  får användas. Den är **förhandstillhandahållen i miljön** (ladda den på vanligt sätt, t.ex.
  `from_pretrained`; det finns ingen internetuppkoppling vid rättningstillfället):
  - **bge-base-en-v1.5** — en text**encoder** (embedding-modell) med 110M parametrar. Den
    producerar mening-/passage-embeddingar; den är inte en generativ språkmodell. Du
    får använda den **som den är (frysta features) eller finjustera den på uppdelningen `train`**
    (fullständig finjustering ryms inom budgeten på 16 GB / 10 minuter).
- Klassiska / statistiska verktyg är obegränsade: du får bygga vilken feature-baserad
  modell som helst (t.ex. klassificerare eller regressorer från scikit-learn) ovanpå embedding-features som du
  beräknar själv. *Förtränade deep learning-vikter* är endast begränsade till listan ovan.

## Baseline

Den tillhandahållna `solution.ipynb` är en trivial referens: den skattar en enda
"genomsnittlig gränsandel" från `dataset/train/` och predikterar samma andel av
längden för varje testpassage. Den får **28.6** på den dolda
uppdelningen **test_leaderboard_a** och finns endast som en körbar mall för loopen
läs-`dataset/test_public/` → skriv-`answers.jsonl`.

Den **vetenskapliga kommitténs poäng på 93.41**, mätt på samma uppdelning och med samma
10-minutersbudget, kommer från att finjustera den tillåtna encodern på `train` och lokalisera
bytet som en brytpunkt (changepoint) över meningar. Det är inte en övre gräns — maximum
på detta mått är 100.
