# Potjera robota

- **Vremensko ograničenje:** 5 minutes
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Prostor za pohranu:** 5 GB 

## Zadatak

Postoji šest robota. Svaki robot djeluje u maloj prostoriji predstavljenoj mrežom. Svaka prostorija ima `6×6` područje za igru okruženo zidovima, tako da puni `image` niz ima veličinu `8×8` (područje za igru + zidovi).

Svaki robot dobija instrukciju na engleskom jeziku koja opisuje zadatak. Snimak stanja može biti napravljen u bilo kojem trenutku dok ga robot izvršava. Vaš cilj je predvidjeti sljedeću akciju robota.

Roboti ne slijede uvijek najkraći put. Robot 0 može se ponašati drugačije od Robota 1, ali svaki robot slijedi vlastiti dosljedan obrazac. Koristite primjere za treniranje, koji uključuju tačne sljedeće akcije, kako biste naučili te obrasce.

![Robot](../robot.jpg)

Postoje tri vrste misija:

- **otići do** predmeta, na primjer `"approach the red ball"`;
- **pokupiti** predmet, na primjer `"grab the blue key"`;
- **staviti jedan predmet pored drugog**, na primjer
  `"place the red box beside the green ball"`.

Ista instrukcija može biti napisana na nekoliko načina. Testni skup može sadržavati nove kombinacije poznatih izraza, boja i vrsta predmeta. Međutim, svaka riječ, obrazac izraza, boja, vrsta predmeta i vrsta misije korištena u testnom skupu također se pojavljuje u skupu za treniranje.

Svaki uzorak ima sljedeća polja:

| Polje | Značenje |
|---|---|
| `robot_id` | koji je ovo od 6 robota (`0`–`5`) |
| `image` | prostorija, `8×8×2` cjelobrojni niz u kojem kanal 0 sadrži kategorički object_idx (npr. 1=prazno, 2=zid, 10=robot), a kanal 1 sadrži kategorički colour_idx (0–5). |
| `direction` | smjer u kojem je robot trenutno okrenut |
| `mission` | vidljiva instrukcija na prirodnom jeziku |
| `carrying` | `null` ili `[object_idx, colour_idx]` za predmet koji robot nosi |

Redovi su nezavisni snimci stanja poredani nasumičnim redoslijedom. Oni ne čine epizode i tokom evaluacije nije dostupno nijedno prethodno opažanje niti akcija.

Dostavljeni `visualize_dataset.ipynb` omogućava vam da pregledate opažanja dostupna modelu u različitim situacijama.

## Kodiranje mreže

`image[row][column] = [object_idx, colour_idx]`. Prvi indeks predstavlja red odozgo prema dolje, a drugi kolonu slijeva nadesno. Niz uključuje vanjski rub od zidova, pa je unutrašnjost kojom se može kretati `6×6`.

ID-jevi predmeta:

| id | predmet |
|---:|---|
| 1 | prazno polje |
| 2 | zid |
| 5 | ključ |
| 6 | lopta |
| 7 | kutija |
| 10 | robot |
| 11 | token |

Tokeni se mogu pojaviti u prostoriji, ali se nikada ne navode u misijama.

ID-jevi boja su `0` crvena, `1` zelena, `2` plava, `3` ljubičasta, `4` žuta i `5` siva. Kanal boje nema značenje za prazna polja i zidove.

Slika ima samo dva prethodno navedena kanala. Smjer robota naveden je jednom, u polju `direction` najvišeg nivoa; nije dupliciran unutar `image`.

## Akcije

Za kodove `0`–`3`, akcije kretanja koriste sljedeće apsolutno mapiranje:

| akcija | značenje |
|---:|---|
| 0 | pomjeri se gore |
| 1 | pomjeri se dolje |
| 2 | pomjeri se lijevo |
| 3 | pomjeri se desno |
| 4 | pokupi |
| 5 | odloži |


Polje `direction` označava trenutnu orijentaciju koristeći: 0 = Gore (red - 1), 1 = Dolje (red + 1), 2 = Lijevo (kolona - 1), 3 = Desno (kolona + 1).

Akcija kretanja prvo okreće robota u taj apsolutni smjer, a zatim ga pokušava pomjeriti za jedno polje. Zid ili predmet može blokirati kretanje, ali se smjer ipak mijenja. `pick up` i `drop` djeluju isključivo na susjedno ciljno polje određeno smjerom (npr. ako je direction=0, djeluje na (red - 1, kolona)).

## Dataset

Dobijate dvije fascikle:

| Fascikla | Redovi | `labels.json`? | Koristite je za |
|---|---:|---|---|
| `dataset/train/` | 60,000 | uključeno | treniranje modela |
| `dataset/test_public/` | 3,600 | uključeno u razvojnu kopiju | pokretanje i samostalno ocjenjivanje vašeg pipelinea |

Svaka fascikla sadrži `observations.json`, JSON listu prethodno opisanih uzoraka.
`labels.json` je poravnata JSON lista akcija (`0`–`5`).

Skup za treniranje sadrži tačno 10,000 redova po robotu i 20,000 redova iz svake
porodice zadataka. Javni test sadrži 600 redova po robotu. Obuhvatite `image` funkcijom
`numpy.asarray(...)` ako vam je potreban niz.

U vrijeme ocjenjivanja, `dataset/test_public/` se transparentno zamjenjuje skrivenim skupom od
3,600 opažanja u istom formatu, ali bez `labels.json`. Javna
rang-lista koristi `test_leaderboard_a`; konačni poredak koristi
`test_leaderboard_b`. Notebook koji bezuslovno čita oznake testa neće uspjeti.
Čitajte oznake samo iz `dataset/train/`.

## Izlaz

Zapišite `predictions.json` u radni direktorij notebooka. To mora biti JSON
lista koja sadrži jednu cjelobrojnu akciju (`0`–`5`) po redu
`dataset/test_public/observations.json`, istim redoslijedom. Za hipotetički testni skup koji sadrži šest uzoraka, ispravan izlaz bio bi:

```json
[0, 3, 2, 2, 5, 4]
```

Nedostajuća ili neispravna JSON datoteka, pogrešan broj predikcija, vrijednost koja nije cijeli broj
ili akcija izvan `{0,1,2,3,4,5}` odbacuje se bez dodjele rezultata.

## Bodovanje

Bodovanje predstavlja **srednju tačnost po robotu** na skali `0`–`100`. Tačnost se prvo
izračunava nezavisno za svakog robota, a zatim se uzima prosjek za svih šest robota. Stoga svaki
robot ima jednaku težinu.

## Kako predati rješenje

1. Otvorite `solution.ipynb` i pokrenite sve ćelije.
2. Potvrdite da zapisuje `predictions.json` sa 3,600 predikcija za javni
   testni skup.
3. Poboljšajte model ako želite; dostavljeni baseline samo demonstrira
   zahtijevani format ulaza i izlaza.
4. U Git kartici JupyterLaba označite `solution.ipynb` za commit i napravite commit, a zatim ga pošaljite.
5. Vratite se na stranicu takmičenja i kliknite **Predaj**.

Predajte tačno jednu datoteku nazvanu `solution.ipynb`.
