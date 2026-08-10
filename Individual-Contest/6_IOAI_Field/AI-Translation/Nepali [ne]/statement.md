# IOAI Field

- **समय सीमा:** 5 minutes
- **भण्डारण:** 5 GB
- **समाधानको आकार:** `solution.ipynb`, `custom_model.py` ≤ 1 MB सँगै
- **पूर्वप्रशिक्षित मोडेलहरू:** कुनै पनि होइन — सुरुदेखि नै प्रशिक्षण गर्नुहोस्, मूल्याङ्कनको समयमा internet उपलब्ध हुँदैन
- **Baseline Score**: 31.2187
- **Scientific Committee को score:** 63.53


## कार्य

Astana का Mayor सहरलाई शैलीकृत IOAI लोगोहरूले सजाउन चाहन्छन्। एक तथ्याङ्कविद्का रूपमा, उनले लोगोसहित सबै कुरालाई एउटा स्थानिक फलन $F(x, y, \overline{W})$ का रूपमा हेर्छन्, जहाँ $x, y \in [0, 1]$ ले 2D समतलमा निर्देशाङ्कहरू जनाउँछन् र $\overline{W}$ अक्षरका रङ र कोणजस्ता शैलीगत विशेषताहरू परिभाषित गर्ने लुकेका parameters को समुच्चय हो।

$F$ लाई स्पष्ट गणितीय समीकरणका रूपमा व्यक्त गर्न अत्यन्त जटिल भएकाले, तपाईंको कार्य यसलाई सन्निकट बनाउन एउटा neural network लाई प्रशिक्षण दिनु हो। उक्त network ले कुनै पनि निर्देशाङ्क जोडी $(x, y)$ का लागि **IOAI field** को मान output गर्नेछ, जसले समतलभरि लोगोको पूर्ण heatmap visualization उत्पन्न गर्नेछ। यहाँ केही निश्चित लुकेका parameters $\overline{W}$ सहित $F$ को heatmap visualization को एउटा उदाहरण छ।

![f1](../../ioai1.png)

IOAI field के-केबाट बनेको हुन्छ? चार अक्षर र background।

- पहिलो `I` अक्षरभित्रका मानहरू linear gradient सहित अत्यन्त ठूला (1e+10 र सोभन्दा बढी) हुन्छन्
- `O` अक्षरका मानहरूले spiral pattern देखाउँछन्
- `A` अक्षरभित्रको मान सधैँ -1 हुन्छ
- अन्तिम `I` अक्षरभित्रका मानहरू एउटै बिन्दुमा दुईपटक मूल्याङ्कन गरिए पनि $[-2026,2026]$ range बाट लिइएका random मानहरू हुनुपर्छ
- अक्षरहरूबाहिरको मान सधैँ zero हुन्छ

फलनमा लुकेका parameters $\overline{W}$ छन्, जसले अक्षरहरूको scale र incline का साथै पहिलो `I` अक्षरभित्रका मानहरूको range लाई असर गर्छन्। तथापि, अक्षरहरू एकअर्कासँग प्रतिच्छेद गर्नेछैनन्। फरक-फरक $\overline{W}$ सँग IOAI field कस्तो देखिन्छ भन्ने देखाउने केही उदाहरणहरू यहाँ छन्:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**तपाईंलाई के दिइएको छ:**

यस समस्यामा कुनै datasets छैनन्। यसको सट्टा, तपाईंलाई `data/train_config/field_config.json` मा रहेको JSON config file द्वारा configure गरिएको generator function दिइएको छ। 

Test config लुकाइएको छ, तर यो उस्तै प्रकृतिको छ। तपाईंको कार्य आफूले चाहे जति data प्रयोग गरी दिइएको generator मा fit गर्नु हो। तपाईंका "train" र "test" distributions एउटै generator बाट उत्पन्न हुन्छन् — तपाईंलाई केवल कुन बिन्दुहरू $(x_i, y_i)$ मा मूल्याङ्कन गरिनेछ भन्ने थाहा हुँदैन।

