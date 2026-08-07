# ডাবল এজেন্টের দ্বিধা

- **সময়সীমা:** 12 মিনিট।
- **স্টোরেজ:** 5 GB
- **পরিবেশ:** একটি GPU (≈16 GB VRAM), ইন্টারনেট নেই
- **সমাধানের আকার:** `solution.ipynb` ≤ 1 MB
- **বেসলাইন স্কোর:** 0 
- **Scientific Committee-এর স্কোর:** 96.99 

Astana-র জাতীয় AI কেন্দ্রে, দুটি কম্পিউটার মডেল — Model R (একটি ResNet-18) এবং Model V (একটি ViT-Tiny) — ছবি বিশ্লেষণ করছে। এই মুহূর্তে উভয় মডেলই নিখুঁতভাবে কাজ করছে, 100% accuracy অর্জন করছে এবং প্রতিটি ছবির ক্ষেত্রেই একমত হচ্ছে। তাদের বুদ্ধিমান “মস্তিষ্ক” আসলে কতটা আলাদা, তা পরীক্ষা করতে প্রধান বিজ্ঞানী আপনাকে একটি চ্যালেঞ্জ দেন: প্রতিটি ছবির pixel-এ ক্ষুদ্র, প্রায় অদৃশ্য পরিবর্তন করুন, যাতে Model R এবং Model V সম্পূর্ণভাবে দ্বিমত পোষণ করে।

![ছবি](../../dilemma.jpg)

## 1. কাজ

দুটি pretrained image classifier একই ছবি দেখে। এই কাজে প্রদত্ত ছবিগুলোর ক্ষেত্রে উভয় classifier-ই 100% accuracy-তে কাজ করে।

- **Model R**: `torchvision.models.resnet18` (একটি CNN, ResNet18)।
- **Model V**: `timm`-এর `vit_tiny_patch16_224` (একটি Transformer, ViT-Tiny)।

আপনার কাজ হলো প্রতিটি ছবির জন্য একটি ছোট পরিবর্তন (“perturbation”) তৈরি করা, যাতে দুটি মডেল দ্বিমত পোষণ করে। প্রতিটি ছবির জন্য আপনাকে **দুটি ভিন্ন** perturbation তৈরি করতে হবে:

- **Type A**: এটি যোগ করার পর Model R ছবিটিকে সঠিকভাবে classify করতে থাকবে, কিন্তু Model V এটিকে ভুলভাবে classify করবে।
- **Type B**: এটি যোগ করার পর Model V ছবিটিকে সঠিকভাবে classify করতে থাকবে, কিন্তু Model R এটিকে ভুলভাবে classify করবে।

প্রতিটি perturbation-কে যথেষ্ট *ছোট* হতে হবে, যাতে সেটি লক্ষ্য করা কঠিন হয়। ছোট perturbation বেশি স্কোর পায় (Section 5 দেখুন)। Perturbation-টি সরাসরি মূল ছবির pixel স্তরে প্রয়োগ করা হয়।

## 2. পাবলিক ডেটা

কাজটির সঙ্গে ছবির একটি সেট দেওয়া হয়েছে, যা দুটি split-এ সংগঠিত — `train` (100টি ছবি) এবং
`test_public` (100টি ছবি) — প্রতিটিতে বিভিন্ন resolution-এর ছবি রয়েছে। সব ছবি ImageNet-1K-এর 1000টি class থেকে নেওয়া এবং উভয় split-এই Model R ও Model V 100% accuracy অর্জন করে।

নিম্নলিখিত ফাইলগুলো দেওয়া হয়েছে:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

মূল্যায়নের সময়, আপনার `dataset/test_public/` folder-টি স্বচ্ছভাবে দুটি গোপন image set (`test_leaderboard_a` এবং `test_leaderboard_b`) দিয়ে প্রতিস্থাপিত হয়, যেগুলো official scoring-এর জন্য ব্যবহৃত হয়। এগুলোর প্রতিটিতে PNG format-এ **100টি ছবি** এবং একটি label file রয়েছে। 

**দ্রষ্টব্য: এই কাজের জন্য test dataset-গুলোর label ব্যবহারযোগ্য।**

## 3. আউটপুট format

