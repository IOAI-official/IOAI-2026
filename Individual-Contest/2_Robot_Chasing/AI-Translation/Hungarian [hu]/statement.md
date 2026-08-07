# Robotüldözés

- **Időkorlát:** 5 minutes
- **Környezet:** egy GPU (≈16 GB VRAM), internet nélkül
- **A megoldás mérete:** `solution.ipynb` ≤ 1 MB
- **Tárhely:** 5 GB 

## Feladat

Hat robot van. Mindegyik robot egy rácsként ábrázolt kis szobában működik. Minden szobának van egy falakkal körülvett `6×6` méretű játékterülete, így a teljes `image` tömb mérete `8×8` (játéktér + falak).

Mindegyik robot kap egy angol nyelvű utasítást, amely leír egy feladatot. A pillanatfelvétel a feladat végrehajtásának bármely pontján készülhet. Az Ön célja a robot következő műveletének előrejelzése.

A robotok nem mindig a legrövidebb útvonalat követik. A 0. robot viselkedhet másként, mint az 1. robot, de mindegyik robot a saját következetes mintáját követi. E minták megtanulásához használja a helyes következő műveleteket is tartalmazó tanítási példákat.

![Robot](../../robot.jpg)

Háromféle küldetés létezik:

- **menjen oda** egy tárgyhoz, például `"approach the red ball"`;
- **vegyen fel** egy tárgyat, például `"grab the blue key"`;
- **helyezzen egy tárgyat egy másik mellé**, például
  `"place the red box beside the green ball"`.

Ugyanaz az utasítás többféleképpen is megfogalmazható. A teszthalmaz ismert kifejezések, színek és tárgytípusok új kombinációit tartalmazhatja. A teszthalmazban használt minden szó, kifejezésminta, szín, tárgytípus és küldetéstípus azonban a tanítási halmazban is előfordul.

Minden minta a következő mezőket tartalmazza:

| Mező | Jelentés |
|---|---|
| `robot_id` | a 6 robot közül melyikről van szó (`0`–`5`) |
| `image` | a szoba, egy `8×8×2` méretű egészértékű tömb, amelyben a 0. csatorna a kategorikus object_idx értéket (pl. 1=üres, 2=fal, 10=robot), az 1. csatorna pedig a kategorikus colour_idx értéket (0–5) tartalmazza. |
| `direction` | az irány, amerre a robot jelenleg néz |
| `mission` | a látható természetes nyelvű utasítás |
| `carrying` | `null` vagy `[object_idx, colour_idx]` a hordozott tárgyhoz |

A sorok véletlenszerű sorrendű, egymástól független pillanatfelvételek. Nem alkotnak epizódokat, és a kiértékeléskor nem áll rendelkezésre korábbi megfigyelés vagy művelet.

A mellékelt `visualize_dataset.ipynb` segítségével megvizsgálhatja a modell számára különböző helyzetekben elérhető megfigyeléseket.

## A rács kódolása

`image[row][column] = [object_idx, colour_idx]`. Az első index a felülről lefelé számozott sor, a második pedig a balról jobbra számozott oszlop. A tömb tartalmazza a külső falszegélyt, ezért a bejárható belső terület `6×6` méretű.

Tárgyazonosítók:

| id | tárgy |
|---:|---|
| 1 | üres mező |
| 2 | fal |
| 5 | kulcs |
| 6 | labda |
| 7 | doboz |
| 10 | robot |
| 11 | token |

A szobában előfordulhatnak tokenek, de a küldetések soha nem nevezik meg őket.

A színazonosítók: `0` piros, `1` zöld, `2` kék, `3` lila, `4` sárga és `5` szürke. A színcsatornának nincs jelentése az üres mezők és a falak esetében.

A kép csak a fenti két csatornát tartalmazza. A robot iránya egyszer, a legfelső szintű `direction` mezőben van megadva; a `image` belsejében nincs megismételve.

## Műveletek

A `0`–`3` kódok esetében a mozgási műveletek a következő abszolút leképezést használják:

