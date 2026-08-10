# IOAI Field

- **Tidsgräns:** 5 minuter
- **Lagring:** 5 GB
- **Lösningens storlek:** `solution.ipynb`, `custom_model.py` ≤ 1 MB tillsammans
- **Förtränade modeller:** inga — träna från grunden, ingen internetåtkomst vid rättningstillfället
- **Baseline-poäng**: 31.2187
- **Vetenskapliga kommitténs poäng:** 63.53


## Uppgift

Astanas borgmästare vill dekorera staden med stiliserade IOAI-logotyper. Som statistiker betraktar han allting — inklusive logotypen — som en spatial funktion $F(x, y, \overline{W})$, där $x, y \in [0, 1]$ representerar koordinater i ett 2D-plan och $\overline{W}$ är en mängd dolda parametrar som definierar stilistiska attribut såsom bokstävernas färger och vinklar.

Eftersom $F$ är för komplex för att uttryckas som en explicit matematisk ekvation är din uppgift att träna ett neuralt nätverk som approximerar den. Nätverket ska ge ett värde för **IOAI field** för varje koordinatpar $(x, y)$, och därmed generera en fullständig heatmap-visualisering av logotypen över planet. Här är ett exempel på en heatmap-visualisering av $F$ med några specifika dolda parametrar $\overline{W}$.

![f1](../../ioai1.png)

Vad består IOAI field av? Fyra bokstäver och bakgrunden.

- Värdena inuti den första bokstaven `I` är mycket stora (1e+10 och mer) med en linjär gradient
- Värdena i bokstaven `O` uppvisar ett spiralmönster
- Värdet inuti bokstaven `A` är alltid -1
- Värdena inuti den sista bokstaven `I` ska vara slumpmässiga värden från intervallet $[-2026,2026]$ även om de utvärderas i samma punkt två gånger
- Utanför bokstäverna är värdet alltid noll

Funktionen har dolda parametrar $\overline{W}$, som påverkar bokstävernas skala och lutning, tillsammans med värdeintervallet inuti den första bokstaven `I`. Bokstäverna kommer dock inte att skära varandra. Här är några illustrativa exempel på hur IOAI field ser ut med olika $\overline{W}$:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Vad du får:**

Detta problem innehåller INGA dataset. I stället får du generatorfunktionen som konfigureras av JSON-konfigurationsfilen på `data/train_config/field_config.json`.

Testkonfigurationen är dold, men den är av liknande slag. Din uppgift är att anpassa modellen till den givna generatorn med så mycket data du vill. Dina "train"- och "test"-fördelningar genereras från samma generator — du vet bara inte i vilka punkter $(x_i, y_i)$ du kommer att utvärderas.

Ditt bidrag ska bestå av:
- träningsmodellklassen sparad som `custom_model.py`. Denna modell ska ärva från klassen `torch.nn.Module` och endast använda `torch`-importer. Den ska innehålla klassen `CustomModel` som används i notebooken `solution.ipynb`.
- notebooken `solution.ipynb`, som ska producera vikterna `model.pt`


## Poängsättning

För varje region är minimipoängen 0 och maxpoängen 1. Slutpoängen är medelvärdet över alla fem regionerna (fyra för varje bokstav och bakgrunden) multiplicerat med 100. Det finns ett **parameterstraff:**

**Om din modell har mer än 20260 parametrar halveras poängen.**

Antalet parametrar mäts med `sum(p.numel() for p in model.parameters())`. Vi förväntar oss att din modell även kan arbeta i ett stokastiskt läge med PyTorchs `nn.Dropout` som en del av modellen.

### För standardregioner

För varje region $R$ (första bokstaven `I`, `O`, `A`, `Background`) utvärderar vi modellen på $N_R = 512$ testpunkter $(x_i, y_i)$ med sanna värden $v_i$ och prediktioner $\hat{v}_i$. Vi använder normaliserat Mean Absolute Error (MAE) som huvudmetrik. MAE definieras som:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

Och normaliseringen utförs som

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

där $s_R > 0$ är en skalkonstant.


### För regionen med den sista bokstaven `I`

I denna region är **dropout aktiverat under utvärderingen**. För varje testpunkt $j$:

1. Vi kör modellen $K = 10$ gånger för att erhålla $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Om något utdatavärde ligger utanför intervallet $[-2026, 2026]$, då är $\mathrm{pointScore}(j) = 0$.
3. Annars beräknas standardavvikelsen $\sigma_j$ för de $K$ utdatavärdena och omvandlas till en poäng:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

där $s_E > 0$ är en fast skalkonstant.

Regionens poäng är medelvärdet över alla punkter i regionen:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

där $N_E = K * N_R$.

Enkelt uttryckt: ju mer diversitet du har, desto högre blir din poäng för denna region. **Du får inte använda slumpmässighet i ren form, inklusive PyTorch-funktionerna `rand*` och `_uniform`; slumpmässigheten ska komma från inferens med aktiverad dropout.**

## Hur du lämnar in

1. Öppna `solution.ipynb` och kör alla celler.
2. Förbättra modellen `CustomModel` i `custom_model.py`
3. Se till att din sista cell sparar din modell till filen `model.pt`.
4. I JupyterLabs Git-flik: staga (stage), kommentera och committa `solution.ipynb` och `custom_model.py`, och pusha sedan.
5. Gå tillbaka till tävlingssidan (Contest) och klicka på **Submit**. Inlämningskommentaren ska vara densamma som kommentaren från föregående steg.
