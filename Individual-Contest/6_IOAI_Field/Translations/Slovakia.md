# Pole IOAI

- **Časový limit:** 5 minút
- **Úložisko:** 5 GB
- **Veľkosť riešenia:** `solution.ipynb`, `custom_model.py` spolu ≤ 1 MB
- **Predtrénované modely:** žiadne — trénovanie od začiatku, bez internetu v čase hodnotenia
- **Baseline skóre**: 31.2187


## Úloha

Primátor Astany chce vyzdobiť mesto štylizovanými logami IOAI. Ako štatistik vníma všetko — vrátane loga — ako priestorovú funkciu $F(x, y, \overline{W})$, kde $x, y \in [0, 1]$ predstavujú súradnice v 2D rovine a $\overline{W}$ je množina skrytých parametrov definujúcich štylistické atribúty, ako sú farby a uhly písmen.

Keďže $F$ je príliš zložitá na to, aby sa dala vyjadriť explicitnou matematickou rovnicou, vašou úlohou je natrénovať neurónovú sieť, ktorá ju aproximuje. Sieť pre ľubovoľnú dvojicu súradníc $(x, y)$ vráti hodnotu **poľa IOAI**, čím vygeneruje úplnú vizualizáciu loga vo forme teplotnej mapy v celej rovine. Tu je príklad vizualizácie $F$ vo forme teplotnej mapy s konkrétnymi skrytými parametrami $\overline{W}$.

![f1](../ioai1.png)

Z čoho sa pole IOAI skladá? Zo štyroch písmen a pozadia.

- Hodnoty v prvom písmene `I` sú veľmi veľké (1e+10 a viac) a majú lineárny gradient
- Hodnoty v písmene `O` vykazujú špirálový vzor
- Hodnota v písmene `A` je vždy -1
- Hodnoty v poslednom písmene `I` by mali byť náhodnými hodnotami z rozsahu $[-2026,2026]$, a to aj v prípade, že sa vyhodnotia dvakrát v tom istom bode
- Mimo písmen je hodnota vždy nula

Funkcia má skryté parametre $\overline{W}$, ktoré ovplyvňujú mierku a sklon písmen spolu s rozsahom hodnôt v prvom písmene `I`. Písmená sa však nebudú pretínať. Tu je niekoľko ilustračných príkladov toho, ako vyzerá pole IOAI s rôznymi $\overline{W}$:

![f2](../ioai2.png)
![f3](../ioai3.png)

**Čo máte k dispozícii:**

Táto úloha neobsahuje ŽIADNE datasety. Namiesto toho máte k dispozícii generujúcu funkciu, ktorá je nakonfigurovaná pomocou konfiguračného súboru JSON v `data/train_config/field_config.json`. 

Testovacia konfigurácia je skrytá, ale má podobný charakter. Vašou úlohou je prispôsobiť model danému generátoru s použitím ľubovoľného množstva dát. Vaše „trénovacie“ a „testovacie“ rozdelenia sú generované tým istým generátorom — iba neviete, v ktorých bodoch $(x_i, y_i)$ budete vyhodnocovaní.

Vaše odovzdané riešenie by malo pozostávať z:
- triedy trénovacieho modelu uloženej ako `custom_model.py`. Tento model by mal dediť z triedy `torch.nn.Module` a používať iba importy z `torch`. Mal by obsahovať triedu `CustomModel` použitú v notebooku `solution.ipynb`. 
- notebooku `solution.ipynb`, ktorý vytvorí váhy `model.pt`


## Hodnotenie

Pre každú oblasť je minimálne skóre 0 a maximálne skóre 1. Výsledné skóre je priemerom skóre všetkých piatich oblastí (štyroch pre jednotlivé písmená a jednej pre pozadie) vynásobeným 100. Uplatňuje sa **penalizácia za počet parametrov:**

**Ak má váš model viac ako 20260 parametrov, skóre sa zníži na polovicu.**

Počet parametrov sa meria pomocou `sum(p.numel() for p in model.parameters())`. Očakávame, že váš model bude pracovať aj v stochastickom režime, pričom súčasťou modelu bude PyTorch `nn.Dropout`.

### Pre štandardné oblasti

Pre každú štamdardnú oblasť $R$ (teda prvé písmeno `I`, `O`, `A`, `Background`) vyhodnocujeme model na $N_R = 512$ testovacích bodoch $(x_i, y_i)$ so skutočnými hodnotami $v_i$ a predikciami $\hat{v}_i$. Ako hlavnú metriku používame normalizovanú strednú absolútnu chybu (MAE). MAE je definovaná ako:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

A normalizácia sa vykonáva ako 

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

kde $s_R > 0$ je konštanta mierky.


### Pre oblasť posledného písmena `I`

V tejto oblasti je **dropout počas vyhodnocovania zapnutý**. Pre každý testovací bod $j$:

1. Model spustíme $K = 10$-krát, aby sme získali $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Ak je ľubovoľný výstup mimo rozsahu $[-2026, 2026]$, potom $\mathrm{pointScore}(j) = 0$.
3. V opačnom prípade vypočítame štandardnú odchýlku $\sigma_j$ z $K$ výstupov a prevedieme ju na skóre:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

kde $s_E > 0$ je pevná konštanta mierky.

Skóre oblasti je priemerom cez všetky body v oblasti:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

kde $N_E = K * N_R$. 

Jednoducho povedané, čím väčšiu rozmanitosť dosiahnete, tým vyššie bude vaše skóre pre túto oblasť. **Nesmiete používať náhodnosť v čistej forme vrátane funkcií PyTorch `rand*` a `_uniform`; náhodnosť by mala pochádzať z inferencie so zapnutým dropoutom.**

## Ako odovzdať riešenie

1. Otvorte `solution.ipynb` a spustite všetky bunky.
2. Vylepšite model `CustomModel` v `custom_model.py`
3. Uistite sa, že vaša posledná bunka uloží model do súboru `model.pt`.
4. Na karte Git v JupyterLab pridajte `solution.ipynb` a `custom_model.py` do staging area, pridajte komentár, vykonajte commit a následne ich odošlite pomocou push.
5. Vráťte sa na stránku súťaže a kliknite na **Submit**. Označenie k odovzdaniu by malo byť rovnaké ako označenie z predchádzajúceho kroku.
