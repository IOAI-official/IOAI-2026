# የድርብ ወኪል አጣብቂኝ

- **የጊዜ ገደብ፦** 12 minutes።
- **ማከማቻ፦** 5 GB
- **አካባቢ፦** አንድ GPU (≈16 GB VRAM)፣ ኢንተርኔት የለም
- **የመፍትሔ መጠን፦** `solution.ipynb` ≤ 1 MB
- **የBaseline ውጤት፦** 0 
- **የሳይንሳዊ ኮሚቴ ውጤት፦** 96.99 

በአስታና ብሔራዊ AI ማዕከል፣ ሁለት የኮምፒውተር ሞዴሎች — Model R (ResNet-18) እና Model V (ViT-Tiny) —ፎቶዎችን እየተነተኑ ነው። በአሁኑ ጊዜ፣ ሁለቱም ሞዴሎች 100% ትክክለኛነት በማስመዝገብና በእያንዳንዱ ምስል ላይ በመስማማት ሥራቸውን ፍጹም በሆነ ሁኔታ እየሠሩ ነው። ብልህ “አእምሯቸው” በእውነት ምን ያህል የተለያየ እንደሆነ ለመፈተሽ፣ ዋና ሳይንቲስቱ አንድ ፈተና ይሰጥዎታል፦ Model R እና Model V ሙሉ በሙሉ እንዳይስማሙ በእያንዳንዱ ፎቶ ላይ ጥቃቅንና ለማየት እጅግ አስቸጋሪ የሆኑ የpixel ለውጦችን ያድርጉ።

![ምስል](../../dilemma.jpg)

## 1. ተግባር

ሁለት pretrained የምስል classifier-ዎች ተመሳሳዩን ምስል ይመለከታሉ። በዚህ ተግባር ውስጥ በቀረቡት ምስሎች ላይ፣ ሁለቱም classifier-ዎች 100% ትክክለኛነት አላቸው።

- **Model R**፦ `torchvision.models.resnet18` (CNN፣ ResNet18)።
- **Model V**፦ የ`timm` `vit_tiny_patch16_224` (Transformer፣ ViT-Tiny)።

ተግባርዎ ሁለቱ ሞዴሎች እንዳይስማሙ ለእያንዳንዱ ምስል አነስተኛ ለውጥ (“perturbation”) መፍጠር ነው። ለእያንዳንዱ ምስል **ሁለት የተለያዩ** perturbation-ዎችን መፍጠር አለብዎት፦

- **Type A**፦ ከተጨመረ በኋላ፣ Model R አሁንም ምስሉን በትክክል classify ያደርጋል፣ Model V ግን በተሳሳተ ሁኔታ classify ያደርገዋል።
- **Type B**፦ ከተጨመረ በኋላ፣ Model V አሁንም ምስሉን በትክክል classify ያደርጋል፣ Model R ግን በተሳሳተ ሁኔታ classify ያደርገዋል።

እያንዳንዱ perturbation ለማስተዋል አስቸጋሪ እስኪሆን ድረስ *አነስተኛ* መሆን አለበት። አነስተኛ perturbation-ዎች ከፍተኛ ውጤት ያስገኛሉ (ክፍል 5ን ይመልከቱ)። Perturbation-ው በpixel ደረጃ በቀጥታ በመጀመሪያው ምስል ላይ ይተገበራል።

## 2. ይፋዊ ውሂብ

ከተግባሩ ጋር የምስሎች ስብስብ ቀርቧል፤ ይህም በሁለት split-ዎች — `train` (100 ምስሎች) እና
`test_public` (100 ምስሎች) — የተደራጀ ሲሆን፣ እያንዳንዱ የተለያየ resolution ያላቸውን ምስሎች ይዟል። ሁሉም ምስሎች ከImageNet-1K 1000 class-ዎች የተወሰዱ ሲሆን፣ Model R እና Model V በሁለቱም split-ዎች ላይ 100% ትክክለኛነት ያገኛሉ።

የሚከተሉት ፋይሎች ቀርበዋል፦

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

በምዘና ጊዜ፣ የእርስዎ `dataset/test_public/` folder ለይፋዊ ውጤት አሰጣጥ በሁለት ድብቅ የምስል ስብስቦች (`test_leaderboard_a` እና `test_leaderboard_b`) በግልጽነት ይተካል። እያንዳንዳቸው በPNG format **100 ምስሎችን** እና label file ይይዛሉ። 

**ማስታወሻ፦ ለዚህ ተግባር፣ በtest dataset-ዎቹ ውስጥ ያሉት label-ዎች ሊደረስባቸው ይችላል።**

## 3. የውጤት format

