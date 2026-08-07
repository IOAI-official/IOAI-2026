# मेसिनको भूत

- **समय सीमा:** 10 minutes
- **Baseline स्कोर:** 28.6
- **वैज्ञानिक समितिको स्कोर:** 93.41
- **वातावरण:** one GPU (≈16 GB VRAM), इन्टरनेट छैन
- **समाधानको आकार:** `solution.ipynb` ≤ 20 MB
- **भण्डारण:** 5 GB
- **Pretrained models:** केवल **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — एउटा पाठ **encoder** (embedding model)।


## कार्य

Kazakhstan को National Archive मा अनौठा घटनाहरू भइरहेका छन्। पुस्तकालयकर्मीहरू भन्छन् कि केही पुस्तकहरू पहिले फरक तरिकाले अन्त्य हुन्थे, तर कसैले पनि यो प्रमाणित गर्न सक्दैन — प्रत्येक प्रति उस्तै छ, र प्रत्येक कथाले अझै पनि अर्थ दिन्छ। परिवर्तनहरू पत्ता लगाउन तपाईंलाई AI अनुसन्धानकर्ताका रूपमा आमन्त्रित गरिएको छ।
![भूत](../../ghost.jpg)

एउटा अनुच्छेद मानवद्वारा लिखित पाठका रूपमा सुरु हुन्छ र कुनै बिन्दुमा चुपचाप भाषा मोडेलद्वारा उत्पन्न गरिएको निरन्तरतामा
परिवर्तन हुन्छ। समग्रमा पढ्दा, यो एउटै सुसङ्गत रचनाजस्तो देखिन्छ — तर बीचमा कतै लेखक
मानिसबाट मेसिनमा परिवर्तन हुन्छ। तपाईंको कार्य **त्यो परिवर्तन पत्ता लगाउनु हो: मानव भाग अन्त्य हुने र
मेसिन भाग सुरु हुने character index**।

प्रत्येक sample एउटा एकल string `text` हो। ठ्याक्कै एउटा सीमा छ। त्यसअघिको सबै कुरा
मानवद्वारा लिखित हो; त्यस बिन्दुदेखि पछाडिको सबै कुरा मेसिनद्वारा उत्पन्न गरिएको हो।

## Dataset

Plain-text अङ्ग्रेजी अनुच्छेदहरू, प्रत्येकमा एउटा सीमा।

- **भाग A** (सीमाअघि): मानवद्वारा लिखित पाठको एउटा अंश।
- **भाग B** (सीमादेखि अगाडि): भाग A मा conditioned गरिएको भाषा मोडेलद्वारा उत्पन्न निरन्तरता।
- प्रत्येक भाग कम्तीमा 180 words को हुन्छ; कुल लम्बाइ ~500–800 words हुन्छ।
- **`boundary_char_index`** भनेको भाग A अन्त्य हुने character offset हो:
  `text[:boundary_char_index]` मानव भाग हो र
  `text[boundary_char_index:].lstrip()` मेसिन भाग हो।

#### तपाईंले के पाउनुहुन्छ

तपाईंले **दुईवटा folders** प्राप्त गर्नुहुन्छ:

| Folder | Samples | `answers.jsonl`? | यसको प्रयोग |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ समावेश गरिएको | आफ्नो विधि train / fine-tune गर्न |
| `dataset/test_public/`  | 380   | ✅ समावेश गरिएको (dev copy) | आफ्नो pipeline चलाउन र स्थानीय रूपमा self-score गर्न |

**मूल्याङ्कनको समयमा** तपाईंको `dataset/test_public/` folder लाई **लुकेको
evaluation set ले प्रतिस्थापन गरिन्छ**। यसको format उही हुन्छ तर **`answers.jsonl` बिना**। तपाईंको
notebook यसमा पुनः चलाइन्छ, र यसले उत्पादन गरेको `answers.jsonl` को स्कोर गणना गरिन्छ।

- सार्वजनिक leaderboard ले लुकेको **test_leaderboard_a** set (380 samples) प्रयोग गर्छ।

- अन्तिम ranking ले लुकेको **test_leaderboard_b** set (380 samples) प्रयोग गर्छ।

तीनैवटा evaluation
sets को आकार उही छ र तिनीहरू `train` कै distribution बाट लिइएका छन्, त्यसैले तपाईंको स्थानीय
`dataset/test_public/` स्कोर तपाईंको leaderboard स्कोरको उचित अनुमान हो।

#### डिस्कमा रहेको format

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- `answers.jsonl` का Ids `data.jsonl` का ids सँग मेल खान्छन्।
- तपाईंले train वा fine-tune गर्दा `dataset/train/` (उत्तरहरूसहित) उपलब्ध हुन्छ।

## Output (submission format)

