# ቅደም ተከተሉን ፈልጉ

- **የጊዜ ገደብ፦** 10 ደቂቃዎች
- **አካባቢ፦** አንድ GPU (≈16 GB VRAM)፣ ኢንተርኔት የለም
- **የመፍትሔ መጠን፦** `solution.ipynb` ≤ 1 MB
- **ማከማቻ፦** 5 GB 

## ችግሩ

በሁለት ተሳታፊዎች፣ *ተናጋሪ A* እና *ተናጋሪ B*፣ መካከል በእንግሊዝኛ የተነገሩ ውይይቶች ተሰጥተዋችኋል። እያንዳንዱ ውይይት በተናጋሪ ተራዎች የተከፋፈለ ሲሆን፣ እያንዳንዱ ተራ የአንድ ተናጋሪ ንግግር ብቻ ይዟል። እያንዳንዱ ተራ እንደ የተለየ `.wav` የድምፅ ፋይል ይቀመጣል፤ ስለዚህ ሙሉ ውይይት ለእያንዳንዱ ተራ አንድ ፋይል በሆነበት የ`.wav` ፋይሎች ስብስብ ይወከላል። 

እንደ አጋጣሚ ሆኖ፣ ተራዎቹ በዘፈቀደ ተቀላቅለዋል፤ ስለዚህ ውይይቱ ከእንግዲህ ትርጉም አይሰጥም። በፋይል ስሙ `chunk_{k}.wav` ውስጥ፣ `k` የሚያመለክተው በተቀላቀለው ስብስብ ውስጥ ያለውን k-th chunk እንጂ በመጀመሪያው ውይይት ውስጥ ያለውን k-th ተራ አይደለም።

**‼️ ተግባራችሁ የውይይቱን የመጀመሪያ የጊዜ ቅደም ተከተል መልሶ መገንባት ነው።**

![ቅደም ተከተሉን ፈልጉ](../find_the_order.jpg)

---

## Dataset

እያንዳንዱ ውይይት `n`፣ `chunk_0.wav`፣ `chunk_1.wav`፣ …፣ `chunk_{n-1}.wav` ተብለው የተሰየሙ የድምፅ ፋይሎችን ይዟል። chunks የተናጠል ተራዎች ናቸው። የፋይል ስሞቹ ከተቀላቀለው ቅደም ተከተል ጋር ብቻ ይዛመዳሉ። አንድ chunk በመጀመሪያው ውይይት ውስጥ የት መገኘት እንዳለበት አያመለክቱም። እያንዳንዱ ውይይት 7–20 chunks ያሉት፣ mono፣ 44.1 kHz ነው (resample ማድረግ
ትችላላችሁ)።

**`prefix.json` በእያንዳንዱ ውይይት ውስጥ ያሉትን የመጀመሪያዎቹ ሁለት chunks የፋይል ስም ኢንዴክሶች ይዟል።** ይህ የውይይቱን ትክክለኛ መጀመሪያ ይለያል፣ እንዲሁም ውይይቱን ወደፊት ወይም ወደኋላ በማንበብ መካከል ያለውን አሻሚነት ያስወግዳል።

ለምሳሌ፦ `11: [7, 12]` ማለት የውይይት 11 የመጀመሪያው እና ሁለተኛው ተራ `chunk_7.wav` እና `chunk_12.wav` ናቸው ማለት ነው።

### የሚሰጣችሁ

**ተመሳሳይ ቅርጸት ያላቸው ሁለት folders** ይሰጧችኋል፦

| Folder | ውይይቶች | `answers.json`? | የሚጠቅመው |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ ተካትቷል | ሞዴላችሁን train / fine-tune ለማድረግ |
| `dataset/test_public/`  | 100   | ✅ ተካትቷል | pipeline-አችሁን ለማስኬድ እና በአካባቢያችሁ ራሳችሁን ለመመዘን |

በውጤት አሰጣጥ ጊዜ፣ የ`dataset/test_public/` folder-አችሁ በራሱ
በ`hidden evaluation set` (ለpublic leaderboard `test_leaderboard_a` እና ለfinal leaderboard `test_leaderboard_b`) ይተካል፤ እነዚህ ከ`dataset/test_public/` ጋር ተመሳሳይ መጠንና ቅርጸት አላቸው፣ ነገር ግን `answers.json` የላቸውም።

notebook-አችሁ በዚያ ውሂብ ላይ እንደገና ይፈጸማል፣ እና የሚያመነጨው `answers.json` ፋይል ለውጤት አሰጣጥ ይውላል። ያልታዩት test ውይይቶች ከ`train` ጋር ከተመሳሳይ distribution የመጡ ናቸው፤ ስለዚህ የአካባቢያችሁ `test_public` ውጤት አስተማማኝ ቅድመ እይታ ነው።

### የdirectory መዋቅር

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

## ውጤት

ለእያንዳንዱ ውይይት፣ የድምፅ chunks-ን የመጀመሪያ የጊዜ ቅደም ተከተል ወስኑ። ትንበያችሁ የ`{0, 1, …, n−1}` permutation `P` መሆን አለበት፤ በዚህም `P[i]` የ`chunk_i.wav` የተተነበየ የጊዜ ቅደም ተከተል ቦታ ነው (0 = የመጀመሪያ)።

የውጤት ፋይላችሁ `answers.json` እያንዳንዱን የውይይት ID ከተተነበየው permutation ጋር ማዛመድ አለበት፦

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### ምሳሌ

አንድ ውይይት 3 የተቀላቀሉ chunks `chunk_0, chunk_1, chunk_2` አሉት፦

