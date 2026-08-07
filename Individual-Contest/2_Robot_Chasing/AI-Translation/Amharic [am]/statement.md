# ሮቦት ማሳደድ

- **የጊዜ ገደብ፦** 5 minutes
- **አካባቢ፦** አንድ GPU (≈16 GB VRAM)፣ ኢንተርኔት የለም
- **የመፍትሔ መጠን፦** `solution.ipynb` ≤ 1 MB
- **ማከማቻ፦** 5 GB 

## ተግባር

ስድስት ሮቦቶች አሉ። እያንዳንዱ ሮቦት በgrid በተወከለ ትንሽ ክፍል ውስጥ ይሠራል። እያንዳንዱ ክፍል በግድግዳዎች የተከበበ `6×6` መጫወቻ ቦታ አለው፤ ስለዚህ ሙሉው `image` array መጠኑ `8×8` ነው (መጫወቻ ቦታ + ግድግዳዎች)።

እያንዳንዱ ሮቦት አንድን ተግባር የሚገልጽ የእንግሊዝኛ መመሪያ ይቀበላል። ሮቦቱ ተግባሩን በማከናወን ላይ እያለ በማንኛውም ጊዜ snapshot ሊወሰድ ይችላል። ግባችሁ የሮቦቱን ቀጣይ ድርጊት መተንበይ ነው።

ሮቦቶች ሁልጊዜ አጭሩን መንገድ አይከተሉም። Robot 0 ከRobot 1 የተለየ ባህሪ ሊያሳይ ይችላል፤ ሆኖም እያንዳንዱ ሮቦት የራሱን ወጥ የሆነ pattern ይከተላል። እነዚህን patterns ለመማር፣ ትክክለኛዎቹን ቀጣይ ድርጊቶች የሚያካትቱትን የሥልጠና ምሳሌዎች ተጠቀሙ።

![ሮቦት](../../robot.jpg)

ሦስት ዓይነት missions አሉ፦

- ወደ አንድ ነገር **መሄድ**፣ ለምሳሌ `"approach the red ball"`፤
- አንድን ነገር **ማንሳት**፣ ለምሳሌ `"grab the blue key"`፤
- **አንድን ነገር ከሌላ ነገር አጠገብ ማስቀመጥ**፣ ለምሳሌ
  `"place the red box beside the green ball"`።

ተመሳሳዩ መመሪያ በተለያዩ መንገዶች ሊጻፍ ይችላል። የፈተናው dataset የታወቁ ሐረጎች፣ ቀለሞች እና የነገር ዓይነቶች አዳዲስ ጥምረቶችን ሊይዝ ይችላል። ሆኖም፣ በፈተናው dataset ውስጥ ጥቅም ላይ የሚውሉ እያንዳንዱ ቃል፣ የሐረግ pattern፣ ቀለም፣ የነገር ዓይነት እና የmission ዓይነት በሥልጠናው dataset ውስጥም ይታያሉ።

እያንዳንዱ sample የሚከተሉት መስኮች አሉት፦

| መስክ | ትርጉም |
|---|---|
| `robot_id` | ይህ ከ6ቱ ሮቦቶች የትኛው እንደሆነ (`0`–`5`) |
| `image` | ክፍሉ፤ `8×8×2` integer array ሲሆን channel 0 categorical object_idxን (ለምሳሌ፣ 1=ባዶ፣ 2=ግድግዳ፣ 10=ሮቦት) እና channel 1 categorical colour_idxን (0–5) ይይዛል። |
| `direction` | ሮቦቱ አሁን የተመለከተበት አቅጣጫ |
| `mission` | የሚታየው የተፈጥሮ ቋንቋ መመሪያ |
| `carrying` | ለተያዘው ነገር `null` ወይም `[object_idx, colour_idx]` |

ረድፎቹ በዘፈቀደ ቅደም ተከተል ያሉ እርስ በርሳቸው ነፃ snapshots ናቸው። episodes አይፈጥሩም፣ እና በግምገማ ጊዜ ምንም ቀዳሚ observation ወይም action አይኖርም።

የቀረበው `visualize_dataset.ipynb` በተለያዩ ሁኔታዎች ለሞዴሉ የሚገኙትን observations እንድትመረምሩ ያስችላችኋል።

## የGrid encoding

`image[row][column] = [object_idx, colour_idx]`። የመጀመሪያው index ከላይ ወደ ታች ያለው ረድፍ ሲሆን፣ ሁለተኛው index ከግራ ወደ ቀኝ ያለው column ነው። arrayው የውጪውን የግድግዳ ድንበር ያካትታል፤ ስለዚህ ሊጓዝበት የሚቻለው ውስጣዊ ክፍል `6×6` ነው።

የነገር ids፦

| id | ነገር |
|---:|---|
| 1 | ባዶ cell |
| 2 | ግድግዳ |
| 5 | ቁልፍ |
| 6 | ኳስ |
| 7 | ሳጥን |
| 10 | ሮቦት |
| 11 | token |

Tokens በክፍሉ ውስጥ ሊታዩ ይችላሉ፣ ነገር ግን በmissions ውስጥ ፈጽሞ አይጠቀሱም።

የቀለም ids፦ `0` ቀይ፣ `1` አረንጓዴ፣ `2` ሰማያዊ፣ `3` ወይን ጠጅ፣ `4` ቢጫ እና `5` ግራጫ ናቸው። የቀለም channel ለባዶ cells እና ለግድግዳዎች ትርጉም የለውም።

