# Najděte pořadí

- **Časový limit:** 10 minut
- **Prostředí:** jeden GPU (≈16 GB VRAM), bez přístupu k internetu
- **Velikost řešení:** `solution.ipynb` ≤ 1 MB
- **Úložiště:** 5 GB 

## Úloha

Jsou vám dány mluvené anglické dialogy mezi dvěma účastníky, *Speaker A* a *Speaker B*. Každý dialog je rozdělen na promluvy, přičemž každá promluva obsahuje řeč pouze jednoho mluvčího. Každá promluva je uložena jako samostatný zvukový soubor `.wav`, takže úplný dialog je reprezentován sadou souborů `.wav`, jedním pro každou promluvu. 

Promluvy byly bohužel náhodně zamíchány, takže konverzace již nedává smysl. V názvu souboru `chunk_{k}.wav` označuje `k` k-tý úsek v zamíchané sadě, nikoli k-tou promluvu v původním dialogu.

**‼️ Vaším úkolem je rekonstruovat původní chronologické pořadí konverzace.**

![Najděte pořadí](../../find_the_order.jpg)

---

## Dataset

Každý dialog obsahuje zvukové soubory `n` pojmenované `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Jednotlivé úseky jsou samostatné promluvy. Názvy souborů odpovídají pouze zamíchanému pořadí. Neudávají, kam úsek patří v původní konverzaci. Každý dialog má 7–20 úseků, mono, 44.1 kHz (můžete
změnit vzorkovací frekvenci).

**`prefix.json` obsahuje indexy názvů souborů prvních dvou úseků každého dialogu.** Tím je určeno skutečné zahájení dialogu a odstraněna nejednoznačnost mezi čtením konverzace směrem dopředu a pozpátku.

Například: `11: [7, 12]` znamená, že první a druhou promluvou dialogu 11 jsou v uvedeném pořadí `chunk_7.wav` a `chunk_12.wav`.

### Co obdržíte

Obdržíte **dvě složky ve shodném formátu**:

| Složka | Dialogy | `answers.json`? | Použijte ji k |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ zahrnuto | trénování / doladění modelu |
| `dataset/test_public/`  | 100   | ✅ zahrnuto | spuštění pipeline a místnímu vyhodnocení vlastního skóre |

Během hodnocení je vaše složka `dataset/test_public/` transparentně nahrazena
složkou `hidden evaluation set` (`test_leaderboard_a` pro veřejný žebříček a `test_leaderboard_b` pro konečný žebříček) — ty mají stejnou velikost a formát jako `dataset/test_public/`, ale bez `answers.json`.

Váš notebook je na těchto datech spuštěn znovu a soubor `answers.json`, který vytvoří, je použit k vyhodnocení. Vyčleněné testovací dialogy pocházejí ze stejného rozdělení jako `train`, takže vaše místní skóre `test_public` poskytuje věrný náhled.

### Adresářová struktura

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

Pro každý dialog určete původní chronologické pořadí jeho zvukových úseků. Vaší predikcí má být permutace `P` množiny `{0, 1, …, n−1}`, kde `P[i]` je predikovaná chronologická pozice souboru `chunk_i.wav` (0 = první).

Váš výstupní soubor `answers.json` má přiřazovat každému ID dialogu jeho predikovanou permutaci:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Příklad

Dialog má 3 zamíchané úseky `chunk_0, chunk_1, chunk_2`:

| zamíchaný úsek | mluvený obsah | skutečná pozice (pořadí) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (poslední) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (první) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Skutečné pořadí je **chunk_1 → chunk_2 → chunk_0**, tedy `P = [2, 0, 1]`, a `prefix.json` obsahuje `[1, 2]`.

⚠️ **P musí být skutečná permutace:** délky n, indexovaná od 0, každá hodnota právě jednou. Duplicitní, chybějící nebo mimo rozsah ležící položky (např. při indexování od 1) znamenají skóre 0 pro daný dialog, stejně jako dialog, který v souboru chybí. Soubor s chybným formátem nebo soubor, který není ve formátu JSON, bude odmítnut.

## Hodnocení

Metrikou této úlohy je **přesnost párového pořadí**. Kontroluje každou dvojici úseků a ptá se: _který z nich má být první?_ Dvojice je správná, pokud vaše predikce dává stejnou odpověď jako referenční správné pořadí. Pro dialog s `n` úseky existuje $$M = n(n-1)/2$$ dvojic; nechť `I` je počet inverzí — dvojic seřazených jinak než v referenčním správném pořadí:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Konečné skóre je průměrem skóre jednotlivých dialogů přes všechny
dialogy v dané části dat.**

## Povolené modely

K řešení této úlohy můžete během trénování i vyhodnocování používat pouze následující předtrénované modely. Všechny tyto modely jsou již staženy a dostupné v prostředí. Příklady jejich použití naleznete v baseline notebooku `solution.ipynb`. Upozorňujeme, že nesmíte použít žádný jiný model a váš program nemá přístup k internetu.

- **Reprezentace řeči:** **wav2vec 2.0**. Jako extraktor příznaků lze použít také **enkodér Whisper**.
[karta modelu wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Automatické rozpoznávání řeči (ASR):** **OpenAI Whisper** (libovolná velikost).
[karta modelu Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Jazykový model:** **Qwen2.5-0.5B**, který lze použít buď v režimu zero-shot, nebo jej doladit na poskytnuté části `train`.
[karta modelu Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Mějte na paměti, že limit 10 minut musí zahrnovat veškeré trénování nebo dolaďování, které provádíte během hodnocení, i inferenci na evaluační sadě.

## Jak řešení odevzdat

- Otevřete `solution.ipynb` a spusťte všechny buňky. Ověřte, že do pracovního adresáře zapíše `answers.json` s permutací pro každý dialog v `dataset/test_public/` (100 dialogů). Během hodnocení je notebook znovu spuštěn na skryté testovací sadě a vyhodnotí se soubor `answers.json`, který na ní vytvoří.
- Pokud chcete, řešení vylepšete — nebo ne; samotný baseline ověřuje funkčnost pipeline.
- Otevřete kartu Git v levém postranním panelu JupyterLab.
- **Přidejte do stage** `solution.ipynb` (ikona + vedle něj).
- Zadejte zprávu commitu a klikněte na **Commit**.
- Kliknutím na ikonu cloudu se šipkou nahoru odešlete změny.
- Vraťte se na tuto stránku soutěže a klikněte na **Submit**.

Odešlete právě jeden soubor s názvem `solution.ipynb`.
