# Krompir

- **Vremensko ograničenje:** 10 minuta
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Prostor za skladištenje:** 5 GB 

## Zadatak
 
Vaš prijatelj predlaže da igrate igru pogađanja.
On, kao sudija, bira jednu skrivenu riječ iz fiksnog vokabulara, a vi je morate pronaći u najviše 30 poteza.
U svakom potezu sudija poredi dvije riječi i saopštava koja je semantički bliža
skrivenoj riječi. Svaka igra počinje
fiksnim parom `lamp vs potato`, jer su to dvije omiljene stvari vašeg prijatelja. Vaš program zatim
predlaže jednu novu riječ. Pobjednik poređenja se zadržava
i poredi sa vašim sljedećim predlogom. 
Pobjeđujete u igri čim predložite tačno skrivenu riječ. Pri poređenju se
ne pravi razlika između velikih i malih slova. Svaka riječ koju predložite mora biti u `dataset/vocabulary.json`.

Potpun primjer sa protokolom i učitavanjem podataka nalazi se u `solution.ipynb`. 
Možete izmijeniti klasu PublicEmbeddingPlayer. Vaš program se inicijalizuje jednom i igra svaku igru u jednom pokretanju;
protokol kreira novi PublicEmbeddingPlayer na početku svake igre.

## Sudija

Vaš program šalje jedan JSON objekat Sudiji, a Sudija odgovara jednim JSON objektom. 

Razrađen primjer, u kojem je skrivena riječ prikazana samo radi objašnjenja protokola:

```text
Hidden word: shovel          Fixed opening: lamp vs potato

<- {"turn": 1, "winner_word": "potato", "verdict": "second", "word1": "lamp",   "word2": "potato"}
-> {"new_word": "rock"}
<- {"turn": 2, "winner_word": "rock",   "verdict": "second", "word1": "potato", "word2": "rock"}
-> {"new_word": "hammer"}
<- {"turn": 3, "winner_word": "hammer", "verdict": "second", "word1": "rock",   "word2": "hammer"}
-> {"new_word": "shovel"}                                    <- matches: game won
-> {"status": "win"}
```

Potezi su indeksirani od 1 do 30.

Opcije za `verdict` su `first`, što znači da je word1 bliža, `second`, što znači da je word2 bliža, ili
`same`, što znači da su obje riječi jednako blizu skrivenoj riječi. 

`winner_word` je riječ koja se zadržava za sljedeće poređenje. Pri presudi `same`, prva riječ ostaje.

## Dataset

Zajedničko svim podjelama:

- `dataset/vocabulary.json` — 1602 jedinstvene riječi napisane malim slovima. Skrivena riječ je uvijek
  jedna od njih.
- `dataset/public_embeddings.npy` — `float32`, oblika `(1602, 2560)`. Red `i`
  odgovara riječi `i` u vokabularu. Ovo su *javni* embedding vektori; sudija
  koristi drugačiju, privatnu reprezentaciju.

Podjele su skupovi skrivenih riječi:

| Podjela | Riječi | Odgovori | Koristite je za |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | pokretanje svog rješenja i samostalno izračunavanje rezultata |
| `test_leaderboard_a` | 120 | skriveni | aktuelnu rang-listu |
| `test_leaderboard_b` | 120 | skriveni | konačni plasman |

Ne postoji podjela `train` — ništa se ne prilagođava na osnovu označenih redova.

### Obezbijeđeni modeli

Uz zadatak se isporučuju dva prethodno obučena embedding modela koja se mogu koristiti:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Oba se moraju učitati sa svoje lokalne putanje; Hugging Face hub id kao što je
`"BAAI/bge-m3"` pokreće preuzimanje i ne uspijeva, jer se ocjenjivanje obavlja bez interneta. Svaki
direktorijum sadrži `example.py` koji se može pokrenuti i prikazuje poziv bez interneta.

Dostupne biblioteke: `numpy`, `torch`, `sentence-transformers`. Nema interneta, nema
preuzimanja, nema drugih paketa.

## Izlaz

Nema ga. Ovo je interaktivni zadatak: vaše rješenje ne upisuje datoteku sa odgovorom; komunicira sa
sudijom preko stdin/stdout kao što je gore opisano.

## Metrika

Igra riješena u potezu `t` dobija `1.0 - 0.02 × max(0, t - 10)`; igra koja nije riješena
u roku od 30 poteza dobija `0`. Dakle, potezi 1–10 donose `1.00`, potez 20 donosi `0.80`, a potez
30 donosi `0.60`.

Vaš rezultat za zadatak je prosječan rezultat igre × 100, između `0.00` i `100.00`.

Ograničenje od 10 minuta predstavlja jedinstveni budžet koji obuhvata pokretanje, pripremu i svih 120
igara u testnom skupu. 

## Kako predati rješenje

1. Otvorite `solution.ipynb`, uredite `PublicEmbeddingPlayer` i pokrenite sve ćelije kako biste se uvjerili da radi.
2. Po želji ga provjerite lokalno: `python local_test.py solution.ipynb --limit 5`.
   Lokalni sudija koristi *javne* embedding vektore, pa je njegov rezultat
   samo orijentacioni.
3. Sačuvajte `solution.ipynb`.
4. Otvorite karticu Git na lijevoj bočnoj traci u JupyterLab.
5. Dodajte `solution.ipynb` u staging area (ikona **+** pored nje).
6. Unesite poruku commita i kliknite na Commit.
7. Kliknite na oblak sa strelicom nagore da biste izvršili push.
8. Vratite se na ovu stranicu takmičenja i kliknite na Submit, pri čemu poruka commita mora odgovarati onoj koju ste naveli.

Predajte tačno jednu datoteku, nazvanu `solution.ipynb`, koja obuhvata sve potrebne pripreme i inferenciju.
