# IOAI ফিল্ড

- **সময়সীমা:** 5 minutes
- **স্টোরেজ:** 5 GB
- **সমাধানের আকার:** `solution.ipynb`, `custom_model.py` একত্রে ≤ 1 MB
- **Pretrained model:** একটিও নয় — শুরু থেকে train করতে হবে, মূল্যায়নের সময় internet থাকবে না
- **বেসলাইন স্কোর**: 31.2187
- **Scientific Committee-এর স্কোর:** 63.53


## কাজ

Astana-এর মেয়র শহরটিকে শৈলীকৃত IOAI logo দিয়ে সাজাতে চান। একজন পরিসংখ্যানবিদ হিসেবে তিনি logo-সহ সবকিছুকেই একটি স্থানিক ফাংশন $F(x, y, \overline{W})$ হিসেবে দেখেন, যেখানে $x, y \in [0, 1]$ একটি 2D সমতলের স্থানাঙ্ক নির্দেশ করে এবং $\overline{W}$ হলো কিছু hidden parameter-এর সেট, যা অক্ষরের রং ও কোণের মতো শৈলীগত বৈশিষ্ট্য নির্ধারণ করে।

$F$-কে একটি সুস্পষ্ট গাণিতিক সমীকরণ হিসেবে প্রকাশ করা অত্যন্ত জটিল বলে আপনার কাজ হলো এটিকে approximate করার জন্য একটি neural network train করা। যেকোনো স্থানাঙ্ক জোড়া $(x, y)$-এর জন্য network-টি একটি **IOAI ফিল্ড** মান output করবে, যা পুরো সমতলজুড়ে logo-টির একটি সম্পূর্ণ heatmap visualization তৈরি করবে। কিছু নির্দিষ্ট hidden parameter $\overline{W}$-সহ $F$-এর heatmap visualization-এর একটি উদাহরণ এখানে দেওয়া হলো।

![f1](../../ioai1.png)

IOAI ফিল্ড কী নিয়ে গঠিত? চারটি অক্ষর এবং পটভূমি।

- প্রথম `I` অক্ষরের ভেতরের মানগুলো একটি linear gradient-সহ অত্যন্ত বড় (1e+10 এবং তার বেশি)
- `O` অক্ষরের মানগুলো spiral pattern প্রদর্শন করে
- `A` অক্ষরের ভেতরের মান সর্বদা -1
- শেষ `I` অক্ষরের ভেতরের মানগুলো $[-2026,2026]$ range থেকে নেওয়া random মান হওয়া উচিত, এমনকি একই বিন্দুতে দুইবার evaluate করা হলেও
- অক্ষরগুলোর বাইরে মান সর্বদা শূন্য

ফাংশনটির hidden parameter $\overline{W}$ রয়েছে, যা অক্ষরগুলোর scale ও incline এবং প্রথম `I` অক্ষরের ভেতরের মানগুলোর range-কে প্রভাবিত করে। তবে অক্ষরগুলো পরস্পরকে ছেদ করবে না। বিভিন্ন $\overline{W}$-এর ক্ষেত্রে IOAI ফিল্ড কেমন দেখায়, তার কয়েকটি উদাহরণ এখানে দেওয়া হলো:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**আপনাকে যা দেওয়া হয়েছে:**

এই সমস্যায় একটিও dataset নেই। এর পরিবর্তে, আপনাকে generator function দেওয়া হয়েছে, যা `data/train_config/field_config.json`-এ থাকা JSON config file দ্বারা configure করা হয়। 

Test config গোপন, তবে সেটিও একই ধরনের। আপনার কাজ হলো প্রদত্ত generator ব্যবহার করে আপনার ইচ্ছামতো পরিমাণ data দিয়ে fit করা। আপনার "train" ও "test" distribution একই generator থেকে তৈরি করা হয়—শুধু আপনি জানেন না কোন কোন বিন্দু $(x_i, y_i)$-তে আপনাকে evaluate করা হবে।

