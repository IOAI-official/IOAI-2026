# Robotachtervolging

- **Tijdslimiet:** 5 minuten
- **Omgeving:** één GPU (≈16 GB VRAM), geen internet
- **Grootte van de oplossing:** `solution.ipynb` ≤ 1 MB
- **Opslagruimte:** 5 GB 

## Opdracht

Er zijn zes robots. Elke robot werkt in een kleine kamer die wordt weergegeven door een raster. Elke kamer heeft een `6×6` speelbaar gebied dat door muren wordt omringd, waardoor de volledige `image`-array een grootte van `8×8` heeft (speelbaar gebied + muren).

Elke robot ontvangt een Engelstalige instructie die een taak beschrijft. De momentopname kan op elk willekeurig moment worden gemaakt terwijl de robot deze uitvoert. Je doel is de volgende actie van de robot te voorspellen.

Robots volgen niet altijd het kortste pad. Robot 0 kan zich anders gedragen dan Robot 1, maar elke robot volgt zijn eigen consistente patroon. Gebruik de trainingsvoorbeelden, die de correcte volgende acties bevatten, om deze patronen te leren.

![Robot](../../robot.jpg)

Er zijn drie soorten missies:

- **ga naar** een object, bijvoorbeeld `"approach the red ball"`;
- **pak** een object **op**, bijvoorbeeld `"grab the blue key"`;
- **plaats één object naast een ander**, bijvoorbeeld
  `"place the red box beside the green ball"`.

Dezelfde instructie kan op verschillende manieren worden geschreven. De testset kan nieuwe combinaties van bekende formuleringen, kleuren en objecttypen bevatten. Elk woord, elk formuleringspatroon, elke kleur, elk objecttype en elk missietype dat in de testset wordt gebruikt, komt echter ook voor in de trainingsset.

Elk sample heeft de volgende velden:

| Veld | Betekenis |
|---|---|
| `robot_id` | om welke van de 6 robots het gaat (`0`–`5`) |
| `image` | de kamer, een `8×8×2`-integer-array waarin kanaal 0 de categorische object_idx bevat (bijv. 1=leeg, 2=muur, 10=robot) en kanaal 1 de categorische colour_idx bevat (0–5). |
| `direction` | de richting waarin de robot momenteel kijkt |
| `mission` | de zichtbare instructie in natuurlijke taal |
| `carrying` | `null` of `[object_idx, colour_idx]` voor het meegedragen object |

Rijen zijn onafhankelijke momentopnamen in willekeurige volgorde. Ze vormen geen episodes en tijdens de evaluatie is geen eerdere observatie of actie beschikbaar.

Met de meegeleverde `visualize_dataset.ipynb` kun je de observaties bekijken die in verschillende situaties voor het model beschikbaar zijn.

## Rastercodering

`image[row][column] = [object_idx, colour_idx]`. De eerste index is de rij van boven naar beneden en de tweede is de kolom van links naar rechts. De array bevat de buitenste rand van muren, waardoor het navigeerbare binnengebied `6×6` is.

Object-id's:

| id | object |
|---:|---|
| 1 | lege cel |
| 2 | muur |
| 5 | sleutel |
| 6 | bal |
| 7 | doos |
| 10 | robot |
| 11 | token |

Tokens kunnen in de kamer voorkomen, maar worden nooit in missies genoemd.

De kleur-id's zijn `0` rood, `1` groen, `2` blauw, `3` paars, `4` geel en `5` grijs. Het kleurkanaal heeft geen betekenis voor lege cellen en muren.

De afbeelding heeft uitsluitend de twee bovenstaande kanalen. De richting van de robot wordt eenmaal opgegeven in het `direction`-veld op het hoogste niveau; deze wordt niet gedupliceerd binnen `image`.

## Acties

Voor codes `0`–`3` gebruiken bewegingsacties de volgende absolute toewijzing:

| actie | betekenis |
|---:|---|
| 0 | beweeg omhoog |
| 1 | beweeg omlaag |
| 2 | beweeg naar links |
| 3 | beweeg naar rechts |
| 4 | pak op |
| 5 | zet neer |


Het `direction`-veld geeft de huidige kijkrichting aan met: 0 = Omhoog (row - 1), 1 = Omlaag (row + 1), 2 = Links (col - 1), 3 = Rechts (col + 1).

Een bewegingsactie draait de robot eerst naar die absolute richting en probeert hem vervolgens één cel te verplaatsen. Een muur of object kan de beweging blokkeren, maar de richting verandert desondanks. `pick up` en `drop` voeren hun actie uitsluitend uit op de aangrenzende doelcel die door de richting wordt bepaald (bijv. als direction=0, wordt de actie uitgevoerd op (row - 1, col)).

## Dataset

Je ontvangt twee mappen:

| Map | Rijen | `labels.json`? | Gebruik deze om |
|---|---:|---|---|
| `dataset/train/` | 60,000 | inbegrepen | je model te trainen |
| `dataset/test_public/` | 3,600 | inbegrepen in de ontwikkelkopie | je pipeline uit te voeren en zelf te scoren |

Elke map bevat `observations.json`, een JSON-lijst van de hierboven beschreven samples.
`labels.json` is een overeenkomstige JSON-lijst van acties (`0`–`5`).

De trainingsset bevat precies 10,000 rijen per robot en 20,000 rijen uit elke
taakfamilie. De openbare testset bevat 600 rijen per robot. Omhul `image` met
`numpy.asarray(...)` als je een array nodig hebt.

Tijdens de beoordeling wordt `dataset/test_public/` op transparante wijze vervangen door een verborgen set van
3,600 observaties in dezelfde indeling, maar zonder `labels.json`. Het openbare
leaderboard gebruikt `test_leaderboard_a`; de eindrangschikking gebruikt
`test_leaderboard_b`. Een notebook dat onvoorwaardelijk testlabels inleest, zal mislukken.
Lees labels uitsluitend uit `dataset/train/`.

## Uitvoer

Schrijf `predictions.json` naar de werkmap van het notebook. Dit moet een JSON-
lijst zijn die voor elke rij van `dataset/test_public/observations.json` één actie als geheel getal (`0`–`5`) bevat,
in dezelfde volgorde. Voor een hypothetische testset met zes samples zou dit geldige uitvoer zijn:

```json
[0, 3, 2, 2, 5, 4]
```

Een ontbrekend of ongeldig JSON-bestand, een verkeerd aantal voorspellingen, een niet-gehele waarde
of een actie buiten `{0,1,2,3,4,5}` wordt zonder score afgewezen.

## Scoring

De score is de **gemiddelde nauwkeurigheid per robot** op een schaal van `0`–`100`. De nauwkeurigheid wordt eerst
onafhankelijk voor elke robot berekend en vervolgens gemiddeld over alle zes robots. Elke
robot heeft daarom hetzelfde gewicht.

## Indienen

1. Open `solution.ipynb` en voer alle cellen uit.
2. Controleer of dit `predictions.json` met 3,600 voorspellingen voor de openbare
   testset schrijft.
3. Verbeter het model als je wilt; de meegeleverde baseline demonstreert alleen de
   vereiste invoer- en uitvoerindeling.
4. Stage en commit `solution.ipynb` in het tabblad Git van JupyterLab en push het vervolgens.
5. Ga terug naar de wedstrijdpagina en klik op **Indienen**.

Dien precies één bestand met de naam `solution.ipynb` in.
