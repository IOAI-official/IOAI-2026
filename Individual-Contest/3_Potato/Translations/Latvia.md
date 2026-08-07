# Potato

- **Laika ierobežojums:** 10 minūtes
- **Vide:** viens GPU (≈16 GB VRAM), nav interneta
- **Risinājuma izmērs:** `solution.ipynb` ≤ 1 MB
- **Krātuve:** 5 GB 

## Uzdevums
 
Jūsu draugs ierosina spēlēt minēšanas spēli.
Viņš kā tiesnesis izvēlas vienu slēptu vārdu no fiksētas vārdnīcas, un jums tas jāatrod ne vairāk kā 30 gājienos.
Katrā gājienā tiesnesis salīdzina divus vārdus un ziņo, kurš no tiem ir semantiski tuvāks
slēptajam vārdam. Katra spēle sākas ar
fiksēto pāri `lamp vs potato`, jo tās ir divas no jūsu drauga mīļākajām lietām. Pēc tam jūsu programma
piedāvā vienu jaunu vārdu. Salīdzinājuma uzvarētājs tiek saglabāts un
salīdzināts ar jūsu nākamo piedāvājumu. 
Jūs uzvarat spēlē tajā mirklī, kad piedāvājat tieši slēpto vārdu. Salīdzināšana
neņem vērā burtu reģistru. Katram jūsu piedāvātajam vārdam jābūt `dataset/vocabulary.json`.

Pilns piemērs ar protokolu un datu ielādi ir `solution.ipynb`. 
Jūs varat mainīt klasi PublicEmbeddingPlayer. Jūsu programma tiek inicializēta vienu reizi un izspēlē katru spēli vienā izpildē;
protokols katras spēles sākumā izveido jaunu PublicEmbeddingPlayer.

## Tiesnesis

Jūsu programma nosūta tiesnesim vienu JSON objektu, un tiesnesis atbild ar vienu JSON objektu. 

Izstrādāts piemērs, kurā slēptais vārds ir parādīts tikai tāpēc, lai paskaidrotu protokolu:

```text
Hidden word: shovel          Fixed opening: lamp vs potato

<- {"turn": 1, "winner_word": "potato", "verdict": "second", "word1": "lamp",   "word2": "potato"}
-> {"new_word": "rock"}
<- {"turn": 2, "winner_word": "rock",   "verdict": "second", "word1": "potato", "word2": "rock"}
-> {"new_word": "hammer"}
<- {"turn": 3, "winner_word": "hammer", "verdict": "second", "word1": "rock",   "word2": "hammer"}
-> {"new_word": "shovel"}                                    <- matches: game won
-> {"status": "win"}
```

Gājieni ir numurēti no 1 līdz 30.

`verdict` iespējamās vērtības ir `first`, kas nozīmē, ka word1 ir tuvāks, `second`, kas nozīmē, ka word2 ir tuvāks, vai
`same`, kas nozīmē, ka abi vārdi ir vienlīdz tuvi slēptajam vārdam. 

`winner_word` ir vārds, kas tiek saglabāts nākamajam salīdzinājumam. `same` verdikta gadījumā paliek pirmais vārds.

## Datu kopa

Kopīgs visiem sadalījumiem (split):

- `dataset/vocabulary.json` — 1602 unikāli vārdi ar mazajiem burtiem. Slēptais vārds vienmēr ir
  viens no tiem.
- `dataset/public_embeddings.npy` — `float32`, forma `(1602, 2560)`. Rinda `i`
  atbilst vārdam `i` vārdnīcā. Šie ir *publiskie* embeddings;
  tiesnesis izmanto citu, privātu reprezentāciju.

Sadalījumi ir slēpto vārdu kopas:

| Sadalījums | Vārdi | Atbildes | Izmantojiet, lai |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | palaistu savu risinājumu un pašnovērtētu rezultātu |
| `test_leaderboard_a` | 120 | slēptas | tiešraides rezultātu tabula (leaderboard) |
| `test_leaderboard_b` | 120 | slēptas | galīgais ranžējums |

`train` sadalījuma nav — nekas netiek pielāgots no marķētām rindām.

### Nodrošinātie modeļi

Kopā ar uzdevumu tiek piegādāti divi iepriekš apmācīti embedding modeļi, kurus drīkst izmantot:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Abi ir jāielādē no to lokālā ceļa; Hugging Face hub id, piemēram,
`"BAAI/bge-m3"`, izraisa lejupielādi un neizdodas, jo vērtēšana notiek bezsaistē. Katrs
katalogs satur izpildāmu `example.py`, kas parāda bezsaistes izsaukumu.

Pieejamās bibliotēkas: `numpy`, `torch`, `sentence-transformers`. Nav interneta, nav
lejupielāžu, nav citu pakotņu.

## Izvade

Nav. Šis ir interaktīvs uzdevums: jūsu risinājums neraksta atbilžu failu; tas sazinās ar
tiesnesi caur stdin/stdout, kā aprakstīts iepriekš.

## Metrika

Spēle, kurā vārds atrasts gājienā `t`, saņem `1.0 - 0.02 × max(0, t - 10)`; spēle, kas nav atrisināta
30 gājienos, saņem `0`. Tātad gājieni 1–10 dod `1.00`, 20. gājiens dod `0.80`, 30.
gājiens dod `0.60`.

Jūsu uzdevuma rezultāts ir vidējais spēles rezultāts × 100, robežās no `0.00` līdz `100.00`.

10 minūšu ierobežojums ir vienots budžets, kas ietver startēšanu, sagatavošanu un visas 120
spēles testa kopā. 

## Kā iesniegt

1. Atveriet `solution.ipynb`, rediģējiet `PublicEmbeddingPlayer` un izpildiet visas šūnas, lai pārliecinātos, ka tas darbojas.
2. (Neobligāti) pārbaudiet to lokāli: `python local_test.py solution.ipynb --limit 5`.
   Lokālais tiesnesis izmanto *publiskos* embeddings, tāpēc tā rezultāts ir
   tikai orientējošs.
3. Saglabājiet `solution.ipynb`.
4. Atveriet Git cilni JupyterLab kreisajā sānjoslā.
5. Sagatavojiet (stage) `solution.ipynb` (**+** ikona tam blakus).
6. Ievadiet commit ziņojumu un noklikšķiniet uz Commit.
7. Noklikšķiniet uz mākoņa ar augšupvērstu bultu, lai veiktu push.
8. Atgriezieties šajā Contest lapā un noklikšķiniet uz Submit, norādot commit ziņojumu, kas atbilst tam, kuru esat sniedzis.

Iesniedziet tieši vienu failu ar nosaukumu `solution.ipynb`, kas ietver visas nepieciešamās sagatavošanās darbības un inferenci.
