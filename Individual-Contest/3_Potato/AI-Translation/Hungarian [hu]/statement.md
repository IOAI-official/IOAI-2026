# Burgonya

- **Időkorlát:** 10 perc
- **Környezet:** egy GPU (≈16 GB VRAM), internetkapcsolat nélkül
- **A megoldás mérete:** `solution.ipynb` ≤ 1 MB
- **Tárhely:** 5 GB 

## Feladat
 
A barátja egy találgatós játékot javasol.
Zsűriként kiválaszt egy rejtett szót egy rögzített szókészletből, Önnek pedig legfeljebb 30 kör alatt meg kell találnia azt.
A zsűri minden körben összehasonlít két szót, és közli, hogy szemantikailag melyik áll közelebb
a rejtett szóhoz. Minden játék a rögzített
`lamp vs potato` párral kezdődik, mivel ezek a barátja két kedvenc dolga. Ezután a programja
javasol egy új szót. Az összehasonlítás győztese megmarad,
és ezt hasonlítják össze a következő javaslatával. 
Abban a pillanatban megnyeri a játékot, amikor pontosan a rejtett szót javasolja. Az egyezés
nem különbözteti meg a kis- és nagybetűket. Minden javasolt szónak szerepelnie kell a `dataset/vocabulary.json` állományban.

A protokollt és az adatok betöltését bemutató teljes példa a `solution.ipynb` állományban található. 
A PublicEmbeddingPlayer osztályt módosíthatja. A program inicializálása egyszer történik meg, és egyetlen futásban játssza le az összes játékot;
a protokoll minden játék kezdetén új PublicEmbeddingPlayer példányt hoz létre.

## A zsűri

A programja egy JSON-objektumot küld a zsűrinek, a zsűri pedig egy JSON-objektummal válaszol. 

Egy kidolgozott példa, amelyben a rejtett szó csak a protokoll szemléltetése érdekében látható:

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

A körök indexelése 1-től 30-ig tart.

A `verdict` lehetséges értékei: `first`, ami azt jelenti, hogy word1 van közelebb; `second`, ami azt jelenti, hogy word2 van közelebb; vagy
`same`, ami azt jelenti, hogy mindkét szó egyformán közel van a rejtett szóhoz. 

A `winner_word` a következő összehasonlításhoz megtartott szó. `same` ítélet esetén az első szó marad meg.

## Adathalmaz

Minden felosztás közösen használja:

- `dataset/vocabulary.json` — 1602 egyedi, kisbetűs szó. A rejtett szó mindig
  ezek egyike.
- `dataset/public_embeddings.npy` — `float32`, alakja `(1602, 2560)`. A `i` sor
  a szókészlet `i` szavának felel meg. Ezek *nyilvános* embeddingek; a
  zsűri egy másik, privát reprezentációt használ.

A felosztások rejtettszó-halmazok:

| Felosztás | Szavak | Válaszok | Felhasználási cél |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | a megoldás futtatása és saját pontszámának kiszámítása |
| `test_leaderboard_a` | 120 | rejtett | élő ranglista |
| `test_leaderboard_b` | 120 | rejtett | végső rangsorolás |

Nincs `train` felosztás — semmi sincs címkézett sorokra illesztve.

### Biztosított modellek

A feladathoz két előre betanított embeddingmodell tartozik, amelyek használhatók:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Mindkettőt a helyi elérési útjáról kell betölteni; egy Hugging Face hubazonosító, például
`"BAAI/bge-m3"`, letöltést indít el és hibát okoz, mivel az értékelés offline történik. Mindegyik
könyvtár tartalmaz egy futtatható `example.py` fájlt, amely bemutatja az offline hívást.

Elérhető könyvtárak: `numpy`, `torch`, `sentence-transformers`. Nincs internetkapcsolat, nincs
letöltés, és más csomagok sem érhetők el.

## Kimenet

Nincs. Ez egy interaktív feladat: a megoldása nem ír válaszfájlt; a fent leírtak szerint
stdin/stdout csatornán kommunikál a zsűrivel.

## Metrika

Egy, a `t` körben megtalált szóval végződő játék pontszáma `1.0 - 0.02 × max(0, t - 10)`; egy 30 körön
belül meg nem oldott játék pontszáma `0`. Így az 1–10 körök pontszáma `1.00`, a 20 köré `0.80`, a
30 köré pedig `0.60`.

A feladatra kapott pontszáma a játékok átlagos pontszáma × 100, értéke `0.00` és `100.00` között van.

A 10 perces időkorlát egyetlen közös keret, amely magában foglalja az indítást, az előkészítést és a teszthalmaz mind a 120
játékát. 

## Beküldés

1. Nyissa meg a `solution.ipynb` fájlt, szerkessze a `PublicEmbeddingPlayer` részt, és futtassa az összes cellát, hogy meggyőződjön a működéséről.
2. Opcionálisan ellenőrizze helyben: `python local_test.py solution.ipynb --limit 5`.
   A helyi zsűri a *nyilvános* embeddingeket használja, ezért a kapott pontszám
   csak tájékoztató jellegű.
3. Mentse a `solution.ipynb` fájlt.
4. Nyissa meg a Git lapot a JupyterLab bal oldalsávjában.
5. Adja hozzá a `solution.ipynb` fájlt az előkészített módosításokhoz (a mellette lévő **+** ikonnal).
6. Adjon meg egy commitüzenetet, majd kattintson a Commit gombra.
7. Kattintson a felfelé mutató nyilat tartalmazó felhő ikonra a push végrehajtásához.
8. Térjen vissza erre a versenyoldalra, és kattintson a Submit gombra; a commitüzenet egyezzen meg az Ön által megadottal.

Pontosan egy, `solution.ipynb` nevű fájlt küldjön be, amely minden szükséges előkészítést és az inferenciát is tartalmazza.
