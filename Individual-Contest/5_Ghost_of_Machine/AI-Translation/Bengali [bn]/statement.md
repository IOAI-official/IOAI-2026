# যন্ত্রের ভূত

- **সময়সীমা:** 10 minutes
- **Baseline স্কোর:** 28.6
- **Scientific Committee স্কোর:** 93.41
- **পরিবেশ:** একটি GPU (≈16 GB VRAM), internet নেই
- **সমাধানের আকার:** `solution.ipynb` ≤ 20 MB
- **Storage:** 5 GB
- **Pretrained model:** শুধুমাত্র **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — একটি text **encoder** (embedding model)।


## কাজ

কাজাখস্তানের জাতীয় আর্কাইভে অদ্ভুত সব ঘটনা ঘটছে। গ্রন্থাগারিকেরা বলছেন, কিছু বই আগে ভিন্নভাবে শেষ হতো, কিন্তু কেউ তা প্রমাণ করতে পারছেন না — প্রতিটি কপি একই, এবং প্রতিটি গল্প এখনও অর্থপূর্ণ। পরিবর্তনগুলো খুঁজে বের করার জন্য আপনাকে একজন AI গবেষক হিসেবে আমন্ত্রণ জানানো হয়েছে।
![ভূত](../../ghost.jpg)

একটি passage মানুষের লেখা text হিসেবে শুরু হয় এবং কোনো এক পর্যায়ে নিঃশব্দে
একটি language model দ্বারা তৈরি continuation-এ পরিবর্তিত হয়। সম্পূর্ণটা একসঙ্গে পড়লে এটিকে
একটি সুসংগত রচনা বলে মনে হয় — কিন্তু মাঝের কোথাও লেখক একজন মানুষ থেকে
একটি যন্ত্রে পরিবর্তিত হন। আপনার কাজ হলো **সেই পরিবর্তনের স্থানটি খুঁজে বের করা: যে character index-এ
মানুষের লেখা অংশটি শেষ হয় এবং যন্ত্রের লেখা অংশটি শুরু হয়**।

প্রতিটি sample একটি একক string `text`। ঠিক একটি boundary রয়েছে। এর
আগের সবকিছু মানুষের লেখা; এটি থেকে শুরু করে পরের সবকিছু যন্ত্র দ্বারা তৈরি।

## Dataset

Plain-text ইংরেজি passage, প্রতিটিতে একটি করে boundary।

- **Part A** (boundary-এর আগে): মানুষের লেখা text-এর একটি excerpt।
- **Part B** (boundary থেকে শুরু করে): Part A-এর ওপর conditioned একটি language model-এর তৈরি continuation।
- প্রতিটি অংশে অন্তত 180 words রয়েছে; মোট দৈর্ঘ্য ~500–800 words।
- **`boundary_char_index`** হলো সেই character offset যেখানে Part A শেষ হয়:
  `text[:boundary_char_index]` হলো মানুষের লেখা অংশ এবং
  `text[boundary_char_index:].lstrip()` হলো যন্ত্রের লেখা অংশ।

#### আপনি যা পাবেন

আপনি **দুটি folder** পাবেন:

| Folder | Samples | `answers.jsonl`? | এটি ব্যবহার করুন |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ অন্তর্ভুক্ত | আপনার পদ্ধতিকে train / fine-tune করতে |
| `dataset/test_public/`  | 380   | ✅ অন্তর্ভুক্ত (dev copy) | আপনার pipeline চালাতে এবং স্থানীয়ভাবে self-score করতে |

**মূল্যায়নের সময়** আপনার `dataset/test_public/` folder-টি একটি গোপন
evaluation set দিয়ে **প্রতিস্থাপন করা হয়**। এটির format একই, তবে এতে **`answers.jsonl` নেই**। আপনার
notebook এটির ওপর পুনরায় চালানো হয়, এবং এটি যে `answers.jsonl` তৈরি করে সেটির score নির্ধারণ করা হয়।

- public leaderboard একটি গোপন **test_leaderboard_a** set (380 samples) ব্যবহার করে।

- চূড়ান্ত ranking একটি গোপন **test_leaderboard_b** set (380 samples) ব্যবহার করে।

তিনটি evaluation
set-ই একই আকারের এবং `train`-এর মতো একই distribution থেকে নেওয়া, তাই আপনার স্থানীয়
`dataset/test_public/` score আপনার leaderboard score-এর একটি যুক্তিসংগত estimation।

#### Disk-এ format

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- `answers.jsonl`-এর Id-গুলো `data.jsonl`-এর Id-গুলোর সঙ্গে মেলে।
- আপনি যখনই train বা fine-tune করবেন, `dataset/train/` (উত্তরসহ) উপলভ্য থাকবে।

## Output (submission format)

