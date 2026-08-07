# Duh mašine

- **Vremensko ograničenje:** 10 minuta
- **Baseline rezultat:** 28.6
- **Rezultat Naučnog komiteta:** 93.41
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 20 MB
- **Prostor za skladištenje:** 5 GB
- **Pretrenirani modeli:** samo **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — tekstualni **enkoder** (embedding model).


## Zadatak

Čudne stvari se dešavaju u Nacionalnom arhivu Kazahstana. Bibliotekari kažu da su se neke knjige ranije završavale drugačije, ali niko to ne može dokazati — svaki primjerak je isti, a svaka priča i dalje ima smisla. Pozvani ste kao istraživač vještačke inteligencije da pronađete izmjene.
![Duh](../../ghost.jpg)

Odlomak počinje kao tekst koji je napisao čovjek i, u nekom trenutku, neprimjetno prelazi
u nastavak koji je generisao jezički model. Kada se čita kao cjelina, djeluje kao
jedan koherentan tekst — ali negdje u sredini autor se mijenja iz čovjeka
u mašinu. Vaš zadatak je da **pronađete taj prelaz: indeks znaka na kojem se
završava ljudski dio i počinje mašinski dio**.

Svaki uzorak je jedan string `text`. Postoji tačno jedna granica. Sve
prije nje napisao je čovjek; sve od nje nadalje generisala je mašina.

## Skup podataka

Tekstualni odlomci na engleskom jeziku, svaki sa jednom granicom.

- **Dio A** (prije granice): odlomak teksta koji je napisao čovjek.
- **Dio B** (od granice nadalje): nastavak koji je proizveo jezički model,
  uslovljen Dijelom A.
- Svaka strana ima najmanje 180 riječi; ukupna dužina je ~500–800 riječi.
- **`boundary_char_index`** je pomak u znakovima na kojem se završava Dio A:
  `text[:boundary_char_index]` je ljudski dio, a
  `text[boundary_char_index:].lstrip()` je mašinski dio.

#### Šta dobijate

Dobijate **dva foldera**:

| Folder | Uzorci | `answers.jsonl`? | Koristite ga za |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ uključen | obuku / fino podešavanje svoje metode |
| `dataset/test_public/`  | 380   | ✅ uključen (dev kopija) | pokretanje svog pipelinea i lokalno izračunavanje rezultata |

Tokom **ocjenjivanja**, vaš folder `dataset/test_public/` **zamjenjuje se skrivenim
evaluacionim skupom**. On ima isti format, ali **bez `answers.jsonl`**. Vaš
notebook se ponovo pokreće nad njim, a `answers.jsonl` koji proizvede se ocjenjuje.

- Javni leaderboard koristi skriveni skup **test_leaderboard_a** (380 uzoraka).

- Konačni poredak koristi skriveni skup **test_leaderboard_b** (380 uzoraka).

Sva tri evaluaciona
skupa iste su veličine i uzorkovana su iz iste distribucije kao `train`, pa je vaš lokalni
rezultat za `dataset/test_public/` razumna procjena vašeg rezultata na leaderboardu.

#### Format na disku

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- ID-jevi u `answers.jsonl` odgovaraju ID-jevima u `data.jsonl`.
- `dataset/train/` (sa odgovorima) dostupan je kad god obučavate ili fino podešavate model.

## Izlaz (format predaje)

Predajete **jedan notebook, koji mora imati naziv `solution.ipynb`**. Ovaj tačan naziv datoteke je obavezan. Sve ostalo se odbacuje bez pokretanja.

Vaš notebook mora **čitati `dataset/test_public/data.jsonl`** i zapisati jednu datoteku
**`answers.jsonl`** u korijenu repozitorijuma — po jedan JSON objekat u svakom redu, koji
mapira ID svakog uzorka na vaš predviđeni indeks graničnog znaka:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` mora biti **cijeli broj u `[0, len(text)]`**.
- Svaki ID iz `dataset/test_public/data.jsonl` treba da se pojavi tačno jednom. Uzorak koji nedostaje
  u `answers.jsonl` (ili ima vrijednost koja nije cijeli broj / koja je van opsega) dobija rezultat 0
  za taj uzorak.

## Bodovanje

Za svaki uzorak, neka je `p` vaš predviđeni indeks, a `t` stvarna granica. Rezultat po uzorku opada eksponencijalno sa udaljenošću u znakovima:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

To dovodi do sljedećeg ponašanja rezultata:
- **=1.0** — tačan granični znak;
- **≈0.78** — odstupanje od 25 znakova; - **≈0.61** — odstupanje od 50 znakova;
- **≈0.37** — odstupanje od 100 znakova;
- **≈0.01** — odstupanje od 500 znakova.

**Konačni rezultat je srednja vrijednost** rezultata po uzorku za sve uzorke u podskupu
(prikazana na skali 0–100). Metrika nagrađuje približavanje granici, a ne samo njeno tačno određivanje.

## Ograničenja

- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta tokom ocjenjivanja — dozvoljeni
  model (naveden ispod) već je obezbijeđen. **Vremenski budžet: 10 minuta** za
  cjelokupno pokretanje — to mora obuhvatiti svu obuku / fino podešavanje koje obavljate tokom ocjenjivanja
  **kao i** inferenciju na evaluacionom skupu.
- **Dozvoljeni pretrenirani model** — ova lista je potpuna; ne smiju se koristiti druge pretrenirane težine.
  Model je **unaprijed obezbijeđen u okruženju** (učitajte ga na uobičajen način, npr.
  `from_pretrained`; tokom ocjenjivanja nema interneta):
  - **bge-base-en-v1.5** — tekstualni **enkoder** (embedding model) sa 110M parametara. On
    proizvodi embeddinge rečenica/odlomaka; nije generativni jezički model. Možete
    ga koristiti **takvog kakav jeste (zamrznute karakteristike) ili ga fino podesiti na podskupu `train`**
    (potpuno fino podešavanje uklapa se u budžet od 16 GB / 10 minuta).
- Klasični / statistički alati nijesu ograničeni: možete napraviti bilo koji model zasnovan na
  karakteristikama (npr. scikit-learn klasifikatore ili regresore) nad embedding karakteristikama koje
  sami izračunate. Ograničenje na prethodno navedenu listu odnosi se samo na *pretrenirane težine modela dubokog učenja*.

## Baseline

Obezbijeđeni `solution.ipynb` je trivijalna referenca: procjenjuje jednu
„prosječnu proporciju granice” iz `dataset/train/` i predviđa tu istu proporciju
dužine za svaki testni odlomak. Ostvaruje rezultat **28.6** na skrivenom
podskupu **test_leaderboard_a** i postoji samo kao izvršivi šablon za
petlju čitanje-`dataset/test_public/` → zapisivanje-`answers.jsonl`.

**Rezultat Naučnog komiteta od 93.41**, izmjeren na istom podskupu i uz isti
budžet od 10 minuta, dobijen je finim podešavanjem dozvoljenog enkodera na `train` i lociranjem
prelaza kao tačke promjene kroz rečenice. To nije gornja granica — maksimum
ove metrike je 100.
