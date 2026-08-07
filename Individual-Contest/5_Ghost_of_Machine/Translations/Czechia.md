# Duch stroje

- **Časový limit:** 10 minut
- **Skóre baseline:** 28.6
- **Prostředí:** jedno GPU (≈16 GB VRAM), bez internetu
- **Velikost řešení:** `solution.ipynb` ≤ 20 MB
- **Úložiště:** 5 GB
- **Předtrénované modely:** pouze **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — textový **enkodér** (model embeddingů).


## Úloha

V Národním archivu Kazachstánu se dějí podivné věci. Knihovníci tvrdí, že některé knihy dříve končily jinak, ale nikdo to nedokáže prokázat — všechny výtisky jsou stejné a každý příběh stále dává smysl. Jako výzkumníci v oblasti AI jste přizváni, abyste změny lokalizovali.
![Duch](../ghost.jpg)

Pasáž začíná jako text napsaný člověkem a v určitém okamžiku nepozorovaně přejde
v pokračování vygenerované jazykovým modelem. Jako celek působí jako jeden
souvislý text — ale někde uprostřed se autor změní z člověka
na stroj. Vaším úkolem je **najít tento přechod: index znaku, na kterém
lidská část končí a strojová část začíná**.

Každý vzorek je jeden řetězec `text`. Existuje právě jedna hranice. Vše
před ní je lidské; vše od ní dále je vygenerované strojem.

## Dataset

Anglické pasáže v prostém textu, každá s jednou hranicí.

- **Část A** (před hranicí): úryvek textu napsaného člověkem.
- **Část B** (od hranice dále): pokračování vytvořené jazykovým modelem,
  podmíněné částí A.
- Každá část má alespoň 180 slov; celková délka je ~500–800 slov.
- **`boundary_char_index`** je posun ve znacích, na kterém část A končí:
  `text[:boundary_char_index]` je lidská část a
  `text[boundary_char_index:].lstrip()` je strojová část.

#### Co dostanete

Obdržíte **dvě složky**:

| Složka | Vzorky | `answers.jsonl`? | Použití |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ obsaženo | trénování / doladění vaší metody |
| `dataset/test_public/`  | 380   | ✅ obsaženo (vývojová kopie) | spuštění vaší pipeline a místní vyhodnocení vlastního skóre |

Při **hodnocení** bude vaše složka `dataset/test_public/` **nahrazena skrytou
evaluační sadou**. Má stejný formát, ale **bez `answers.jsonl`**. Váš
notebook se na ní znovu spustí a `answers.jsonl`, který vytvoří, bude vyhodnocen.

- Veřejný žebříček používá skrytou sadu **test_leaderboard_a** (380 vzorků).

- Konečné pořadí používá skrytou sadu **test_leaderboard_b** (380 vzorků).

Všechny tři evaluační
sady mají stejnou velikost a pocházejí ze stejného rozdělení jako `train`, takže vaše místní
skóre `dataset/test_public/` je rozumným odhadem vašeho skóre v žebříčku.

#### Formát na disku

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- ID v `answers.jsonl` odpovídají ID v `data.jsonl`.
- `dataset/train/` (s odpověďmi) je k dispozici vždy, když trénujete nebo dolaďujete.

## Výstup (formát odevzdání)

Odevzdáváte **jediný notebook, který musí být pojmenován `solution.ipynb`**. Tento přesný název souboru je povinný. Cokoli jiného bude odmítnuto bez spuštění.

Váš notebook musí **načíst `dataset/test_public/data.jsonl`** a zapsat jediný soubor
**`answers.jsonl`** do kořenového adresáře repozitáře — jeden objekt JSON na řádek, který
mapuje ID každého vzorku na vámi předpovězený index znaku hranice:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` musí být **celé číslo v `[0, len(text)]`**.
- Každé ID v `dataset/test_public/data.jsonl` by se mělo objevit právě jednou. Vzorek, který chybí
  v `answers.jsonl` (nebo má neceločíselnou / mimo rozsah ležící hodnotu), získá za tento vzorek skóre 0.

## Hodnocení

Pro každý vzorek nechť `p` je vámi předpovězený index a `t` je skutečná hranice. Skóre za vzorek exponenciálně klesá se vzdáleností ve znacích:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

To vede k následujícímu chování skóre:
- **=1.0** — přesný znak hranice;
- **≈0.78** — odchylka 25 znaků; - **≈0.61** — odchylka 50 znaků;
- **≈0.37** — odchylka 100 znaků;
- **≈0.01** — odchylka 500 znaků.

**Konečné skóre je průměrem** skóre za jednotlivé vzorky přes všechny vzorky v dané části
(uváděným na škále 0–100). Metrika odměňuje přiblížení se, nejen přesnost.

## Omezení

- **Prostředí:** jedno GPU (≈16 GB VRAM), při hodnocení bez internetu — povolený
  model (níže) je již poskytnut. **Limit reálného času: 10 minut** pro celý
  běh — ten musí zahrnovat veškeré trénování / dolaďování prováděné při hodnocení
  **i** inferenci na evaluační sadě.
- **Povolený předtrénovaný model** — tento seznam je úplný; žádné jiné předtrénované váhy
  nesmějí být použity. Model je **předem poskytnut v prostředí** (načtěte jej běžným způsobem, např.
  `from_pretrained`; při hodnocení není k dispozici internet):
  - **bge-base-en-v1.5** — textový **enkodér** se 110M parametry (model embeddingů). Vytváří
    embeddingy vět/pasáží; není to generativní jazykový model. Můžete jej
    použít **tak, jak je (se zmrazenými příznaky), nebo jej doladit na části `train`**
    (úplné doladění se vejde do limitu 16 GB / 10 minut).
- Klasické / statistické nástroje nejsou omezeny: nad příznaky embeddingů, které
  si sami vypočítáte, můžete vytvořit libovolný model založený na příznacích
  (např. klasifikátory nebo regresory scikit-learn). *Předtrénované váhy hlubokého učení* jsou omezeny pouze na výše uvedený seznam.
