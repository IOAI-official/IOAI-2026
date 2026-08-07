# डबल एजेन्ट दुविधा

- **समय सीमा:** 12 minutes।
- **भण्डारण:** 5 GB
- **वातावरण:** एउटा GPU (≈16 GB VRAM), internet छैन
- **समाधानको आकार:** `solution.ipynb` ≤ 1 MB
- **Baseline स्कोर:** 0 
- **वैज्ञानिक समितिको स्कोर:** 96.99 

Astana को राष्ट्रिय AI केन्द्रमा, दुईवटा कम्प्युटर मोडेल — Model R (एउटा ResNet-18) र Model V (एउटा ViT-Tiny) — तस्बिरहरू विश्लेषण गरिरहेका छन्। अहिले, दुवै मोडेलले पूर्ण रूपमा काम गरिरहेका छन्, 100% accuracy प्राप्त गरिरहेका छन् र प्रत्येक तस्बिरमा सहमत छन्। तिनका स्मार्ट "मस्तिष्कहरू" वास्तवमा कति फरक छन् भनेर परीक्षण गर्न, प्रमुख वैज्ञानिकले तपाईंलाई एउटा चुनौती दिन्छन्: प्रत्येक तस्बिरका pixel मा साना, लगभग अदृश्य परिवर्तनहरू गर्नुहोस्, जसले गर्दा Model R र Model V पूर्ण रूपमा असहमत होऊन्।

![चित्र](../../dilemma.jpg)

## 1. कार्य

दुईवटा पूर्व-प्रशिक्षित image classifier ले एउटै तस्बिर हेर्छन्। यस कार्यमा प्रदान गरिएका तस्बिरहरूमा, दुवै classifier ले 100% accuracy का साथ काम गर्छन्।

- **Model R**: `torchvision.models.resnet18` (एउटा CNN, ResNet18)।
- **Model V**: `timm` को `vit_tiny_patch16_224` (एउटा Transformer, ViT-Tiny)।

तपाईंको कार्य प्रत्येक तस्बिरका लागि एउटा सानो परिवर्तन ("विक्षोभ" (perturbation)) सिर्जना गर्नु हो, जसले गर्दा दुई मोडेल असहमत होऊन्। प्रत्येक तस्बिरका लागि, तपाईंले **दुई फरक** विक्षोभ सिर्जना गर्नुपर्छ:

- **Type A**: यसलाई थपेपछि, Model R ले अझै पनि तस्बिरलाई सही रूपमा वर्गीकरण गर्छ, तर Model V ले यसलाई गलत रूपमा वर्गीकरण गर्छ।
- **Type B**: यसलाई थपेपछि, Model V ले अझै पनि तस्बिरलाई सही रूपमा वर्गीकरण गर्छ, तर Model R ले यसलाई गलत रूपमा वर्गीकरण गर्छ।

प्रत्येक विक्षोभ ध्यान दिन गाह्रो हुने गरी पर्याप्त *सानो* हुनुपर्छ। अझ साना विक्षोभहरूले अझ उच्च स्कोर प्राप्त गर्छन् (Section 5 हेर्नुहोस्)। विक्षोभलाई मूल तस्बिरमा सीधै pixel स्तरमा लागू गरिन्छ।

## 2. सार्वजनिक data

कार्यसँगै तस्बिरहरूको एउटा set प्रदान गरिएको छ, जसलाई दुईवटा split — `train` (100 तस्बिर) र
`test_public` (100 तस्बिर) — मा व्यवस्थित गरिएको छ, र प्रत्येकमा फरक-फरक resolution का तस्बिरहरू छन्। सबै तस्बिरहरू ImageNet-1K का 1000 classes बाट लिइएका हुन् र Model R तथा Model V दुवैले दुवै split मा 100% accuracy प्राप्त गर्छन्।

निम्न files प्रदान गरिएका छन्:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

मूल्याङ्कनको समयमा, तपाईंको `dataset/test_public/` folder लाई official scoring का लागि पारदर्शी रूपमा तस्बिरका दुईवटा लुकेका set (`test_leaderboard_a` र `test_leaderboard_b`) ले प्रतिस्थापन गरिन्छ। ती प्रत्येकमा PNG format का **100 तस्बिर** र एउटा label file हुन्छ। 

