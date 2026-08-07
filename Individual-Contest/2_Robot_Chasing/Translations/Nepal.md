# रोबोटको पछ्याइ

- **समय सीमा:** 5 minutes
- **वातावरण:** एउटा GPU (≈16 GB VRAM), इन्टरनेट छैन
- **समाधानको आकार:** `solution.ipynb` ≤ 1 MB
- **भण्डारण:** 5 GB 

## कार्य

छवटा रोबोट छन्। प्रत्येक रोबोटले ग्रिडद्वारा निरूपित एउटा सानो कोठामा काम गर्छ। प्रत्येक कोठामा भित्ताहरूले घेरिएको `6×6` खेल्न मिल्ने क्षेत्र हुन्छ, त्यसैले पूर्ण `image` array को आकार `8×8` (खेल्न मिल्ने क्षेत्र + भित्ताहरू) हुन्छ।

प्रत्येक रोबोटले एउटा कार्य वर्णन गर्ने अङ्ग्रेजी निर्देशन प्राप्त गर्छ। रोबोटले उक्त कार्य गरिरहेको कुनै पनि बिन्दुमा snapshot लिइएको हुन सक्छ। तपाईंको लक्ष्य रोबोटको अर्को action को पूर्वानुमान गर्नु हो।

रोबोटहरूले सधैँ सबैभन्दा छोटो बाटो पछ्याउँदैनन्। Robot 0 ले Robot 1 भन्दा फरक व्यवहार गर्न सक्छ, तर प्रत्येक रोबोटले आफ्नै सुसङ्गत ढाँचा पछ्याउँछ। यी ढाँचाहरू सिक्न सही अर्को actions समावेश भएका training उदाहरणहरू प्रयोग गर्नुहोस्।

![रोबोट](../robot.jpg)

मिसनका तीन प्रकार छन्:

- कुनै वस्तुमा **जानुहोस्**, उदाहरणका लागि `"approach the red ball"`;
- कुनै वस्तु **उठाउनुहोस्**, उदाहरणका लागि `"grab the blue key"`;
- **एउटा वस्तुलाई अर्कोको छेउमा राख्नुहोस्**, उदाहरणका लागि
  `"place the red box beside the green ball"`।

एउटै निर्देशन धेरै तरिकाले लेखिएको हुन सक्छ। test set मा परिचित वाक्यांश, रङ र वस्तुका प्रकारका नयाँ संयोजनहरू हुन सक्छन्। यद्यपि, test set मा प्रयोग भएका हरेक शब्द, वाक्यांशको ढाँचा, रङ, वस्तुको प्रकार र मिसनको प्रकार training set मा पनि देखा पर्छन्।

प्रत्येक sample मा निम्न fields हुन्छन्:

| Field | अर्थ |
|---|---|
| `robot_id` | यो 6 रोबोटमध्ये कुन हो (`0`–`5`) |
| `image` | कोठा, एउटा `8×8×2` integer array जसमा channel 0 ले categorical object_idx (जस्तै, 1=खाली, 2=भित्ता, 10=रोबोट) र channel 1 ले categorical colour_idx (0–5) राख्छ। |
| `direction` | रोबोटले हाल सामना गरिरहेको दिशा |
| `mission` | देखिने प्राकृतिक-भाषाको निर्देशन |
| `carrying` | बोकिएको वस्तुका लागि `null` वा `[object_idx, colour_idx]` |

Rows अनियमित क्रममा रहेका स्वतन्त्र snapshots हुन्। तिनीहरूले episodes बनाउँदैनन्, र evaluation को समयमा कुनै अघिल्लो observation वा action उपलब्ध हुँदैन।

उपलब्ध गराइएको `visualize_dataset.ipynb` ले तपाईंलाई विभिन्न परिस्थितिहरूमा model लाई उपलब्ध observations निरीक्षण गर्न दिन्छ।

## ग्रिड encoding

`image[row][column] = [object_idx, colour_idx]`। पहिलो index माथिदेखि तलसम्मको row हो, र दोस्रो बायाँदेखि दायाँसम्मको column हो। array मा बाहिरी भित्ताको किनारा समावेश छ, त्यसैले आवागमनयोग्य भित्री भाग `6×6` हो।

वस्तुका ids:

| id | वस्तु |
|---:|---|
| 1 | खाली cell |
| 2 | भित्ता |
| 5 | साँचो |
| 6 | बल |
| 7 | बाकस |
| 10 | रोबोट |
| 11 | token |

Tokens कोठामा देखा पर्न सक्छन् तर मिसनहरूमा तिनको नाम कहिल्यै उल्लेख हुँदैन।

रङका ids `0` रातो, `1` हरियो, `2` नीलो, `3` बैजनी, `4` पहेँलो र `5` खैरो हुन्। खाली cells र भित्ताहरूका लागि colour channel को कुनै अर्थ हुँदैन।

