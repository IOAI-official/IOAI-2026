# Pombiteer

- **Diggante waxtu:** 10 simili
- **Environment:** benn GPU (≈16 GB VRAM), internet amul
- **Dayob solution:** `solution.ipynb` ≤ 1 MB
- **Stockage:** 5 GB 

## Liggéey bi
 
Sa xarit digal la ngeen fo benn po bu ñuy seet baat.
Moom, muy àttekat bi, dina tànn benn baat bu làqu ci vocabulary bu ñu saxal, te war nga ko gis ci lu ëppul 30 tour.
Ci bépp tour, àttekat bi dina méngale ñaari baat, ba wax ban moo ci maana gën a jege
baat bi làqu. Po bu nekk dafay tàmbalee ci
paire bi ñu saxal `lamp vs potato`, ndaxte ñoom ñaar ñoo bokk ci mbir yi sa xarit gën a bëgg. Sa program bi dina
joxe benn baat bu bees. Baat bi raw ci méngale bi, dees koy denc
te méngale ko ak sa jooxe bi ci topp. 
Dinga daan po bi saa si nga joxee baat bi làqu ci anam wu dëppoo. Dëppale bi
case-insensitive la. Bépp baat boo joxe war na nekk ci `dataset/vocabulary.json`.

Am na misaal bu mat sëkk ci `solution.ipynb`, ànd ak protocol ak charger donnees yi. 
Mën nga soppi class PublicEmbeddingPlayer. Dees na initialise sa program bi benn yoon, mu fo po yépp ci benn doxal;
protocol bi dafay sos PublicEmbeddingPlayer bu bees ci njàlbéenug bépp po.

## Àttekat bi

Sa program bi dafay yónnee Àttekat bi benn objet JSON , Àttekat bi tontu ak benn objet JSON. 

Misaal bu baax, te ñu wone baat bi làqu ngir rekk leeral protocol bi:

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

Ñu ngi index tour yi dale ko ci 1 ba 30.

Tànneefi `verdict` yi ñooy `first`, maanaam word1 moo gën a jege, `second`, maanaam word2 moo gën a jege, walla
`same`, maanaam baat yépp ñoo yem ci ni ñu jege baat bi làqu. 

`winner_word` mooy baat bi ñuy denc ngir méngale gi ci topp. Su verdict bi dee `same`, baat bu njëkk bi dafay des.

## Dataset

Xajalé yépp dañuy bokk yii:

- `dataset/vocabulary.json` — 1602 baat yu bokkul te ñépp miniscule lañu. Baat bi làqu dafay nekk saa su nekk
  benn ci yii.
- `dataset/public_embeddings.npy` — `float32`, shape `(1602, 2560)`. Row `i`
  dafay méngoo ak baat `i` ci vocabulaire bi. Yii ay embedding *public* lañu;
  àttekat bi dafay jëfandikoo representation bu wuute te private.

Xajalé yi ay mbooloom baat yu làqu lañu:

| Xajalé | Baat yi | Tontu yi | Jëfandikoo ko ngir |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | doxal sa solution te xayma ko |
| `test_leaderboard_a` | 120 | làqu | classement buy dox |
| `test_leaderboard_b` | 120 | làqu | classement bu mujj |

Amul Xajale `train` — dara du nu ko jele ci ligne yu am label.

### Model yi ñu joxe

Ñaari pretrained embedding model dañu ànd ak liggéey bi te mën nañu leen jëfandikoo:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Dees na leen ñaar yépp charger ci seen chemin local; Hugging Face hub id bu mel ni
`"BAAI/bge-m3"` dafay déclencher telecharhement te du antu, ndax àtte bi amul internet. Bépp
dossier am na `example.py` bu mën a dox, biy wone wote bu amul internet.

Librarie yi am: `numpy`, `torch`, `sentence-transformers`. Internet amul, telecharment amul,
te yenen package amul.

## Génne gi

Dara. Liggéey bu interactive la: sa solution du bind fichier tontou; dafay jokkoo ak
àttekat bi jaarale ci stdin/stdout, ni ñu ko tëral ci kaw.

## Jooxe Score

Po bu ñu gis ci tour `t` dafay am score `1.0 - 0.02 × max(0, t - 10)`; po bu ñu saafaraagul
ci biir 30 tour dafay am score `0`. Kon tour 1–10 yi dañuy am score `1.00`, tour 20 dafay am score `0.80`, tour
30 dafay am score `0.60`.

Score sa liggéey mooy moyenne score po yi × 100, diggante `0.00` ak `100.00`.

Diggante 10 simili bi benn budget la buy mboole tambali, preparation ak po yépp 120
ci test set bi. 

## Naka lañuy yónnee

1. Ubbi `solution.ipynb`, soppi `PublicEmbeddingPlayer`, te doxal celluless yépp ngir wóor ne dafay dox.
2. Soo bëggee, seetal ko ci local: `python local_test.py solution.ipynb --limit 5`.
   Àttekat bu local bi dafay jëfandikoo embedding yu *public*, kon score bi
   ab tegtal rekk la.
3. Sauvegarder `solution.ipynb`.
4. Ubbi Git tab bi ci sidebar bu càmmooñu JupyterLab.
5. Def **Stage** `solution.ipynb` (natal **+** bi ci wetam).
6. Bind commit message, ba noppi bës ci **Commit**.
7. Bës ci niir bi ànd ak fitt buy jëm kaw ngir push.
8. Dellu ci xëtum Contest bii, te bës ci **Submit**, commit message bi war a méngoo ak bi nga joxe.

Yónne benn fichier rekk, turam di `solution.ipynb`, buy mboole bépp preparation ak inference bu war.