**नोट: यस कार्यका लागि, test datasets का labels पहुँचयोग्य छन्।**

## 3. Output format

प्रत्येक तस्बिरका लागि, तपाईंले दुईवटा files उत्पादन गर्नुपर्छ:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), datasets मा रहेको तस्बिरको नामसँग मेल खान्छ।
- प्रत्येक file `torch.save` प्रयोग गरेर save गरिएको एउटा tensor हो। यसको shape `3 x H x W` हुनुपर्छ, जहाँ `H` र `W` उक्त तस्बिरको **मूल** resolution सँग मेल खान्छन् (`224 x 224` होइन)।
- code ले केवल एउटा ZIP file, `submission.zip`, उत्पादन गर्नुपर्छ। सबै `.pt` files लाई ZIP archive को top level मा राख्नुहोस्, कुनै enclosing folder वा subdirectories बिना। 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

output format मा कुनै समस्याहरू भए notebook ले तपाईंलाई सचेत गराउनेछ।

## 4. सीमाहरू

- **Models:** तपाईंले `torchvision.models.resnet18(pretrained=True)` र `timm.create_model('vit_tiny_patch16_224', pretrained=True)` प्रयोग गर्नैपर्छ। अन्य कुनै पनि pretrained models अनुमति छैन।
- **Transform pipeline (मूल्याङ्कनमा लागू गरिने):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` विस्तृत विवरणका लागि। 
- **Perturbation resolution:** **मूल** raw image resolution सँग मेल खानैपर्छ (224×224 होइन)। tensor लाई transform pipeline भन्दा *अघि* raw image मा थपिन्छ।
- **Output format:** `.pt` files मात्र — PNG/JPG होइनन्। tensors लाई raw image मा थपिन्छ र preprocessing अघि pixel values लाई `[0, 1]` मा clip गरिन्छ।
- **File naming:** Flat-listed, कडाइका साथ `{index}_a.pt` / `{index}_b.pt` format। zip भित्र कुनै subdirectories हुनु हुँदैन।
- **Libraries:** `torch`, `torchvision`, `timm`। 

## 5. Scoring

अन्तिम स्कोर निम्नानुसार गणना गरिन्छ। `M` लाई split मा भएका तस्बिरहरूको सङ्ख्या, $Score_A$ लाई सफल Type A विक्षोभहरूको सङ्ख्या, र $Score_B$ लाई सफल Type B विक्षोभहरूको सङ्ख्या मान्नुहोस्:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF उच्च norm भएका विक्षोभहरूलाई दण्डित गर्न र performance को ceiling नजिक अत्यन्त संवेदनशील हुन डिजाइन गरिएको function हो। यो यो 0.5 देखि 1 को दायरामा सीमाबद्ध छ। पूर्ण implementation `solution.ipynb` को Section  8 मा हेर्न सकिन्छ। 

![चित्र](../../curves.jpeg)
चित्र: penalty function को curve।

## 6. Submission जाँच गर्नुहोस्

`solution.ipynb` notebook को Section 7 मा formatting सम्बन्धी समस्याहरू भए तपाईंलाई सचेत गराउने checks छन्।

## 7. स्थानीय परीक्षण

`solution.ipynb` मा एउटा पूर्ण, काम गर्ने उदाहरण छ। यसले public data, दुवै models, र official scorer load गर्छ, र submission ZIP file लेख्छ। सुरु गर्नुअघि यसलाई पढ्नुहोस्।

## 8. कसरी submit गर्ने

- आफ्ना परिवर्तनहरू `solution.ipynb` मा save गर्नुहोस्।
- JupyterLab को बायाँ sidebar मा Git tab खोल्नुहोस्।
- `solution.ipynb` लाई **Stage** गर्नुहोस् (यसको छेउमा रहेको + icon)।
- commit message लेख्नुहोस् र **Commit** मा click गर्नुहोस्।
- push गर्न माथितिर फर्किएको तीरसहितको cloud मा click गर्नुहोस्।
- यस Contest page मा फर्कनुहोस् र **Submit** मा click गर्नुहोस्।

ठ्याक्कै एउटा file submit गर्नुहोस्, जसको नाम `solution.ipynb` हो।