image मा माथिका दुई channels मात्र छन्। रोबोटको दिशा top-level `direction` field मा एकपटक प्रदान गरिएको हुन्छ; यसलाई `image` भित्र दोहोर्‍याइएको हुँदैन।

## Actions

Codes `0`–`3` का लागि, movement actions ले निम्न absolute mapping प्रयोग गर्छन्:

| action | अर्थ |
|---:|---|
| 0 | माथि सर्नुहोस् |
| 1 | तल सर्नुहोस् |
| 2 | बायाँ सर्नुहोस् |
| 3 | दायाँ सर्नुहोस् |
| 4 | उठाउनुहोस् |
| 5 | राख्नुहोस् |


`direction` field ले हालको अभिमुखीकरण यसरी जनाउँछ: 0 = माथि (row - 1), 1 = तल (row + 1), 2 = बायाँ (col - 1), 3 = दायाँ (col + 1)।

एउटा movement action ले पहिले रोबोटलाई उक्त absolute दिशातर्फ फर्काउँछ र त्यसपछि त्यसलाई एक cell सार्ने प्रयास गर्छ। भित्ता वा वस्तुले चाल रोक्न सक्छ, तर दिशा भने अझै परिवर्तन हुन्छ। `pick up` र `drop` ले direction द्वारा परिभाषित छेउको target cell मा मात्र कार्य गर्छन् (जस्तै, direction=0 भएमा, यसले (row - 1, col) मा कार्य गर्छ)।

## Dataset

तपाईंले दुई folders प्राप्त गर्नुहुन्छ:

| Folder | Rows | `labels.json`? | यसको प्रयोग |
|---|---:|---|---|
| `dataset/train/` | 60,000 | समावेश गरिएको | आफ्नो model train गर्न |
| `dataset/test_public/` | 3,600 | development copy मा समावेश गरिएको | आफ्नो pipeline चलाउन र आफैँ score गर्न |

प्रत्येक folder मा माथि वर्णन गरिएका samples को JSON list, `observations.json`, हुन्छ।
`labels.json` actions (`0`–`5`) को aligned JSON list हो।

training set मा प्रत्येक रोबोटका लागि ठ्याक्कै 10,000 rows र प्रत्येक
task family बाट 20,000 rows छन्। public test मा प्रत्येक रोबोटका लागि 600 rows छन्। तपाईंलाई array चाहिएमा `image` लाई
`numpy.asarray(...)` ले wrap गर्नुहोस्।

grade गर्ने समयमा, `dataset/test_public/` लाई पारदर्शी रूपमा उही format का
3,600 observations भएको, तर `labels.json` नभएको hidden set ले प्रतिस्थापन गर्छ। public
leaderboard ले `test_leaderboard_a` प्रयोग गर्छ; final ranking ले
`test_leaderboard_b` प्रयोग गर्छ। test labels लाई बिना सर्त पढ्ने notebook असफल हुनेछ।
Labels केवल `dataset/train/` बाट पढ्नुहोस्।

## Output

notebook को working directory मा `predictions.json` लेख्नुहोस्। यो `dataset/test_public/observations.json` को प्रत्येक row का लागि
एउटा integer action (`0`–`5`) उही क्रममा समावेश गर्ने JSON
list हुनुपर्छ। छवटा samples भएको काल्पनिक test set का लागि, मान्य output यस्तो हुनेछ:

```json
[0, 3, 2, 2, 5, 4]
```

हराएको वा अमान्य JSON file, गलत सङ्ख्याका predictions, non-integer value,
वा `{0,1,2,3,4,5}` बाहिरको action लाई score नदिई अस्वीकार गरिन्छ।

## Scoring

Scoring `0`–`100` scale मा **प्रति-रोबोट औसत accuracy** हो। Accuracy पहिले
प्रत्येक रोबोटका लागि स्वतन्त्र रूपमा गणना गरिन्छ, त्यसपछि सबै छवटा रोबोटमाथि औसत निकालिन्छ। त्यसैले हरेक
रोबोटको weight बराबर हुन्छ।

## कसरी submit गर्ने

1. `solution.ipynb` खोल्नुहोस् र सबै cells चलाउनुहोस्।
2. यसले public test set का लागि 3,600 predictions सहित `predictions.json` लेख्छ भन्ने पुष्टि गर्नुहोस्।
3. चाहनुहुन्छ भने model सुधार्नुहोस्; उपलब्ध गराइएको baseline ले आवश्यक input र output format मात्र देखाउँछ।
4. JupyterLab Git tab मा `solution.ipynb` लाई stage र commit गर्नुहोस्, त्यसपछि push गर्नुहोस्।
5. प्रतियोगिता पृष्ठमा फर्कनुहोस् र **Submit** मा click गर्नुहोस्।

`solution.ipynb` नामको ठ्याक्कै एउटा file submit गर्नुहोस्।
