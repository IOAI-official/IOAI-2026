# Nájdite poradie

- **Časový limit:** 10 minút
- **Prostredie:** jedna GPU (≈16 GB VRAM), bez internetu
- **Veľkosť riešenia:** `solution.ipynb` ≤ 1 MB
- **Úložisko:** 5 GB 

## Úloha

Dostanete hovorené anglické dialógy medzi dvoma účastníkmi, *Rečníkom A* a *Rečníkom B*. Každý dialóg je rozdelený na repliky, pričom každá replika obsahuje reč iba jedného rečníka. Každá replika je uložená ako samostatný zvukový súbor `.wav`, takže úplný dialóg je reprezentovaný množinou súborov `.wav`, po jednom pre každú repliku. 

Repliky boli, žiaľ, náhodne premiešané, takže konverzácia už nedáva zmysel. V názve súboru `chunk_{k}.wav` sa `k` vzťahuje na k-tu časť v premiešanej množine, nie na k-tu repliku v pôvodnom dialógu.

**‼️ Vašou úlohou je zrekonštruovať pôvodné chronologické poradie konverzácie.**

![Nájdite poradie](../../find_the_order.jpg)

---

## Dataset

Každý dialóg obsahuje zvukové súbory `n` s názvami `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Jednotlivé časti predstavujú samostatné repliky. Názvy súborov zodpovedajú iba premiešanému poradiu. Neuvádzajú, kam daná časť patrí v pôvodnej konverzácii. Každý dialóg má 7–20 častí, mono, 44.1 kHz (môžete
prevzorkovať).

**`prefix.json` obsahuje indexy názvov súborov prvých dvoch častí každého dialógu.** Tým sa identifikuje skutočný začiatok dialógu a odstráni sa nejednoznačnosť medzi čítaním konverzácie smerom dopredu alebo dozadu.

Napríklad: `11: [7, 12]` znamená, že prvou a druhou replikou dialógu 11 sú `chunk_7.wav` a `chunk_12.wav` v uvedenom poradí.

### Čo dostanete

Dostanete **dva priečinky v identickom formáte**:

| Priečinok | Dialógy | `answers.json`? | Použite ho na |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ zahrnutý | trénovanie / dolaďovanie vášho modelu |
| `dataset/test_public/`  | 100   | ✅ zahrnutý | spustenie vášho pipeline a lokálne vyhodnotenie vlastného skóre |

Počas hodnotenia sa váš priečinok `dataset/test_public/` transparentne nahradí priečinkom
`hidden evaluation set` (`test_leaderboard_a` pre verejný rebríček a `test_leaderboard_b` pre konečný rebríček) — tieto priečinky majú rovnakú veľkosť a formát ako `dataset/test_public/`, ale bez `answers.json`.

Váš notebook sa na týchto dátach spustí znova a na hodnotenie sa použije súbor `answers.json`, ktorý vytvorí. Odložené testovacie dialógy pochádzajú z rovnakého rozdelenia ako `train`, takže vaše lokálne skóre `test_public` je spoľahlivou ukážkou.

### Štruktúra adresárov

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

## Výstup

Pre každý dialóg určte pôvodné chronologické poradie jeho zvukových častí. Vaša predikcia má byť permutáciou `P` množiny `{0, 1, …, n−1}`, kde `P[i]` je predikovaná chronologická pozícia časti `chunk_i.wav` (0 = prvá).

Váš výstupný súbor `answers.json` má priradiť každému ID dialógu jeho predikovanú permutáciu:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Príklad

Dialóg má 3 premiešané časti `chunk_0, chunk_1, chunk_2`:

| premiešaná časť | hovorený obsah | skutočná pozícia (poradie) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (posledná) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (prvá) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Skutočné poradie je **chunk_1 → chunk_2 → chunk_0**, teda `P = [2, 0, 1]`, a `prefix.json` obsahuje `[1, 2]`.

⚠️ **P musí byť skutočná permutácia:** dĺžka n, indexovanie od 0, každá hodnota presne raz. Duplikáty, chýbajúce hodnoty alebo položky mimo rozsahu (napr. indexované od 1) znamenajú skóre 0 pre daný dialóg, rovnako ako dialóg chýbajúci v súbore. Súbor s nesprávnym formátom alebo súbor, ktorý nie je vo formáte JSON, bude odmietnutý.

## Hodnotenie

Metrikou hodnotenia tejto úlohy je **presnosť párového usporiadania**. Kontroluje každú dvojicu častí a kladie otázku: _ktorá z nich má byť prvá?_ Dvojica je správna, ak vaša predikcia dáva rovnakú odpoveď ako referenčné správne poradie. Pre dialóg s `n` časťami existuje $$M = n(n-1)/2$$ dvojíc; nech `I` je počet inverzií — dvojíc usporiadaných inak než v referenčnom správnom poradí:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Konečné skóre je priemerom skóre jednotlivých dialógov zo všetkých
dialógov v danej časti datasetu.**

## Povolené modely

Na riešenie tejto úlohy môžete počas trénovania aj vyhodnocovania používať iba nasledujúce predtrénované modely. Všetky tieto modely sú už stiahnuté a dostupné v prostredí. Príklady ich použitia nájdete v baseline notebooku `solution.ipynb`. Upozorňujeme, že nemôžete použiť žiadny iný model a váš program nemá prístup na internet.

- **Reprezentácie reči:** **wav2vec 2.0**. Ako extraktor príznakov možno použiť aj **Whisper encoder**.
[Karta modelu wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automatické rozpoznávanie reči (ASR):** **OpenAI Whisper** (ľubovoľná veľkosť).
[Karta modelu Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Jazykový model:** **Qwen2.5-0.5B**, ktorý možno použiť buď v režime zero-shot, alebo doladiť na poskytnutej časti `train`.
[Karta modelu Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Upozorňujeme, že limit 10 minút musí zahŕňať akékoľvek trénovanie alebo dolaďovanie, ktoré vykonáte počas hodnotenia, aj inferenciu na vyhodnocovacej množine.

## Ako odovzdať riešenie

- Otvorte `solution.ipynb` a spustite všetky bunky. Overte, že sa v pracovnom adresári vytvorí súbor `answers.json` s permutáciou pre každý dialóg v `dataset/test_public/` (100 dialógov). Počas hodnotenia sa notebook znova spustí na skrytej testovacej množine a vyhodnotí sa súbor `answers.json`, ktorý tam vytvorí.
- Ak chcete, riešenie vylepšite — alebo nie; samotný baseline overuje pipeline.
- Otvorte kartu Git na ľavom bočnom paneli JupyterLab.
- Pridajte `solution.ipynb` do **Stage** (ikona + vedľa neho).
- Zadajte správu commitu a kliknite na **Commit**.
- Kliknutím na ikonu oblaku so šípkou nahor vykonajte push.
- Vráťte sa na túto stránku súťaže a kliknite na **Submit**.

Odovzdajte presne jeden súbor s názvom `solution.ipynb`.
