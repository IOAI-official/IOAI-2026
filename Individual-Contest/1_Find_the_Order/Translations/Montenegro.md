# Pronađite redosljed

- **Vremensko ograničenje:** 10 minuta
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Prostor za skladištenje:** 5 GB 

## Problem

Dati su vam govorni dijalozi na engleskom jeziku između dva učesnika, *Govornika A* i *Govornika B*. Svaki dijalog je podijeljen na govorne poteze, pri čemu svaki potez sadrži govor samo jednog govornika. Svaki potez je sačuvan kao zasebna `.wav` audio datoteka, tako da je kompletan dijalog predstavljen skupom `.wav` datoteka, po jednom za svaki potez. 

Nažalost, potezi su nasumično izmiješani, pa razgovor više nema smisla. U nazivu datoteke `chunk_{k}.wav`, `k` označava k-ti segment u izmiješanom skupu, a ne k-ti potez u originalnom dijalogu.

**‼️ Vaš zadatak je da rekonstruišete originalni hronološki redosljed razgovora.**

![Pronađite redosljed](../find_the_order.jpg)

---

## Dataset

Svaki dijalog sadrži `n` audio datoteka nazvanih `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Segmenti predstavljaju pojedinačne poteze. Nazivi datoteka odgovaraju samo izmiješanom redosljedu. Oni ne ukazuju na to gdje segment pripada u originalnom razgovoru. Svaki dijalog ima 7–20 segmenata, mono, 44.1 kHz (možete
promijeniti frekvenciju uzorkovanja).

**`prefix.json` sadrži indekse naziva datoteka prva dva segmenta u svakom dijalogu.** Time se određuje stvarni početak dijaloga i uklanja dvosmislenost između čitanja razgovora unaprijed ili unazad.

Na primjer: `11: [7, 12]` znači da su prvi i drugi potez dijaloga 11 redom `chunk_7.wav` i `chunk_12.wav`.

### Šta dobijate

Dobijate **dva foldera identičnog formata**:

| Folder | Dijalozi | `answers.json`? | Koristite ga za |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ uključeno | treniranje / fino podešavanje vašeg modela |
| `dataset/test_public/`  | 100   | ✅ uključeno | pokretanje vašeg pipeline-a i lokalno samostalno ocjenjivanje |

Tokom ocjenjivanja, vaš folder `dataset/test_public/` neprimjetno se zamjenjuje
folderom `hidden evaluation set` (`test_leaderboard_a` za javnu rang-listu i `test_leaderboard_b` za konačnu rang-listu) — oni imaju istu veličinu i format kao `dataset/test_public/`, ali bez `answers.json`.

Vaš notebook se ponovo izvršava nad tim podacima, a datoteka `answers.json` koju proizvede koristi se za ocjenjivanje. Skriveni testni dijalozi potiču iz iste distribucije kao `train`, pa vaš lokalni rezultat `test_public` predstavlja pouzdanu najavu rezultata.

### Struktura direktorijuma

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

Za svaki dijalog odredite originalni hronološki redosljed njegovih audio segmenata. Vaše predviđanje treba da bude permutacija `P` skupa `{0, 1, …, n−1}`, gdje je `P[i]` predviđena hronološka pozicija segmenta `chunk_i.wav` (0 = prvi).

Vaša izlazna datoteka `answers.json` treba da preslika svaki ID dijaloga u njegovu predviđenu permutaciju:

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
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (posljednji) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (prvi) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Stvarni redosljed je **chunk_1 → chunk_2 → chunk_0**, pa je `P = [2, 0, 1]`, a `prefix.json` sadrži `[1, 2]`.

⚠️ **P mora biti prava permutacija:** dužine n, indeksirana od 0, pri čemu se svaka vrijednost pojavljuje tačno jednom. Duplikati, nedostajuće vrijednosti ili vrijednosti van opsega (npr. indeksiranje od 1) donose rezultat 0 za taj dijalog, kao i dijalog koji nedostaje u datoteci. Neispravna datoteka ili datoteka koja nije u JSON formatu se odbacuje.

## Ocjenjivanje

Za ocjenjivanje ovog zadatka koristi se **tačnost redosljeda parova**. Provjerava se svaki par segmenata i postavlja pitanje: _koji od njih treba da bude prvi?_ Par je tačan ako vaše predviđanje daje isti odgovor kao tačno rješenje. Za dijalog sa `n` segmenata postoji $$M = n(n-1)/2$$ parova; neka je `I` broj inverzija — parova koji su poređani drugačije nego u tačnom rješenju:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Konačni rezultat je prosjek rezultata po dijalogu za sve
dijaloge u podskupu.**

## Dozvoljeni modeli

Za rješavanje ovog zadatka možete koristiti samo sljedeće prethodno trenirane modele, kako tokom treniranja tako i tokom evaluacije. Svi ovi modeli su već preuzeti i dostupni u okruženju. Primjere njihove upotrebe možete vidjeti u početnom notebook-u `solution.ipynb`. Imajte na umu da ne možete koristiti nijedan drugi model i da vaš program nema pristup internetu.

- **Reprezentacije govora:** **wav2vec 2.0**. **Whisper encoder** takođe se može koristiti za izdvajanje karakteristika.
[Kartica modela wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automatsko prepoznavanje govora (ASR):** **OpenAI Whisper** (bilo koje veličine).
[Kartica modela Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Jezički model:** **Qwen2.5-0.5B**, koji se može koristiti bez prethodnog prilagođavanja (zero-shot) ili fino podesiti na datom podskupu `train`.
[Kartica modela Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Imajte na umu da ograničenje od 10 minuta mora obuhvatiti svako treniranje ili fino podešavanje koje obavljate tokom ocjenjivanja, kao i inferenciju na evaluacionom skupu.

## Kako predati rješenje

- Otvorite `solution.ipynb` i pokrenite sve ćelije. Potvrdite da se u radnom direktorijumu zapisuje `answers.json` sa permutacijom za svaki dijalog u `dataset/test_public/` (100 dijaloga). Tokom ocjenjivanja, notebook se ponovo pokreće na skrivenom testnom skupu i ocjenjuje se `answers.json` koji tada proizvede.
- Poboljšajte rješenje ako želite — ili nemojte; samo početno rješenje potvrđuje ispravnost pipeline-a.
- Otvorite karticu Git na lijevoj bočnoj traci u JupyterLab-u.
- Dodajte u pripremnu oblast (**Stage**) `solution.ipynb` (ikona + pored njega).
- Unesite poruku commita i kliknite na **Commit**.
- Kliknite na oblak sa strelicom nagore da izvršite push.
- Vratite se na ovu stranicu takmičenja i kliknite na **Submit**.

Predajte tačno jednu datoteku, nazvanu `solution.ipynb`.
