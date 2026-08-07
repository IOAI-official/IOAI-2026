# የማሽኑ መንፈስ

- **የጊዜ ገደብ፦** 10 ደቂቃዎች
- **የመነሻ ነጥብ፦** 28.6
- **አካባቢ፦** አንድ GPU (≈16 GB VRAM)፣ ኢንተርኔት የለም
- **የመፍትሔ መጠን፦** `solution.ipynb` ≤ 20 MB
- **ማከማቻ፦** 5 GB
- **ቀድመው የሰለጠኑ ሞዴሎች፦** **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** ብቻ — የጽሑፍ **encoder** (embedding model)።


## ተግባር

በካዛክስታን ብሔራዊ መዝገብ ቤት እንግዳ ነገሮች እየተከሰቱ ነው። የቤተ መጻሕፍት ሠራተኞች አንዳንድ መጻሕፍት ቀደም ሲል በተለየ ሁኔታ ይጠናቀቁ እንደነበር ይናገራሉ፤ ነገር ግን ማንም ማረጋገጥ አይችልም — እያንዳንዱ ቅጂ ተመሳሳይ ነው፣ እና እያንዳንዱ ታሪክ አሁንም ትርጉም ይሰጣል። ለውጦቹን እንዲያገኙ እንደ AI ተመራማሪ ተጋብዘዋል።
![መንፈስ](../ghost.jpg)

አንድ ምንባብ በሰው የተጻፈ ጽሑፍ ሆኖ ይጀምራል፣ እና በአንድ ነጥብ ላይ ሳይታወቅ
በቋንቋ ሞዴል ወደተፈጠረ ቀጣይ ጽሑፍ ይቀየራል። በአጠቃላይ ሲነበብ፣
አንድ ወጥ ጽሑፍ ይመስላል — ነገር ግን መሀሉ ላይ በሆነ ቦታ ደራሲው ከሰው
ወደ ማሽን ይቀየራል። ተግባራችሁ **ያንን መቀየሪያ ማግኘት ነው፦ የሰው ክፍሉ የሚያበቃበትና
የማሽኑ ክፍል የሚጀምርበትን የቁምፊ index**።

እያንዳንዱ sample አንድ string `text` ነው። በትክክል አንድ boundary አለ። ከእሱ
በፊት ያለው ሁሉ በሰው የተጻፈ ነው፤ ከእሱ ጀምሮ ያለው ሁሉ በማሽን የተፈጠረ ነው።

## Dataset

በplain-text የቀረቡ የእንግሊዝኛ ምንባቦች፣ እያንዳንዳቸው አንድ boundary አላቸው።

- **ክፍል A** (ከboundary በፊት)፦ በሰው ከተጻፈ ጽሑፍ የተወሰደ ክፍል።
- **ክፍል B** (ከboundary ጀምሮ)፦ በክፍል A ላይ ተመሥርቶ በቋንቋ ሞዴል
  የተፈጠረ ቀጣይ ጽሑፍ።
- እያንዳንዱ ወገን ቢያንስ 180 ቃላት አሉት፤ አጠቃላይ ርዝመቱ ~500–800 ቃላት ነው።
- **`boundary_char_index`** ክፍል A የሚያበቃበት የቁምፊ offset ነው፦
  `text[:boundary_char_index]` የሰው ክፍል ሲሆን
  `text[boundary_char_index:].lstrip()` የማሽን ክፍል ነው።

#### የሚሰጣችሁ

**ሁለት folders** ይሰጣችኋል፦

| Folder | Samples | `answers.jsonl`? | የሚጠቅመው |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ ተካትቷል | method-ዎን ለማሰልጠን / fine-tune ለማድረግ |
| `dataset/test_public/`  | 380   | ✅ ተካትቷል (የdev ቅጂ) | pipeline-ዎን ለማስኬድና በአካባቢው ራስዎን ለመመዘን |

**በምዘና ጊዜ** የእርስዎ `dataset/test_public/` folder **በተደበቀ
የምዘና set ይተካል**። ተመሳሳይ format አለው፣ ነገር ግን **`answers.jsonl` የለውም**። notebook-ዎ
በዚህ ላይ እንደገና ይሠራል፣ እና የሚያመነጨው `answers.jsonl` ይመዘናል።

- ይፋዊው leaderboard የተደበቀ **test_leaderboard_a** set (380 samples) ይጠቀማል።

- የመጨረሻው ranking የተደበቀ **test_leaderboard_b** set (380 samples) ይጠቀማል።

ሦስቱም የምዘና
sets ተመሳሳይ መጠን ያላቸው ሲሆኑ ከ`train` ጋር ከተመሳሳይ distribution የተወሰዱ ናቸው፤ ስለዚህ የአካባቢው
`dataset/test_public/` score-ዎ የleaderboard score-ዎን በተመጣጣኝ ሁኔታ ይገምታል።

