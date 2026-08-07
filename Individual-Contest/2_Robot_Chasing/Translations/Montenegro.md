# Potjera robota

- **Vremensko ograničenje:** 5 minuta
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Prostor za skladištenje:** 5 GB 

## Zadatak

Postoji šest robota. Svaki robot radi u maloj prostoriji predstavljenoj mrežom. Svaka prostorija ima `6×6` područje za igru okruženo zidovima, tako da puni niz `image` ima veličinu `8×8` (područje za igru + zidovi).

Svaki robot dobija uputstvo na engleskom jeziku koje opisuje zadatak. Snimak može biti napravljen u bilo kom trenutku dok ga robot izvršava. Vaš cilj je da predvidite sljedeću akciju robota.

Roboti ne prate uvijek najkraću putanju. Robot 0 može se ponašati drugačije od Robota 1, ali svaki robot prati sopstveni dosljedan obrazac. Upotrijebite primjere za treniranje, koji uključuju tačne sljedeće akcije, kako biste naučili ove obrasce.

![Robot](../robot.jpg)

Postoje tri vrste misija:

- **idi do** objekta, na primjer `"approach the red ball"`;
- **podigni** objekat, na primjer `"grab the blue key"`;
- **stavi jedan objekat pored drugog**, na primjer
  `"place the red box beside the green ball"`.

Isto uputstvo može biti napisano na nekoliko načina. Testni skup može sadržati nove kombinacije poznatih fraza, boja i vrsta objekata. Međutim, svaka riječ, obrazac fraze, boja, vrsta objekta i vrsta misije korišćena u testnom skupu takođe se pojavljuje u skupu za treniranje.

Svaki uzorak ima sljedeća polja:

| Polje | Značenje |
|---|---|
| `robot_id` | koji je ovo od 6 robota (`0`–`5`) |
| `image` | prostorija, cjelobrojni niz `8×8×2` u kojem kanal 0 sadrži kategorički object_idx (npr. 1=empty, 2=wall, 10=robot), a kanal 1 sadrži kategorički colour_idx (0–5). |
| `direction` | smjer u kojem je robot trenutno okrenut |
| `mission` | vidljivo uputstvo na prirodnom jeziku |
| `carrying` | `null` ili `[object_idx, colour_idx]` za objekat koji robot nosi |

Redovi su nezavisni snimci u nasumičnom redosljedu. Oni ne čine epizode i tokom evaluacije nije dostupno nijedno prethodno opažanje niti akcija.

Obezbijeđeni `visualize_dataset.ipynb` omogućava vam da pregledate opažanja dostupna modelu u različitim situacijama.

## Kodiranje mreže

`image[row][column] = [object_idx, colour_idx]`. Prvi indeks je red odozgo prema dolje, a drugi je kolona slijeva nadesno. Niz uključuje spoljašnji rub od zidova, tako da je unutrašnjost kroz koju se može kretati `6×6`.

ID-jevi objekata:

| id | objekat |
|---:|---|
| 1 | prazno polje |
| 2 | zid |
| 5 | ključ |
| 6 | lopta |
| 7 | kutija |
| 10 | robot |
| 11 | token |

Tokeni se mogu pojaviti u prostoriji, ali se nikada ne imenuju u misijama.

ID-jevi boja su `0` crvena, `1` zelena, `2` plava, `3` ljubičasta, `4` žuta i `5` siva. Kanal boje nema značenje za prazna polja i zidove.

Slika ima samo dva prethodno navedena kanala. Smjer robota naveden je jednom, u polju najvišeg nivoa `direction`; nije dupliran unutar `image`.

## Akcije

Za kodove `0`–`3`, akcije kretanja koriste sljedeće apsolutno mapiranje:

| akcija | značenje |
|---:|---|
| 0 | pomjeri se gore |
| 1 | pomjeri se dolje |
| 2 | pomjeri se lijevo |
| 3 | pomjeri se desno |
| 4 | podigni |
| 5 | ispusti |


Polje `direction` označava trenutnu orijentaciju koristeći: 0 = Gore (row - 1), 1 = Dolje (row + 1), 2 = Lijevo (col - 1), 3 = Desno (col + 1).

Akcija kretanja prvo okreće robota u taj apsolutni smjer, a zatim pokušava da ga pomjeri za jedno polje. Zid ili objekat može blokirati pomjeranje, ali se smjer ipak mijenja. `pick up` i `drop` djeluju isključivo na susjedno ciljno polje određeno smjerom (npr. ako je direction=0, djeluje na (row - 1, col)).

## Dataset

Dobijate dva foldera:

| Folder | Redovi | `labels.json`? | Koristite ga za |
|---|---:|---|---|
| `dataset/train/` | 60,000 | uključeno | treniranje modela |
| `dataset/test_public/` | 3,600 | uključeno u razvojnu kopiju | pokretanje i samostalno ocjenjivanje vašeg pipeline-a |

Svaki folder sadrži `observations.json`, JSON listu prethodno opisanih uzoraka.
`labels.json` je poravnata JSON lista akcija (`0`–`5`).

Skup za treniranje sadrži tačno 10,000 redova po robotu i 20,000 redova iz svake
porodice zadataka. Javni test sadrži 600 redova po robotu. Obuhvatite `image` sa
`numpy.asarray(...)` ako vam je potreban niz.

Tokom ocjenjivanja, `dataset/test_public/` se transparentno zamjenjuje skrivenim skupom od
3,600 opažanja u istom formatu, ali bez `labels.json`. Javna
rang-lista koristi `test_leaderboard_a`; konačno rangiranje koristi
`test_leaderboard_b`. Notebook koji bezuslovno učitava oznake testa neće uspjeti.
Učitavajte oznake samo iz `dataset/train/`.

## Izlaz

Upišite `predictions.json` u radni direktorijum notebook-a. To mora biti JSON
lista koja sadrži jednu cjelobrojnu akciju (`0`–`5`) po redu
`dataset/test_public/observations.json`, istim redosljedom. Za hipotetički testni skup koji sadrži šest uzoraka, ispravan izlaz bio bi:

```json
[0, 3, 2, 2, 5, 4]
```

JSON fajl koji nedostaje ili nije ispravan, pogrešan broj predikcija, vrijednost koja nije cijeli broj
ili akcija izvan `{0,1,2,3,4,5}` odbacuju se bez dodjeljivanja rezultata.

## Bodovanje

Bodovanje je **srednja tačnost po robotu** na skali `0`–`100`. Tačnost se prvo
izračunava nezavisno za svakog robota, a zatim se računa prosjek za svih šest robota. Svaki
robot stoga ima jednaku težinu.

## Kako predati rješenje

1. Otvorite `solution.ipynb` i pokrenite sve ćelije.
2. Potvrdite da upisuje `predictions.json` sa 3,600 predikcija za javni
   testni skup.
3. Poboljšajte model ako želite; obezbijeđeni baseline samo demonstrira
   zahtijevani format ulaza i izlaza.
4. U JupyterLab Git kartici, pripremite i commit-ujte `solution.ipynb`, a zatim ga push-ujte.
5. Vratite se na stranicu Contest i kliknite na **Submit**.

Predajte tačno jedan fajl pod nazivom `solution.ipynb`.
