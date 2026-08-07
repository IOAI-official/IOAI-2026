# Seet toppante bi

- **Digalu waxtu:** 10 simili
- **Environnement:** benn GPU (≈16 GB VRAM), internet amul
- **Dayob solution bi:** `solution.ipynb` ≤ 1 MB
- **Dencukaay:** 5 GB 

## Jafe-jafe bi

Jox nañu la ay waxtaan ci English yu ñu wax, diggante ñaari bokk, *Speaker A* ak *Speaker B*. Waxtaan bu nekk, séddalees na ko ay tour de parole, te tour bu nekk waxu benn speaker rekk la ëmb. Tour bu nekk, denc nañu ko ni benn fichier audio `.wav` bu boppam, kon benn waxtaan bu mat, benn mbooloom fichiers `.wav` moo koy wone, benn ci tour bu nekk. 

Waaye, jaxase nañu tours yi ci lu kenn tëralul, ba tax waxtaan bi dootul am maana. Ci turu fichier bi `chunk_{k}.wav`, `k` mooy k-eelu chunk bi ci mbooloo mi ñu jaxase, du k-eelu tour bi ci waxtaanu cosaan bi.

**‼️ Liggéey bi ñu la sant mooy nga tabaxaat toppanteg waxtaan bi ci jamono ni mu nekkoon ca cosaan.**

![Seet toppante bi](../find_the_order.jpg)

---

## Dataset

Waxtaan bu nekk am na fichiers audio `n` yu tudd `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Chunks yi ay tours yu kenn kese lañu. Turi fichiers yi toppante bi ñu jaxase rekk lañuy méngool. Duñu wone fu chunk bi bokk ci waxtaanu cosaan bi. Waxtaan bu nekk am na 7–20 chunks, mono, 44.1 kHz (mën nga
def resampling).

**`prefix.json` ëmb na indexes yu turi fichiers yi ñu jëkkële ci ñaari chunks yi ci waxtaan bu nekk.** Loolu day wone tàmbalig dëggu waxtaan bi te dindi xel-ñaar gi ci diggante jàng waxtaan bi jëm kanam walla jëm gannaaw.

Misaal: `11: [7, 12]` dafay tekki ne tour bu njëkk ak ñaareelu tour ci dialogue 11 ñooy `chunk_7.wav` ak `chunk_12.wav`, ci toppante boobu.

### Li nga jot

Dinga jot **ñaari dossiers yu am benn format bi**:

| Dossier | Waxtaan yi | `answers.json`? | Jëfandikoo ko ngir |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ boole nañu ko | train / fine-tune sa model |
| `dataset/test_public/`  | 100   | ✅ boole nañu ko | doxal sa pipeline te nga xayma sa score ci sa masin |

Bu waxtuw xayma bi agsee, dañuy weccee sa dossier `dataset/test_public/` ci lu feeñul ak
benn `hidden evaluation set` (`test_leaderboard_a` ngir public leaderboard bi ak `test_leaderboard_b` ngir final leaderboard bi) — yii am nañu dayo ak format bu mel ni `dataset/test_public/` waaye amuñu `answers.json`.

Dañuy doxalaat sa notebook ci donnees yooyu, te fichier `answers.json` bi mu génne lañuy jëfandikoo ngir joxe score bi. Waxtaani test yu ñu nëbb jóge nañu ci distribution bu méngoo ak bu `train`, kon sa score `test_public` ci sa masin dafay jox nataalu dëgg bu li ngay jot.

### Tëgginu dossiers yi

```bash
dataset/train/
    prefix.json  # {dialogue_id: [first_idx, second_idx]} filename index 
    answers.json  # {dialogue_id: P}  ground-truth order (rank convention)
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav

dataset/test_public/
    prefix.json
    answers.json     # present only in the development copy
    <dialogue_id>/
        chunk_0.wav
        ...
        chunk_{n-1}.wav
