# Lampa

- **Časový limit:** 10 minút
- **Prostredie:** jedna GPU (≈16 GB VRAM), bez internetu
- **Veľkosť riešenia:** `solution.ipynb` ≤ 1 MB
- **Úložisko:** 5 GB 

## Úloha
 
Váš priateľ navrhuje zahrať si hádaciu hru.
Ako rozhodca vyberie jedno skryté slovo z pevne stanovenej slovnej zásoby a vy ho musíte nájsť najviac za 30 ťahov.
V každom ťahu rozhodca porovná dve slová a oznámi, ktoré z nich je sémanticky bližšie k skrytému slovu. Každá hra sa začína
pevne stanovenou dvojicou `lamp - potato`, pretože sú to dve z obľúbených vecí vášho priateľa. Váš program potom
navrhne jedno nové slovo. Víťaz porovnania zostáva
a porovná sa s vaším ďalším návrhom. 
Hru vyhráte v okamihu, keď presne navrhnete skryté slovo. Pri porovnávaní sa
nerozlišujú veľké a malé písmená. Každé slovo, ktoré navrhnete, musí byť v `dataset/vocabulary.json`.

Úplný príklad s protokolom a načítaním dát sa nachádza v `solution.ipynb`. 
Môžete zmeniť triedu PublicEmbeddingPlayer. Váš program sa inicializuje raz a odohrá všetky hry v rámci jedného spustenia;
protokol na začiatku každej hry vytvorí nový objekt `PublicEmbeddingPlayer`.

## Rozhodca

Váš program odošle rozhodcovi jeden objekt JSON a rozhodca odpovie jedným objektom JSON. 

Spracovaný príklad, v ktorom je skryté slovo uvedené iba na vysvetlenie protokolu:

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

Ťahy sú očíslované od 1 do 30.

Možnosti `verdict` sú `first`, čo znamená, že word1 je bližšie, `second`, čo znamená, že word2 je bližšie, alebo
`same`, čo znamená, že obe slová sú rovnako blízko k skrytému slovu. 

`winner_word` je slovo ponechané na ďalšie porovnanie. Pri verdikte `same` zostáva prvé slovo.

## Dataset

Spoločné pre všetky splity:

- `dataset/vocabulary.json` — 1602 jedinečných slov napísaných malými písmenami. Skryté slovo je vždy
  jedným z nich.
- `dataset/public_embeddings.npy` — `float32`, tvar `(1602, 2560)`. Riadok `i`
  zodpovedá slovu `i` v slovnej zásobe. Ide o *verejné* embeddingy;
  rozhodca používa inú, súkromnú reprezentáciu.

Splity sú množiny skrytých slov:

| Split | Slová | Odpovede | Použitie |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | spustenie vášho riešenia a vlastné vyhodnotenie |
| `test_leaderboard_a` | 120 | skryté | priebežný rebríček |
| `test_leaderboard_b` | 120 | skryté | konečné poradie |

Split `train` neexistuje — z označených riadkov sa nič netrénuje.

### Poskytnuté modely

S úlohou sa dodávajú dva predtrénované embeddingové modely, ktoré možno použiť:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Oba sa musia načítať zo svojej lokálnej cesty; identifikátor hubu Hugging Face, napríklad
`"BAAI/bge-m3"`, spustí sťahovanie a zlyhá, pretože vyhodnocovanie prebieha offline. Každý
adresár obsahuje spustiteľný súbor `example.py`, ktorý ukazuje volanie offline.

Dostupné knižnice: `numpy`, `torch`, `sentence-transformers`. Bez internetu, bez
sťahovania, bez ďalších balíkov.

## Výstup

Žiadny. Toto je interaktívna úloha: vaše riešenie nezapisuje žiadny súbor s odpoveďou; komunikuje
s rozhodcom cez stdin/stdout tak, ako je opísané vyššie.

## Metrika

Hra vyriešená v ťahu `t` získava skóre `1.0 - 0.02 × max(0, t - 10)`; hra nevyriešená
do 30 ťahov získava skóre `0`. Ťahy 1–10 teda získavajú skóre `1.00`, ťah 20 získava skóre `0.80` a ťah
30 získava skóre `0.60`.

Vaše skóre za úlohu je priemerné skóre z hier × 100, medzi `0.00` a `100.00`.

Limit 10 minút predstavuje celkové ohraničenie zahŕňajúcie spustenie, prípravu a odohranie všetkých 120 hier v testovacej množine. 

## Ako odovzdať riešenie

1. Otvorte `solution.ipynb`, upravte `PublicEmbeddingPlayer` a spustite všetky bunky, aby ste sa uistili, že riešenie funguje.
2. Voliteľne ho skontrolujte lokálne: `python local_test.py solution.ipynb --limit 5`.
   Lokálny rozhodca používa *verejné* embeddingy, takže jeho skóre je
   iba orientačné.
3. Uložte `solution.ipynb`.
4. Otvorte kartu Git na ľavom bočnom paneli JupyterLab.
5. Pridajte `solution.ipynb` do oblasti stage (ikona **+** vedľa neho).
6. Zadajte označenie commitu a kliknite na Commit.
7. Kliknutím na oblak so šípkou nahor vykonajte push.
8. Vráťte sa na túto stránku súťaže a kliknite na Submit, pričom označenie commitu musí zodpovedať označeniu, ktorú ste uviedli v kroku 6.

Odovzdajte presne jeden súbor s názvom `solution.ipynb`, ktorý zahŕňa všetky potrebné prípravy a inferenciu.
