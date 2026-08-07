# Duh mašine

- **Vremensko ograničenje:** 10 minuta
- **Osnovni rezultat:** 28.6
- **Rezultat Naučnog komiteta:** 93.41
- **Okruženje:** jedan GPU (≈16 GB VRAM-a), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 20 MB
- **Prostor za pohranu:** 5 GB
- **Pretrenirani modeli:** samo **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — tekstualni **enkoder** (model za embedding).


## Zadatak

Neobične stvari se događaju u Nacionalnom arhivu Kazahstana. Bibliotekari kažu da su neke knjige nekada imale drugačije završetke, ali niko to ne može dokazati — svaki primjerak je isti i svaka priča i dalje ima smisla. Pozvani ste kao istraživač umjetne inteligencije da pronađete izmjene.
![Duh](../../ghost.jpg)

Odlomak počinje kao tekst koji je napisao čovjek i, u nekom trenutku, neprimjetno prelazi
u nastavak koji je generisao jezički model. Kada se čita kao cjelina, izgleda kao
jedan koherentan tekst — ali negdje u sredini autor se mijenja iz čovjeka
u mašinu. Vaš zadatak je **pronaći taj prijelaz: indeks znaka na kojem se
završava ljudski dio, a počinje mašinski dio**.

Svaki uzorak je jedan string `text`. Postoji tačno jedna granica. Sve
prije nje napisao je čovjek; sve od nje nadalje generisala je mašina.

## Dataset

Engleski odlomci u običnom tekstu, sa po jednom granicom.

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
| `dataset/train/` | 1,221 | ✅ uključen | treniranje / fino podešavanje vaše metode |
| `dataset/test_public/`  | 380   | ✅ uključen (razvojna kopija) | pokretanje vašeg pipelinea i lokalno samostalno ocjenjivanje |

U **vrijeme ocjenjivanja** vaš folder `dataset/test_public/` **zamjenjuje se skrivenim
evaluacijskim skupom**. On ima isti format, ali je **bez `answers.jsonl`**. Vaš
notebook ponovo se pokreće na njemu, a `answers.jsonl` koji proizvede se ocjenjuje.

- Javna rang-lista koristi skriveni skup **test_leaderboard_a** (380 uzoraka).

- Konačni poredak koristi skriveni skup **test_leaderboard_b** (380 uzoraka).

Sva tri evaluacijska
skupa iste su veličine i izvučena su iz iste distribucije kao `train`, pa je vaš lokalni
rezultat za `dataset/test_public/` razumna procjena vašeg rezultata na rang-listi.

#### Format na disku

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- ID-jevi u `answers.jsonl` odgovaraju ID-jevima u `data.jsonl`.
- `dataset/train/` (s odgovorima) dostupan je kad god trenirate ili fino podešavate.

## Izlaz (format predaje)

Predajete **jedan notebook, koji mora imati naziv `solution.ipynb`**. Ovaj tačan naziv datoteke je obavezan. Sve ostalo se odbija bez pokretanja.

Vaš notebook mora **učitati `dataset/test_public/data.jsonl`** i zapisati jednu datoteku
**`answers.jsonl`** u korijenu repozitorija — jedan JSON objekt po redu, koji
svaki ID uzorka preslikava u vaš predviđeni indeks znaka granice:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` mora biti **cijeli broj u `[0, len(text)]`**.
- Svaki ID u `dataset/test_public/data.jsonl` treba se pojaviti tačno jednom. Uzorak koji nedostaje
  u `answers.jsonl` (ili ima vrijednost koja nije cijeli broj / izvan je raspona) dobija rezultat 0
  za taj uzorak.

## Bodovanje

Za svaki uzorak, neka je `p` vaš predviđeni indeks, a `t` stvarna granica. Rezultat po uzorku eksponencijalno opada s udaljenošću u znakovima:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

To dovodi do sljedećeg ponašanja rezultata:
- **=1.0** — tačan znak granice;
- **≈0.78** — odstupanje od 25 znakova; - **≈0.61** — odstupanje od 50 znakova;
- **≈0.37** — odstupanje od 100 znakova;
- **≈0.01** — odstupanje od 500 znakova.

**Konačni rezultat je srednja vrijednost** rezultata po uzorku za sve uzorke u podskupu
(prikazana na skali 0–100). Metrika nagrađuje približavanje, a ne samo tačnost.

## Ograničenja

- **Okruženje:** jedan GPU (≈16 GB VRAM-a), bez interneta u vrijeme ocjenjivanja — dozvoljeni
  model (ispod) već je obezbijeđen. **Vremenski budžet prema zidnom satu: 10 minuta** za
  cijelo pokretanje — to mora obuhvatiti svako treniranje / fino podešavanje koje obavljate u vrijeme ocjenjivanja
  **plus** inferenciju na evaluacijskom skupu.
- **Dozvoljeni pretrenirani model** — ova lista je potpuna; ne smiju se koristiti druge pretrenirane težine.
  On je **unaprijed obezbijeđen u okruženju** (učitajte ga na uobičajen način, npr.
  `from_pretrained`; nema interneta u vrijeme ocjenjivanja):
  - **bge-base-en-v1.5** — tekstualni **enkoder** sa 110M parametara (model za embedding). On
    proizvodi embeddinge rečenica/odlomaka; nije generativni jezički model. Možete
    ga koristiti **takvog kakav jeste (zamrznute karakteristike) ili ga fino podesiti na podskupu `train`**
    (potpuno fino podešavanje uklapa se u budžet od 16 GB / 10 minuta).
- Klasični / statistički alati nisu ograničeni: možete izgraditi bilo koji model zasnovan na karakteristikama
  (npr. scikit-learn klasifikatore ili regresore) povrh embedding karakteristika koje
  sami izračunate. *Pretrenirane težine dubokog učenja* ograničene su samo na gornju listu.

## Osnovno rješenje

Obezbijeđeni `solution.ipynb` trivijalna je referenca: procjenjuje jedan
„prosječni udio granice” iz `dataset/train/` i predviđa taj isti udio
dužine za svaki testni odlomak. Ostvaruje rezultat **28.6** na skrivenom
podskupu **test_leaderboard_a** i postoji samo kao izvršivi predložak za petlju
učitaj-`dataset/test_public/` → zapiši-`answers.jsonl`.

**Rezultat Naučnog komiteta od 93.41**, izmjeren na istom podskupu i uz isti
vremenski budžet od 10 minuta, potiče od finog podešavanja dozvoljenog enkodera na `train` i određivanja
prijelaza kao tačke promjene kroz rečenice. To nije gornja granica — maksimum
za ovu metriku je 100.
