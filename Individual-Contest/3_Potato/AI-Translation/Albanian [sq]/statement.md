# Patatja

- **Kufiri kohor:** 10 minuta
- **Mjedisi:** një GPU (≈16 GB VRAM), pa internet
- **Madhësia e zgjidhjes:** `solution.ipynb` ≤ 1 MB
- **Hapësira ruajtëse:** 5 GB 

## Detyra
 
Miku juaj sugjeron të luani një lojë hamendësimi.
Ai, në rolin e gjykatësit, zgjedh një fjalë të fshehtë nga një fjalor fiks dhe ju duhet ta gjeni atë në jo më shumë se 30 raunde.
Në çdo raund, gjykatësi krahason dy fjalë dhe raporton se cila është semantikisht më e afërt me
fjalën e fshehtë. Çdo lojë fillon me
çiftin fiks `lamp vs potato`, sepse ato janë dy nga gjërat e preferuara të mikut tuaj. Më pas, programi juaj
propozon një fjalë të re. Fituesi i krahasimit mbahet
dhe krahasohet me propozimin tuaj të radhës. 
Ju e fitoni lojën në çastin kur propozoni saktësisht fjalën e fshehtë. Krahasimi nuk dallon
shkronjat e mëdha nga ato të vogla. Çdo fjalë që propozoni duhet të jetë në `dataset/vocabulary.json`.

Ka një shembull të plotë në `solution.ipynb` me protokollin dhe ngarkimin e të dhënave. 
Mund ta ndryshoni klasën PublicEmbeddingPlayer. Programi juaj inicializohet një herë dhe i luan të gjitha lojërat në një ekzekutim të vetëm;
protokolli krijon një PublicEmbeddingPlayer të ri në fillim të çdo loje.

## Gjykatësi

Programi juaj i dërgon një objekt JSON Gjykatësit dhe Gjykatësi përgjigjet me një objekt JSON. 

Një shembull i zgjidhur, ku fjala e fshehtë tregohet vetëm për të shpjeguar protokollin:

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

Raundet indeksohen nga 1 deri në 30.

Opsionet e `verdict` janë `first`, që do të thotë se word1 është më afër, `second`, që do të thotë se word2 është më afër, ose
`same`, që do të thotë se të dyja fjalët janë njëlloj afër fjalës së fshehtë. 

`winner_word` është fjala që mbahet për krahasimin e radhës. Në rast të një vendimi `same`, fjala e parë mbetet.

## Dataset-i

Të përbashkëta për çdo ndarje:

- `dataset/vocabulary.json` — 1602 fjalë unike me shkronja të vogla. Fjala e fshehtë është gjithmonë
  njëra prej tyre.
- `dataset/public_embeddings.npy` — `float32`, me formë `(1602, 2560)`. Rreshti `i`
  i korrespondon fjalës `i` në fjalor. Këto janë embedding-e *publike*;
  gjykatësi përdor një paraqitje tjetër, private.

Ndarjet janë bashkësi fjalësh të fshehta:

| Ndarja | Fjalët | Përgjigjet | Përdoreni për të |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | ekzekutuar zgjidhjen tuaj dhe llogaritur vetë rezultatin |
| `test_leaderboard_a` | 120 | të fshehura | renditjen e drejtpërdrejtë |
| `test_leaderboard_b` | 120 | të fshehura | renditjen përfundimtare |

Nuk ka ndarje `train` — asgjë nuk përshtatet nga rreshtat e etiketuar.

### Modelet e ofruara

Me detyrën ofrohen dy modele embedding të paratrajnuara, të cilat mund të përdoren:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Të dyja duhet të ngarkohen nga shtegu i tyre lokal; një identifikues i Hugging Face hub, si
`"BAAI/bge-m3"`, shkakton një shkarkim dhe dështon, sepse vlerësimi kryhet offline. Çdo
direktori përmban një `example.py` të ekzekutueshëm që tregon thirrjen offline.

Bibliotekat e disponueshme: `numpy`, `torch`, `sentence-transformers`. Pa internet, pa
shkarkime, pa paketa të tjera.

## Dalja

Asnjë. Kjo është një detyrë interaktive: zgjidhja juaj nuk shkruan skedar përgjigjeje; ajo komunikon me
gjykatësin përmes stdin/stdout siç përshkruhet më sipër.

## Metrika

Një lojë e zgjidhur në raundin `t` merr `1.0 - 0.02 × max(0, t - 10)` pikë; një lojë që nuk zgjidhet
brenda 30 raundeve merr `0` pikë. Pra, raundet 1–10 marrin `1.00` pikë, raundi 20 merr `0.80` pikë, ndërsa raundi
30 merr `0.60` pikë.

Rezultati juaj për detyrën është rezultati mesatar i lojërave × 100, midis `0.00` dhe `100.00`.

Kufiri prej 10 minutash është një buxhet i vetëm që mbulon nisjen, përgatitjen dhe të gjitha 120
lojërat në bashkësinë e testimit. 

## Si të dorëzoni

1. Hapni `solution.ipynb`, redaktoni `PublicEmbeddingPlayer` dhe ekzekutoni të gjitha qelizat për t'u siguruar se funksionon.
2. Nëse dëshironi, kontrollojeni lokalisht: `python local_test.py solution.ipynb --limit 5`.
   Gjykatësi lokal përdor embedding-et *publike*, prandaj rezultati i tij është
   vetëm orientues.
3. Ruani `solution.ipynb`.
4. Hapni skedën Git në shiritin anësor të majtë të JupyterLab.
5. Vendosni në staging `solution.ipynb` (ikona **+** pranë tij).
6. Shkruani një mesazh commit-i dhe klikoni Commit.
7. Klikoni renë me shigjetë lart për të kryer push.
8. Kthehuni në këtë faqe të Konkursit dhe klikoni Submit, me mesazhin e commit-it që përputhet me atë që keni dhënë.

Dorëzoni saktësisht një skedar, me emrin `solution.ipynb`, që përfshin çdo përgatitje dhe inferencë të nevojshme.
