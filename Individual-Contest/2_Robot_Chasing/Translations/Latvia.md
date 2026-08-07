# Robotu izsekošana

- **Laika ierobežojums:** 5 minūtes
- **Vide:** viens GPU (≈16 GB VRAM), bez interneta
- **Risinājuma izmērs:** `solution.ipynb` ≤ 1 MB
- **Krātuve:** 5 GB

## Uzdevums

Ir seši roboti. Katrs robots darbojas nelielā telpā, kas attēlota kā režģis. Katrai telpai ir `6×6` spēlējamais laukums, ko ieskauj sienas, tāpēc pilnajam `image` masīvam ir izmērs `8×8` (spēlējamais laukums + sienas).

Katrs robots saņem instrukciju angļu valodā, kas apraksta uzdevumu. Momentuzņēmums var būt uzņemts jebkurā brīdī, kamēr robots to izpilda. Jūsu mērķis ir prognozēt robota nākamo darbību.

Roboti ne vienmēr izvēlas īsāko ceļu. Robots 0 var uzvesties citādi nekā Robots 1, taču katrs robots ievēro savu konsekventu likumsakarību. Izmantojiet apmācības piemērus, kas ietver pareizās nākamās darbības, lai apgūtu šīs likumsakarības.

![Robots](../robot.jpg)

Ir trīs misiju veidi:

- **doties uz** objektu, piemēram, `"approach the red ball"`;
- **pacelt** objektu, piemēram, `"grab the blue key"`;
- **nolikt vienu objektu blakus citam**, piemēram,
  `"place the red box beside the green ball"`.

Vienu un to pašu instrukciju var uzrakstīt vairākos veidos. Testa kopa var saturēt jaunas pazīstamu frāžu, krāsu un objektu tipu kombinācijas. Tomēr katrs vārds, frāzes veidne, krāsa, objekta tips un misijas veids, kas izmantots testa kopā, parādās arī apmācības kopā.

Katram paraugam ir šādi lauki:

| Lauks | Nozīme |
|---|---|
| `robot_id` | kurš no 6 robotiem tas ir (`0`–`5`) |
| `image` | telpa — `8×8×2` veselu skaitļu masīvs, kur kanāls 0 satur kategorisku object_idx (piem., 1=empty, 2=wall, 10=robot) un kanāls 1 satur kategorisku colour_idx (0–5). |
| `direction` | virziens, kurā robots šobrīd ir pagriezts |
| `mission` | redzamā dabiskās valodas instrukcija |
| `carrying` | `null` vai `[object_idx, colour_idx]` nestajam objektam |

Rindas ir neatkarīgi momentuzņēmumi nejaušā secībā. Tās neveido epizodes, un vērtēšanas laikā nav pieejams neviens iepriekšējs novērojums vai darbība.

Piedāvātais `visualize_dataset.ipynb` ļauj apskatīt novērojumus, kas modelim pieejami dažādās situācijās.

## Režģa kodējums

`image[row][column] = [object_idx, colour_idx]`. Pirmais indekss ir rinda no augšas uz leju, bet otrais — kolonna no kreisās uz labo. Masīvs ietver ārējo sienu apmali, tāpēc pārvietošanai pieejamā iekšpuse ir `6×6`.

Objektu id:

| id | objekts | meaning |
|---:|---|---|
| 1 | tukša šūna | empty cell |
| 2 | siena | wall |
| 5 | atslēga | key |
| 6 | bumba | ball |
| 7 | kaste | box |
| 10 | robots | robot |
| 11 | tokens | token |

Tokeni var atrasties telpā, taču misijās tie nekad netiek nosaukti.

Krāsu id ir `0` sarkans, `1` zaļš, `2` zils, `3` violets, `4` dzeltens un `5` pelēks. Krāsas kanālam nav nozīmes tukšām šūnām un sienām.

Attēlam ir tikai divi iepriekš minētie kanāli. Robota virziens tiek norādīts vienu reizi — augšējā līmeņa laukā `direction`; tas nav dublēts `image` iekšienē.

## Darbības

