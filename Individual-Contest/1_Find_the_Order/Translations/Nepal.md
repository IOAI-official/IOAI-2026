# क्रम पत्ता लगाउनुहोस्

- **समय सीमा:** 10 minutes
- **वातावरण:** एउटा GPU (≈16 GB VRAM), internet छैन
- **समाधानको आकार:** `solution.ipynb` ≤ 1 MB
- **भण्डारण:** 5 GB 

## समस्या

तपाईंलाई दुई सहभागी, *Speaker A* र *Speaker B*, बीचका बोलिएका अंग्रेजी संवादहरू दिइएका छन्। प्रत्येक संवादलाई वक्ताका पालोहरूमा विभाजन गरिएको छ, जहाँ प्रत्येक पालोमा एक जना वक्ताको मात्र बोली समावेश हुन्छ। प्रत्येक पालोलाई छुट्टै `.wav` audio file का रूपमा भण्डारण गरिएको छ, त्यसैले पूर्ण संवादलाई प्रत्येक पालोका लागि एउटा गरी `.wav` files को set ले प्रतिनिधित्व गर्छ। 

दुर्भाग्यवश, पालोहरूलाई अनियमित रूपमा फेरबदल गरिएको छ, त्यसैले वार्तालाप अब अर्थपूर्ण छैन। फाइलनाम `chunk_{k}.wav` मा, `k` ले फेरबदल गरिएको set को k-th chunk जनाउँछ, मूल संवादको k-th पालो होइन।

**‼️ तपाईंको कार्य वार्तालापको मूल कालानुक्रमिक क्रम पुनर्निर्माण गर्नु हो।**

![क्रम पत्ता लगाउनुहोस्](../find_the_order.jpg)

---

## Dataset

प्रत्येक संवादमा `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav` नाम भएका `n` audio files हुन्छन्। chunks अलग-अलग पालोहरू हुन्। फाइलनामहरू फेरबदल गरिएको क्रमसँग मात्र सम्बन्धित हुन्छन्। तिनले मूल वार्तालापमा कुनै chunk कहाँ पर्छ भन्ने जनाउँदैनन्। प्रत्येक संवादमा 7–20 chunks, mono, 44.1 kHz हुन्छन् (तपाईंले
resample गर्न सक्नुहुन्छ)।

**`prefix.json` मा प्रत्येक संवादका पहिलो दुई chunks का फाइलनाम indexes हुन्छन्।** यसले संवादको वास्तविक सुरुवात पहिचान गर्छ र वार्तालापलाई अगाडिबाट वा पछाडिबाट पढ्ने बीचको द्विविधा हटाउँछ।

उदाहरणका लागि: `11: [7, 12]` को अर्थ संवाद 11 का पहिलो र दोस्रो पालो क्रमशः `chunk_7.wav` र `chunk_12.wav` हुन्।

### तपाईंले के पाउनुहुन्छ

तपाईंले **समान format भएका दुई folders** प्राप्त गर्नुहुन्छ:

| Folder | संवादहरू | `answers.json`? | यसको प्रयोग |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ समावेश गरिएको | आफ्नो model लाई train / fine-tune गर्न |
| `dataset/test_public/`  | 100   | ✅ समावेश गरिएको | आफ्नो pipeline चलाउन र स्थानीय रूपमा आफ्नै score गणना गर्न |

grading का बेला, तपाईंको `dataset/test_public/` folder लाई पारदर्शी रूपमा
एउटा `hidden evaluation set` (public leaderboard का लागि `test_leaderboard_a` र final leaderboard का लागि `test_leaderboard_b`) द्वारा प्रतिस्थापन गरिन्छ — यिनको आकार र format `dataset/test_public/` कै जस्तो हुन्छ तर `answers.json` हुँदैन।

तपाईंको notebook लाई उक्त data मा फेरि चलाइन्छ, र यसले उत्पादन गरेको `answers.json` file scoring का लागि प्रयोग गरिन्छ। छुट्याएर राखिएका test dialogues `train` कै distribution बाट आउँछन्, त्यसैले तपाईंको स्थानीय `test_public` score भरपर्दो पूर्वावलोकन हो।

### Directory संरचना

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

## Output

प्रत्येक संवादका लागि, यसका audio chunks को मूल कालानुक्रमिक क्रम निर्धारण गर्नुहोस्। तपाईंको prediction `{0, 1, …, n−1}` को एउटा permutation `P` हुनुपर्छ, जहाँ `P[i]` भनेको `chunk_i.wav` को अनुमानित कालानुक्रमिक स्थान हो (0 = पहिलो)।

