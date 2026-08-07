# Duch stroja

- **Časový limit:** 10 minút
- **Základné skóre:** 28.6
- **Skóre vedeckého výboru:** 93.41
- **Prostredie:** jedna GPU (≈16 GB VRAM), bez internetu
- **Veľkosť riešenia:** `solution.ipynb` ≤ 20 MB
- **Úložisko:** 5 GB
- **Predtrénované modely:** iba **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — textový **enkóder** (embeddingový model).


## Úloha

V Národnom archíve Kazachstanu sa dejú zvláštne veci. Knihovníci tvrdia, že niektoré knihy sa kedysi končili inak, ale nikto to nedokáže preukázať — každý výtlačok je rovnaký a každý príbeh stále dáva zmysel. Ako výskumník v oblasti AI ste pozvaní, aby ste našli zmeny.
![Duch](../../ghost.jpg)

Pasáž sa začína ako text napísaný človekom a v istom bode nepozorovane prejde
na pokračovanie vygenerované jazykovým modelom. Keď sa číta ako celok, pôsobí ako
jeden súvislý text — niekde uprostred sa však autor zmení z človeka
na stroj. Vašou úlohou je **nájsť tento prechod: index znaku, na ktorom sa
končí ľudská časť a začína strojová časť**.

Každá vzorka je jeden reťazec `text`. Existuje presne jedna hranica. Všetko
pred ňou je vytvorené človekom; všetko od nej ďalej je vygenerované strojom.

## Dataset

Anglické pasáže vo formáte obyčajného textu, každá s jednou hranicou.

- **Časť A** (pred hranicou): úryvok textu napísaného človekom.
- **Časť B** (od hranice ďalej): pokračovanie vytvorené jazykovým modelom
  podmienené časťou A.
- Každá strana má aspoň 180 slov; celková dĺžka je ~500–800 slov.
- **`boundary_char_index`** je posun v znakoch, na ktorom sa končí časť A:
  `text[:boundary_char_index]` je ľudská časť a
  `text[boundary_char_index:].lstrip()` je strojová časť.

#### Čo dostanete

Dostanete **dva priečinky**:

| Priečinok | Vzorky | `answers.jsonl`? | Použite ho na |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ zahrnuté | trénovanie/doladenie vašej metódy |
| `dataset/test_public/`  | 380   | ✅ zahrnuté (vývojová kópia) | spustenie vášho postupu a lokálne vyhodnotenie vlastného skóre |

Počas **hodnotenia** sa váš priečinok `dataset/test_public/` **nahradí skrytou
vyhodnocovacou množinou**. Má rovnaký formát, ale je **bez `answers.jsonl`**. Váš
notebook sa na nej znova spustí a výstup `answers.jsonl`, ktorý vytvorí, sa vyhodnotí.

- Verejný rebríček používa skrytú množinu **test_leaderboard_a** (380 vzoriek).

- Konečné poradie používa skrytú množinu **test_leaderboard_b** (380 vzoriek).

Všetky tri vyhodnocovacie
množiny majú rovnakú veľkosť a pochádzajú z rovnakého rozdelenia ako `train`, takže vaše lokálne
skóre `dataset/test_public/` je rozumným odhadom vášho skóre v rebríčku.

#### Formát na disku

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- ID v `answers.jsonl` zodpovedajú ID v `data.jsonl`.
- `dataset/train/` (s odpoveďami) je k dispozícii vždy, keď trénujete alebo dolaďujete.

## Výstup (formát odovzdania)

Odovzdávate **jeden notebook, ktorý musí mať názov `solution.ipynb`**. Tento presný názov súboru je povinný. Akýkoľvek iný názov bude zamietnutý bez spustenia.

Váš notebook musí **načítať `dataset/test_public/data.jsonl`** a zapísať jeden súbor
**`answers.jsonl`** do koreňového adresára repozitára — jeden objekt JSON na riadok, ktorý
mapuje ID každej vzorky na vami predpovedaný index znaku hranice:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` musí byť **celé číslo v `[0, len(text)]`**.
- Každé ID v `dataset/test_public/data.jsonl` by sa malo objaviť presne raz. Vzorka, ktorá chýba
  v `answers.jsonl` (alebo má neceločíselnú hodnotu/hodnotu mimo rozsahu), získa 0
  bodov za danú vzorku.

## Hodnotenie

Pre každú vzorku nech `p` označuje vami predpovedaný index a `t` skutočnú hranicu. Skóre za vzorku klesá exponenciálne so vzdialenosťou v znakoch:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

To vedie k nasledujúcemu správaniu skóre:
- **=1.0** — presný znak hranice;
- **≈0.78** — odchýlka 25 znakov; - **≈0.61** — odchýlka 50 znakov;
- **≈0.37** — odchýlka 100 znakov;
- **≈0.01** — odchýlka 500 znakov.

**Konečné skóre je priemerom** skóre za jednotlivé vzorky zo všetkých vzoriek v danej časti
(uvádza sa na stupnici 0–100). Metrika odmeňuje priblíženie sa, nielen presnosť.

## Obmedzenia

- **Prostredie:** jedna GPU (≈16 GB VRAM), počas hodnotenia bez internetu — povolený
  model (uvedený nižšie) je už poskytnutý. **Časový limit reálneho času: 10 minút** na
  celé spustenie — musí zahŕňať akékoľvek trénovanie/dolaďovanie, ktoré vykonáte počas hodnotenia,
  **vrátane** inferencie na vyhodnocovacej množine.
- **Povolený predtrénovaný model** — tento zoznam je úplný; nemožno použiť žiadne iné predtrénované váhy.
  Model je **vopred poskytnutý v prostredí** (načítajte ho bežným spôsobom, napr.
  `from_pretrained`; počas hodnotenia nie je k dispozícii internet):
  - **bge-base-en-v1.5** — textový **enkóder** so 110M parametrami (embeddingový model). Vytvára
    embeddingy viet/pasáží; nie je to generatívny jazykový model. Môžete
    ho použiť **v pôvodnom stave (so zmrazenými príznakmi) alebo ho doladiť na časti `train`**
    (úplné doladenie sa zmestí do limitu 16 GB / 10 minút).
- Klasické/štatistické nástroje nie sú obmedzené: nad embeddingovými príznakmi, ktoré
  si sami vypočítate, môžete vytvoriť ľubovoľný model založený na príznakoch
  (napr. klasifikátory alebo regresory scikit-learn). *Predtrénované váhy hlbokého učenia*
  sú obmedzené iba na zoznam uvedený vyššie.

## Základné riešenie

Poskytnutý `solution.ipynb` je triviálne referenčné riešenie: odhadne jeden
„priemerný podiel hranice“ z `dataset/train/` a pre každú testovaciu pasáž predpovie rovnaký podiel
jej dĺžky. Na skrytej časti **test_leaderboard_a** dosahuje skóre **28.6**
a slúži iba ako spustiteľná šablóna pre postup
načítať-`dataset/test_public/` → zapísať-`answers.jsonl`.

**Skóre vedeckého výboru 93.41**, namerané na rovnakej časti a pri rovnakom
časovom limite 10 minút, pochádza z doladenia povoleného enkódera na `train` a lokalizácie
prechodu ako bodu zmeny medzi vetami. Nejde o hornú hranicu — maximum
tejto metriky je 100.
