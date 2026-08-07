# Njuumaayu Masin bi

- **Digalu waxtu:** 10 minutes
- **Baseline score:** 28.6
- **Score bu Komite Xam-xam bi:** 93.41
- **Environment:** benn GPU (≈16 GB VRAM), internet amul
- **Dayo bi solution bi:** `solution.ipynb` ≤ 20 MB
- **Dencukaay:** 5 GB
- **Pretrained models:** **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** rekk — ab **encoder** bu mbind (embedding model).


## Liggéey bi

Ay mbir yu yéeme di xew ca Arsip Nasyonal bu Kazakhstan. Bibliotekeer yi dañuy wax ne yenn téere yi daan jeex ci anam wu wuute, waaye kenn mënu koo firndeel — bépp sotti yem na, te bépp nettali ba tey am na maanaa. Ñu woo la, yaw miy AI researcher, ngir nga seet fu coppite yi nekk.
![Njuumaay](../../ghost.jpg)

Ab passage dafay tàmbalee ne nit moo ko bind, ba ci benn bérab, mu soppeeku ci lu kenn yégul
nekk continuation bu language model sos. Boo ko jàngée mu mat, dafay mel ni
benn mbind mu ànd — waaye am na fu nekk ci digg bi bindkat bi soppeekoo nit
nekk masin. Liggéey bi mooy nga **gis soppeekoo boobu: character index bi fi
wàllu nit ñi bind jeex te wàllu masin bi tàmbalee**.

Sample bu nekk benn string la `text`. Benn boundary rekk a am. Lépp lu
ko jiitu nit moo ko bind; lépp lu tàmbalee ci moom ba ca kanam masin moo ko sos.

## Dataset

Passage yu plain-text English, ku nekk ak benn boundary.

- **Part A** (lu jiitu boundary bi): ab excerpt ci mbind mu nit bind.
- **Part B** (li tàmbalee ci boundary bi): ab continuation bu language model sos,
  te Part A moo doon context bi.
- Wàll wu nekk am na lu tollu ci 180 baat; guddaayu lépp di ~500–800 baat.
- **`boundary_char_index`** mooy character offset bi fi Part A jeex:
  `text[:boundary_char_index]` mooy wàllu nit bi te
  `text[boundary_char_index:].lstrip()` mooy wàllu masin bi.

#### Li ñu lay jox

Dinga jot **ñaari folder**:

| Folder | Samples | `answers.jsonl`? | Jëfandikoo ko ngir |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ ci biir | train / fine-tune sa méthode |
| `dataset/test_public/`  | 380   | ✅ ci biir (dev copy) | doxal sa pipeline te nga natt sa bopp ci sa masin |

Ci **waxtu notation bi**, ñuy **wuutal sa folder `dataset/test_public/` ak ab
evaluation set bu nëbbu**. Format bi benn la, waaye **`answers.jsonl` amu ci**. Ñuy
dellu doxal sa notebook ci kaw set boobu, ba noppi natt `answers.jsonl` bi mu génne.

- Public leaderboard bi dafay jëfandikoo set **test_leaderboard_a** bu nëbbu (380 samples).

- Classement final bi dafay jëfandikoo set **test_leaderboard_b** bu nëbbu (380 samples).

Ñetti evaluation
set yépp dañoo yem ci dayo te joge ci distribution bu mel ni bu `train`, kon sa
score `dataset/test_public/` ci sa masin man naa doon nattukaay bu yéeme ngir sa score ci leaderboard bi.

#### Format bi ci disk bi

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- Ids yi ci `answers.jsonl` dañuy méngoo ak ids yi ci `data.jsonl`.
- `dataset/train/` (ak tontu yi) jàppandi na saa su nekk boo bëggee train walla fine-tune.

## Output (formatu submission bi)

Danga war a yónnee **benn notebook rekk, te turam war naa doon `solution.ipynb`**. Turu file bii ci boppam moo war. Lépp lu dul loolu dees na ko bañ te doxaluñu ko.

Sa notebook war naa **jàng `dataset/test_public/data.jsonl`** te bind benn file rekk
**`answers.jsonl`** ci root bu repository bi — benn JSON object ci bépp rëdd, buy map
id bu bépp sample ak boundary character index bi nga predict:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` war naa doon **integer ci `[0, len(text)]`**.
- Bépp id bu nekk ci `dataset/test_public/data.jsonl` war naa feeñ benn yoon rekk. Sample bu ñàkk
  ci `answers.jsonl` (walla am value bu dul integer / nekk ci biti range bi) dina am score 0
  ci sample boobu.

## Natt gi

Ci bépp sample, na `p` doon index bi nga predict te `t` doon boundary bi dëgg. Score bu sample bi dafay wàññiku ci anam exponential, aju ci soriwaayu araf yi:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Loolu moo waral score bi di dox nii:
- **=1.0** — boundary character bi jub na;
- **≈0.78** — juum nga 25 araf; - **≈0.61** — juum nga 50 araf;
- **≈0.37** — juum nga 100 araf;
- **≈0.01** — juum nga 500 araf.

**Score final bi mooy moyenne bi** ci score yu sample yépp ci split bi
(ñu koy joxe ci échelle 0–100). Metric bi day fey bu baax boo *jege*, du rekk boo jub.

## Contraintes

- **Environment:** benn GPU (≈16 GB VRAM), internet amul ci waxtu notation bi — model bi ñu may
  ci suuf jàppandi na ba noppi. **Wall-clock budget: 10 minutes** ngir
  doxal lépp — loolu war naa doy ci bépp training / fine-tuning boo def ci waxtu notation bi
  **ak it** inference ci evaluation set bi.
- **Pretrained model bi ñu may** — bii moo mat sëkk; kenn mënu jëfandikoo yeneen pretrained weights.
  Ñu **jàppandil nañu ko ci environment bi** (yeb ko ci anam gu biasa, misaal
  `from_pretrained`; internet amul ci waxtu notation bi):
  - **bge-base-en-v1.5** — ab **encoder** bu mbind (embedding model) bu am 110M-parameter. Dafay
    sos sentence/passage embeddings; du generative language model. Mën nga ko
    jëfandikoo **ni mu mel (frozen features) walla fine-tune ko ci split `train`**
    (full fine-tuning dina dugg ci budget bu 16 GB / 10-minute).
- Classical / statistical tools yi amuñu tere: mën nga tabax bépp feature-based
  model (misaal, scikit-learn classifiers walla regressors) ci kaw embedding features yi nga
  compute sa bopp. *Pretrained deep-learning weights* yi rekk la restriction bi aju ci list bi ci kaw.

## Baseline

`solution.ipynb` bi ñu joxe ab reference bu yomb la: dafay estimé benn
"average boundary fraction" bu joge ci `dataset/train/` te predict fraction boobu ci
guddaayu bépp test passage. Mu am score **28.6** ci split **test_leaderboard_a**
bu nëbbu te nekk rekk ngir doon template buy dox ngir loop
jàng-`dataset/test_public/` → bind-`answers.jsonl`.

**Score bu Komite Xam-xam bi, 93.41**, ñu natt ko ci split boobu ak budget bu
10-minute boobu, jóge na ci fine-tuning encoder bi ñu may ci `train` ak ci gis
soppeekoo bi ni changepoint ci digg sentence yi. Du upper bound — maximum
ci metric bii mooy 100.