| művelet | jelentés |
|---:|---|
| 0 | mozgás felfelé |
| 1 | mozgás lefelé |
| 2 | mozgás balra |
| 3 | mozgás jobbra |
| 4 | felvétel |
| 5 | lerakás |


A `direction` mező a jelenlegi nézési irányt a következőképpen jelöli: 0 = fel (row - 1), 1 = le (row + 1), 2 = balra (col - 1), 3 = jobbra (col + 1).

Egy mozgási művelet először az adott abszolút irányba fordítja a robotot, majd megpróbálja egy mezővel elmozdítani. Egy fal vagy tárgy megakadályozhatja a mozgást, de az irány ekkor is megváltozik. A `pick up` és a `drop` kizárólag az irány által meghatározott szomszédos célmezőn hajt végre műveletet (pl. ha direction=0, akkor a (row - 1, col) mezőn).

## Adathalmaz

Két mappát kap:

| Mappa | Sorok | `labels.json`? | Felhasználás |
|---|---:|---|---|
| `dataset/train/` | 60,000 | mellékelve | a modell tanítása |
| `dataset/test_public/` | 3,600 | a fejlesztési példányban mellékelve | a folyamat futtatása és önálló pontozása |

Mindegyik mappa tartalmazza a `observations.json` fájlt, amely a fent leírt minták JSON-listája.
A `labels.json` a műveletek (`0`–`5`) hozzáigazított JSON-listája.

A tanítási halmaz robotonként pontosan 10,000 sort és minden
feladatcsaládból 20,000 sort tartalmaz. A nyilvános teszthalmaz robotonként 600 sort tartalmaz. Ha tömbre van szüksége, foglalja a `image` értéket
`numpy.asarray(...)` kifejezésbe.

A pontozáskor a `dataset/test_public/` átlátható módon egy ugyanilyen formátumú,
3,600 megfigyelést tartalmazó rejtett halmazra cserélődik, de `labels.json` nélkül. A nyilvános
ranglista a `test_leaderboard_a` értéket használja; a végső rangsor a
`test_leaderboard_b` értéket használja. A tesztcímkéket feltétel nélkül beolvasó notebook hibát fog jelezni.
Címkéket csak a `dataset/train/` helyről olvasson be.

## Kimenet

Írja ki a `predictions.json` fájlt a notebook munkakönyvtárába. Ennek egy olyan JSON-
listának kell lennie, amely a `dataset/test_public/observations.json` minden sorához ugyanabban a sorrendben egy egész értékű műveletet (`0`–`5`) tartalmaz.
Egy hat mintát tartalmazó hipotetikus teszthalmaz esetén egy érvényes kimenet a következő lenne:

```json
[0, 3, 2, 2, 5, 4]
```

A hiányzó vagy érvénytelen JSON-fájlt, a helytelenszámú előrejelzést, a nem egész értéket,
illetve a `{0,1,2,3,4,5}` tartományon kívüli műveletet pontszám nélkül elutasítjuk.

## Pontozás

A pontszám a **robotonkénti pontosság átlaga** egy `0`–`100` skálán. A pontosságot először
mindegyik robotra külön számítjuk ki, majd átlagoljuk mind a hat robotra. Ezért minden
robot azonos súlyú.

## Beküldés

1. Nyissa meg a `solution.ipynb` fájlt, és futtassa az összes cellát.
2. Ellenőrizze, hogy létrehozza a `predictions.json` fájlt a nyilvános
   teszthalmazhoz tartozó 3,600 előrejelzéssel.
3. Ha szeretné, javítsa a modellt; a mellékelt baseline csak a
   szükséges bemeneti és kimeneti formátumot szemlélteti.
4. A JupyterLab Git lapján adja a stage-hez, majd commitolja a `solution.ipynb` fájlt, ezután pusholja.
5. Térjen vissza a verseny oldalára, és kattintson a **Beküldés** gombra.

Pontosan egy `solution.ipynb` nevű fájlt küldjön be.
