# Mašīnas spoks

- **Laika ierobežojums:** 10 minūtes
- **Bāzlīnijas (baseline) rezultāts:** 28.6
- **Zinātniskās komitejas rezultāts:** 93.41
- **Vide:** viens GPU (≈16 GB VRAM), nav interneta
- **Risinājuma izmērs:** `solution.ipynb` ≤ 20 MB
- **Krātuve:** 5 GB
- **Iepriekš apmācītie modeļi:** tikai **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — teksta **kodētājs** (embedding modelis).


## Uzdevums

Kazahstānas Nacionālajā arhīvā notiek dīvainas lietas. Bibliotekāri stāsta, ka dažas grāmatas agrāk beidzās citādi, taču neviens to nevar pierādīt — visi eksemplāri ir vienādi, un katrs stāsts joprojām ir loģisks. Jūs esat aicināts kā AI pētnieks atrast izmaiņas.
![Spoks](../../ghost.jpg)

Fragments sākas kā cilvēka rakstīts teksts un kādā brīdī klusi pārslēdzas
uz valodas modeļa ģenerētu turpinājumu. Lasot to kā vienotu veselumu, tas izskatās kā
viens saskanīgs teksts — taču kaut kur vidū autors mainās no cilvēka
uz mašīnu. Jūsu uzdevums ir **atrast šo pārslēgšanos: rakstzīmes indeksu, kur beidzas
cilvēka daļa un sākas mašīnas daļa**.

Katrs paraugs ir viena virkne `text`. Ir tieši viena robeža. Viss,
kas atrodas pirms tās, ir cilvēka veidots; viss, sākot no tās, ir mašīnas ģenerēts.

## Datu kopa

Vienkārša teksta fragmenti angļu valodā, katram viena robeža.

- **A daļa** (pirms robežas): cilvēka rakstīta teksta izvilkums.
- **B daļa** (no robežas tālāk): valodas modeļa radīts turpinājums,
  kas nosacīts ar A daļu.
- Katra puse ir vismaz 180 vārdu gara; kopējais garums ir ~500–800 vārdu.
- **`boundary_char_index`** ir rakstzīmju nobīde, kurā beidzas A daļa:
  `text[:boundary_char_index]` ir cilvēka daļa un
  `text[boundary_char_index:].lstrip()` ir mašīnas daļa.

#### Ko jūs saņemat

Jūs saņemat **divas mapes**:

| Mape | Paraugi | `answers.jsonl`? | Izmantojiet to, lai |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ iekļauts | apmācītu / veiktu fine-tuning savai metodei |
| `dataset/test_public/`  | 380   | ✅ iekļauts (izstrādes kopija) | palaistu savu pipeline un lokāli pašnovērtētu rezultātu |

**Vērtēšanas laikā** jūsu `dataset/test_public/` mape tiek **aizstāta ar slēptu
vērtēšanas kopu**. Tai ir tāds pats formāts, bet **bez `answers.jsonl`**. Jūsu
notebook tiek atkārtoti palaists uz tās, un tā radītais `answers.jsonl` tiek novērtēts.

- Publiskais leaderboard izmanto slēptu **test_leaderboard_a** kopu (380 paraugi).

- Gala ranžējums izmanto slēptu **test_leaderboard_b** kopu (380 paraugi).

Visas trīs vērtēšanas
kopas ir vienāda izmēra un iegūtas no tā paša sadalījuma kā `train`, tāpēc jūsu lokālais
`dataset/test_public/` rezultāts ir saprātīgs novērtējums jūsu leaderboard rezultātam.

#### Formāts diskā

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- Id vērtības failā `answers.jsonl` atbilst id vērtībām failā `data.jsonl`.
- `dataset/train/` (ar atbildēm) ir pieejams vienmēr, kad apmācāt vai veicat fine-tuning.

## Izvade (iesniegšanas formāts)

Jūs iesniedzat **vienu notebook, kuram jābūt nosauktam `solution.ipynb`**. Šis precīzais faila nosaukums ir obligāts. Jebkas cits tiek atteikts, to nemaz nepalaižot.