#### በዲስክ ላይ ያለው format

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- በ`answers.jsonl` ውስጥ ያሉ IDs በ`data.jsonl` ውስጥ ካሉ IDs ጋር ይዛመዳሉ።
- `dataset/train/` (መልሶችን የያዘ) በማሰልጠን ወይም fine-tune በማድረግ ጊዜ ሁሉ ይገኛል።

## Output (የsubmission format)

**`solution.ipynb` ተብሎ መሰየም ያለበትን አንድ notebook** ያስገባሉ። ይህ ትክክለኛ የfile ስም አስፈላጊ ነው። ሌላ ማንኛውም ነገር ሳይሠራ ውድቅ ይደረጋል።

notebook-ዎ **`dataset/test_public/data.jsonl`ን ማንበብ** እና በrepository root ላይ አንድ
**`answers.jsonl`** file መጻፍ አለበት — በእያንዳንዱ መስመር አንድ JSON object፣
እያንዳንዱን sample id እርስዎ ከገመቱት የboundary ቁምፊ index ጋር በማዛመድ፦

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` **በ`[0, len(text)]` ውስጥ ያለ integer** መሆን አለበት።
- በ`dataset/test_public/data.jsonl` ውስጥ ያለ እያንዳንዱ id በትክክል አንድ ጊዜ መታየት አለበት። ከ`answers.jsonl` የጎደለ
  sample (ወይም integer ያልሆነ / ከrange ውጭ የሆነ value ያለው) ለዚያ sample 0
  ነጥብ ያገኛል።

## አሰጣጥ

ለእያንዳንዱ sample፣ `p` እርስዎ የገመቱት index እና `t` ትክክለኛው boundary ይሁኑ። የእያንዳንዱ sample ነጥብ እንደ የቁምፊ ርቀቱ በexponential ሁኔታ ይቀንሳል፦

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

ይህ የነጥቡን የሚከተለውን ባህሪ ያስከትላል፦
- **=1.0** — ትክክለኛው የboundary ቁምፊ፤
- **≈0.78** — በ25 ቁምፊዎች ስህተት፤ - **≈0.61** — በ50 ቁምፊዎች ስህተት፤
- **≈0.37** — በ100 ቁምፊዎች ስህተት፤
- **≈0.01** — በ500 ቁምፊዎች ስህተት።

**የመጨረሻው ነጥብ አማካይ ነው**፤ ይህም በsplit ውስጥ ባሉ ሁሉም samples ላይ የእያንዳንዱ sample ነጥብ አማካይ ነው
(በ0–100 scale ይቀርባል)። metric-ው ትክክለኛውን ብቻ ሳይሆን *መቅረብን* ይሸልማል።

## ገደቦች

- **አካባቢ፦** አንድ GPU (≈16 GB VRAM)፣ በምዘና ጊዜ ኢንተርኔት የለም — የተፈቀደው
  model (ከታች) አስቀድሞ ቀርቧል። **የwall-clock ጊዜ ገደብ፦ 10 ደቂቃዎች** ለጠቅላላው
  ሂደት — ይህ በምዘና ጊዜ የሚያደርጉትን ማንኛውንም training / fine-tuning
  **እና** በምዘና set ላይ inference ማድረግን መሸፈን አለበት።
- **የተፈቀደ pretrained model** — ይህ ዝርዝር ሙሉ ነው፤ ሌሎች pretrained weights
  መጠቀም አይቻልም። ይህ **በአካባቢው አስቀድሞ ቀርቧል** (በመደበኛው መንገድ load ያድርጉት፣ ለምሳሌ
  `from_pretrained`፤ በምዘና ጊዜ ኢንተርኔት የለም)፦
  - **bge-base-en-v1.5** — 110M-parameter ያለው የጽሑፍ **encoder** (embedding model)። ይህ
    የsentence/passage embeddings ያመነጫል፤ generative language model አይደለም። ይህንን
    **እንዳለ (እንደ frozen features) መጠቀም ወይም በ`train` split ላይ fine-tune ማድረግ** ይችላሉ
    (full fine-tuning በ16 GB / 10-minute ገደብ ውስጥ ይሠራል)።
- Classical / statistical tools ገደብ የላቸውም፦ እርስዎ ራስዎ
  በሚያሰሉት embedding features ላይ ማንኛውንም feature-based model (ለምሳሌ፣ scikit-learn classifiers ወይም regressors) መገንባት ይችላሉ። *Pretrained deep-learning weights* ከላይ ባለው ዝርዝር ብቻ የተገደቡ ናቸው።
