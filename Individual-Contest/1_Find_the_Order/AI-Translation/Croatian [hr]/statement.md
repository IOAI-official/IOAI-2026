# Pronađite redoslijed

- **Vremensko ograničenje:** 10 minuta
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez pristupa internetu
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Pohrana:** 5 GB 

## Zadatak

Zadani su vam govorni dijalozi na engleskom jeziku između dvoje sudionika, *Govornika A* i *Govornika B*. Svaki je dijalog podijeljen na replike, pri čemu svaka replika sadržava govor samo jednog govornika. Svaka je replika pohranjena kao zasebna `.wav` audiodatoteka, pa je cijeli dijalog predstavljen skupom `.wav` datoteka, po jednom za svaku repliku. 

Nažalost, replike su nasumično izmiješane, pa razgovor više nema smisla. U nazivu datoteke `chunk_{k}.wav`, `k` odnosi se na k-ti isječak u izmiješanom skupu, a ne na k-tu repliku u izvornom dijalogu.

**‼️ Vaš je zadatak rekonstruirati izvorni kronološki redoslijed razgovora.**

![Pronađite redoslijed](../../find_the_order.jpg)

---

## Dataset

Svaki dijalog sadržava `n` audiodatoteka nazvanih `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Isječci su pojedinačne replike. Nazivi datoteka odgovaraju samo izmiješanom redoslijedu. Ne pokazuju gdje isječak pripada u izvornom razgovoru. Svaki dijalog ima 7–20 isječaka, mono, 44.1 kHz (možete
promijeniti frekvenciju uzorkovanja).

**`prefix.json` sadržava indekse naziva datoteka prvih dvaju isječaka u svakom dijalogu.** Time se određuje stvarni početak dijaloga i uklanja dvosmislenost između praćenja razgovora unaprijed ili unatrag.

Na primjer: `11: [7, 12]` znači da su prva i druga replika dijaloga 11 redom `chunk_7.wav` i `chunk_12.wav`.

### Što dobivate

Dobivate **dvije mape jednakog formata**:

| Mapa | Dijalozi | `answers.json`? | Upotrijebite je za |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ uključeno | treniranje / fino ugađanje modela |
| `dataset/test_public/`  | 100   | ✅ uključeno | pokretanje obrade i lokalno izračunavanje vlastitog rezultata |

Tijekom ocjenjivanja vaša se mapa `dataset/test_public/` transparentno zamjenjuje
mapom `hidden evaluation set` (`test_leaderboard_a` za javnu ljestvicu poretka i `test_leaderboard_b` za konačnu ljestvicu poretka) — one imaju istu veličinu i format kao `dataset/test_public/`, ali bez `answers.json`.

Vaša se bilježnica ponovno izvršava na tim podatcima, a datoteka `answers.json` koju proizvede upotrebljava se za bodovanje. Izdvojeni testni dijalozi dolaze iz iste distribucije kao `train`, pa je vaš lokalni rezultat `test_public` pouzdan pokazatelj očekivanog rezultata.

### Struktura direktorija

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

## Izlaz

Za svaki dijalog odredite izvorni kronološki redoslijed njegovih audioisječaka. Vaše predviđanje treba biti permutacija `P` skupa `{0, 1, …, n−1}`, pri čemu je `P[i]` predviđeni kronološki položaj isječka `chunk_i.wav` (0 = prvi).

Vaša izlazna datoteka `answers.json` treba preslikavati svaki ID dijaloga u njegovu predviđenu permutaciju:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Primjer

Dijalog ima 3 izmiješana isječka `chunk_0, chunk_1, chunk_2`:

| izmiješani isječak | izgovoreni sadržaj | stvarni položaj (rang) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (posljednji) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (prvi) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Stvarni je redoslijed **chunk_1 → chunk_2 → chunk_0**, pa je `P = [2, 0, 1]`, a `prefix.json` sadržava `[1, 2]`.

⚠️ **P mora biti valjana permutacija:** duljine n, indeksirana od 0, pri čemu se svaka vrijednost pojavljuje točno jednom. Duplikati, vrijednosti koje nedostaju ili vrijednosti izvan raspona (npr. indeksiranje od 1) donose rezultat 0 za taj dijalog, kao i dijalog koji nedostaje u datoteci. Neispravna datoteka ili datoteka koja nije u formatu JSON bit će odbijena.

## Bodovanje

Mjera bodovanja ovog zadatka jest **točnost poretka parova**. Provjerava svaki par isječaka i postavlja pitanje: _koji od njih treba doći prvi?_ Par je točan ako vaše predviđanje daje isti odgovor kao stvarni poredak. Za dijalog s `n` isječaka postoji $$M = n(n-1)/2$$ parova; neka je `I` broj inverzija — parova poredanih drukčije nego u stvarnom poretku:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Konačni je rezultat prosjek rezultata po dijalogu za sve
dijaloge u podskupu.**

## Dopušteni modeli

Za rješavanje ovog zadatka smijete upotrebljavati samo sljedeće unaprijed istrenirane modele, i tijekom treniranja i tijekom evaluacije. Svi su ti modeli već preuzeti i dostupni u okruženju. Primjere njihove uporabe možete vidjeti u bilježnici s osnovnim rješenjem `solution.ipynb`. Imajte na umu da ne smijete upotrebljavati nijedan drugi model te da vaš program nema pristup internetu.

- **Reprezentacije govora:** **wav2vec 2.0**. **Whisper encoder** također se smije upotrebljavati za izdvajanje značajki.
[Kartica modela wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automatsko prepoznavanje govora (ASR):** **OpenAI Whisper** (bilo koje veličine).
[Kartica modela Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Jezični model:** **Qwen2.5-0.5B**, koji se može upotrebljavati u zero-shot načinu ili fino ugoditi na priloženom podskupu `train`.
[Kartica modela Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Imajte na umu da ograničenje od 10 minuta mora obuhvatiti svako treniranje ili fino ugađanje koje provodite tijekom ocjenjivanja, kao i inferenciju na evaluacijskom skupu.

## Kako predati rješenje

- Otvorite `solution.ipynb` i pokrenite sve ćelije. Potvrdite da se u radnom direktoriju zapisuje `answers.json` s permutacijom za svaki dijalog u `dataset/test_public/` (100 dijaloga). Tijekom ocjenjivanja bilježnica se ponovno pokreće na skrivenom testnom skupu, a `answers.json` koji ondje proizvede upotrebljava se za bodovanje.
- Poboljšajte rješenje ako želite — ili nemojte; samo osnovno rješenje dovoljno je za provjeru cijelog procesa.
- Otvorite karticu Git na liječnoj bočnoj traci JupyterLaba.
- Označite `solution.ipynb` za **Stage** (ikona + pokraj njega).
- Unesite poruku commita i kliknite **Commit**.
- Kliknite ikonu oblaka sa strelicom prema gore kako biste izvršili push.
- Vratite se na ovu stranicu natjecanja i kliknite **Submit**.

Predajte točno jednu datoteku nazvanu `solution.ipynb`.
