# Pronásledování robota

- **Časový limit:** 5 minut
- **Prostředí:** jedno GPU (≈16 GB VRAM), bez internetu
- **Velikost řešení:** `solution.ipynb` ≤ 1 MB
- **Úložiště:** 5 GB 

## Úloha

Je zde šest robotů. Každý robot pracuje v malé místnosti reprezentované mřížkou. Každá místnost má hratelnou oblast `6×6` obklopenou zdmi, takže celé pole `image` má rozměry `8×8` (hratelná oblast + zdi).

Každý robot obdrží anglickou instrukci popisující úkol. Snímek může být pořízen v libovolném okamžiku během jeho plnění. Vaším cílem je předpovědět další akci robota.

Roboti ne vždy postupují po nejkratší cestě. Robot 0 se může chovat jinak než Robot 1, ale každý robot se řídí svým vlastním konzistentním vzorcem. K naučení těchto vzorců použijte trénovací příklady, které obsahují správné následující akce.

![Robot](../robot.jpg)

Existují tři typy misí:

- **dojít k** předmětu, například `"approach the red ball"`;
- **zvednout** předmět, například `"grab the blue key"`;
- **položit jeden předmět vedle jiného**, například
  `"place the red box beside the green ball"`.

Stejnou instrukci lze zapsat několika způsoby. Testovací sada může obsahovat nové kombinace známých frází, barev a typů předmětů. Každé slovo, vzor fráze, barva, typ předmětu a typ mise použitý v testovací sadě se však objevuje také v trénovací sadě.

Každý vzorek má následující pole:

| Pole | Význam |
|---|---|
| `robot_id` | o kterého z 6 robotů se jedná (`0`–`5`) |
| `image` | místnost, celočíselné pole `8×8×2`, kde kanál 0 obsahuje kategoriální object_idx (např. 1=prázdné, 2=zeď, 10=robot) a kanál 1 obsahuje kategoriální colour_idx (0–5). |
| `direction` | směr, kterým je robot právě otočen |
| `mission` | viditelná instrukce v přirozeném jazyce |
| `carrying` | `null` nebo `[object_idx, colour_idx]` pro nesený předmět |

Řádky jsou nezávislé snímky v náhodném pořadí. Netvoří epizody a při vyhodnocení není k dispozici žádné předchozí pozorování ani akce.

Poskytnutý `visualize_dataset.ipynb` umožňuje prohlížet pozorování dostupná modelu v různých situacích.

## Kódování mřížky

`image[row][column] = [object_idx, colour_idx]`. První index označuje řádek shora dolů a druhý sloupec zleva doprava. Pole zahrnuje vnější okrajovou zeď, takže průchozí vnitřní oblast je `6×6`.

ID předmětů:

| id | předmět |
|---:|---|
| 1 | prázdné políčko |
| 2 | zeď |
| 5 | klíč |
| 6 | míč |
| 7 | krabice |
| 10 | robot |
| 11 | token |

Tokeny se mohou v místnosti vyskytovat, ale v misích nejsou nikdy uvedeny.

ID barev jsou `0` červená, `1` zelená, `2` modrá, `3` fialová, `4` žlutá a `5` šedá. Barevný kanál nemá pro prázdná políčka a zdi žádný význam.

Obraz obsahuje pouze dva výše uvedené kanály. Směr robota je uveden jednou v poli `direction` nejvyšší úrovně; uvnitř `image` není duplikován.

## Akce

Pro kódy `0`–`3` používají pohybové akce následující absolutní mapování:

| akce | význam |
|---:|---|
| 0 | pohyb nahoru |
| 1 | pohyb dolů |
| 2 | pohyb doleva |
| 3 | pohyb doprava |
| 4 | zvednutí |
| 5 | položení |


Pole `direction` udává aktuální orientaci pomocí: 0 = nahoru (row - 1), 1 = dolů (row + 1), 2 = doleva (col - 1), 3 = doprava (col + 1).

Pohybová akce nejprve otočí robota do daného absolutního směru a poté se jej pokusí posunout o jedno políčko. Zeď nebo předmět může pohyb zablokovat, ale směr se přesto změní. `pick up` a `drop` působí výhradně na sousední cílové políčko určené směrem (např. pokud direction=0, působí na (row - 1, col)).

## Dataset

Obdržíte dvě složky:

| Složka | Řádky | `labels.json`? | Použijte ji k |
|---|---:|---|---|
| `dataset/train/` | 60,000 | zahrnuto | trénování vašeho modelu |
| `dataset/test_public/` | 3,600 | zahrnuto ve vývojové kopii | spuštění a vlastnímu vyhodnocení vašeho řešení |

Každá složka obsahuje `observations.json`, seznam JSON výše popsaných vzorků.
`labels.json` je odpovídající seznam JSON akcí (`0`–`5`).

Trénovací sada obsahuje přesně 10,000 řádků pro každého robota a 20,000 řádků z každé
rodiny úloh. Veřejná testovací sada obsahuje 600 řádků pro každého robota. Pokud potřebujete pole, obalte `image` pomocí
`numpy.asarray(...)`.

Při hodnocení je `dataset/test_public/` transparentně nahrazen skrytou sadou
3,600 pozorování ve stejném formátu, ale bez `labels.json`. Veřejný
žebříček používá `test_leaderboard_a`; konečné pořadí používá
`test_leaderboard_b`. Notebook, který bezpodmínečně načítá štítky testovací sady, selže.
Štítky načítejte pouze z `dataset/train/`.

## Výstup

Zapište `predictions.json` do pracovního adresáře notebooku. Musí jít o seznam JSON
obsahující jednu celočíselnou akci (`0`–`5`) pro každý řádek
`dataset/test_public/observations.json`, ve stejném pořadí. Pro hypotetickou testovací sadu obsahující šest vzorků by platným výstupem bylo:

```json
[0, 3, 2, 2, 5, 4]
```

Chybějící nebo neplatný soubor JSON, nesprávný počet predikcí, neceločíselná hodnota
nebo akce mimo `{0,1,2,3,4,5}` budou odmítnuty bez bodového hodnocení.

## Hodnocení

Hodnocení je **průměrná přesnost pro jednotlivé roboty** na stupnici `0`–`100`. Přesnost se nejprve
vypočítá nezávisle pro každého robota a poté se zprůměruje přes všech šest robotů. Každý
robot má proto stejnou váhu.

## Jak odevzdat řešení

1. Otevřete `solution.ipynb` a spusťte všechny buňky.
2. Ověřte, že zapíše `predictions.json` s 3,600 predikcemi pro veřejnou
   testovací sadu.
3. Pokud chcete, model vylepšete; poskytnutý baseline pouze demonstruje
   požadovaný formát vstupu a výstupu.
4. Na kartě Git v JupyterLab zařaďte `solution.ipynb` do indexu, vytvořte commit a poté jej odešlete.
5. Vraťte se na stránku soutěže a klikněte na **Odevzdat**.

Odevzdejte právě jeden soubor s názvem `solution.ipynb`.