तपाईंको output file `answers.json` ले प्रत्येक dialogue ID लाई यसको अनुमानित permutation सँग map गर्नुपर्छ:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### उदाहरण

एउटा संवादमा 3 वटा फेरबदल गरिएका chunks `chunk_0, chunk_1, chunk_2` छन्:

| फेरबदल गरिएको chunk | बोलिएको सामग्री | वास्तविक स्थान (rank) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (अन्तिम) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (पहिलो) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

वास्तविक क्रम **chunk_1 → chunk_2 → chunk_0** हो, त्यसैले `P = [2, 0, 1]`, र `prefix.json` मा `[1, 2]` हुन्छ।

⚠️ **P वास्तविक permutation हुनैपर्छ:** लम्बाइ n, 0-indexed, प्रत्येक value ठ्याक्कै एक पटक। Duplicates, छुटेका values वा दायराबाहिरका entries (जस्तै 1-indexed) भएमा उक्त संवादका लागि score 0 हुन्छ; file मा नभएको संवादका लागि पनि त्यस्तै हुन्छ। गलत संरचना भएको वा non-JSON file अस्वीकार गरिन्छ।

## Scoring

यस कार्यको scoring **जोडागत क्रम शुद्धता (pairwise ordering accuracy)** हो। यसले chunks का प्रत्येक जोडी जाँच्छ र सोध्छ: _यी दुईमध्ये कुन पहिले आउनुपर्छ?_ यदि तपाईंको prediction ले ground truth कै जस्तो उत्तर दिन्छ भने जोडी सही हुन्छ। `n` chunks भएको संवादमा $$M = n(n-1)/2$$ pairs हुन्छन्; `I` लाई inversions को सङ्ख्या — ground truth भन्दा फरक क्रममा राखिएका pairs — मान्नुहोस्:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **अन्तिम score उक्त split का सबै
संवादहरूको प्रति-संवाद scores को औसत हो।**

## अनुमति प्राप्त models

तपाईंले training र evaluation दुवैका क्रममा यो कार्य समाधान गर्न निम्न pre-trained models मात्र प्रयोग गर्न सक्नुहुन्छ। यी सबै models पहिले नै download गरिएका छन् र environment मा उपलब्ध छन्। तिनलाई कसरी प्रयोग गर्ने भन्ने उदाहरण baseline notebook `solution.ipynb` मा हेर्न सक्नुहुन्छ। कृपया ध्यान दिनुहोस्, तपाईंले अन्य कुनै model प्रयोग गर्न सक्नुहुन्न, र तपाईंको program सँग internet access छैन।

- **Speech representations:** **wav2vec 2.0**। **Whisper encoder** लाई feature extractor का रूपमा पनि प्रयोग गर्न सकिन्छ।
[wav2vec model card](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **स्वचालित वाक् पहिचान (ASR):** **OpenAI Whisper** (कुनै पनि size)।
[Whisper model card](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Language model:** **Qwen2.5-0.5B**, जसलाई zero-shot रूपमा वा उपलब्ध गराइएको `train` split मा fine-tune गरेर प्रयोग गर्न सकिन्छ।
[Qwen model card](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
ध्यान दिनुहोस्, 10-minute सीमा अन्तर्गत grade का बेला तपाईंले गर्ने कुनै पनि training वा fine-tuning र evaluation set मा गरिने inference दुवै समेटिनुपर्छ।

## कसरी submit गर्ने

- `solution.ipynb` खोल्नुहोस् र सबै cells चलाउनुहोस्। यसले working directory मा `answers.json` लेख्छ र `dataset/test_public/` का प्रत्येक संवादका लागि permutation समावेश गर्छ (100 dialogues) भन्ने निश्चित गर्नुहोस्। grade का बेला notebook लाई hidden test set मा फेरि चलाइन्छ र त्यहाँ यसले उत्पादन गरेको `answers.json` को score गणना गरिन्छ।
- चाहनुहुन्छ भने समाधान सुधार गर्नुहोस् — वा नगर्नुहोस्; baseline ले मात्र पनि pipeline validate गर्छ।
- JupyterLab को बायाँ sidebar मा रहेको Git tab खोल्नुहोस्।
- `solution.ipynb` लाई **Stage** गर्नुहोस् (यसको छेउमा रहेको + icon)।
- commit message प्रविष्ट गर्नुहोस् र **Commit** मा click गर्नुहोस्।
- push गर्न cloud-with-up-arrow मा click गर्नुहोस्।
- यो Contest page मा फर्कनुहोस् र **Submit** मा click गर्नुहोस्।

ठ्याक्कै एउटा file submit गर्नुहोस्, जसको नाम `solution.ipynb` हो।