तपाईंले **एउटा मात्र notebook submit गर्नुपर्छ, जसको नाम `solution.ipynb` हुनैपर्छ**। यो ठ्याक्कै यही file name हुनु आवश्यक छ। अरू कुनै पनि नाम भएको file नचलाईकनै अस्वीकार गरिन्छ।

तपाईंको notebook ले **`dataset/test_public/data.jsonl` पढ्नुपर्छ** र repository root मा एउटा मात्र file
**`answers.jsonl`** लेख्नुपर्छ — प्रत्येक line मा एउटा JSON object, जसले
प्रत्येक sample id लाई तपाईंले अनुमान गरेको boundary character index सँग map गर्छ:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` **`[0, len(text)]` भित्रको integer हुनैपर्छ**।
- `dataset/test_public/data.jsonl` मा भएको प्रत्येक id ठ्याक्कै एकपटक देखा पर्नुपर्छ। `answers.jsonl` बाट छुटेको
  sample (वा non-integer / दायराबाहिरको value भएको sample) ले त्यस sample का लागि 0
  स्कोर पाउँछ।

## स्कोरिङ

प्रत्येक sample का लागि, `p` तपाईंले अनुमान गरेको index र `t` वास्तविक सीमा मान्नुहोस्। प्रति-sample स्कोर character distance सँगै exponential रूपमा घट्छ:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

यसले स्कोरमा निम्न व्यवहार निम्त्याउँछ:
- **=1.0** — ठ्याक्कै boundary character;
- **≈0.78** — 25 characters को फरक; - **≈0.61** — 50 characters को फरक;
- **≈0.37** — 100 characters को फरक;
- **≈0.01** — 500 characters को फरक।

**अन्तिम स्कोर split का सबै samples का प्रति-sample स्कोरहरूको mean हो**
(0–100 scale मा report गरिन्छ)। Metric ले ठ्याक्कै मिलेको मात्र होइन, *नजिक* पुगेकोलाई पनि पुरस्कृत गर्छ।

## सीमाहरू

- **वातावरण:** one GPU (≈16 GB VRAM), मूल्याङ्कनको समयमा इन्टरनेट हुँदैन — अनुमति दिइएको
  model (तल) पहिले नै उपलब्ध गराइएको हुन्छ। **Wall-clock budget: 10 minutes**
  सम्पूर्ण run का लागि — यसले मूल्याङ्कनको समयमा तपाईंले गर्ने कुनै पनि training / fine-tuning
  **र** evaluation set मा inference दुवै समेट्नुपर्छ।
- **अनुमति दिइएको pretrained model** — यो सूची पूर्ण हो; अन्य कुनै pretrained weights
  प्रयोग गर्न पाइँदैन। यो **वातावरणमा पहिले नै उपलब्ध गराइएको हुन्छ** (यसलाई सामान्य रूपमा load गर्नुहोस्, जस्तै
  `from_pretrained`; मूल्याङ्कनको समयमा इन्टरनेट हुँदैन):
  - **bge-base-en-v1.5** — 110M-parameter भएको पाठ **encoder** (embedding model)। यसले
    sentence/passage embeddings उत्पादन गर्छ; यो generative language model होइन। तपाईंले
    यसलाई **जस्ताको तस्तै (frozen features) प्रयोग गर्न वा `train` split मा fine-tune गर्न**
    सक्नुहुन्छ (full fine-tuning 16 GB / 10-minute budget भित्र अटाउँछ)।
- Classical / statistical tools मा कुनै प्रतिबन्ध छैन: तपाईंले आफैँ गणना गरेका embedding features माथि
  कुनै पनि feature-based model (जस्तै, scikit-learn classifiers वा regressors) बनाउन सक्नुहुन्छ।
  *Pretrained deep-learning weights* माथिको सूचीमा मात्र सीमित छन्।

## Baseline

उपलब्ध गराइएको `solution.ipynb` एउटा साधारण सन्दर्भ हो: यसले `dataset/train/` बाट एउटै
"औसत boundary fraction" अनुमान गर्छ र प्रत्येक test passage का लागि त्यसको लम्बाइको उही fraction
अनुमान गर्छ। यसले लुकेको **test_leaderboard_a** split मा **28.6** स्कोर गर्छ र
read-`dataset/test_public/` → write-`answers.jsonl` loop का लागि चलाउन मिल्ने template का रूपमा मात्र
रहेको छ।

**वैज्ञानिक समितिको 93.41 स्कोर**, उही split र उही
10-minute budget मा मापन गरिएको, अनुमति दिइएको encoder लाई `train` मा fine-tune गरेर र
sentence हरूमाथि changepoint का रूपमा परिवर्तन पत्ता लगाएर प्राप्त भएको हो। यो upper bound होइन — यस
metric मा अधिकतम 100 हो।
