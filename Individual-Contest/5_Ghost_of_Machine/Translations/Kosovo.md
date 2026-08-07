# Fantazma e Makinerisë

- **Kufiri kohor:** 10 minuta
- **Rezultati bazë:** 28.6
- **Mjedisi:** një GPU (≈16 GB VRAM), pa internet
- **Madhësia e zgjidhjes:** `solution.ipynb` ≤ 20 MB
- **Hapësira e ruajtjes:** 5 GB
- **Modelet e paratrajnuara:** vetëm **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — një **enkoder** teksti (embedding model).


## Detyra

Gjëra të çuditshme po ndodhin në Arkivin Kombëtar të Kazakistanit. Bibliotekarët thonë se disa libra dikur përfundonin ndryshe, por askush nuk mund ta vërtetojë — çdo kopje është e njëjtë dhe çdo histori ende ka kuptim. Jeni ftuar si studiues i AI-së për të gjetur ndryshimet.
![Fantazma](../ghost.jpg)

Një fragment fillon si tekst i shkruar nga një njeri dhe, në një pikë të caktuar, kalon në heshtje
në një vazhdim të gjeneruar nga një model gjuhësor (language model). I lexuar si një i tërë, ai duket si
një pjesë koherente — por diku në mes autori ndryshon nga një person
në një makinë. Detyra juaj është të **gjeni atë kalim: indeksin e karakterit ku
përfundon pjesa njerëzore dhe fillon pjesa e makinës**.

Çdo mostër është një string i vetëm `text`. Ekziston saktësisht një kufi. Gjithçka
para tij është njerëzore; gjithçka prej tij e tutje është gjeneruar nga makina.

## Dataset

Fragmente teksti në anglisht të thjeshtë, me nga një kufi secili.

- **Pjesa A** (para kufirit): një fragment nga një tekst i shkruar nga njeriu.
- **Pjesa B** (nga kufiri e tutje): një vazhdim i prodhuar nga një model gjuhësor,
  i kushtëzuar nga Pjesa A.
- Secila anë ka të paktën 180 fjalë; gjatësia totale është ~500–800 fjalë.
- **`boundary_char_index`** është indeksi i **karakterit të parë të Pjesës B**:
  `text[boundary_char_index:]` është saktësisht pjesa e makinës dhe
  `text[:boundary_char_index]` është pjesa njerëzore së bashku me hapësirën që i ndan dy pjesët.

#### Çfarë merrni

Ju merrni **dy folderë**:

| Folderi | Mostrat | `answers.jsonl`? | Përdoreni për të |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ i përfshirë | trajnuar / fine-tune metodën tuaj |
| `dataset/test_public/`  | 380   | ✅ i përfshirë (kopje dev) | ekzekutuar pipeline-in tuaj dhe llogaritur lokalisht rezultatin tuaj |

Në **kohën e vlerësimit**, folderi juaj `dataset/test_public/` **zëvendësohet nga një
bashkësi e fshehur vlerësimi**. Ajo ka të njëjtin format, por **pa `answers.jsonl`**. Notebook-u juaj
ekzekutohet përsëri mbi të dhe vlerësohet `answers.jsonl` që ai prodhon.

- Tabela publike e renditjes përdor një bashkësi të fshehur **test_leaderboard_a** (380 mostra).

- Renditja përfundimtare përdor një bashkësi të fshehur **test_leaderboard_b** (380 mostra).

Të tria bashkësitë e
vlerësimit kanë të njëjtën madhësi dhe janë marrë nga e njëjta shpërndarje si `train`, kështu që rezultati juaj lokal
`dataset/test_public/` është një vlerësim i arsyeshëm i rezultatit tuaj në tabelën e renditjes.

#### Formati në disk

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- Id-të në `answers.jsonl` përputhen me id-të në `data.jsonl`.
- `dataset/train/` (me përgjigjet) është i disponueshëm sa herë që kryeni trajnim ose fine-tune.

## Output (formati i dorëzimit)

Ju dorëzoni **një notebook të vetëm, i cili duhet të emërtohet `solution.ipynb`**. Ky emër i saktë skedari është i detyrueshëm. Çdo gjë tjetër refuzohet pa u ekzekutuar.

Notebook-u juaj duhet të **lexojë `dataset/test_public/data.jsonl`** dhe të shkruajë një skedar të vetëm
**`answers.jsonl`** në rrënjën e repository-t — një objekt JSON për çdo rresht, që lidh
çdo id mostre me indeksin e parashikuar të karakterit të kufirit:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` duhet të jetë një **numër i plotë në `[0, len(text)]`**.
- Çdo id në `dataset/test_public/data.jsonl` duhet të shfaqet saktësisht një herë. Një mostër që mungon
  nga `answers.jsonl` (ose me një vlerë jo të plotë / jashtë intervalit) merr rezultatin 0
  për atë mostër.

## Vlerësimi

Për çdo mostër, le të jetë `p` indeksi juaj i parashikuar dhe `t` kufiri i vërtetë. Rezultati për mostër bie në mënyrë eksponenciale me largësinë në karaktere:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Kjo sjell sjelljen e mëposhtme të rezultatit:
- **=1.0** — karakteri i saktë i kufirit;
- **≈0.78** — devijim prej 25 karakteresh; - **≈0.61** — devijim prej 50 karakteresh;
- **≈0.37** — devijim prej 100 karakteresh;
- **≈0.01** — devijim prej 500 karakteresh.

**Rezultati përfundimtar është mesatarja** e rezultateve për mostër mbi të gjitha mostrat e ndarjes
(raportohet në një shkallë 0–100). Metrika shpërblen afrimin, jo vetëm saktësinë.

## Kufizimet

- **Mjedisi:** një GPU (≈16 GB VRAM), pa internet në kohën e vlerësimit — modeli i lejuar
  (më poshtë) është tashmë i siguruar. **Buxheti i kohës reale: 10 minuta** për të gjithë
  ekzekutimin — ky duhet të mbulojë çdo trajnim / fine-tune që kryeni në kohën e vlerësimit
  **plus** inferencën në bashkësinë e vlerësimit.
- **Modeli i paratrajnuar i lejuar** — kjo listë është shteruese; nuk mund të përdoren pesha të tjera
  të paratrajnuara. Ai është **i siguruar paraprakisht në mjedis** (ngarkojeni normalisht, p.sh.
  `from_pretrained`; nuk ka internet në kohën e vlerësimit):
  - **bge-base-en-v1.5** — një **enkoder** teksti me 110M parametra (embedding model). Ai
    prodhon embeddings fjalish/fragmentesh; nuk është një model gjuhësor gjenerues. Ju
    mund ta përdorni **siç është (veçori të ngrira) ose ta bëni fine-tune në ndarjen `train`**
    (fine-tune i plotë përshtatet brenda buxhetit prej 16 GB / 10 minutash).
- Mjetet klasike / statistikore janë të pakufizuara: mund të ndërtoni çfarëdo modeli të bazuar në veçori
  (p.sh., klasifikues ose regresorë scikit-learn) mbi veçoritë embedding që
  llogaritni vetë. *Peshat e paratrajnuara të deep learning* kufizohen vetëm në listën e mësipërme.
