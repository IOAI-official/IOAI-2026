# Toppante robot yi

- **Yàggay waxtu:** 5 minutes
- **Environment:** benn GPU (≈16 GB VRAM), internet amul
- **Dayob solution bi:** `solution.ipynb` ≤ 1 MB
- **Dencukaay:** 5 GB 

## Task bi

Am na juróom-benn robot. Robot bu nekk dafay dox ci néeg bu ndaw bu grid màndargaale. Néeg bu nekk am na ab `6×6` playable area bu miir yi wër, kon array `image` bi yépp dayobu `8×8` la (playable area + miir yi).

Robot bu nekk dafay jot ndigal ci English buy melal task bi. Snapshot bi mën nañu ko jël ci saa su nekk bi robot biy def task bi. Sa mébet mooy wax jëfu robot bi ci topp.

Robot yi duñu topp saa su nekk yoon wi gën a gàtt. Robot 0 mën na jëfe wuute ak Robot 1, waaye robot bu nekk dafay topp pattern bu moom te dëppoo. Jëfandikool training examples yi, yu ànd ak jëf yi jub ci topp, ngir jàng pattern yooyu.

![Robot](../robot.jpg)

Am na ñetti xeeti mission:

- **dem ci** ab object, ci misaal `"approach the red ball"`;
- **for** ab object, ci misaal `"grab the blue key"`;
- **teg benn object ci wetu beneen**, ci misaal
  `"place the red box beside the green ball"`.

Mën nañu bind benn ndigal ci ay anam yu bare. Test set bi mën na am ay boole yu bees ci phrase, colour ak xeeti object yi ñu xam. Waaye, baat bu nekk, pattern bu phrase bu nekk, colour bu nekk, xeetu object bu nekk ak xeetu mission bu nekk bi ñuy jëfandikoo ci test set bi, feeñ na itam ci training set bi.

Sample bu nekk am na field yii:

| Field | Tekki |
|---|---|
| `robot_id` | kan ci 6 robot yi la (`0`–`5`) |
| `image` | néeg bi, tableau integer `8×8×2` bu channel 0 yor categorical object_idx (ci misaal, 1=empty, 2=wall, 10=robot) te channel 1 yor categorical colour_idx (0–5). |
| `direction` | jublou way bi robot bi juboo léegi |
| `mission` | ndigalu natural language bi ñuy gis |
| `carrying` | `null` walla `[object_idx, colour_idx]` ngir object bi robot bi yore |

Row yi ay snapshot yu kennal lañu te nekk ci toppandoo bu yéeme. Duñu nekk ay episode, te kenn du  ci am observation walla action bu jiitu ci waxtuw evaluation.

`visualize_dataset.ipynb` bi ñu joxe dafay la may nga seet observation yi model bi mën a am ci situaton yu wuute.

## Encoding bu grid bi

`image[row][column] = [object_idx, colour_idx]`. Index bu njëkk bi mooy ligne bi, dale ko ci kaw jëm ci suuf, te ñaareel bi mooy colonne bi, dale ko ci càmmooñ jëm ci ndijoor. tableau bi dafa ëmb bordure bu miir bi ci biti, kon biir bi ñuy dox mooy `6×6`.

Object ids:

| id | object |
|---:|---|
| 1 | cellule bu neen |
| 2 | miir |
| 5 | caabi |
| 6 | bal |
| 7 | boyetu |
| 10 | robot |
| 11 | token |

Token yi mën nañu feeñ ci néeg bi waaye duñu leen tudd mukk ci mission yi.

Colour ids yi mooy `0` xonq, `1` wert, `2` baxa, `3` yolet, `4` mboq ak `5` suuf. Colour channel bi amul tekki ci cellule yu neen yi ak miir yi.

Image bi am na rekk ñaari channel yi ci kaw. Direction bu robot bi ñu ngi ko joxe benn yoon, ci champ `direction` bi ci kaw bi; duñu ko ñaareel ci biir `image`.