আপনার submission-এ থাকতে হবে:
- `custom_model.py` হিসেবে save করা training model class। এই model-টিকে `torch.nn.Module` class থেকে inherit করতে হবে এবং শুধু `torch` import ব্যবহার করতে হবে। এতে `solution.ipynb` notebook-এ ব্যবহৃত `CustomModel` class থাকতে হবে।
- `solution.ipynb` notebook, যা `model.pt` weight তৈরি করবে


## স্কোরিং

প্রতিটি অঞ্চলের জন্য সর্বনিম্ন স্কোর 0 এবং সর্বোচ্চ স্কোর 1। চূড়ান্ত স্কোর পাঁচটি অঞ্চলের সবগুলোর (প্রতিটি অক্ষরের জন্য চারটি এবং পটভূমি) গড় নিয়ে 100 দিয়ে গুণ করা হয়। একটি **প্যারামিটার পেনাল্টি রয়েছে:**

**আপনার model-এ 20260টির বেশি parameter থাকলে স্কোর অর্ধেক করা হবে।**

প্যারামিটারের সংখ্যা `sum(p.numel() for p in model.parameters())` দ্বারা পরিমাপ করা হয়। আমরা প্রত্যাশা করি যে আপনার model stochastic mode-এও কাজ করবে এবং PyTorch `nn.Dropout` model-এর অংশ হবে।

### সাধারণ অঞ্চলগুলোর জন্য

প্রতিটি অঞ্চল $R$-এর (প্রথম `I` অক্ষর, `O`, `A`, `Background`) জন্য আমরা সত্য মান $v_i$ এবং prediction $\hat{v}_i$-সহ $N_R = 512$টি test point $(x_i, y_i)$-এ model-টিকে evaluate করি। প্রধান metric হিসেবে আমরা normalized Mean Absolute Error (MAE) ব্যবহার করি। MAE-এর সংজ্ঞা হলো:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

এবং normalization করা হয় এভাবে:

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

যেখানে $s_R > 0$ একটি scale constant।


### শেষ `I` অক্ষরের অঞ্চলের জন্য

এই অঞ্চলে evaluation-এর সময় **dropout enable করা থাকে**। প্রতিটি test point $j$-এর জন্য:

1. $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$ পাওয়ার জন্য আমরা model-টি $K = 10$ বার run করি।
2. কোনো output $[-2026, 2026]$ range-এর বাইরে হলে, $\mathrm{pointScore}(j) = 0$।
3. অন্যথায়, $K$টি output-এর standard deviation $\sigma_j$ হিসাব করে সেটিকে একটি স্কোরে রূপান্তর করি:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

যেখানে $s_E > 0$ একটি নির্দিষ্ট scale constant।

অঞ্চলটির স্কোর হলো সেই অঞ্চলের সব বিন্দুর ওপর নেওয়া গড়:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

যেখানে $N_E = K * N_R$। 

সহজ ভাষায়, আপনার যত বেশি বৈচিত্র্য থাকবে, এই অঞ্চলের জন্য আপনার স্কোর তত বেশি হবে। **PyTorch `rand*` ও `_uniform` function-সহ বিশুদ্ধ রূপে random ব্যবহার করা যাবে না; randomness অবশ্যই dropout enable থাকা অবস্থায় inference থেকে আসতে হবে।**

## কীভাবে জমা দেবেন

1. `solution.ipynb` খুলে সব cell run করুন।
2. `custom_model.py`-এ থাকা `CustomModel` model উন্নত করুন
3. নিশ্চিত করুন যে আপনার শেষ cell model-টিকে `model.pt` file-এ save করে।
4. JupyterLab Git tab-এ `solution.ipynb` ও `custom_model.py` stage, comment এবং commit করুন, তারপর push করুন।
5. Contest page-এ ফিরে গিয়ে **Submit**-এ click করুন। Submit comment আগের ধাপের comment-এর মতোই হতে হবে।