```

---

## Génne gi

Ci waxtaan bu nekk, seetal toppante ci jamono ni mu nekkoon ca cosaan, ci chunks audio yi. Sa prediction war na doon permutation `P` bu `{0, 1, …, n−1}`, te `P[i]` mooy barab ci jamono bi nga xayma ngir `chunk_i.wav` (0 = bu njëkk).

Sa fichier génne `answers.json` war na lëkkale ID waxtaan bu nekk ak permutation bi nga xayma:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Misaal

Benn waxtaan am na 3 chunks yu ñu jaxase `chunk_0, chunk_1, chunk_2`:

| chunk bi ñu jaxase | li ñu wax | barabu dëgg bi (rang) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (bu mujj) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (bu njëkk) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Toppante bu dëgg bi mooy **chunk_1 → chunk_2 → chunk_0**, kon `P = [2, 0, 1]`, te `prefix.json` ëmb na `[1, 2]`.

⚠️ **P war na doon permutation bu dëgg:** guddaay n, 0-indexed, te valeur bu nekk war na feeñ benn yoon rekk. Valeurs yu ñaare, valeurs yu manke walla valeurs yu génn digal bi (misaal, 1-indexed) dañuy am score 0 ngir waxtaan boobu; waxtaan bu nekkul ci fichier bi itam noonu la. Fichier bu yàqu walla bu dul JSON dees koy bañ.

## Joxe score 

Score bi ñuy joxe ci liggéey bii mooy **pairwise ordering accuracy**. Dafay seet bépp ñaari chunks te laaj: _kan ci ñaar ñii moo wara jiitu?_ Paire bi jub na su sa prediction joxee tontu bu méngoo ak ground truth bi. Ci waxtaan bu am chunks `n`, am na $$M = n(n-1)/2$$ pairs; na `I` doon limu inversions yi — pairs yi ñu toppante wuute ak ground truth bi:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Score bu mujj bi mooy moyenne bi ci scores yu waxtaan bu nekk, ci waxtaan yépp
yu nekk ci split bi.**

## Models yi ñu maye

Models pre-trained yii rekk nga mën a jëfandikoo ngir saafara liggéey bii, ci training ak evaluation ñépp. Models yii yépp yeb nañu leen ba noppi te ñu ngi ci environnement bi. Mën nga gis ay misaali ni ñu leen di jëfandikoo ci baseline notebook `solution.ipynb`. Na nga xam ne doo mën a jëfandikoo beneen model, te sa program amul internet.

- **Speech representations:** **wav2vec 2.0**. Mën nga itam jëfandikoo **Whisper encoder** ni feature extractor.
[Model card bu wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automatic speech recognition (ASR):** **OpenAI Whisper** (benn dayo bu nekk).
[Model card bu Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Language model:** **Qwen2.5-0.5B**, mën nga ko jëfandikoo zero-shot walla nga fine-tune ko ci split `train` bi ñu joxe.
[Model card bu Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Na nga xam ne digalu 10 simili bi war na doy ngir mboolem training walla fine-tuning bi ngay def ci waxtuw not bi, ak inference ci evaluation set bi.

## Naka lañuy yónnee

- Ubbi `solution.ipynb` te doxal cells yépp. Wóorliku ne dafay bind `answers.json` ci working directory bi, ak permutation ngir waxtaan bu nekk ci `dataset/test_public/` (100 dialogues). Ci waxtuw not bi, dees na doxalaat notebook bi ci hidden test set bi, te `answers.json` bi mu génne foofa lañuy jox score.
- Gënal solution bi soo ko bëggee — walla bul ko def; baseline bi rekk sax dafay dëggal pipeline bi.
- Ubbi Git tab bi ci sidebar bu càmmooñ ci JupyterLab.
- Defal **Stage** `solution.ipynb` (icon + bi nekk ci wetam).
- Bind commit message te bës **Commit**.
- Bës cloud-with-up-arrow bi ngir push.
- Dellu ci xëtum Contest bii te bës **Submit**.

Yónnee benn fichier kese, bu tudd `solution.ipynb`.
