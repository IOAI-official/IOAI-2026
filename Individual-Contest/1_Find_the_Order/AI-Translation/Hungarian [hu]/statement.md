# Találja meg a sorrendet

- **Időkorlát:** 10 perc
- **Környezet:** egy GPU (≈16 GB VRAM), internet-hozzáférés nélkül
- **A megoldás mérete:** `solution.ipynb` ≤ 1 MB
- **Tárhely:** 5 GB 

## Feladat

Két résztvevő, *A beszélő* és *B beszélő* közötti, angol nyelven elhangzó párbeszédeket kap. Minden párbeszéd beszélői megszólalásokra van felosztva, és minden megszólalás csak egyetlen beszélő beszédét tartalmazza. Minden megszólalás külön `.wav` hangfájlban van tárolva, így egy teljes párbeszédet `.wav` fájlok egy halmaza képvisel, megszólalásonként egy fájllal. 

Sajnos a megszólalásokat véletlenszerűen összekeverték, ezért a beszélgetésnek már nincs értelme. A `chunk_{k}.wav` fájlnévben `k` az összekevert halmaz k-adik hangrészletére utal, nem az eredeti párbeszéd k-adik megszólalására.

**‼️ Az Ön feladata a beszélgetés eredeti időrendi sorrendjének rekonstruálása.**

![Találja meg a sorrendet](../../find_the_order.jpg)

---

## Adathalmaz

Minden párbeszéd `n` hangfájlt tartalmaz, amelyek neve `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. A hangrészletek egy-egy megszólalást tartalmaznak. A fájlnevek csak az összekevert sorrendnek felelnek meg. Nem jelzik, hogy egy hangrészlet hová tartozik az eredeti beszélgetésben. Minden párbeszéd 7–20 hangrészletből áll, monó, 44.1 kHz mintavételi frekvenciával (újra-
mintavételezhető).

**A `prefix.json` minden párbeszéd első két hangrészletének fájlnévindexét tartalmazza.** Ez azonosítja a párbeszéd valódi kezdetét, és megszünteti a beszélgetés előre vagy visszafelé olvasása közötti kétértelműséget.

Például: `11: [7, 12]` azt jelenti, hogy a 11. párbeszéd első és második megszólalása rendre `chunk_7.wav` és `chunk_12.wav`.

### Amit megkap

**Két, azonos formátumú mappát** kap:

| Mappa | Párbeszédek | `answers.json`? | Felhasználás |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ mellékelve | a modell tanítása / finomhangolása |
| `dataset/test_public/`  | 100   | ✅ mellékelve | a pipeline futtatása és helyi önértékelés |

Az értékelés során az Ön `dataset/test_public/` mappáját átlátható módon lecserélik
egy `hidden evaluation set` mappára (`test_leaderboard_a` a nyilvános ranglistához és `test_leaderboard_b` a végső ranglistához) — ezek mérete és formátuma megegyezik a `dataset/test_public/` mappáéval, de nem tartalmaznak `answers.json` fájlt.

A notebookot ezen az adaton ismét végrehajtják, és az általa létrehozott `answers.json` fájlt használják a pontozáshoz. A visszatartott tesztpárbeszédek ugyanabból az eloszlásból származnak, mint a `train`, ezért az Ön helyi `test_public` pontszáma megbízható előrejelzést ad.

### Könyvtárstruktúra

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

## Kimenet

Minden párbeszédhez határozza meg a hangrészletek eredeti időrendi sorrendjét. Az előrejelzésnek `P` egy `{0, 1, …, n−1}` feletti permutációjának kell lennie, ahol `P[i]` a `chunk_i.wav` előre jelzett időrendi pozíciója (0 = első).

A `answers.json` kimeneti fájlnak minden párbeszéd-azonosítót hozzá kell rendelnie az előre jelzett permutációjához:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Példa

Egy párbeszédnek 3 összekevert hangrészlete van `chunk_0, chunk_1, chunk_2`:

| összekevert hangrészlet | elhangzott tartalom | valódi pozíció (rang) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (utolsó) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (első) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

A valódi sorrend **chunk_1 → chunk_2 → chunk_0**, ezért `P = [2, 0, 1]`, és a `prefix.json` tartalma `[1, 2]`.

⚠️ **P-nek valódi permutációnak kell lennie:** hossza n, 0-indexelt, és minden értéket pontosan egyszer tartalmaz. Ismétlődő vagy hiányzó értékek, illetve a tartományon kívüli elemek (például 1-indexelés) esetén az adott párbeszédre kapott pontszám 0, ahogy akkor is, ha egy párbeszéd hiányzik a fájlból. A hibás formátumú vagy nem JSON-formátumú fájlt elutasítják.

## Pontozás

A feladat pontozási mérőszáma a **páronkénti sorrendi pontosság**. Minden hangrészletpárt ellenőriz, és felteszi a kérdést: _a kettő közül melyiknek kell előbb következnie?_ Egy pár akkor helyes, ha az előrejelzés ugyanazt a választ adja, mint az alapigazság. Egy `n` hangrészletből álló párbeszédben $$M = n(n-1)/2$$ pár van; legyen `I` az inverziók száma — azon pároké, amelyek sorrendje eltér az alapigazságtól:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **A végső pontszám a részhalmaz összes
párbeszédére számított, párbeszédenkénti pontszámok átlaga.**

## Engedélyezett modellek

A feladat megoldásához mind a tanítás, mind az értékelés során kizárólag az alábbi előtanított modelleket használhatja. Ezek a modellek már le vannak töltve, és elérhetők a környezetben. Használatukra példákat talál a `solution.ipynb` baseline notebookban. Vegye figyelembe, hogy semmilyen más modellt nem használhat, és a programjának nincs internet-hozzáférése.

- **Beszédreprezentációk:** **wav2vec 2.0**. A **Whisper encoder** jellemzőkinyerőként is használható.
[wav2vec modellkártya](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automatikus beszédfelismerés (ASR):** **OpenAI Whisper** (bármely méret).
[Whisper modellkártya](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Nyelvi modell:** **Qwen2.5-0.5B**, amely zero-shot módon vagy a megadott `train` részhalmazon finomhangolva is használható.
[Qwen modellkártya](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Vegye figyelembe, hogy a 10 perces korlátnak az értékeléskor végzett minden tanítást vagy finomhangolást, valamint az értékelési halmazon végzett inferenciát is magában kell foglalnia.

## Beküldés módja

- Nyissa meg a `solution.ipynb` fájlt, és futtassa az összes cellát. Ellenőrizze, hogy létrehozza-e a `answers.json` fájlt a munkakönyvtárban, a `dataset/test_public/` minden párbeszédéhez egy permutációval (100 párbeszéd). Az értékeléskor a notebookot újra futtatják a rejtett teszthalmazon, és az ott létrehozott `answers.json` fájlt pontozzák.
- Ha szeretné, javítsa a megoldást — vagy ne tegye; már önmagában a baseline is ellenőrzi a pipeline működését.
- Nyissa meg a Git lapot a JupyterLab bal oldalsávjában.
- Adja a **Stage**-hez a `solution.ipynb` fájlt (a mellette lévő + ikonnal).
- Adjon meg egy commitüzenetet, és kattintson a **Commit** gombra.
- A push végrehajtásához kattintson a felfelé mutató nyilat tartalmazó felhőikonra.
- Térjen vissza erre a Contest oldalra, és kattintson a **Submit** gombra.

Pontosan egy, `solution.ipynb` nevű fájlt küldjön be.