तपाईंको submission मा निम्न कुरा हुनुपर्छ:
- `custom_model.py` का रूपमा save गरिएको training model class। यो model ले `torch.nn.Module` class बाट inherit गर्नुपर्छ र `torch` imports मात्र प्रयोग गर्नुपर्छ। यसमा `solution.ipynb` notebook मा प्रयोग हुने `CustomModel` class हुनुपर्छ। 
- `solution.ipynb` notebook, जसले `model.pt` weights उत्पादन गर्नेछ


## Scoring

प्रत्येक region का लागि न्यूनतम score 0 र अधिकतम score 1 हो। अन्तिम score सबै पाँचवटा regions (प्रत्येक अक्षरका लागि चारवटा र background) मा औसत निकालेर 100 ले गुणन गरिन्छ। यहाँ एउटा **parameter penalty छ:**

**यदि तपाईंको model मा 20260 भन्दा बढी parameters छन् भने, score आधा गरिन्छ।**

Parameters को सङ्ख्या `sum(p.numel() for p in model.parameters())` द्वारा मापन गरिन्छ। हामी तपाईंको model ले stochastic mode मा पनि काम गर्ने अपेक्षा गर्छौँ, जसमा PyTorch `nn.Dropout` model को अंश हुन्छ।

### Standard Regions का लागि

प्रत्येक region $R$ (पहिलो `I` अक्षर, `O`, `A`, `Background`) का लागि, हामी true values $v_i$ र predictions $\hat{v}_i$ भएका $N_R = 512$ test points $(x_i, y_i)$ मा model को मूल्याङ्कन गर्छौँ। हामी normalized Mean Absolute Error (MAE) लाई मुख्य metric का रूपमा प्रयोग गर्छौँ। MAE लाई यसरी परिभाषित गरिएको छ:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

र normalization यसरी गरिन्छ 

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

जहाँ $s_R > 0$ एउटा scale constant हो।


### अन्तिम `I` अक्षरको region का लागि

यस region मा, **मूल्याङ्कनका क्रममा dropout enabled हुन्छ**। प्रत्येक test point $j$ का लागि:

1. $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$ प्राप्त गर्न हामी model लाई $K = 10$ पटक चलाउँछौँ।
2. यदि कुनै output $[-2026, 2026]$ range बाहिर छ भने, $\mathrm{pointScore}(j) = 0$।
3. अन्यथा, $K$ outputs को standard deviation $\sigma_j$ गणना गर्नुहोस् र त्यसलाई score मा रूपान्तरण गर्नुहोस्:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

जहाँ $s_E > 0$ एउटा fixed scale constant हो।

Region score उक्त region का सबै बिन्दुहरूको औसत हो:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

जहाँ $N_E = K * N_R$। 

सरल शब्दमा, तपाईंसँग जति बढी विविधता हुन्छ, यस region का लागि तपाईंको score त्यति नै ठूलो हुनेछ। **तपाईंले pure form मा random प्रयोग गर्न सक्नुहुन्न, जसमा PyTorch का `rand*` र `_uniform` functions समेत पर्छन्; randomness enabled dropout सहितको inference बाट आउनुपर्छ।**

## कसरी submit गर्ने

1. `solution.ipynb` खोल्नुहोस् र सबै cells चलाउनुहोस्।
2. `custom_model.py` मा रहेको `CustomModel` model सुधार गर्नुहोस्
3. तपाईंको अन्तिम cell ले तपाईंको model लाई `model.pt` file मा save गर्ने सुनिश्चित गर्नुहोस्।
4. JupyterLab Git tab मा `solution.ipynb` र `custom_model.py` लाई stage, comment र commit गर्नुहोस्, त्यसपछि push गर्नुहोस्।
5. Contest page मा फर्कनुहोस् र **Submit** मा click गर्नुहोस्। Submit comment अघिल्लो चरणको comment सँग उही हुनुपर्छ।