ምስሉ ከላይ ያሉትን ሁለት channels ብቻ ይዟል። የሮቦቱ አቅጣጫ በtop-level `direction` መስክ ውስጥ አንድ ጊዜ ይቀርባል፤ በ`image` ውስጥ በድጋሚ አልተካተተም።

## Actions

ለcodes `0`–`3`፣ የእንቅስቃሴ actions የሚከተለውን absolute mapping ይጠቀማሉ፦

| action | ትርጉም |
|---:|---|
| 0 | ወደ ላይ መንቀሳቀስ |
| 1 | ወደ ታች መንቀሳቀስ |
| 2 | ወደ ግራ መንቀሳቀስ |
| 3 | ወደ ቀኝ መንቀሳቀስ |
| 4 | ማንሳት |
| 5 | ማስቀመጥ |


የ`direction` መስክ የአሁኑን የፊት አቅጣጫ እንዲህ ያመለክታል፦ 0 = ወደ ላይ (row - 1)፣ 1 = ወደ ታች (row + 1)፣ 2 = ወደ ግራ (col - 1)፣ 3 = ወደ ቀኝ (col + 1)።

አንድ የእንቅስቃሴ action መጀመሪያ ሮቦቱን ወደዚያ absolute direction ያዞረዋል፣ ከዚያም በአንድ cell ለማንቀሳቀስ ይሞክራል። ግድግዳ ወይም ነገር እንቅስቃሴውን ሊከለክል ይችላል፣ ነገር ግን direction አሁንም ይቀየራል። `pick up` እና `drop` በdirection በተወሰነው አጎራባች target cell ላይ ብቻ ይሠራሉ (ለምሳሌ፣ direction=0 ከሆነ፣ በ(row - 1, col) ላይ ይሠራል)።

## Dataset

ሁለት folders ይሰጧችኋል፦

| Folder | ረድፎች | `labels.json`? | የሚጠቅመው |
|---|---:|---|---|
| `dataset/train/` | 60,000 | ተካትቷል | ሞዴላችሁን ለማሠልጠን |
| `dataset/test_public/` | 3,600 | በdevelopment copy ውስጥ ተካትቷል | pipelineያችሁን ለማስኬድ እና ውጤቱን በራሳችሁ ለማስላት |

እያንዳንዱ folder ከላይ የተገለጹትን samples የያዘ JSON list የሆነውን `observations.json` ይዟል። `labels.json` በተመሳሳይ ቅደም ተከተል የተደረደረ የactions JSON list ነው (`0`–`5`)።

የሥልጠናው dataset ለእያንዳንዱ ሮቦት በትክክል 10,000 ረድፎችን እና ከእያንዳንዱ
የተግባር family 20,000 ረድፎችን ይዟል። የpublic test ለእያንዳንዱ ሮቦት 600 ረድፎችን ይዟል። array ካስፈለጋችሁ `image`ን በ
`numpy.asarray(...)` ጠቅልሉት።

ውጤት በሚሰጥበት ጊዜ፣ `dataset/test_public/` ተመሳሳይ format ባላቸው ነገር ግን
`labels.json` በሌላቸው 3,600 observations የተደበቀ set በግልጽነት ይተካል። የpublic
leaderboard `test_leaderboard_a`ን ይጠቀማል፤ የመጨረሻው ranking ደግሞ
`test_leaderboard_b`ን ይጠቀማል። ያለምንም ቅድመ ሁኔታ test labelsን የሚያነብ notebook ይወድቃል።
Labelsን ከ`dataset/train/` ብቻ አንብቡ።

## Output

በnotebookው working directory ውስጥ `predictions.json`ን ጻፉ። ይህም ለእያንዳንዱ የ
`dataset/test_public/observations.json` ረድፍ፣ በተመሳሳይ ቅደም ተከተል፣ አንድ integer action (`0`–`5`) የያዘ JSON
list መሆን አለበት። ስድስት samples ላለው መላምታዊ test set፣ ተቀባይነት ያለው output የሚከተለው ሊሆን ይችላል፦

```json
[0, 3, 2, 2, 5, 4]
```

የጎደለ ወይም ልክ ያልሆነ JSON file፣ የተሳሳተ የpredictions ብዛት፣ integer ያልሆነ value፣
ወይም ከ`{0,1,2,3,4,5}` ውጭ የሆነ action ያለው output ያለምንም ውጤት ውድቅ ይደረጋል።

## ውጤት አሰጣጥ

የውጤት አሰጣጡ በ`0`–`100` scale ላይ **የእያንዳንዱ ሮቦት accuracy አማካይ** ነው። Accuracy መጀመሪያ
ለእያንዳንዱ ሮቦት በተናጠል ይሰላል፤ ከዚያም የስድስቱም ሮቦቶች አማካይ ይወሰዳል። ስለዚህ እያንዳንዱ
ሮቦት እኩል weight አለው።

## እንዴት submit እንደሚደረግ

1. `solution.ipynb`ን ከፍታችሁ ሁሉንም cells አስኪዱ።
2. ለpublic
   test set 3,600 predictions ያለው `predictions.json` እንደሚጽፍ አረጋግጡ።
3. ከፈለጋችሁ ሞዴሉን አሻሽሉ፤ የቀረበው baseline የሚያሳየው የሚፈለገውን
   input እና output format ብቻ ነው።
4. በJupyterLab Git tab ውስጥ `solution.ipynb`ን stage እና commit አድርጉ፣ ከዚያም push አድርጉት።
5. ወደ Contest page ተመልሳችሁ **Submit**ን ጠቅ አድርጉ።

`solution.ipynb` የተባለ በትክክል አንድ file submit አድርጉ።
