# Kettősügynök-dilemma

- **Időkorlát:** 12 perc.
- **Tárhely:** 5 GB
- **Környezet:** egy GPU (≈16 GB VRAM), internet nélkül
- **A megoldás mérete:** `solution.ipynb` ≤ 1 MB
- **Alappontszám (baseline pontszám):** 0 

Az asztanai nemzeti MI-központban két számítógépes modell — az R modell (egy ResNet-18) és a V modell (egy ViT-Tiny) — elemez fényképeket. Jelenleg mindkét modell tökéletesen teljesít: 100%-os pontosságot érnek el, és minden egyes képen azonos eredményt adnak. Annak tesztelésére, hogy valójában mennyire különböznek intelligens „agyaik”, a vezető kutató a következő kihívást adja Önnek: végezzen apró, szinte láthatatlan pixelmódosításokat minden fényképen úgy, hogy az R modell és a V modell eredménye teljesen eltérjen.

![kép](../dilemma.jpg)

## 1. Feladat

Két előtanított képosztályozó ugyanazt a képet vizsgálja. Az ebben a feladatban megadott képeken mindkét osztályozó 100%-os pontossággal teljesít.

- **R modell**: `torchvision.models.resnet18` (egy CNN, ResNet18).
- **V modell**: `timm` `vit_tiny_patch16_224` modellje (egy Transformer, ViT-Tiny).

Az Ön feladata, hogy minden képhez egy kis módosítást („perturbációt”) hozzon létre úgy, hogy a két modell eredménye eltérjen. Minden képhez **két különböző** perturbációt kell létrehoznia:

- **A típus**: hozzáadása után az R modell továbbra is helyesen osztályozza a képet, a V modell azonban helytelenül osztályozza.
- **B típus**: hozzáadása után a V modell továbbra is helyesen osztályozza a képet, az R modell azonban helytelenül osztályozza.

Minden perturbációnak elég *kicsinek* kell lennie ahhoz, hogy nehéz legyen észrevenni. A kisebb perturbációk magasabb pontszámot érnek (lásd az 5. szakaszt). A perturbáció közvetlenül, pixelszinten kerül alkalmazásra az eredeti képre.

## 2. Nyilvános adatok

A feladathoz egy képhalmaz tartozik, amely két részre — `train` (100 kép) és
`test_public` (100 kép) — van felosztva; mindkettő változó felbontású képeket tartalmaz. Minden kép az ImageNet-1K 1000 osztályának valamelyikéből származik, és az R modell, valamint a V modell is 100%-os pontosságot ér el mindkét részhalmazon.

A következő fájlok állnak rendelkezésre:

```text
train/images/*.png         # 100 kép PNG formátumban
train/labels.json          # a 100 kép helyes címkéje (a korrekt osztály) 
test_public/images/*.png   # 100 kép PNG formátumban
test_public/labels.json    # a 100 kép helyes címkéje (a korrekt osztály) 
```

A kiértékelés során az Ön `dataset/test_public/` mappáját két másik (rejtett) képhalmazzal (`test_leaderboard_a` és `test_leaderboard_b`) helyettesítjük a hivatalos pontozáshoz. Mindkettő **100 képet** tartalmaz PNG formátumban, valamint egy-egy címkefájlt. 

**Megjegyzés: Ennél a feladatnál a tesztadatkészletek címkéi hozzáférhetők.**

## 3. Kimeneti formátum

Minden képhez két fájlt kell létrehoznia:

```text
{index}_a.pt   # A típusú (Type A) perturbáció
{index}_b.pt   # B típusú (Type B) perturbáció
```

- Az `{index}` (`0`, `1`, `2`, ...) megegyezik a kép adathalmazokban szereplő nevével.
- Minden fájl egyetlen, a `torch.save` használatával mentett tenzor. Az alakjának `3 x H x W` kell lennie, ahol `H` és `W` megegyezik az adott kép **eredeti** felbontásával (nem `224 x 224`-gyel).
- A kódnak csak egy ZIP-fájlt, a `submission.zip` fájlt kell létrehoznia. Az összes `.pt` fájlt a ZIP-archívum legfelső szintjén helyezze el, befoglaló mappa és alkönyvtárak nélkül. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

A notebook figyelmezteti Önt, ha  probléma adódik a kimeneti formátummal.

## 4. Korlátozások

- **Modellek:** A `torchvision.models.resnet18(pretrained=True)` és a `timm.create_model('vit_tiny_patch16_224', pretrained=True)` modelleket kell használnia. Más előtanított modell nem engedélyezett.
- **Transzformációs folyamat (a kiértékelés során kikényszerítve):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. Lásd a `baseline.ipynb` 3-ik szakaszát a részletekért. 
- **A perturbáció felbontása:** Meg kell egyeznie az **eredeti** nyers kép felbontásával (nem 224×224-gyel). A tenzort a transzformációs folyamat *előtt* adjuk hozzá a nyers képhez.
- **Kimeneti formátum:** Csak `.pt` fájlok — PNG/JPG nem . A tenzorokat hozzáadjuk a nyers képhez, és a pixelértékeket az előfeldolgozás előtt a `[0, 1]` tartományra korlátozzuk.
- **Fájlelnevezés:** Lapos (hierarchia nélküli) felsorolás, szigorú `{index}_a.pt` / `{index}_b.pt` formátumban. A zipen belül nem lehetnek alkönyvtárak.
- **Könyvtárak:** `torch`, `torchvision`, `timm`. 

## 5. Pontozás

A végső pontszámot a következőképpen számítjuk ki. Legyen `M` a részhalmazban lévő képek száma, $Score_A$ a sikeres A típusú perturbációk száma, $Score_B$ pedig a sikeres B típusú perturbációk száma:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

A PF egy olyan függvény, amelyet a nagy normájú perturbációk büntetésére terveztek, és amely nagyon érzékeny a teljesítmény felső határának közelében. Ez a 0.5 és 1 közötti tartományra van korlátozva. A teljes implementáció a `solution.ipynb`  8. szakaszában tekinthető meg. 

![kép](../curves.jpeg)
Ábra: A büntetőfüggvény görbéje.

## 6. A beadandó ellenőrzése

A notebook ellenőrzéseket tartalmaz, amelyek formázási problémák esetén figyelmeztetik Önt. Az ellenőrzés a `solution.ipynb` notebook 7. szakaszában található.

## 7. Helyi tesztelés

A `solution.ipynb` egy teljes, működő példát tartalmaz. Betölti a nyilvános adatokat, mindkét modellt és a hivatalos pontozót, valamint létrehoz egy beadandó ZIP-fájlt. Mielőtt elkezdené a munkát, olvassa el!

## 8. A beadás módja

- Mentse a módosításait a `solution.ipynb` fájlba!
- Nyissa meg a Git lapot a JupyterLab bal oldali oldalsávjában (tab)!
- Adja a staging area-hoz a `solution.ipynb` fájlt (a mellette lévő + ikonnal)!
- Írjon be egy commitüzenetet, majd kattintson a **Commit** gombra!
- Kattintson a felfelé mutató nyilat tartalmazó felhőikonra a push végrehajtásához!
- Térjen vissza erre a Contest oldalra, és kattintson a **Submit** gombra!

Pontosan egy darab, `solution.ipynb` nevű fájlt adjon be!