## Action yi

Ngir code `0`–`3`, action yi dañuy jëfandikoo teralin bii:

| action | tekki |
|---:|---|
| 0 | dem ci kaw |
| 1 | dem ci suuf |
| 2 | dem ci càmmooñ |
| 3 | dem ci ndijoor |
| 4 | for |
| 5 | teg |


Champ `direction` bi dafay màndarga orientation bi robot bi juboo léegi, ci anam yii: 0 = Kaw (row - 1), 1 = Suuf (row + 1), 2 = Càmmooñ (col - 1), 3 = Ndijoor (col + 1).

Action bu movement day njëkk a walbati robot bi ci direction absolue boobu, ba noppi jéem koo yóbbu par benn cellule. Miir walla object mën na tere mouvement bi, waaye direction bi dina soppeeku ba tey. `pick up` ak `drop` dañuy jëf rekk ci wetu cellule bi nuy wutu te direction bi di ko wax (ci misaal, bu direction=0, day jëf ci (row - 1, col)).

## Dataset

Dinga jot ñaari dossier:

| Folder | Rows | `labels.json`? | Jëfandikoo ko ngir |
|---|---:|---|---|
| `dataset/train/` | 60,000 | ci biir | entrainer sa model |
| `dataset/test_public/` | 3,600 | ci biir development copie bi | doxal sa pipeline te xayma sa score |

Dossier bu nekk am na `observations.json`, maanaam JSON list bu exemples yi ñu melal
ci kaw. `labels.json` mooy JSON list bu action yi méngoo (`0`–`5`).

Training set bi am na dëgg-dëgg 10,000 lignes ci robot bu nekk ak 20,000 lignes ci
task family bu nekk. Public test bi am na 600 liignes ci robot bu nekk. Wërale `image` ak
`numpy.asarray(...)` su fekkee tableau nga soxla.

Ci waxtuw xayma, dañuy wuutal `dataset/test_public/` ci anam bu kenn du gis ak ensemble bu nebu bu
3,600 observation ci format bu mel ni moom, waaye `labels.json` amul. Public
leaderboard bi dafay jëfandikoo `test_leaderboard_a`; classement final bi dafay jëfandikoo
`test_leaderboard_b`. Notebook buy jàng test labels saa su nekk dina lajj. Jàngal labels yi rekk ci `dataset/train/`.

## Génne gi

Bindal `predictions.json` ci dossier liggeyu kay bu notebook bi. War na doon ab liste JSON
 bu ëmb benn integer action (`0`–`5`) ci row bu nekk bu
`dataset/test_public/observations.json`, ci toppandoo boobu. Ngir test set bu ñu misaal te am juróom-benn sample, output bu baax mën na doon:

```json
[0, 3, 2, 2, 5, 4]
```

Fichier JSON  bu ñàkk walla bu baaxul, limu prediction bu jubul, valeur bu dul entier,
walla action bu génn `{0,1,2,3,4,5}`, dañu koy bañ te du am score.

## Joxe score

Score bi mooy **digg-dóomu accuracy ci robot bu nekk** ci diggante `0`–`100`. Dañuy njëkk a xayma accuracy ci robot bu nekk
ci anam bu kennal, ba noppi jël seen digg-dóomu ci juróom-benn robot yépp. Kon robot bu nekk
am na benn poids.

## Naka lañuy yónnee

1. Ubbi `solution.ipynb` te doxal cellule yépp.
2. Wóorliku ne dafay bind `predictions.json` ak 3,600 prediction ngir public
   test set bi.
3. Gënal model bi su la neexee; baseline bi ñu joxe dafay wone rekk
   format bu dugg ak guen bi ñu laaj.
4. Ci JupyterLab Git tab bi, **Stage** te **commit** `solution.ipynb`, ba noppi push ko.
5. Dellu ci xëtu Contest bi te bës **Submit**.

Yónne benn fichier rekk bu tudd `solution.ipynb`. 
