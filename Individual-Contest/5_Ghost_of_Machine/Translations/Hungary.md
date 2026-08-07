# A gép szelleme

- **Időkorlát:** 10 perc
- **Alappontszám (baseline):** 28.6
- **Környezet:** egy GPU (≈16 GB VRAM), internetkapcsolat nélkül
- **A megoldás mérete:** `solution.ipynb` ≤ 20 MB
- **Tárhely:** 5 GB
- **Előre betanított modellek:** kizárólag a **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — egy szöveg**enkóder** (embedding/beágyazó modell).


## Feladat

Különös dolgok történnek a Kazah Nemzeti Levéltárban. A könyvtárosok szerint egyes könyvek korábban máshogy végződtek, de ezt senki sem tudja bizonyítani — minden példány ugyanolyan, és továbbra is minden történet értelmes. Önt MI-kutatóként felkérik a változtatások helyének meghatározására.
![Kísértet](../ghost.jpg)

Egy szövegrészlet ember által írt szövegként kezdődik, majd egy ponton észrevétlenül
egy nyelvi modell által generált folytatásra vált. Egészként olvasva egyetlen
összefüggő műnek tűnik — de valahol középen a szerző emberről
gépre változik. Az Ön feladata **megtalálni ezt a váltást: azt a karakterindexet, ahol az
emberi rész véget ér, és a gépi rész elkezdődik**.

Minden minta egyetlen `text` sztring. Pontosan egy határ van. Minden,
ami előtte található, emberi; minden, ami attól kezdve található, gép által generált.

## Adatok (Dataset)

Egyszerű szöveges (plain text) angol nyelvű részletek, mindegyikben egy határral.

- **A rész** (a határ előtti): részlet egy ember által írt szövegből.
- **B rész** (a határtól kezdve): mesterséges folytatás, amit egy nyelvi modell generált. A nyelvi modell az A részre volt kondícionálva.
- Mindkét oldal legalább 180 szóból áll; a teljes hossz ~500–800 szó.
- A **`boundary_char_index`** az a karakterpozíció, ahol a B rész kezdődik: a
  `text[boundary_char_index:]` a gép alkotta rész és a
  `text[:boundary_char_index]` az ember alkotta rész, a két részt elválasztó egyetlen szóközzel együtt.

#### Amit megkap

**Két mappát** kap:

| Mappa | Minták száma| `answers.jsonl`? | Felhasználás |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ mellékelve | a módszer betanítása / finomhangolása |
| `dataset/test_public/`  | 380   | ✅ mellékelve (a fejlesztés alatt) | a pipeline futtatása és helyi kiértékelés (self-score)|

**Értékeléskor** az Ön `dataset/test_public/` mappáját **egy rejtett
teszt (kiértékelési) halmaz váltja fel**. Ennek formátuma megegyezik a nyilvánossal, de **nem tartalmaz `answers.jsonl`** fájlt. Az Ön
notebookját ezen újrafuttatják, és az általa előállított `answers.jsonl` kerül pontozásra.

- A nyilvános ranglista egy rejtett **test_leaderboard_a** halmazt használ (380 minta).

- A végső rangsorolás egy rejtett **test_leaderboard_b** halmazt használ (380 minta).

Mindhárom értékelési
halmaz azonos méretű, és ugyanabból az eloszlásból származik, mint a `train`, ezért az Ön helyi
`dataset/test_public/` pontszáma észszerű becslést ad a ranglistán elérhető pontszámára.

#### Lemezen tárolt formátum

```
dataset/train/data.jsonl      # egy JSON objektum soronként: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # csak a fejlesztés alatt — NEM elérhető a rejtett teszt (kiértékelési) halmazban
```

- A `answers.jsonl` azonosítói megfelelnek a `data.jsonl` azonosítóinak.
- A `dataset/train/` (a válaszokkal együtt) mindig elérhető, amikor Ön betanítást vagy finomhangolást végez.

## Kimenet (a beadás formátuma)

Önnek **egyetlen notebookot kell beadnia, amelynek neve kötelezően `solution.ipynb`**. Pontosan ez a fájlnév szükséges. Minden más fájlt futtatás nélkül elutasítanak.

A notebooknak **be kell olvasnia a `dataset/test_public/data.jsonl` fájlt**, és egyetlen
**`answers.jsonl`** fájlt kell írnia a repository gyökérkönyvtárába — soronként egy JSON-objektummal, amely
minden minta azonosítójához hozzárendeli az Ön által előre jelzett határ karakterindexét:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- A `boundary_char_index` értékének **a `[0, len(text)]` tartományba eső egész számnak kell lennie**.
- A `dataset/test_public/data.jsonl` minden azonosítójának pontosan egyszer kell szerepelnie. Minden, a
  `answers.jsonl` fájlból hiányzó minta (vagy nem egész / tartományon kívüli érték) 0
  pontot kap az adott mintára.

## Pontozás

Minden mintánál legyen `p` az Ön által előre jelzett index, `t` pedig a valódi határ. A mintánkénti pontszám exponenciálisan csökken a karaktertávolsággal:

$$\text{pontszám} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{ahol} ~ \tau = 100.$$

Ez a pontszám következő viselkedéséhez vezet:
- **=1.0** — pontos a határkarakter érték;
- **≈0.78** — 25 karakter eltérés; - **≈0.61** — 50 karakter eltérés;
- **≈0.37** — 100 karakter eltérés;
- **≈0.01** — 500 karakter eltérés.

A **végső pontszám a mintánkénti pontszámok átlaga** az adott halmaz összes mintájára
(0–100 közé átskálázva). Ez a metrika a *közeli* eredményt is jutalmazza, nem csupán a pontosat.

## Korlátozások

- **Környezet:** egy GPU (≈16 GB VRAM), az értékeléskor internetkapcsolat nélkül — az engedélyezett
  modell (lásd alább) már rendelkezésre áll. **Futtatási időkeret: 10 perc** a teljes
  futtatásra — ennek magában kell foglalnia az értékeléskor végzett minden betanítást / finomhangolást
  **és** az értékelési halmazon végzett inferenciát.
- **Engedélyezett előre betanított modell** — a lista teljes körű; semmilyen más előre betanított súly
  nem használható. A modell **előre rendelkezésre áll a környezetben** (a szokásos módon töltse be, például
  `from_pretrained`; az értékeléskor nincs internetkapcsolat):
  - **bge-base-en-v1.5** — egy 110M-paraméteres szöveg**enkóder** (embedding/beágyazó modell). Mondat-
    és szövegrészlet-embeddingeket állít elő; nem generatív nyelvi modell. Ön
    használhatja **változatlanul (befagyasztott jellemzőkkel), vagy finomhangolhatja a `train` halmazon**
    (a teljes finomhangolás belefér a 16 GB / 10-perces keretbe).
- A klasszikus / statisztikai eszközök használata nincs korlátozva: bármilyen jellemzőalapú (feature-based)
  modellt építhet (például scikit-learn-osztályozókat vagy -regresszorokat) a saját maga által
  kiszámított embeddingjellemzőkre. Az *előre betanított mélytanulási súlyok* használata viszont kizárólag  a fenti listára van korlátozva.
