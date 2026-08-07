# Robotjakt

- **Tidsgräns:** 5 minuter
- **Miljö:** en GPU (≈16 GB VRAM), ingen internetuppkoppling
- **Lösningens storlek:** `solution.ipynb` ≤ 1 MB
- **Lagring:** 5 GB

## Uppgift

Det finns sex robotar. Varje robot arbetar i ett litet rum som representeras av ett rutnät. Varje rum har ett spelbart område på `6×6` omgivet av väggar, så hela `image`-arrayen har storleken `8×8` (spelbart område + väggar).

Varje robot får en instruktion på engelska som beskriver en uppgift. Ögonblicksbilden kan vara tagen vid vilken tidpunkt som helst medan roboten utför den. Ditt mål är att förutsäga robotens nästa handling.

Robotarna följer inte alltid den kortaste vägen. Robot 0 kan bete sig annorlunda än Robot 1, men varje robot följer sitt eget konsekventa mönster. Använd träningsexemplen, som innehåller de korrekta nästa handlingarna, för att lära dig dessa mönster.

![Robot](../../robot.jpg)

Det finns tre typer av uppdrag:

- **gå till** ett objekt, till exempel `"approach the red ball"`;
- **plocka upp** ett objekt, till exempel `"grab the blue key"`;
- **placera ett objekt intill ett annat**, till exempel
  `"place the red box beside the green ball"`.

Samma instruktion kan formuleras på flera sätt. Testmängden kan innehålla nya kombinationer av bekanta fraser, färger och objekttyper. Varje ord, frasmönster, färg, objekttyp och uppdragstyp som används i testmängden förekommer dock även i träningsmängden.

Varje sampel har följande fält:

| Fält | Betydelse |
|---|---|
| `robot_id` | vilken av de 6 robotarna detta är (`0`–`5`) |
| `image` | rummet, en `8×8×2` heltalsarray där kanal 0 innehåller kategoriskt object_idx (t.ex. 1=empty, 2=wall, 10=robot) och kanal 1 innehåller kategoriskt colour_idx (0–5). |
| `direction` | riktningen som roboten just nu är vänd mot |
| `mission` | den synliga instruktionen i naturligt språk |
| `carrying` | `null` eller `[object_idx, colour_idx]` för det burna objektet |

Raderna är oberoende ögonblicksbilder i slumpmässig ordning. De utgör inte episoder, och ingen tidigare observation eller handling är tillgänglig vid utvärderingen.

Den medföljande `visualize_dataset.ipynb` låter dig granska de observationer som är tillgängliga för modellen i olika situationer.

## Rutnätskodning

`image[row][column] = [object_idx, colour_idx]`. Det första indexet är raden från topp till botten, och det andra är kolumnen från vänster till höger. Arrayen inkluderar den yttre väggkanten, så det navigerbara inre området är `6×6`.

Objekt-id:n:

| id | objekt |
|---:|---|
| 1 | tom ruta |
| 2 | vägg |
| 5 | nyckel |
| 6 | boll |
| 7 | låda |
| 10 | robot |
| 11 | token |

Tokens kan förekomma i rummet men nämns aldrig i uppdragen.

Färg-id:n är `0` röd, `1` grön, `2` blå, `3` lila, `4` gul och `5` grå. Färgkanalen har ingen betydelse för tomma rutor och väggar.

Bilden har endast de två kanalerna ovan. Robotens riktning ges en gång, i toppnivåfältet `direction`; den dupliceras inte inuti `image`.

## Handlingar

För koderna `0`–`3` använder förflyttningshandlingarna följande absoluta mappning:

| handling | betydelse |
|---:|---|
| 0 | flytta upp |
| 1 | flytta ner |
| 2 | flytta vänster |
| 3 | flytta höger |
| 4 | plocka upp |
| 5 | släpp |


Fältet `direction` anger den aktuella riktningen enligt: 0 = Upp (rad - 1), 1 = Ner (rad + 1), 2 = Vänster (kol - 1), 3 = Höger (kol + 1).

En förflyttningshandling vänder först roboten mot den absoluta riktningen och försöker sedan flytta den en ruta. En vägg eller ett objekt kan blockera förflyttningen, men riktningen ändras ändå. `pick up` och `drop` verkar uteslutande på den intilliggande målruta som definieras av riktningen (t.ex. om direction=0 verkar den på (rad - 1, kol)).

## Dataset

Du får två mappar:

| Mapp | Rader | `labels.json`? | Använd den för att |
|---|---:|---|---|
| `dataset/train/` | 60,000 | inkluderad | träna din modell |
| `dataset/test_public/` | 3,600 | inkluderad i utvecklingskopian | köra och själv poängsätta din pipeline |

Varje mapp innehåller `observations.json`, en JSON-lista med de sampel som beskrivs
ovan. `labels.json` är en motsvarande JSON-lista med handlingar (`0`–`5`).

Träningsmängden innehåller exakt 10,000 rader per robot och 20,000 rader från varje
uppgiftsfamilj. Det publika testet innehåller 600 rader per robot. Omslut `image` med
`numpy.asarray(...)` om du behöver en array.

Vid rättning ersätts `dataset/test_public/` transparent av en dold mängd med
3,600 observationer i samma format, men utan `labels.json`. Den publika
leaderboarden använder `test_leaderboard_a`; den slutliga rangordningen använder
`test_leaderboard_b`. En notebook som villkorslöst läser testetiketter kommer att misslyckas.
Läs etiketter endast från `dataset/train/`.

## Utdata

Skriv `predictions.json` i notebookens arbetskatalog. Den måste vara en JSON-lista
som innehåller en heltalshandling (`0`–`5`) per rad i
`dataset/test_public/observations.json`, i samma ordning. För en hypotetisk testmängd med sex sampel skulle en giltig utdata vara:

```json
[0, 3, 2, 2, 5, 4]
```

En saknad eller ogiltig JSON-fil, ett felaktigt antal förutsägelser, ett icke-heltalsvärde,
eller en handling utanför `{0,1,2,3,4,5}` avvisas utan poäng.

## Poängsättning

Poängsättningen är **genomsnittlig accuracy per robot** på skalan `0`–`100`. Accuracy beräknas
först oberoende för varje robot och medelvärdesbildas sedan över alla sex robotar. Varje
robot har därför lika vikt.

## Hur du lämnar in

1. Öppna `solution.ipynb` och kör alla celler.
2. Bekräfta att den skriver `predictions.json` med 3,600 förutsägelser för den publika
   testmängden.
3. Förbättra modellen om du vill; den medföljande baseline demonstrerar endast det
   nödvändiga in- och utdataformatet.
4. I JupyterLabs Git-flik, lägg till (stage) och committa `solution.ipynb`, och pusha den sedan.
5. Gå tillbaka till Contest-sidan och klicka på **Submit**.

Lämna in exakt en fil med namnet `solution.ipynb`.