Kodiem `0`–`3` kustības darbības izmanto šādu absolūto attēlojumu:

| darbība | nozīme | meaning |
|---:|---|---|
| 0 | kustība augšup | move up |
| 1 | kustība lejup | move down |
| 2 | kustība pa kreisi | move left |
| 3 | kustība pa labi | move right |
| 4 | pacelt | pick up |
| 5 | nomest | drop |

Lauks `direction` norāda pašreizējo pagriešanās virzienu, izmantojot: 0 = Augšup (row - 1), 1 = Lejup (row + 1), 2 = Pa kreisi (col - 1), 3 = Pa labi (col + 1).

Kustības darbība vispirms pagriež robotu uz šo absolūto virzienu un pēc tam mēģina to pārvietot par vienu šūnu. Siena vai objekts var bloķēt kustību, bet virziens tomēr mainās. `pacelt` un `nomest` darbojas tikai ar blakus esošo mērķa šūnu, ko nosaka direction (piem., ja direction=0, tā darbojas ar (row - 1, col)).

## Datu kopa

Jūs saņemat divas mapes:

| Mape | Rindas | `labels.json`? | Izmantojiet, lai |
|---|---:|---|---|
| `dataset/train/` | 60,000 | iekļauts | apmācītu savu modeli |
| `dataset/test_public/` | 3,600 | iekļauts izstrādes kopijā | palaistu un pašnovērtētu savu pipeline |

Katra mape satur `observations.json` — JSON sarakstu ar iepriekš aprakstītajiem paraugiem.
`labels.json` ir tam atbilstoši sakārtots JSON saraksts ar darbībām (`0`–`5`).

Apmācības kopa satur tieši 10,000 rindas katram robotam un 20,000 rindas no katras
uzdevumu saimes. Publiskā testa kopa satur 600 rindas katram robotam. Ietiniet `image` ar
`numpy.asarray(...)`, ja jums nepieciešams masīvs.

Vērtēšanas laikā `dataset/test_public/` tiek nemanāmi aizstāta ar slēptu kopu, kurā ir
3,600 novērojumi tādā pašā formātā, taču bez `labels.json`. Publiskā
rezultātu tabula izmanto `test_leaderboard_a`; galīgais vērtējums izmanto
`test_leaderboard_b`. Notebook, kas beznosacījumu veidā nolasa testa etiķetes (labels), neizdosies.
Nolasiet etiķetes tikai no `dataset/train/`.

## Izvade

Ierakstiet `predictions.json` notebook darba direktorijā. Tam jābūt JSON
sarakstam, kas satur vienu veselu skaitli — darbību (`0`–`5`) — katrai
`dataset/test_public/observations.json` rindai tādā pašā secībā. Hipotētiskai testa kopai, kas satur sešus paraugus, derīga izvade būtu:

```json
[0, 3, 2, 2, 5, 4]
```

Trūkstošs vai nederīgs JSON fails, nepareizs prognožu skaits, vērtība, kas nav vesels skaitlis,
vai darbība ārpus `{0,1,2,3,4,5}` tiek atmesta bez vērtējuma.

## Vērtēšana

Vērtējums ir **vidējā precizitāte pa robotiem** skalā `0`–`100`. Precizitāte vispirms tiek
aprēķināta neatkarīgi katram robotam, pēc tam vidējota pa visiem sešiem robotiem. Tādējādi katram
robotam ir vienāds svars.

## Kā iesniegt

1. Atveriet `solution.ipynb` un izpildiet visas šūnas.
2. Pārliecinieties, ka tas ieraksta `predictions.json` ar 3,600 prognozēm publiskajai
   testa kopai.
3. Ja vēlaties, uzlabojiet modeli; piedāvātais baseline tikai demonstrē
   nepieciešamo ievades un izvades formātu.
4. JupyterLab Git cilnē pievienojiet (stage) un iekomitējiet `solution.ipynb`, pēc tam veiciet push.
5. Atgriezieties Contest lapā un noklikšķiniet **Submit**.

Iesniedziet tieši vienu failu ar nosaukumu `solution.ipynb`.
