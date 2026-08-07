# Potjera robota

- **Vremensko ograničenje:** 5 minuta
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Prostor za pohranu:** 5 GB 

## Zadatak

Postoji šest robota. Svaki robot djeluje u maloj prostoriji predstavljenoj mrežom. Svaka prostorija ima igrivo područje veličine `6×6` okruženo zidovima, pa cijelo polje `image` ima veličinu `8×8` (igrivo područje + zidovi).

Svaki robot dobiva uputu na engleskom jeziku koja opisuje zadatak. Snimka može biti napravljena u bilo kojem trenutku dok ga robot izvršava. Vaš je cilj predvidjeti sljedeću radnju robota.

Roboti ne slijede uvijek najkraći put. Robot 0 može se ponašati drukčije od Robota 1, ali svaki robot slijedi vlastiti dosljedan obrazac. Upotrijebite primjere za treniranje, koji uključuju točne sljedeće radnje, kako biste naučili te obrasce.

![Robot](../../robot.jpg)

Postoje tri vrste misija:

- **otići do** objekta, na primjer `"approach the red ball"`;
- **podići** objekt, na primjer `"grab the blue key"`;
- **staviti jedan objekt pokraj drugoga**, na primjer
  `"place the red box beside the green ball"`.

Ista uputa može biti napisana na nekoliko načina. Testni skup može sadržavati nove kombinacije poznatih fraza, boja i vrsta objekata. Međutim, svaka riječ, obrazac fraze, boja, vrsta objekta i vrsta misije upotrijebljena u testnom skupu pojavljuje se i u skupu za treniranje.

Svaki uzorak ima sljedeća polja:

| Polje | Značenje |
|---|---|
| `robot_id` | koji je ovo od 6 robota (`0`–`5`) |
| `image` | prostorija, cjelobrojno polje `8×8×2` u kojem kanal 0 sadržava kategorijski object_idx (npr. 1=prazno, 2=zid, 10=robot), a kanal 1 sadržava kategorijski colour_idx (0–5). |
| `direction` | smjer u kojem je robot trenutačno okrenut |
| `mission` | vidljiva uputa na prirodnom jeziku |
| `carrying` | `null` ili `[object_idx, colour_idx]` za objekt koji robot nosi |

Redci su neovisne snimke poredane nasumičnim redoslijedom. Ne tvore epizode, a tijekom evaluacije nije dostupno nijedno prethodno opažanje ni radnja.

Priloženi `visualize_dataset.ipynb` omogućuje vam pregled opažanja dostupnih modelu u različitim situacijama.

## Kodiranje mreže

`image[row][column] = [object_idx, colour_idx]`. Prvi indeks označava redak odozgo prema dolje, a drugi stupac slijeva nadesno. Polje uključuje vanjski rub od zidova, pa je unutrašnjost kojom se može kretati `6×6`.

Identifikatori objekata:

| id | objekt |
|---:|---|
| 1 | prazno polje |
| 2 | zid |
| 5 | ključ |
| 6 | lopta |
| 7 | kutija |
| 10 | robot |
| 11 | žeton |

Žetoni se mogu pojaviti u prostoriji, ali nikada nisu navedeni u misijama.

Identifikatori boja jesu `0` crvena, `1` zelena, `2` plava, `3` ljubičasta, `4` žuta i `5` siva. Kanal boje nema značenje za prazna polja i zidove.

Slika ima samo dva prethodno navedena kanala. Smjer robota naveden je jednom, u polju `direction` najviše razine; nije dupliciran unutar `image`.

## Radnje

Za kodove `0`–`3` radnje kretanja koriste sljedeće apsolutno preslikavanje:

| radnja | značenje |
|---:|---|
| 0 | pomakni se gore |
| 1 | pomakni se dolje |
| 2 | pomakni se ulijevo |
| 3 | pomakni se udesno |
| 4 | podigni |
| 5 | spusti |


Polje `direction` označava trenutačnu orijentaciju pomoću: 0 = gore (row - 1), 1 = dolje (row + 1), 2 = lijevo (col - 1), 3 = desno (col + 1).

Radnja kretanja najprije okreće robota u taj apsolutni smjer, a zatim ga pokušava pomaknuti za jedno polje. Zid ili objekt može spriječiti pomicanje, ali smjer se svejedno mijenja. `pick up` i `drop` djeluju isključivo na susjedno ciljno polje određeno smjerom (npr. ako je direction=0, djeluju na (row - 1, col)).

## Dataset

Dobivate dvije mape:

| Mapa | Redci | `labels.json`? | Upotrijebite je za |
|---|---:|---|---|
| `dataset/train/` | 60,000 | uključeno | treniranje svojeg modela |
| `dataset/test_public/` | 3,600 | uključeno u razvojnu kopiju | pokretanje i samostalno bodovanje svojeg sustava |

Svaka mapa sadržava `observations.json`, JSON popis prethodno opisanih uzoraka.
`labels.json` je poravnati JSON popis radnji (`0`–`5`).

Skup za treniranje sadržava točno 10,000 redaka po robotu i 20,000 redaka iz svake
porodice zadataka. Javni testni skup sadržava 600 redaka po robotu. Omotajte `image` s
`numpy.asarray(...)` ako vam je potrebno polje.

Tijekom ocjenjivanja `dataset/test_public/` neprimjetno se zamjenjuje skrivenim skupom od
3,600 opažanja u istom formatu, ali bez `labels.json`. Javna
ljestvica poretka koristi `test_leaderboard_a`; konačni poredak koristi
`test_leaderboard_b`. Bilježnica koja bezuvjetno čita oznake testnog skupa neće uspjeti.
Oznake čitajte samo iz `dataset/train/`.

## Izlaz

Zapišite `predictions.json` u radni direktorij bilježnice. To mora biti JSON
popis koji sadržava jednu cjelobrojnu radnju (`0`–`5`) po retku
`dataset/test_public/observations.json`, istim redoslijedom. Za hipotetski testni skup koji sadržava šest uzoraka valjani bi izlaz bio:

```json
[0, 3, 2, 2, 5, 4]
```

JSON datoteka koja nedostaje ili nije valjana, pogrešan broj predviđanja, vrijednost koja nije cijeli broj
ili radnja izvan `{0,1,2,3,4,5}` odbacuje se bez bodova.

## Bodovanje

Bodovanje je **srednja točnost po robotu** na ljestvici `0`–`100`. Točnost se najprije
izračunava neovisno za svakog robota, a zatim se računa prosjek za svih šest robota. Stoga svaki
robot ima jednaku težinu.

## Kako predati rješenje

1. Otvorite `solution.ipynb` i pokrenite sve ćelije.
2. Potvrdite da zapisuje `predictions.json` s 3,600 predviđanja za javni
   testni skup.
3. Poboljšajte model ako želite; priloženi baseline samo prikazuje
   potrebni format ulaza i izlaza.
4. U kartici Git u JupyterLabu dodajte u pripremno područje i zabilježite `solution.ipynb`, a zatim ga pošaljite na udaljeni repozitorij.
5. Vratite se na stranicu natjecanja i kliknite **Predaj**.

Predajte točno jednu datoteku naziva `solution.ipynb`.