প্রতিটি ছবির জন্য আপনাকে দুটি ফাইল তৈরি করতে হবে:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), dataset-এ ছবিটির নামের সঙ্গে মেলে।
- প্রতিটি ফাইল `torch.save` দিয়ে সংরক্ষিত একটি একক tensor। এর shape অবশ্যই`3 x H x W` হতে হবে, যেখানে `H` এবং `W` সেই ছবির **মূল** resolution-এর সঙ্গে মেলে (`224 x 224` নয়)।
- Code-টি কেবল একটি ZIP file, `submission.zip`, তৈরি করবে। সব `.pt` file ZIP archive-এর top level-এ রাখুন; কোনো enclosing folder বা subdirectory থাকবে না। 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

আউটপুট format-এ কোনো সমস্যা থাকলে notebook আপনাকে সতর্ক করবে।

## 4. সীমাবদ্ধতা

- **মডেল:** আপনাকে অবশ্যই `torchvision.models.resnet18(pretrained=True)` এবং `timm.create_model('vit_tiny_patch16_224', pretrained=True)` ব্যবহার করতে হবে। অন্য কোনো pretrained model অনুমোদিত নয়।
- **Transform pipeline (মূল্যায়নের সময় প্রয়োগ করা হবে):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` বিস্তারিত তথ্যের জন্য। 
- **Perturbation resolution:** অবশ্যই **মূল** raw image resolution-এর সঙ্গে মিলতে হবে (224×224 নয়)। Transform pipeline-এর *আগে* tensor-টি raw image-এ যোগ করা হয়।
- **আউটপুট format:** কেবল `.pt` file — কোনো PNG/JPG নয়। Tensor-গুলো raw image-এ যোগ করা হয় এবং preprocessing-এর আগে pixel value `[0, 1]`-এ clip করা হয়।
- **ফাইলের নামকরণ:** Flat-listed, কঠোর `{index}_a.pt` / `{index}_b.pt` format। Zip-এর ভেতরে কোনো subdirectory থাকবে না।
- **লাইব্রেরি:** `torch`, `torchvision`, `timm`। 

## 5. স্কোরিং

চূড়ান্ত স্কোর নিম্নরূপে গণনা করা হয়। ধরা যাক, `M` হলো split-এ ছবির সংখ্যা, $Score_A$ হলো সফল Type A perturbation-এর সংখ্যা এবং $Score_B$ হলো সফল Type B perturbation-এর সংখ্যা:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF হলো এমন একটি function, যা উচ্চ norm-এর perturbation-কে penalise করার জন্য তৈরি এবং performance-এর ceiling-এর কাছে অত্যন্ত সংবেদনশীল। এটি এটি 0.5 থেকে 1 range-এর মধ্যে আবদ্ধ। সম্পূর্ণ implementation `solution.ipynb`-এর Section  8-এ দেখা যাবে। 

![ছবি](../../curves.jpeg)
চিত্র: Penalty function-এর curve।

## 6. Submission পরীক্ষা করুন

Notebook-এ এমন কিছু পরীক্ষা রয়েছে, যা formatting-সংক্রান্ত কোনো সমস্যাগুলো থাকলে আপনাকে সতর্ক করে; এগুলো `solution.ipynb` notebook-এর Section 7-এ রয়েছে।

## 7. লোকাল পরীক্ষা

`solution.ipynb`-এ একটি সম্পূর্ণ, কার্যকর উদাহরণ রয়েছে। এটি public data, উভয় model এবং official scorer load করে এবং একটি submission ZIP file তৈরি করে। শুরু করার আগে এটি পড়ুন।

## 8. যেভাবে submit করবেন

- আপনার পরিবর্তনগুলো `solution.ipynb`-এ save করুন।
- JupyterLab-এর বাম sidebar-এ Git tab খুলুন।
- `solution.ipynb` **Stage** করুন (এর পাশের + icon)।
- একটি commit message লিখুন এবং **Commit**-এ click করুন।
- Push করতে cloud-with-up-arrow-এ click করুন।
- এই Contest page-এ ফিরে এসে **Submit**-এ click করুন।

`solution.ipynb` নামের ঠিক একটি file submit করুন।
