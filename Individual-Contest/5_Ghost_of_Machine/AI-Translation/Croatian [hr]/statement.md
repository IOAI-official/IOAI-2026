# Duh stroja

- **Vremensko ograničenje:** 10 minuta
- **Osnovni rezultat:** 28.6
- **Rezultat Znanstvenog odbora:** 93.41
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 20 MB
- **Prostor za pohranu:** 5 GB
- **Pretrenirani modeli:** samo **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — tekstni **enkoder** (embedding model).


## Zadatak

Čudne se stvari događaju u Nacionalnom arhivu Kazahstana. Knjižničari kažu da su neke knjige nekoć završavale drukčije, ali nitko to ne može dokazati — svaki je primjerak isti i svaka priča i dalje ima smisla. Pozvani ste kao istraživač umjetne inteligencije da pronađete promjene.
![Duh](../../ghost.jpg)

Odlomak započinje tekstom koji je napisao čovjek i u nekom trenutku neprimjetno prelazi
na nastavak koji je generirao jezični model. Pročitan kao cjelina, djeluje kao
jedan koherentan tekst — ali negdje u sredini autor se mijenja iz čovjeka
u stroj. Vaš je zadatak **pronaći taj prijelaz: indeks znaka na kojem završava
ljudski dio i počinje strojni dio**.

Svaki je uzorak jedan znakovni niz `text`. Postoji točno jedna granica. Sve
prije nje napisao je čovjek; sve od nje nadalje generirao je stroj.

## Skup podataka

Tekstni odlomci na engleskom jeziku, svaki s jednom granicom.

- **Dio A** (prije granice): ulomak teksta koji je napisao čovjek.
- **Dio B** (od granice nadalje): nastavak koji je proizveo jezični model,
  uvjetovan dijelom A.
- Svaka strana ima najmanje 180 riječi; ukupna je duljina ~500–800 riječi.
- **`boundary_char_index`** je pomak u znakovima na kojem završava dio A:
  `text[:boundary_char_index]` je ljudski dio, a
  `text[boundary_char_index:].lstrip()` je strojni dio.

#### Što dobivate

Dobivate **dvije mape**:

| Mapa | Uzorci | `answers.jsonl`? | Upotrijebite za |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ uključeno | treniranje / dodatno treniranje svoje metode |
| `dataset/test_public/`  | 380   | ✅ uključeno (razvojna kopija) | pokretanje svojeg postupka i lokalno samostalno ocjenjivanje |

U **vrijeme ocjenjivanja** vaša mapa `dataset/test_public/` **zamjenjuje se skrivenim
evaluacijskim skupom**. Ima isti format, ali **bez `answers.jsonl`**. Vaš se
notebook ponovno pokreće na njemu, a `answers.jsonl` koji proizvede ocjenjuje se.

- Javna ljestvica koristi skriveni skup **test_leaderboard_a** (380 uzoraka).

- Konačni poredak koristi skriveni skup **test_leaderboard_b** (380 uzoraka).

Sva tri evaluacijska
skupa jednake su veličine i uzorkovana iz iste distribucije kao `train`, pa je vaš lokalni
rezultat za `dataset/test_public/` razumna procjena vašeg rezultata na ljestvici.

#### Format na disku

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- ID-jevi u `answers.jsonl` odgovaraju ID-jevima u `data.jsonl`.
- `dataset/train/` (s odgovorima) dostupan je kad god trenirate ili dodatno trenirate.

## Izlaz (format predaje)

Predajete **jedan notebook, koji se mora zvati `solution.ipynb`**. Obvezan je upravo taj naziv datoteke. Sve ostalo odbacuje se bez pokretanja.

Vaš notebook mora **pročitati `dataset/test_public/data.jsonl`** i zapisati jednu datoteku
**`answers.jsonl`** u korijenu repozitorija — jedan JSON objekt po retku, koji
svaki ID uzorka preslikava u vaš predviđeni indeks znaka granice:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` mora biti **cijeli broj u `[0, len(text)]`**.
- Svaki ID u `dataset/test_public/data.jsonl` trebao bi se pojaviti točno jednom. Uzorak koji nedostaje
  u `answers.jsonl` (ili ima necjelobrojnu vrijednost / vrijednost izvan raspona) dobiva 0
  bodova za taj uzorak.

## Bodovanje

Za svaki uzorak neka je `p` vaš predviđeni indeks, a `t` stvarna granica. Rezultat po uzorku eksponencijalno opada s udaljenošću u znakovima:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

To dovodi do sljedećeg ponašanja rezultata:
- **=1.0** — točan znak granice;
- **≈0.78** — odstupanje od 25 znakova; - **≈0.61** — odstupanje od 50 znakova;
- **≈0.37** — odstupanje od 100 znakova;
- **≈0.01** — odstupanje od 500 znakova.

**Konačni rezultat jest aritmetička sredina** rezultata po uzorku za sve uzorke u podskupu
(iskazana na ljestvici 0–100). Metrika nagrađuje približavanje granici, a ne samo njezino točno određivanje.

## Ograničenja

- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta u vrijeme ocjenjivanja — dopušteni
  model (naveden u nastavku) već je dostupan. **Ukupno vremensko ograničenje: 10 minuta** za
  cijelo izvođenje — to mora obuhvatiti svako treniranje / dodatno treniranje koje obavljate u vrijeme ocjenjivanja
  **kao i** inferenciju na evaluacijskom skupu.
- **Dopušteni pretrenirani model** — ovaj je popis potpun; ne smiju se
  upotrebljavati nikakve druge pretrenirane težine. Model je **unaprijed dostupan u okruženju** (učitajte ga na uobičajen način, npr.
  `from_pretrained`; u vrijeme ocjenjivanja nema interneta):
  - **bge-base-en-v1.5** — tekstni **enkoder** sa 110M parametara (embedding model). On
    proizvodi embeddinge rečenica/odlomaka; nije generativni jezični model. Možete
    ga upotrebljavati **u neizmijenjenom obliku (zamrznute značajke) ili ga dodatno trenirati na podskupu `train`**
    (potpuno dodatno treniranje uklapa se u ograničenja od 16 GB / 10 minuta).
- Klasični / statistički alati nisu ograničeni: možete izgraditi bilo koji model temeljen na
  značajkama (npr. klasifikatore ili regresore iz scikit-learn) nad embedding značajkama koje
  sami izračunate. *Pretrenirane težine dubokog učenja* ograničene su samo na prethodno navedeni popis.

## Osnovno rješenje

Priloženi `solution.ipynb` trivijalno je referentno rješenje: procjenjuje jedan
„prosječni udio granice” iz `dataset/train/` i za svaki testni odlomak predviđa isti udio
duljine. Ostvaruje rezultat **28.6** na skrivenom podskupu
**test_leaderboard_a** i postoji samo kao izvršivi predložak za petlju
čitanje-`dataset/test_public/` → zapisivanje-`answers.jsonl`.

**Rezultat Znanstvenog odbora od 93.41**, izmjeren na istom podskupu i uz isto
vremensko ograničenje od 10 minuta, dobiven je dodatnim treniranjem dopuštenog enkodera na `train` i pronalaženjem
prijelaza kao točke promjene među rečenicama. To nije gornja granica — maksimum
ove metrike iznosi 100.
