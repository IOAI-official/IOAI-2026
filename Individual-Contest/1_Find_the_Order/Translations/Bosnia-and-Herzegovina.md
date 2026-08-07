# Pronađite redoslijed

- **Vremensko ograničenje:** 10 minuta
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Prostor za pohranu:** 5 GB 

## Problem

Dati su vam govorni dijalozi na engleskom jeziku između dva učesnika, *Govornika A* i *Govornika B*. Svaki dijalog podijeljen je na replike govornika, pri čemu svaka replika sadrži govor samo jednog govornika. Svaka replika pohranjena je kao zasebna `.wav` audiodatoteka, tako da je cijeli dijalog predstavljen skupom `.wav` datoteka, po jednom za svaku repliku. 

Nažalost, replike su nasumično izmiješane, tako da razgovor više nema smisla. U nazivu datoteke `chunk_{k}.wav`, `k` označava k-ti segment u izmiješanom skupu, a ne k-tu repliku u izvornom dijalogu.

**‼️ Vaš zadatak je rekonstruirati izvorni hronološki redoslijed razgovora.**

![Pronađite redoslijed](../find_the_order.jpg)

---

## Dataset 

Svaki dijalog sadrži `n` audiodatoteka nazvanih `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Segmenti su pojedinačne replike. Nazivi datoteka odgovaraju samo izmiješanom redoslijedu. Oni ne ukazuju na to gdje segment pripada u izvornom razgovoru. Svaki dijalog ima 7–20 segmenata, mono, 44.1 kHz (možete
promijeniti frekvenciju uzorkovanja).

**`prefix.json` sadrži indekse naziva datoteka prva dva segmenta u svakom dijalogu.** Time se određuje stvarni početak dijaloga i uklanja dvosmislenost između čitanja razgovora unaprijed ili unazad.

Naprimjer: `11: [7, 12]` znači da su prva i druga replika dijaloga 11 redom `chunk_7.wav` i `chunk_12.wav`.

### Šta dobijate

Dobijate **dva direktorija u identičnom formatu**:

| Direktorij | Dijalozi | `answers.json`? | Koristite ga za |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ uključeno | treniranje / fino podešavanje modela |
| `dataset/test_public/`  | 100   | ✅ uključeno | pokretanje pipelinea i lokalno samostalno ocjenjivanje |

Tokom ocjenjivanja, vaš direktorij `dataset/test_public/` transparentno se zamjenjuje
direktorijem `hidden evaluation set` (`test_leaderboard_a` za javnu rang-listu i `test_leaderboard_b` za konačnu rang-listu) — oni imaju istu veličinu i format kao `dataset/test_public/`, ali bez `answers.json`.

Vaš notebook ponovo se izvršava nad tim podacima, a datoteka `answers.json` koju proizvede koristi se za ocjenjivanje. Izdvojeni testni dijalozi dolaze iz iste distribucije kao `train`, tako da je vaš lokalni rezultat `test_public` vjerodostojan pokazatelj.

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

Za svaki dijalog odredite izvorni hronološki redoslijed njegovih audiosegmenata. Vaše predviđanje treba biti permutacija `P` od `{0, 1, …, n−1}`, gdje je `P[i]` predviđena hronološka pozicija za `chunk_i.wav` (0 = prvo).

Vaša izlazna datoteka `answers.json` treba preslikati svaki ID dijaloga na njegovu predviđenu permutaciju:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Primjer

Dijalog ima 3 izmiješana segmenta `chunk_0, chunk_1, chunk_2`:

| izmiješani segment | izgovoreni sadržaj | stvarna pozicija (rang) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *„Nema problema — poslije ću ti poslati bilješke.“* | 2 (posljednje) |
| `chunk_1.wav` | *„Hej, dolaziš li na sastanak u tri sata?“* | 0 (prvo) |
| `chunk_2.wav` | *„Ne mogu — tada imam termin kod zubara.“* | 1 |

Stvarni redoslijed je **chunk_1 → chunk_2 → chunk_0**, pa je `P = [2, 0, 1]`, a `prefix.json` sadrži `[1, 2]`.

⚠️ **P mora biti ispravna permutacija:** dužine n, indeksirana od 0, sa svakom vrijednošću tačno jednom. Duplikati, nedostajuće vrijednosti ili vrijednosti izvan raspona (npr. indeksiranje od 1) donose 0 bodova za taj dijalog, kao i dijalog koji nedostaje u datoteci. Neispravna datoteka ili datoteka koja nije u JSON formatu bit će odbijena.

## Bodovanje

Za bodovanje ovog zadatka koristi se **tačnost redoslijeda parova**. Provjerava se svaki par segmenata i postavlja pitanje: _koji od njih treba doći prvi?_ Par je tačan ako vaše predviđanje daje isti odgovor kao referentni redoslijed. Za dijalog sa `n` segmenata postoji $$M = n(n-1)/2$$ parova; neka je `I` broj inverzija — parova poredanih drugačije od referentnog redoslijeda:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Konačni rezultat je prosjek rezultata po dijalogu za sve
dijaloge u podjeli.**

## Dozvoljeni modeli

Za rješavanje ovog zadatka možete koristiti samo sljedeće prethodno trenirane modele, i tokom treniranja i tokom evaluacije. Svi ovi modeli već su preuzeti i dostupni u okruženju. Primjere njihove upotrebe možete vidjeti u baseline notebooku `solution.ipynb`. Imajte na umu da ne možete koristiti nijedan drugi model i da vaš program nema pristup internetu.

- **Reprezentacije govora:** **wav2vec 2.0**. **Whisper encoder** također se može koristiti kao ekstraktor obilježja.
[kartica modela wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automatsko prepoznavanje govora (ASR):** **OpenAI Whisper** (bilo koje veličine).
[kartica modela Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Jezički model:** **Qwen2.5-0.5B**, koji se može koristiti u zero-shot režimu ili fino podesiti na dostavljenoj podjeli `train`.
[kartica modela Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Imajte na umu da ograničenje od 10 minuta mora obuhvatiti svako treniranje ili fino podešavanje koje obavljate tokom ocjenjivanja, kao i inferenciju na evaluacijskom skupu.

## Kako predati rješenje

- Otvorite `solution.ipynb` i pokrenite sve ćelije. Potvrdite da zapisuje `answers.json` u radni direktorij s permutacijom za svaki dijalog u `dataset/test_public/` (100 dijaloga). Tokom ocjenjivanja notebook se ponovo pokreće na skrivenom testnom skupu, a `answers.json` koji tamo proizvede koristi se za ocjenjivanje.
- Poboljšajte rješenje ako želite — ili nemojte; sam baseline potvrđuje ispravnost pipelinea.
- Otvorite karticu Git na lijevoj bočnoj traci u JupyterLabu.
- **Dodajte u pripremno područje** `solution.ipynb` (ikona + pored njega).
- Unesite poruku commita i kliknite **Commit**.
- Kliknite oblak sa strelicom prema gore da izvršite push.
- Vratite se na ovu stranicu takmičenja i kliknite **Submit**.

Predajte tačno jednu datoteku, nazvanu `solution.ipynb`.
