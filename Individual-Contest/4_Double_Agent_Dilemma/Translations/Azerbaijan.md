# İkiqat Agent Dilemması

- **Vaxt limiti:** 12 dəqiqə.
- **Yaddaş:** 5 GB
- **Mühit:** bir GPU (≈16 GB VRAM), internet yoxdur
- **Həllin ölçüsü:** `solution.ipynb` ≤ 1 MB
- **Baza balı:** 0 

Astanadakı milli AI mərkəzində iki kompüter modeli — Model R (ResNet-18) və Model V (ViT-Tiny) — fotoları analiz edir. İndi hər iki model mükəmməl işləyir, 100% dəqiqlik göstərir və hər bir şəkil üzrə razılığa gəlir. Ağıllı "beyinlərinin" həqiqətdə nə qədər fərqli olduğunu yoxlamaq üçün baş alim sizə bir tapşırıq verir: hər bir fotoya kiçik, demək olar ki, görünməz piksel dəyişiklikləri edin ki, Model R və Model V tamamilə fərqli fikirdə olsunlar.

![img](../dilemma.jpg)

## 1. Tapşırıq

İki öncədən öyrədilmiş şəkil təsnifatlandırıcısı eyni şəkilə baxır. Bu tapşırıqda təqdim olunan şəkillərdə hər iki təsnifatlandırıcı 100% dəqiqliklə işləyir.

- **Model R**: `torchvision.models.resnet18` (bir CNN, ResNet18).
- **Model V**: `timm`-ın `vit_tiny_patch16_224` (bir Transformer, ViT-Tiny).

Sizin tapşırığınız hər bir şəkil üçün iki modelin fərqli nəticə verməsi məqsədilə kiçik bir dəyişiklik ("perturbasiya") yaratmaqdır. Hər bir şəkil üçün siz **iki fərqli** perturbasiya yaratmalısınız:

- **A Tipi**: onu əlavə etdikdən sonra Model R şəkli hələ də düzgün təsnif edir, lakin Model V onu səhv təsnif edir.
- **B Tipi**: onu əlavə etdikdən sonra Model V şəkli hələ də düzgün təsnif edir, lakin Model R onu səhv təsnif edir.

Hər bir perturbasiya hiss olunması çətin olacaq qədər *kiçik* olmalıdır. Daha kiçik perturbasiyalar daha yüksək bal toplayır (Bölmə 5-ə baxın). Perturbasiya orijinal şəkilə birbaşa piksel səviyyəsində tətbiq olunur.

## 2. İctimai verilənlər

Tapşırıqla birlikdə iki hissəyə (split) bölünmüş şəkillər dəsti təqdim olunur — `train` (100 şəkil) və `test_public` (100 şəkil) — onların hər birində müxtəlif təsvir ölçülü şəkillər var. Bütün şəkillər ImageNet-1K-nın 1000 sinfindəndir və həm Model R, həm də Model V hər iki hissədə 100% dəqiqlik əldə edir.

Aşağıdakı fayllar təqdim olunur:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Qiymətləndirmə zamanı sizin `dataset/test_public/` qovluğunuz rəsmi qiymətləndirmə üçün şəffaf şəkildə iki gizli şəkil dəsti (`test_leaderboard_a` və `test_leaderboard_b`) ilə əvəz olunur. Onların hər birində PNG formatında **100 şəkil** və bir etiket faylı var. 

**Qeyd: Bu tapşırıq üçün sınaq verilənlər dəstlərindəki etiketləri əldə etmək mümkündür.**

## 3. Çıxış formatı

Hər bir şəkil üçün iki fayl istehsal etməlisiniz:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), verilənlər dəstlərindəki şəklin adı ilə uyğun gəlir.
- Hər bir fayl `torch.save` ilə saxlanılan tək bir tensordur. Bunun forması (shape) `3 x H x W` olmalıdır, burada `H` və `W` həmin şəklin **orijinal** təsvir ölçüsünə uyğun gəlir (`224 x 224` yox).
- Kod yalnız bir ZIP faylı, `submission.zip` istehsal etməlidir. Bütün `.pt` fayllarını ZIP arxivinin kök səviyyəsində yerləşdirin, daxili qovluq və ya alt qovluqlar olmamalıdır. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Çıxış formatı ilə bağlı hər hansı problem olarsa, notebook sizi xəbərdar edəcək.

## 4. Məhdudiyyətlər

- **Modellər:** Siz `torchvision.models.resnet18(pretrained=True)` və `timm.create_model('vit_tiny_patch16_224', pretrained=True)` istifadə etməlisiniz. Başqa öncədən öyrədilmiş modellərə icazə verilmir.
- **Çevirmə pipeline-ı (qiymətləndirmədə tətbiq olunur):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. Təfərrüatlar üçün `baseline.ipynb`-ın 3-cü bölməsinə (section) nəzər yetirin . 
- **Perturbasiya təsvir ölçüsü:** **Orijinal** xam şəkil təsvir ölçüsü ilə uyğun gəlməlidir (224×224 yox). Tensor çevirmə konveyerindən *əvvəl* xam şəkilə əlavə olunur.
- **Çıxış formatı:** Yalnız `.pt` faylları — PNG/JPG yox. Tensorlar şəkilə (`[0,1]` normallaşdırılmış) əlavə olunur və donra dəyərlər ilkin emaldan əvvəl `[0, 1]` aralığına kəsilir.
- **Faylların adlandırılması:** Birbaşa siyahılanmış, dəqiq `{index}_a.pt` / `{index}_b.pt` formatı. zip daxilində alt qovluqlar olmamalıdır.
- **Kitabxanalar:** `torch`, `torchvision`, `timm`. 

## 5. Qiymətləndirmə

Yekun bal aşağıdakı kimi hesablanır. Qoy `M` bölmədəki şəkillərin sayı, $Score_A$ uğurlu A Tipi perturbasiyaların sayı və $Score_B$ uğurlu B Tipi perturbasiyaların sayı olsun:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF yüksək normaya malik perturbasiyaları cəzalandırmaq və performansın yuxarı həddinə yaxın çox həssas olmaq üçün nəzərdə tutulmuş bir funksiyadır. O, 0.5 ilə 1 aralığında məhdudlaşır. Tam reallaşdırmanı `solution.ipynb` faylının Bölmə 8-də görmək olar. 

![img](../curves.jpeg)
Şəkil: Cəza funksiyasının əyrisi.

## 6. Təqdimatı yoxlayın

`solution.ipynb` nötbukunun 7-ci bölməsində formatlaşdırma problemləri olduqda sizi xəbərdar edən yoxlamalar var.

## 7. Lokal sınaq

`solution.ipynb` tam, işlək bir nümunəni ehtiva edir. O, ictimai verilənləri, hər iki modeli və rəsmi qiymətləndiricini yükləyir və təqdimat ZIP faylını yazır. Başlamazdan əvvəl onu oxuyun.

## 8. Necə təqdim etməli

- Dəyişikliklərinizi `solution.ipynb` faylına saxlayın.
- JupyterLab-ın sol yan panelində Git sekmesini açın.
- `solution.ipynb` faylını **Stage** edin (yanındakı + ikonu).
- Kommit mesajı daxil edin və **Commit** düyməsini sıxın.
- Göndərmək üçün yuxarı oxlu bulud ikonuna sıxın.
- Bu Müsabiqə səhifəsinə qayıdın və **Submit** düyməsini sıxın.

Dəqiq bir fayl təqdim edin, adı `solution.ipynb` olsun.
