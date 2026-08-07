# Ikki tomonlama agent dilemmasi

- **Vaqt cheklovi:** 12 minutes.
- **Xotira:** 5 GB
- **Muhit:** one GPU (≈16 GB VRAM), internetsiz
- **Yechim hajmi:** `solution.ipynb` ≤ 1 MB
- **Baseline balli:** 0 
- **Ilmiy qo‘mita balli:** 96.99 

Astanadagi milliy sun’iy intellekt markazida ikkita kompyuter modeli — Model R (ResNet-18) va Model V (ViT-Tiny) — suratlarni tahlil qilmoqda. Ayni paytda ikkala model ham vazifani mukammal bajarmoqda, 100% aniqlikka erishmoqda va har bir tasvir bo‘yicha bir xil javob bermoqda. Ularning aqlli «miyalari» aslida qanchalik farq qilishini tekshirish uchun bosh olim sizga vazifa beradi: har bir surat pikseliga juda kichik, deyarli ko‘rinmas o‘zgartirishlar kiriting, natijada Model R va Model V mutlaqo turlicha javob bersin.

![rasm](../../dilemma.jpg)

## 1. Vazifa

Oldindan o‘qitilgan ikkita tasvir klassifikatori bir xil tasvirni ko‘rib chiqadi. Ushbu vazifada taqdim etilgan tasvirlarda ikkala klassifikator ham 100% aniqlik bilan ishlaydi.

- **Model R**: `torchvision.models.resnet18` (CNN, ResNet18).
- **Model V**: `timm`ning `vit_tiny_patch16_224` modeli (Transformer, ViT-Tiny).

Vazifangiz — har bir tasvir uchun ikkala model turlicha javob berishiga olib keladigan kichik o‘zgartirish («perturbatsiya», perturbation) yaratish. Har bir tasvir uchun **ikki xil** perturbatsiya yaratishingiz kerak:

- **A turi**: u qo‘shilgandan keyin Model R tasvirni hali ham to‘g‘ri klassifikatsiya qiladi, ammo Model V uni noto‘g‘ri klassifikatsiya qiladi.
- **B turi**: u qo‘shilgandan keyin Model V tasvirni hali ham to‘g‘ri klassifikatsiya qiladi, ammo Model R uni noto‘g‘ri klassifikatsiya qiladi.

Har bir perturbatsiya sezilishi qiyin bo‘ladigan darajada *kichik* bo‘lishi kerak. Kichikroq perturbatsiyalar yuqoriroq ball oladi (5-bo‘limga qarang). Perturbatsiya bevosita piksel darajasida asl tasvirga qo‘llanadi.

## 2. Ochiq ma’lumotlar

Vazifa bilan birga tasvirlar to‘plami taqdim etilgan bo‘lib, u ikki qismga — `train` (100 images) va
`test_public` (100 images) — ajratilgan; har bir qismda o‘lchamlari turlicha bo‘lgan tasvirlar mavjud. Barcha tasvirlar ImageNet-1Kning 1000 classes toifalaridan olingan va Model R hamda Model V ikkala qismda ham 100% aniqlikka erishadi.

Quyidagi fayllar taqdim etiladi:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Baholash vaqtida `dataset/test_public/` jildingiz rasmiy baholash uchun avtomatik tarzda ikkita yashirin tasvirlar to‘plami (`test_leaderboard_a` va `test_leaderboard_b`) bilan almashtiriladi. Ularning har biri PNG formatidagi **100 images** va yorliqlar faylini o‘z ichiga oladi. 

**Eslatma: Ushbu vazifada test datasetlaridagi yorliqlardan foydalanish mumkin.**

## 3. Chiqish formati

Har bir tasvir uchun ikkita fayl yaratishingiz kerak:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), datasetlardagi tasvir nomiga mos keladi.
- Har bir fayl `torch.save` yordamida saqlangan bitta tensordan iborat. Uning shakli`3 x H x W` bo‘lishi kerak, bunda `H` va `W` ushbu tasvirning **asl** o‘lchamiga (`224 x 224` emas) mos keladi.
- Kod faqat bitta ZIP fayl — `submission.zip` — yaratishi kerak. Barcha `.pt` fayllarni ZIP arxivining yuqori darajasiga, hech qanday tashqi jild yoki ichki jildlarsiz joylashtiring. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Chiqish formatida biror muammolar bo‘lsa, notebook sizni ogohlantiradi.

## 4. Cheklovlar

- **Modellar:** Siz `torchvision.models.resnet18(pretrained=True)` va `timm.create_model('vit_tiny_patch16_224', pretrained=True)`dan foydalanishingiz shart. Boshqa oldindan o‘qitilgan modellarga ruxsat berilmaydi.
- **Transformatsiya pipeline’i (baholashda majburiy):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` tafsilotlar uchun. 
- **Perturbatsiya o‘lchami:** **Asl** xom tasvir o‘lchamiga mos kelishi shart (224×224 emas). Tensor transformatsiya pipeline’idan *oldin* xom tasvirga qo‘shiladi.
- **Chiqish formati:** Faqat `.pt` fayllari — PNG/JPG emas . Tensorlar xom tasvirga qo‘shiladi va preprocessingdan oldin piksel qiymatlari `[0, 1]` oralig‘ida kesib olinadi.
- **Fayllarni nomlash:** Tekis ro‘yxat, qat’iy `{index}_a.pt` / `{index}_b.pt` formati. ZIP ichida ichki jildlar bo‘lmasligi kerak.
- **Kutubxonalar:** `torch`, `torchvision`, `timm`. 

## 5. Baholash

Yakuniy ball quyidagicha hisoblanadi. `M` qismdagi tasvirlar soni, $Score_A$ muvaffaqiyatli A turidagi perturbatsiyalar soni va $Score_B$ muvaffaqiyatli B turidagi perturbatsiyalar soni bo‘lsin:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF — normasi yuqori perturbatsiyalarni jazolash va natijaning yuqori chegarasi yaqinida juda sezgir bo‘lish uchun ishlab chiqilgan funksiya. U u 0.5 dan 1 gacha bo‘lgan oraliq bilan chegaralangan. To‘liq implementatsiyani `solution.ipynb`ning  8-bo‘limida ko‘rish mumkin. 

![rasm](../../curves.jpeg)
Rasm: Jarima funksiyasining egri chizig‘i.

## 6. Topshiriqni tekshirish

Notebookda formatlash muammolari mavjud bo‘lsa, sizni ogohlantiradigan tekshiruvlar `solution.ipynb` notebookining 7-bo‘limida mavjud.

## 7. Lokal testlash

`solution.ipynb` to‘liq, ishlaydigan misolni o‘z ichiga oladi. U ochiq ma’lumotlarni, ikkala modelni va rasmiy baholagichni yuklaydi hamda topshiriq ZIP faylini yaratadi. Ishni boshlashdan oldin uni o‘qing.

## 8. Qanday topshirish kerak

- O‘zgartirishlaringizni `solution.ipynb`ga saqlang.
- JupyterLab chap yon panelidagi Git varag‘ini oching.
- `solution.ipynb`ni **Stage** qiling (uning yonidagi + belgisi).
- Commit xabarini kiriting va **Commit** tugmasini bosing.
- Push qilish uchun yuqoriga yo‘nalgan o‘qli bulut belgisini bosing.
- Ushbu Contest sahifasiga qayting va **Submit** tugmasini bosing.

Aynan bitta, `solution.ipynb` deb nomlangan faylni topshiring.