আপনাকে **একটি মাত্র notebook জমা দিতে হবে, যার নাম অবশ্যই `solution.ipynb` হতে হবে**। ঠিক এই file name-টিই আবশ্যক। অন্য যেকোনো কিছু চালানো ছাড়াই প্রত্যাখ্যান করা হবে।

আপনার notebook-কে অবশ্যই **`dataset/test_public/data.jsonl` পড়তে হবে** এবং repository root-এ একটি মাত্র file
**`answers.jsonl`** লিখতে হবে — প্রতি line-এ একটি JSON object, যা
প্রতিটি sample id-কে আপনার পূর্বানুমান করা boundary character index-এর সঙ্গে map করবে:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` অবশ্যই **`[0, len(text)]`-এর মধ্যে একটি integer** হতে হবে।
- `dataset/test_public/data.jsonl`-এর প্রতিটি id ঠিক একবার উপস্থিত হওয়া উচিত। `answers.jsonl` থেকে অনুপস্থিত কোনো sample
  (অথবা non-integer / out-of-range value-সহ কোনো sample) সেই sample-এর জন্য 0
  score পাবে।

## Scoring

প্রতিটি sample-এর জন্য, `p`-কে আপনার পূর্বানুমান করা index এবং `t`-কে প্রকৃত boundary ধরা যাক। প্রতি-sample score character distance-এর সঙ্গে সূচকীয়ভাবে হ্রাস পায়:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

এর ফলে score-এর আচরণ নিম্নরূপ হয়:
- **=1.0** — একদম সঠিক boundary character;
- **≈0.78** — 25 characters দূরে; - **≈0.61** — 50 characters দূরে;
- **≈0.37** — 100 characters দূরে;
- **≈0.01** — 500 characters দূরে।

**চূড়ান্ত score হলো split-এর সব sample-এর প্রতি-sample score-এর mean**
(0–100 scale-এ প্রকাশিত)। Metric-টি শুধু একদম সঠিক হওয়াকেই নয়, *কাছাকাছি* হওয়াকেও পুরস্কৃত করে।

## Constraints

- **পরিবেশ:** একটি GPU (≈16 GB VRAM), মূল্যায়নের সময় internet নেই — অনুমোদিত
  model-টি (নিচে) ইতিমধ্যেই সরবরাহ করা আছে। **Wall-clock budget: 10 minutes**
  পুরো run-এর জন্য — মূল্যায়নের সময় আপনি যে training / fine-tuning করবেন
  **এবং** evaluation set-এর ওপর inference, উভয়ই এর মধ্যে সম্পন্ন করতে হবে।
- **অনুমোদিত pretrained model** — এই তালিকাই সম্পূর্ণ; অন্য কোনো pretrained weights
  ব্যবহার করা যাবে না। এটি **পরিবেশে আগে থেকেই সরবরাহ করা আছে** (স্বাভাবিকভাবে load করুন, যেমন
  `from_pretrained`; মূল্যায়নের সময় internet থাকবে না):
  - **bge-base-en-v1.5** — একটি 110M-parameter text **encoder** (embedding model)। এটি
    sentence/passage embedding তৈরি করে; এটি কোনো generative language model নয়। আপনি
    এটিকে **বর্তমান অবস্থাতেই (frozen features) ব্যবহার করতে পারেন অথবা `train` split-এর ওপর fine-tune করতে পারেন**
    (full fine-tuning 16 GB / 10-minute budget-এর মধ্যে সম্পন্ন হয়)।
- Classical / statistical tool-এর ওপর কোনো বিধিনিষেধ নেই: আপনি নিজে গণনা করা embedding feature-এর
  ওপর যেকোনো feature-based model (যেমন, scikit-learn classifier বা regressor) তৈরি করতে পারেন।
  *Pretrained deep-learning weights* শুধু ওপরের তালিকা অনুযায়ী সীমাবদ্ধ।

## Baseline

প্রদত্ত `solution.ipynb` একটি তুচ্ছ reference: এটি `dataset/train/` থেকে একটি একক
"average boundary fraction" estimate করে এবং প্রতিটি test passage-এর জন্য length-এর একই fraction
পূর্বানুমান করে। এটি গোপন **test_leaderboard_a** split-এ **28.6** score করে এবং কেবল
read-`dataset/test_public/` → write-`answers.jsonl` loop-এর একটি runnable template হিসেবে রয়েছে।

একই split এবং একই 10-minute budget-এ পরিমাপ করা **Scientific Committee score 93.41**
এসেছে `train`-এর ওপর অনুমোদিত encoder-টিকে fine-tune করা এবং sentence-গুলোর ওপর changepoint হিসেবে
switch-টি শনাক্ত করা থেকে। এটি কোনো upper bound নয় — এই metric-এ সর্বোচ্চ score 100।
