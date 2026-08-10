# IOAI መስክ

- **የጊዜ ገደብ:** 5 minutes
- **ማከማቻ:** 5 GB
- **የመፍትሔ መጠን:** `solution.ipynb`፣ `custom_model.py` በአንድ ላይ ≤ 1 MB
- **ቀድሞ የሠለጠኑ models:** የሉም — ከመነሻው ያሠለጥኑ፤ በማረሚያ ጊዜ internet አይኖርም
- **የBaseline ውጤት**: 31.2187
- **የሳይንሳዊ ኮሚቴ ውጤት:** 63.53


## ተግባር

የAstana ከንቲባ ከተማዋን በቅጥ በተዘጋጁ የIOAI logos ማስዋብ ይፈልጋል። እንደ ስታቲስቲክስ ባለሙያ፣ logoን ጨምሮ ሁሉንም ነገር እንደ የቦታ ፋንክሽን $F(x, y, \overline{W})$ ይመለከታል፤ በዚህም $x, y \in [0, 1]$ በ2D ፕሌን ላይ ያሉ መጋጠሚያዎችን የሚወክሉ ሲሆን፣ $\overline{W}$ እንደ የፊደሎች ቀለሞችና ማዕዘኖች ያሉ የቅጥ ባህሪያትን የሚወስኑ የተደበቁ parameters ስብስብ ነው።

$F$ በግልጽ የሒሳብ ቀመር ለመግለጽ እጅግ ውስብስብ ስለሆነ፣ ተግባራችሁ እሱን የሚገምት neural network ማሠልጠን ነው። Networkው ለማንኛውም የመጋጠሚያ ጥንድ $(x, y)$ የ**IOAI መስክ** እሴት በማውጣት፣ በፕሌኑ ሁሉ ላይ የlogoውን ሙሉ የሙቀት ካርታ (heatmap) ምስላዊ አቀራረብ ያመነጫል። ይህ የ$F$ የheatmap ምስላዊ አቀራረብ ምሳሌ ሲሆን፣ የተወሰኑ የተደበቁ parameters $\overline{W}$ አሉት።

![f1](../../ioai1.png)

የIOAI መስክ ምንን ያካትታል? አራት ፊደሎችንና backgroundን።

- በመጀመሪያው `I` ፊደል ውስጥ ያሉ እሴቶች መስመራዊ ቅልመት ያላቸው እጅግ ትልቅ እሴቶች (1e+10 እና ከዚያ በላይ) ናቸው
- በ`O` ፊደል ውስጥ ያሉ እሴቶች ጥምዝ ንድፍ ያሳያሉ
- በ`A` ፊደል ውስጥ ያለው እሴት ሁልጊዜ -1 ነው
- በመጨረሻው `I` ፊደል ውስጥ ያሉ እሴቶች፣ ተመሳሳዩ ነጥብ ሁለት ጊዜ ቢገመገምም እንኳ፣ ከክልሉ $[-2026,2026]$ የተወሰዱ random እሴቶች መሆን አለባቸው
- ከፊደሎቹ ውጭ እሴቱ ሁልጊዜ ዜሮ ነው

ፋንክሽኑ የተደበቁ parameters $\overline{W}$ አሉት፤ እነዚህም የፊደሎቹን መጠንና ዘንበል፣ እንዲሁም በመጀመሪያው `I` ፊደል ውስጥ ያሉትን የእሴቶች ክልል ይነካሉ። ሆኖም፣ ፊደሎቹ አይደራረቡም። IOAI መስክ በተለያዩ $\overline{W}$ ምን እንደሚመስል የሚያሳዩ ጥቂት ምሳሌዎች እነሆ፦

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**የተሰጣችሁ፦**

ይህ ችግር ምንም datasets አልያዘም። በምትኩ፣ በ`data/train_config/field_config.json` ላይ ባለው JSON config file የሚዋቀር አመንጪ ፋንክሽን (generator function) ተሰጥቷችኋል። 

የፈተናው config የተደበቀ ነው፣ ነገር ግን ተመሳሳይ ባህሪ አለው። ተግባራችሁ የፈለጋችሁትን ያህል data በመጠቀም በተሰጠው generator ላይ model ማስማማት ነው። የእናንተ `"train"` እና `"test"` distributions ከተመሳሳዩ generator የሚመነጩ ናቸው፤ የማታውቁት የትኞቹ ነጥቦች $(x_i, y_i)$ ላይ እንደምትገመገሙ ብቻ ነው።

