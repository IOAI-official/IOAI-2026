# Urmărirea roboților

- **Limită de timp:** 5 minute
- **Mediu:** un GPU (≈16 GB VRAM), fără internet
- **Dimensiunea soluției:** `solution.ipynb` ≤ 1 MB
- **Spațiu de stocare:** 5 GB 

## Sarcină

Există șase roboți. Fiecare robot operează într-o cameră mică reprezentată printr-o grilă. Fiecare cameră are o zonă accesibilă `6×6` înconjurată de pereți, astfel încât tabloul `image` complet are dimensiunea `8×8` (zona accesibilă + pereți).

Fiecare robot primește o instrucțiune în limba engleză care descrie o sarcină. Instantaneul poate fi realizat în orice moment în timp ce robotul o execută. Scopul dumneavoastră este să preziceți următoarea acțiune a robotului.

Roboții nu urmează întotdeauna calea cea mai scurtă. Robotul 0 se poate comporta diferit față de Robotul 1, dar fiecare robot își urmează propriul tipar consecvent. Folosiți exemplele de antrenare, care includ acțiunile următoare corecte, pentru a învăța aceste tipare.

![Robot](../../robot.jpg)

Există trei tipuri de misiuni:

- **deplasarea la** un obiect, de exemplu `"approach the red ball"`;
- **ridicarea** unui obiect, de exemplu `"grab the blue key"`;
- **așezarea unui obiect lângă altul**, de exemplu
  `"place the red box beside the green ball"`.

Aceeași instrucțiune poate fi formulată în mai multe moduri. Setul de testare poate conține combinații noi de expresii, culori și tipuri de obiecte cunoscute. Totuși, fiecare cuvânt, tipar de expresie, culoare, tip de obiect și tip de misiune utilizat în setul de testare apare și în setul de antrenare.

Fiecare eșantion are următoarele câmpuri:

| Câmp | Semnificație |
|---|---|
| `robot_id` | care dintre cei 6 roboți este acesta (`0`–`5`) |
| `image` | camera, un tablou de numere întregi `8×8×2` în care canalul 0 conține object_idx categorial (de exemplu, 1=celulă goală, 2=perete, 10=robot), iar canalul 1 conține colour_idx categorial (0–5). |
| `direction` | direcția spre care este orientat în prezent robotul |
| `mission` | instrucțiunea vizibilă în limbaj natural |
| `carrying` | `null` sau `[object_idx, colour_idx]` pentru obiectul transportat |

Rândurile sunt instantanee independente, într-o ordine aleatoare. Ele nu formează episoade, iar la momentul evaluării nu este disponibilă nicio observație sau acțiune anterioară.

Fișierul `visualize_dataset.ipynb` furnizat vă permite să inspectați observațiile disponibile modelului în diferite situații.

## Codificarea grilei

`image[row][column] = [object_idx, colour_idx]`. Primul indice reprezintă rândul de sus în jos, iar al doilea reprezintă coloana de la stânga la dreapta. Tabloul include marginea exterioară formată din pereți, astfel încât interiorul navigabil este `6×6`.

ID-urile obiectelor:

| id | obiect |
|---:|---|
| 1 | celulă goală |
| 2 | perete |
| 5 | cheie |
| 6 | minge |
| 7 | cutie |
| 10 | robot |
| 11 | token |

În cameră pot apărea tokeni, dar aceștia nu sunt niciodată menționați în misiuni.

ID-urile culorilor sunt `0` roșu, `1` verde, `2` albastru, `3` violet, `4` galben și `5` gri. Canalul de culoare nu are nicio semnificație pentru celulele goale și pereți.

Imaginea are doar cele două canale de mai sus. Direcția robotului este furnizată o singură dată, în câmpul `direction` de nivel superior; aceasta nu este duplicată în `image`.

## Acțiuni

Pentru codurile `0`–`3`, acțiunile de deplasare utilizează următoarea corespondență absolută:

| acțiune | semnificație |
|---:|---|
| 0 | deplasare în sus |
| 1 | deplasare în jos |
| 2 | deplasare la stânga |
| 3 | deplasare la dreapta |
| 4 | ridicare |
| 5 | lăsare |


Câmpul `direction` indică orientarea curentă folosind: 0 = Sus (rând - 1), 1 = Jos (rând + 1), 2 = Stânga (coloană - 1), 3 = Dreapta (coloană + 1).

O acțiune de deplasare întoarce mai întâi robotul în direcția absolută respectivă și apoi încearcă să îl deplaseze cu o celulă. Un perete sau un obiect poate bloca deplasarea, dar direcția se schimbă totuși. `pick up` și `drop` acționează exclusiv asupra celulei-țintă adiacente definite de direcție (de exemplu, dacă direction=0, acționează asupra (row - 1, col)).

## Dataset

Primiți două foldere:

| Folder | Rânduri | `labels.json`? | Folosiți-l pentru a |
|---|---:|---|---|
| `dataset/train/` | 60,000 | inclus | vă antrena modelul |
| `dataset/test_public/` | 3,600 | inclus în copia de dezvoltare | rula și autoevalua pipeline-ul |

Fiecare folder conține `observations.json`, o listă JSON cu eșantioanele descrise
mai sus. `labels.json` este o listă JSON aliniată de acțiuni (`0`–`5`).

Setul de antrenare conține exact 10,000 de rânduri per robot și 20,000 de rânduri din fiecare
familie de sarcini. Setul public de testare conține 600 de rânduri per robot. Încapsulați `image` cu
`numpy.asarray(...)` dacă aveți nevoie de un tablou.

La evaluare, `dataset/test_public/` este înlocuit în mod transparent cu un set ascuns de
3,600 de observații în același format, dar fără `labels.json`. Clasamentul
public utilizează `test_leaderboard_a`; clasamentul final utilizează
`test_leaderboard_b`. Un notebook care citește necondiționat etichetele de testare va eșua.
Citiți etichetele numai din `dataset/train/`.

## Ieșire

Scrieți `predictions.json` în directorul de lucru al notebook-ului. Acesta trebuie să fie o listă
JSON care conține câte o acțiune întreagă (`0`–`5`) pentru fiecare rând din
`dataset/test_public/observations.json`, în aceeași ordine. Pentru un set de testare ipotetic care conține șase eșantioane, o ieșire validă ar fi:

```json
[0, 3, 2, 2, 5, 4]
```

Un fișier JSON lipsă sau nevalid, un număr greșit de predicții, o valoare care nu este întreagă
sau o acțiune din afara `{0,1,2,3,4,5}` este respinsă fără punctaj.

## Punctare

Punctajul este **acuratețea medie per robot** pe o scară `0`–`100`. Acuratețea este mai întâi
calculată independent pentru fiecare robot, apoi se face media pentru toți cei șase roboți. Prin urmare,
fiecare robot are aceeași pondere.

## Cum să trimiteți soluția

1. Deschideți `solution.ipynb` și rulați toate celulele.
2. Confirmați că acesta scrie `predictions.json` cu 3,600 de predicții pentru setul
   public de testare.
3. Îmbunătățiți modelul dacă doriți; baseline-ul furnizat demonstrează doar
   formatul necesar pentru intrare și ieșire.
4. În fila Git din JupyterLab, adăugați în staging și faceți commit pentru `solution.ipynb`, apoi faceți push.
5. Reveniți la pagina concursului și faceți clic pe **Trimiteți**.

Trimiteți exact un fișier numit `solution.ipynb`.
