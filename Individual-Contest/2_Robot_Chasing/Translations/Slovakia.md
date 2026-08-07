# Naháňanie robotov

- **Časový limit:** 5 minút
- **Prostredie:** jedna GPU (≈16 GB VRAM), bez internetu
- **Veľkosť riešenia:** `solution.ipynb` ≤ 1 MB
- **Úložisko:** 5 GB 

## Úloha

Existuje šesť robotov. Každý robot pracuje v malej miestnosti reprezentovanej mriežkou. Každá miestnosť má hrateľnú oblasť veľkosti `6×6` obklopenú stenami, takže celé pole `image` má veľkosť `8×8` (hrateľná oblasť + steny).

Každý robot dostane inštrukciu v angličtine opisujúcu úlohu. Snímka môže byť vytvorená v ľubovoľnom okamihu počas jej plnenia robotom. Vaším cieľom je predpovedať nasledujúcu akciu robota.

Roboty nie vždy postupujú po najkratšej ceste. Robot 0 sa môže správať inak ako Robot 1, každý robot sa však riadi vlastným konzistentným vzorcom. Pomocou tréningových príkladov, ktoré obsahujú správne nasledujúce akcie, sa naučte tieto vzorce.

![Robot](../robot.jpg)

Existujú tri typy misií:

- **ísť k** objektu, napríklad `"approach the red ball"`;
- **zdvihnúť** objekt, napríklad `"grab the blue key"`;
- **položiť jeden objekt vedľa druhého**, napríklad
  `"place the red box beside the green ball"`.

Tá istá inštrukcia môže byť formulovaná niekoľkými spôsobmi. Testovacia množina môže obsahovať nové kombinácie známych fráz, farieb a typov objektov. Každé slovo, vzor frázy, farba, typ objektu a typ misie použité v testovacej množine sa však nachádzajú aj v tréningovej množine.

Každá vzorka má nasledujúce polia:

| Pole | Význam |
|---|---|
| `robot_id` | ktorý zo 6 robotov to je (`0`–`5`) |
| `image` | miestnosť, celočíselné pole `8×8×2`, v ktorom kanál 0 obsahuje kategorické object_idx (napr. 1=prázdne, 2=stena, 10=robot) a kanál 1 obsahuje kategorické colour_idx (0–5). |
| `direction` | smer, ktorým je robot práve otočený |
| `mission` | inštrukcia zadaná v angličtine |
| `carrying` | `null` alebo `[object_idx, colour_idx]` pre nesený objekt |

Riadky sú nezávislé snímky v náhodnom poradí. Netvoria epizódy a počas vyhodnocovania nie je k dispozícii žiadne predchádzajúce pozorovanie ani akcia.

Pomocou poskytnutého `visualize_dataset.ipynb` môžete preskúmať pozorovania dostupné modelu v rôznych situáciách.

## Kódovanie mriežky

`image[row][column] = [object_idx, colour_idx]`. Prvý index je riadok zhora nadol a druhý je stĺpec zľava doprava. Pole zahŕňa vonkajší okraj tvorený stenou, takže priechodné vnútro je `6×6`.

Identifikátory objektov:

| id | objekt |
|---:|---|
| 1 | prázdna bunka |
| 2 | stena |
| 5 | kľúč |
| 6 | lopta |
| 7 | škatuľa |
| 10 | robot |
| 11 | token |

Tokeny sa môžu nachádzať v miestnosti, ale v misiách sa nikdy nespomínajú.

Identifikátory farieb sú `0` červená, `1` zelená, `2` modrá, `3` fialová, `4` žltá a `5` sivá. Kanál farby nemá význam pre prázdne bunky a steny.

Obrázok obsahuje iba dva vyššie uvedené kanály. Smer robota je uvedený raz v poli `direction` najvyššej úrovne; nie je duplikovaný v `image`.

## Akcie

Pre kódy `0`–`3` používajú pohybové akcie nasledujúce absolútne mapovanie:

| akcia | význam |
|---:|---|
| 0 | pohyb nahor |
| 1 | pohyb nadol |
| 2 | pohyb doľava |
| 3 | pohyb doprava |
| 4 | zdvihnúť |
| 5 | položiť |


Pole `direction` udáva aktuálnu orientáciu pomocou: 0 = Hore (row - 1), 1 = Dole (row + 1), 2 = Vľavo (col - 1), 3 = Vpravo (col + 1).

Pohybová akcia najprv otočí robota do daného absolútneho smeru a potom sa ho pokúsi presunúť o jednu bunku. Stena alebo objekt môžu pohyb zablokovať, smer sa však napriek tomu zmení. Akcie `zdvihnúť` a `položiť` pôsobia výlučne na susednú cieľovú bunku určenú smerom (napr. ak direction=0, pôsobia na (row - 1, col)).

## Dataset

Dostanete dva priečinky:

| Priečinok | Riadky | `labels.json`? | Použite na |
|---|---:|---|---|
| `dataset/train/` | 60,000 | zahrnuté | trénovanie vášho modelu |
| `dataset/test_public/` | 3,600 | zahrnuté len vo vývojovej kópii | spustenie a vlastné vyhodnotenie vášho pipeline |

Každý priečinok obsahuje `observations.json`, zoznam JSON vyššie opísaných vzoriek.
`labels.json` je zarovnaný zoznam JSON akcií (`0`–`5`).

Tréningová množina obsahuje presne 10,000 riadkov na každého robota a 20,000 riadkov z každej
rodiny úloh. Verejná testovacia množina obsahuje 600 riadkov na každého robota. Ak potrebujete pole, obaľte `image` pomocou
`numpy.asarray(...)`.

Počas hodnotenia sa `dataset/test_public/` transparentne nahradí skrytou množinou
3,600 pozorovaní v rovnakom formáte, ale bez `labels.json`. Verejný
rebríček používa `test_leaderboard_a`; konečné poradie používa
`test_leaderboard_b`. Notebook, ktorý bezpodmienečne načítava označenia testovacej množiny, zlyhá.
Označenia načítavajte iba z `dataset/train/`.

## Výstup

Zapíšte `predictions.json` do pracovného adresára notebooku. Musí to byť zoznam JSON
obsahujúci jednu celočíselnú akciu (`0`–`5`) pre každý riadok
`dataset/test_public/observations.json` v rovnakom poradí. Pre hypotetickú testovaciu množinu obsahujúcu šesť vzoriek by platný výstup vyzeral takto:

```json
[0, 3, 2, 2, 5, 4]
```

Chýbajúci alebo neplatný súbor JSON, nesprávny počet predikcií, neceločíselná hodnota
alebo akcia mimo `{0,1,2,3,4,5}` budú odmietnuté bez pridelenia skóre.

## Hodnotenie

Skóre je **priemerná presnosť jednotlivých robotov** na škále `0`–`100`. Presnosť sa najprv
vypočíta nezávisle pre každého robota a potom sa spriemeruje cez všetkých šesť robotov. Každý
robot má preto rovnakú váhu.

## Ako odovzdať riešenie

1. Otvorte `solution.ipynb` a spustite všetky bunky.
2. Overte, že zapíše `predictions.json` s 3,600 predikciami pre verejnú
   testovaciu množinu.
3. Ak chcete, model zlepšite; poskytnutý baseline iba demonštruje
   požadovaný vstupný a výstupný formát.
4. Na karte Git prostredia JupyterLab pripravte a commitnite `solution.ipynb` a potom ho pushnite.
5. Vráťte sa na stránku súťaže a kliknite na **Submit**.

Odošlite presne jeden súbor s názvom `solution.ipynb`.