Submissionዎ የሚከተሉትን ማካተት አለበት፦
- እንደ `custom_model.py` የተቀመጠ የማሠልጠኛ model class። ይህ model ከ`torch.nn.Module` class መውረስ እና የ`torch` importsን ብቻ መጠቀም አለበት። በ`solution.ipynb` notebook ውስጥ ጥቅም ላይ የሚውለውን `CustomModel` class መያዝ አለበት። 
- `model.pt` weightsን የሚያመነጭ `solution.ipynb` notebook


## አሰጣጥ

ለእያንዳንዱ region፣ ዝቅተኛው ውጤት 0 ሲሆን ከፍተኛው ውጤት 1 ነው። የመጨረሻው ውጤት በአምስቱም regions (ለእያንዳንዱ ፊደል አንድ በድምሩ አራት፣ እና background) ላይ አማካይ ተወስዶ በ100 ይባዛል። **የparameter ቅጣት አለ፦**

**Modelዎ ከ20260 parameters በላይ ካለው፣ ውጤቱ በግማሽ ይቀነሳል።**

የparameters ብዛት በ`sum(p.numel() for p in model.parameters())` ይለካል። Modelዎ PyTorch `nn.Dropout` የmodelው አካል ሆኖ በstochastic modeም እንዲሠራ እንጠብቃለን።

### ለመደበኛ Regions

ለእያንዳንዱ region $R$ (የመጀመሪያው `I` ፊደል፣ `O`፣ `A`፣ `Background`)፣ modelውን በ$N_R = 512$ የፈተና ነጥቦች $(x_i, y_i)$፣ ትክክለኛ እሴቶች $v_i$ እና predictions $\hat{v}_i$ ላይ እንገመግማለን። Normalized Mean Absolute Error (MAE)ን እንደ ዋና metric እንጠቀማለን። MAE እንደሚከተለው ይገለጻል፦

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

Normalization ደግሞ እንደሚከተለው ይከናወናል፦ 

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

እዚህ $s_R > 0$ የscale ቋሚ ነው።


### ለመጨረሻው `I` ፊደል region

በዚህ region ውስጥ፣ **በግምገማ ጊዜ dropout ይነቃል**። ለእያንዳንዱ የፈተና ነጥብ $j$፦

1. $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$ን ለማግኘት modelውን $K = 10$ ጊዜ እናስኬዳለን።
2. ማንኛውም output ከክልሉ $[-2026, 2026]$ ውጭ ከሆነ፣ $\mathrm{pointScore}(j) = 0$።
3. ካልሆነ፣ የ$K$ outputsን standard deviation $\sigma_j$ አስሉና ወደ ውጤት ቀይሩት፦

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

እዚህ $s_E > 0$ የተወሰነ የscale ቋሚ ነው።

የregionው ውጤት በregionው ውስጥ ባሉ ሁሉም ነጥቦች ላይ የተወሰደ አማካይ ነው፦

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

እዚህ $N_E = K * N_R$። 

በቀላሉ ሲገለጽ፣ ያላችሁ ልዩነት በጨመረ መጠን ለዚህ region የምታገኙት ውጤት ከፍ ይላል። **PyTorch `rand*` እና `_uniform` functionsን ጨምሮ randomን በቀጥታ መጠቀም አትችሉም፤ randomness መምጣት ያለበት dropout ነቅቶ ከሚከናወን inference ነው።**

## እንዴት submission ማድረግ እንደሚቻል

1. `solution.ipynb`ን ክፈቱና ሁሉንም cells አስኪዱ።
2. በ`custom_model.py` ውስጥ ያለውን `CustomModel` model አሻሽሉ
3. የመጨረሻው cellዎ modelዎን ወደ `model.pt` file እንደሚያስቀምጥ ያረጋግጡ።
4. በJupyterLab Git tab ውስጥ `solution.ipynb`ን እና `custom_model.py`ን stage፣ comment እና commit ያድርጉ፤ ከዚያ push ያድርጉ።
5. ወደ Contest page ተመለሱና **Submit**ን ጠቅ ያድርጉ። የSubmit comment ከቀደመው ደረጃ comment ጋር ተመሳሳይ መሆን አለበት።