Jūsu notebook ir **jānolasa `dataset/test_public/data.jsonl`** un jāizveido viens fails
**`answers.jsonl`** repozitorija saknē — viens JSON objekts katrā rindā, kas
katram parauga id piekārto jūsu prognozēto robežas rakstzīmes indeksu:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` jābūt **veselam skaitlim diapazonā `[0, len(text)]`**.
- Katram id no `dataset/test_public/data.jsonl` jāparādās tieši vienu reizi. Paraugs, kas nav atrodams
  failā `answers.jsonl` (vai kuram ir vērtība, kas nav vesels skaitlis / ir ārpus diapazona), saņem 0
  punktus par šo paraugu.

## Vērtēšana

Katram paraugam lai `p` ir jūsu prognozētais indekss un `t` — patiesā robeža. Katra parauga rezultāts eksponenciāli samazinās atkarībā no rakstzīmju attāluma:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Tas rada šādu rezultāta uzvedību:
- **=1.0** — precīza robežas rakstzīme;
- **≈0.78** — 25 rakstzīmju nobīde; - **≈0.61** — 50 rakstzīmju nobīde;
- **≈0.37** — 100 rakstzīmju nobīde;
- **≈0.01** — 500 rakstzīmju nobīde.

**Gala rezultāts ir vidējais** no katra parauga rezultātiem visos šī sadalījuma paraugos
(uzrādīts 0–100 skalā). Metrika atalgo par *tuvu* atbildi, ne tikai par precīzu.

## Ierobežojumi

- **Vide:** viens GPU (≈16 GB VRAM), vērtēšanas laikā nav interneta — atļautais
  modelis (zemāk) jau ir nodrošināts. **Reālā laika (wall-clock) budžets: 10 minūtes** visam
  izpildījumam — tam jāietver jebkāda apmācība / fine-tuning, ko veicat vērtēšanas laikā,
  **plus** inference uz vērtēšanas kopas.
- **Atļautais iepriekš apmācītais modelis** — šis saraksts ir izsmeļošs; nekādi citi iepriekš apmācīti svari
  nedrīkst tikt izmantoti. Tas ir **iepriekš nodrošināts vidē** (ielādējiet to parastā veidā, piemēram,
  `from_pretrained`; vērtēšanas laikā nav interneta):
  - **bge-base-en-v1.5** — teksta **kodētājs** (embedding modelis) ar 110M parametriem. Tas
    veido teikumu/fragmentu embeddings; tas nav ģeneratīvs valodas modelis. Jūs
    varat to izmantot **tādu, kāds tas ir (iesaldētas pazīmes), vai veikt tam fine-tuning uz `train` sadalījuma**
    (pilns fine-tuning iekļaujas 16 GB / 10 minūšu budžetā).
- Klasiskie / statistiskie rīki nav ierobežoti: jūs varat veidot jebkādu uz pazīmēm balstītu
  modeli (piemēram, scikit-learn klasifikatorus vai regresorus) virs embedding pazīmēm, kuras
  aprēķināt paši. *Iepriekš apmācīti dziļās mašīnmācīšanās svari* ir ierobežoti tikai ar iepriekš minēto sarakstu.

## Bāzlīnija

Dotais `solution.ipynb` ir triviāla atsauce: tas no `dataset/train/` novērtē vienu
"vidējo robežas daļu" un katram testa fragmentam prognozē to pašu
garuma daļu. Tas iegūst **28.6** uz slēptā
**test_leaderboard_a** sadalījuma un pastāv tikai kā palaižama veidne
lasīt-`dataset/test_public/` → rakstīt-`answers.jsonl` ciklam.

**Zinātniskās komitejas rezultāts 93.41**, mērīts uz tā paša sadalījuma un ar tādu pašu
10 minūšu budžetu, ir iegūts, veicot atļautā kodētāja fine-tuning uz `train` un nosakot
pārslēgšanos kā izmaiņu punktu (changepoint) pār teikumiem. Tā nav augšējā robeža — šīs metrikas
maksimums ir 100.
