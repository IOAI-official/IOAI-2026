# Krumpir

- **Vremensko ograničenje:** 10 minuta
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Prostor za pohranu:** 5 GB 

## Zadatak
 
Vaš prijatelj predlaže igru pogađanja.
On, u ulozi suca, odabire jednu skrivenu riječ iz fiksnog rječnika, a vi je morate pronaći u najviše 30 poteza.
U svakom potezu sudac uspoređuje dvije riječi i javlja koja je semantički bliža
skrivenoj riječi. Svaka igra počinje
fiksnim parom `lamp vs potato` jer su to dvije omiljene stvari vašeg prijatelja. Vaš program zatim
predlaže jednu novu riječ. Pobjednik usporedbe zadržava se
i uspoređuje s vašim sljedećim prijedlogom. 
Pobjeđujete u igri čim predložite točno skrivenu riječ. Pri podudaranju se
ne razlikuju velika i mala slova. Svaka riječ koju predložite mora biti u `dataset/vocabulary.json`.

Potpuni primjer s protokolom i učitavanjem podataka nalazi se u `solution.ipynb`. 
Možete izmijeniti klasu PublicEmbeddingPlayer. Vaš se program inicijalizira jednom i igra svaku igru u jednom pokretanju;
protokol stvara novi primjerak klase PublicEmbeddingPlayer na početku svake igre.

## Sudac

Vaš program šalje jedan JSON objekt Sucu, a Sudac odgovara jednim JSON objektom. 

Razrađeni primjer, u kojem je skrivena riječ prikazana samo radi objašnjenja protokola:

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

Mogućnosti za `verdict` jesu `first`, što znači da je word1 bliža, `second`, što znači da je word2 bliža, ili
`same`, što znači da su obje riječi jednako blizu skrivenoj riječi. 

`winner_word` je riječ koja se zadržava za sljedeću usporedbu. U slučaju odluke `same` prva riječ ostaje.

## Skup podataka

Zajedničko svim podjelama:

- `dataset/vocabulary.json` — 1602 jedinstvene riječi zapisane malim slovima. Skrivena riječ uvijek je
  jedna od njih.
- `dataset/public_embeddings.npy` — `float32`, oblika `(1602, 2560)`. Redak `i`
  odgovara riječi `i` u rječniku. To su *javni* embedding-vektori; sudac
  upotrebljava drukčiju, privatnu reprezentaciju.

Podjele su skupovi skrivenih riječi:

| Podjela | Riječi | Odgovori | Upotrijebite za |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | pokretanje svojeg rješenja i samostalno izračunavanje rezultata |
| `test_leaderboard_a` | 120 | skriveni | trenutačnu ljestvicu poretka |
| `test_leaderboard_b` | 120 | skriveni | konačni poredak |

Ne postoji podjela `train` — ništa se ne prilagođava na temelju označenih redaka.

### Priloženi modeli

Uz zadatak se isporučuju dva unaprijed istrenirana modela embeddinga koja se mogu upotrebljavati:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Oba se moraju učitati sa svoje lokalne putanje; identifikator na Hugging Face hubu kao što je
`"BAAI/bge-m3"` pokreće preuzimanje i ne uspijeva jer se ocjenjivanje provodi bez interneta. Svaki
direktorij sadržava izvršivu datoteku `example.py` koja prikazuje poziv bez interneta.

Dostupne biblioteke: `numpy`, `torch`, `sentence-transformers`. Nema interneta, nema
preuzimanja ni drugih paketa.

## Izlaz

Nema ga. Ovo je interaktivni zadatak: vaše rješenje ne zapisuje datoteku s odgovorom, nego komunicira sa
sucem putem standardnog ulaza/izlaza kako je prethodno opisano.

## Metrika

Igra u kojoj je riječ pronađena u potezu `t` donosi `1.0 - 0.02 × max(0, t - 10)`; igra koja nije riješena
unutar 30 poteza donosi `0`. Stoga potezi 1–10 donose `1.00`, potez 20 donosi `0.80`, a potez
30 donosi `0.60`.

Vaš rezultat za zadatak srednja je vrijednost rezultata igara × 100, između `0.00` i `100.00`.

Ograničenje od 10 minuta jedinstven je vremenski budžet koji obuhvaća pokretanje, pripremu i svih 120
igara u testnom skupu. 

## Kako predati rješenje

1. Otvorite `solution.ipynb`, uredite `PublicEmbeddingPlayer` i izvršite sve ćelije kako biste provjerili da sve radi.
2. Neobavezno ga provjerite lokalno: `python local_test.py solution.ipynb --limit 5`.
   Lokalni sudac upotrebljava *javne* embedding-vektore, pa je njegov rezultat
   samo orijentacijski.
3. Spremite `solution.ipynb`.
4. Otvorite karticu Git u lijevoj bočnoj traci JupyterLaba.
5. Dodajte `solution.ipynb` u pripremljene promjene (ikona **+** pokraj nje).
6. Unesite poruku commita i kliknite Commit.
7. Kliknite oblak sa strelicom prema gore kako biste poslali promjene.
8. Vratite se na ovu stranicu natjecanja i kliknite Submit, pri čemu poruka commita mora odgovarati onoj koju ste naveli.

Predajte točno jednu datoteku naziva `solution.ipynb`, koja obuhvaća sve potrebne pripreme i inferenciju.