| የተቀላቀለ chunk | የተነገረው ይዘት | ትክክለኛ ቦታ (rank) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"ምንም ችግር የለም — ማስታወሻዎቹን በኋላ እልክልሃለሁ።"* | 2 (የመጨረሻ) |
| `chunk_1.wav` | *"ሰላም፣ ወደ ሦስት ሰዓት ስብሰባው ትመጣለህ?"* | 0 (የመጀመሪያ) |
| `chunk_2.wav` | *"አልችልም — በዚያ ሰዓት የጥርስ ሐኪም ቀጠሮ አለኝ።"* | 1 |

ትክክለኛው ቅደም ተከተል **chunk_1 → chunk_2 → chunk_0** ነው፤ ስለዚህ `P = [2, 0, 1]`፣ እና `prefix.json` `[1, 2]`ን ይይዛል።

⚠️ **P ትክክለኛ permutation መሆን አለበት፦** ርዝመቱ n፣ በ0 የሚጀምር ኢንዴክስ፣ እያንዳንዱ እሴት በትክክል አንድ ጊዜ። የተደጋገሙ፣ የጎደሉ ወይም ከክልል ውጭ የሆኑ ግቤቶች (ለምሳሌ በ1 የሚጀምር ኢንዴክስ) ለዚያ ውይይት 0 ያስመዘግባሉ፤ ከፋይሉ የጎደለ ውይይትም እንዲሁ ነው። ቅርጹ የተበላሸ ወይም JSON ያልሆነ ፋይል ውድቅ ይደረጋል።

## ውጤት አሰጣጥ

የዚህ ተግባር ውጤት አሰጣጥ **የጥንድ ቅደም ተከተል ትክክለኛነት (pairwise ordering accuracy)** ነው። እያንዳንዱን የchunks ጥንድ ይፈትሻል እና፦ *ከሁለቱ የትኛው መቅደም አለበት?* ብሎ ይጠይቃል። ትንበያችሁ ከትክክለኛው መልስ ጋር ተመሳሳይ መልስ ከሰጠ፣ ጥንዱ ትክክል ነው። `n` chunks ላለው ውይይት $$M = n(n-1)/2$$ ጥንዶች አሉ፤ `I` ደግሞ የinversions ብዛት፣ ማለትም ከትክክለኛው ቅደም ተከተል በተለየ የተደረደሩ ጥንዶች ብዛት፣ ይሁን፦

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **የመጨረሻው ውጤት በsplit ውስጥ ባሉ ሁሉም
ውይይቶች ላይ የእያንዳንዱ ውይይት ውጤቶች አማካይ ነው።**

## የተፈቀዱ ሞዴሎች

ይህን ተግባር ለመፍታት፣ በስልጠናም ሆነ በግምገማ ወቅት፣ የሚከተሉትን pre-trained ሞዴሎች ብቻ መጠቀም ትችላላችሁ። እነዚህ ሁሉ ሞዴሎች አስቀድመው ወርደው በአካባቢው ውስጥ ይገኛሉ። እንዴት መጠቀም እንደሚቻል የሚያሳዩ ምሳሌዎችን በbaseline notebook `solution.ipynb` ውስጥ ማየት ትችላላችሁ። ሌላ ማንኛውንም ሞዴል መጠቀም እንደማትችሉ እና ፕሮግራማችሁ የኢንተርኔት መዳረሻ እንደሌለው ልብ በሉ።

- **የንግግር ውክልናዎች፦** **wav2vec 2.0**። **Whisper encoder** እንደ feature extractor መጠቀምም ይቻላል።
[የwav2vec ሞዴል ካርድ](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **ራስ-ሰር የንግግር ለይቶ ማወቂያ (ASR)፦** **OpenAI Whisper** (ማንኛውም መጠን)።
[የWhisper ሞዴል ካርድ](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **የቋንቋ ሞዴል፦** **Qwen2.5-0.5B**፤ ይህም zero-shot ሆኖ ወይም በተሰጠው `train` split ላይ fine-tune ተደርጎ መጠቀም ይቻላል።
[የQwen ሞዴል ካርድ](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
የ10-ደቂቃው ገደብ በውጤት አሰጣጥ ጊዜ የምታደርጉትን ማንኛውንም training ወይም fine-tuning፣ እንዲሁም በevaluation set ላይ inference ማድረግን መሸፈን እንዳለበት ልብ በሉ።

## እንዴት ማስገባት እንደሚቻል

- `solution.ipynb`ን ክፈቱ እና ሁሉንም cells አስኪዱ። በ`dataset/test_public/` ውስጥ ላለ እያንዳንዱ ውይይት (100 ውይይቶች) permutation የያዘ `answers.json`ን በworking directory ውስጥ እንደሚጽፍ አረጋግጡ። በውጤት አሰጣጥ ጊዜ notebook-ው በስውር test set ላይ እንደገና ይፈጸማል፣ እና በዚያ የሚያመነጨው `answers.json` ውጤት ይሰጠዋል።
- ከፈለጋችሁ መፍትሔውን አሻሽሉ — ወይም አታሻሽሉት፤ baseline-ው ብቻውን pipeline-ውን ያረጋግጣል።
- በJupyterLab የግራ sidebar ውስጥ ያለውን Git tab ክፈቱ።
- `solution.ipynb`ን **Stage** አድርጉ (ከእሱ ቀጥሎ ያለው + ምልክት)።
- የcommit መልዕክት አስገቡ እና **Commit**ን ጠቅ አድርጉ።
- push ለማድረግ ደመናና ወደላይ ቀስት ያለውን ምልክት ጠቅ አድርጉ።
- ወደዚህ የContest ገጽ ተመለሱ እና **Submit**ን ጠቅ አድርጉ።

በትክክል አንድ ፋይል፣ `solution.ipynb` ተብሎ የተሰየመ፣ አስገቡ።