ለእያንዳንዱ ምስል፣ ሁለት ፋይሎችን ማዘጋጀት አለብዎት፦

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`፣ `1`፣ `2`፣ ...)፣ በdataset-ዎቹ ውስጥ ካለው የምስሉ ስም ጋር ይዛመዳል።
- እያንዳንዱ ፋይል በ`torch.save` የተቀመጠ አንድ tensor ነው። Shape-ው`3 x H x W` መሆን አለበት፤ በዚህም `H` እና `W` ከምስሉ **የመጀመሪያ** resolution ጋር ይዛመዳሉ (`224 x 224` አይደለም)።
- Code-ው `submission.zip` የተባለ አንድ ZIP file ብቻ ማዘጋጀት አለበት። ሁሉንም `.pt` file-ዎች ያለ መያዣ folder ወይም subdirectory በZIP archive-ው ከፍተኛ ደረጃ ላይ ያስቀምጡ። 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

በውጤት format-ው ላይ ማንኛውም ችግር ካለ notebook-ው ያስጠነቅቅዎታል።

## 4. ገደቦች

- **ሞዴሎች፦** `torchvision.models.resnet18(pretrained=True)` እና `timm.create_model('vit_tiny_patch16_224', pretrained=True)`ን መጠቀም አለብዎት። ሌሎች pretrained model-ዎች አይፈቀዱም።
- **Transform pipeline (በምዘና ወቅት የሚገደድ)፦** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` ለዝርዝሮች። 
- **የPerturbation resolution፦** ከ**መጀመሪያው** raw image resolution ጋር መዛመድ አለበት (224×224 አይደለም)። Tensor-ው ከtransform pipeline-ው *በፊት* ወደ raw image-ው ይጨመራል።
- **የውጤት format፦** `.pt` file-ዎች ብቻ — PNG/JPG አይፈቀድም። Tensor-ዎቹ ወደ raw image-ው ይጨመራሉ፣ እና ከpreprocessing በፊት የpixel እሴቶች ወደ `[0, 1]` ይቆረጣሉ።
- **የፋይል ስያሜ፦** Flat-listed፣ ጥብቅ `{index}_a.pt` / `{index}_b.pt` format። በzip-ው ውስጥ subdirectory አይኑር።
- **Library-ዎች፦** `torch`፣ `torchvision`፣ `timm`። 

## 5. ውጤት አሰጣጥ

የመጨረሻው ውጤት እንደሚከተለው ይሰላል። `M` በsplit-ው ውስጥ ያሉት የምስሎች ብዛት፣ $Score_A$ የተሳኩ Type A perturbation-ዎች ብዛት፣ እና $Score_B$ የተሳኩ Type B perturbation-ዎች ብዛት ይሁኑ፦
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF ከፍተኛ norm ያላቸውን perturbation-ዎች ለመቅጣትና ከከፍተኛው የአፈጻጸም ጣሪያ አቅራቢያ በጣም ስሱ እንዲሆን የተነደፈ function ነው። እሱ እሱ ከ0.5 እስከ 1 ባለው ክልል የተገደበ ነው። ሙሉ implementation-ው በ`solution.ipynb` ክፍል  8 ውስጥ ሊታይ ይችላል። 

![ምስል](../../curves.jpeg)
ሥዕል፦ የpenalty function-ው curve።

## 6. Submission-ውን ያረጋግጡ

በ`solution.ipynb` notebook ክፍል 7 ላይ፣ የformat ችግሮች ካሉ የሚያስጠነቅቁዎት check-ዎች notebook-ው ውስጥ አሉ።

## 7. አካባቢያዊ ሙከራ

`solution.ipynb` ሙሉና የሚሠራ example ይዟል። ይፋዊውን ውሂብ፣ ሁለቱንም ሞዴሎች እና ይፋዊውን scorer ይጭናል፣ እንዲሁም submission ZIP file ይጽፋል። ከመጀመርዎ በፊት ያንብቡት።

## 8. እንዴት submit ማድረግ እንደሚቻል

- ለውጦችዎን በ`solution.ipynb` ያስቀምጡ።
- በJupyterLab የግራ sidebar ውስጥ Git tab-ን ይክፈቱ።
- `solution.ipynb`ን **Stage** ያድርጉ (ከእሱ አጠገብ ያለው + icon)።
- Commit message ያስገቡና **Commit**ን click ያድርጉ።
- Push ለማድረግ cloud-with-up-arrowን click ያድርጉ።
- ወደዚህ Contest page ይመለሱና **Submit**ን click ያድርጉ።

`solution.ipynb` የተባለ በትክክል አንድ file submit ያድርጉ።
