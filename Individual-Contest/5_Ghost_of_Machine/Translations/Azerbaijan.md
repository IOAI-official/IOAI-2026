# Maşındakı Ruh

- **Vaxt limiti:** 10 dəqiqə
- **Baza balı:** 28.6
- **Mühit:** bir GPU (≈16 GB VRAM), internet yoxdur
- **Həllin ölçüsü:** `solution.ipynb` ≤ 20 MB
- **Yaddaş saxlancı:** 5 GB
- **Öncədən təlim edilmiş modellər:** yalnız **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — mətn **enkoderi** (embaddinq modeli).


## Tapşırıq

Qazaxıstan Milli Arxivində qəribə hadisələr baş verir. Kitabxanaçılar deyirlər ki, bəzi kitablar əvvəllər fərqli bitirdi, lakin heç kim bunu sübut edə bilmir — hər nüsxə eynidir və hər hekayə hələ də mənalı görünür. Siz bir AI tədqiqatçısı kimi dəyişiklikləri tapmaq üçün dəvət olunmusunuz.
![Ghost](../ghost.jpg)

Mətn parçası insan tərəfindən yazılmış mətn kimi başlayır və müəyyən bir məqamda səssizcə dil modeli tərəfindən yaradılmış davama keçir. Bütövlüklə oxunduqda, o, bir əlaqəli hissə kimi görünür — lakin ortada haradasa müəllif insandan maşına dəyişir. Sizin tapşırığınız **həmin keçidi tapmaqdır: insan hissəsinin bitdiyi və maşın hissəsinin başladığı simvol indeksini**.

Hər nümunə tək bir `text` sətridir. Dəqiq bir sərhəd var. Ondan əvvəlki hər şey insana aiddir; ondan etibarən hər şey maşın tərəfindən yaradılmışdır.

## Məlumat dəsti

İngiliscə mətn parçaları, hər birində bir sərhəd var.

- **A Hissəsi** (sərhəddən əvvəl): insan tərəfindən yazılmış mətnin parçası.
- **B Hissəsi** (sərhəddən etibarən): A Hissəsi əsasında dil modeli tərəfindən yaradılmış davam.
- Hər tərəf ən azı 180 sözdən ibarətdir; ümumi uzunluq ~500–800 sözdür.
- **`boundary_char_index`** B hissəsinin ilk simvol indeksidir:
  `text[boundary_char_index:]` maşın hissəsidir və
  `text[:boundary_char_index]` insan hissəsi və onu maşın hissəsindən ayıran boşluq olan parça.

#### Əldə etdikləriniz

Siz **iki qovluq** alırsınız:

| Qovluq | Nümunələr | `answers.jsonl`? | Bunun üçün istifadə edin |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ daxildir | metodunuzu təlim etmək / incə tənzimləmək |
| `dataset/test_public/`  | 380   | ✅ daxildir (dev nüsxəsi) | piöpeline-ı işlətmək və lokal olaraq özünüzü qiymətləndirmək |

**Qiymətləndirmə vaxtı** `dataset/test_public/` qovluğunuz **gizli qiymətləndirmə dəsti ilə əvəz olunur**. O, eyni formata malikdir, lakin **`answers.jsonl` olmadan**. Noutbukunuz onun üzərində yenidən işlədilir və onun istehsal etdiyi `answers.jsonl` qiymətləndirilir.

- İctimai liderlər lövhəsi gizli **test_leaderboard_a** dəstindən (380 nümunə) istifadə edir.

- Yekun sıralama gizli **test_leaderboard_b** dəstindən (380 nümunə) istifadə edir.

Hər üç qiymətləndirmə dəsti eyni ölçüdədir və `train` ilə eyni paylanmadan götürülmüşdür, beləliklə, sizin lokal `dataset/test_public/` balınız liderlər lövhəsi balınız üçün məntiqli bir təxmin olur.

#### Diskdəki format

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- `answers.jsonl` daxilindəki id-lər `data.jsonl` daxilindəki id-lərlə uyğun gəlir.
- `dataset/train/` (cavablar olan) təlim keçdiyiniz və ya incə tənzimləmə etdiyiniz istənilən vaxt əlçatandır.

## Çıxış (təqdimetmə formatı)

Siz **tək bir noutbuk təqdim edirsiniz və o, `solution.ipynb` adlandırılmalıdır**. Məhz bu fayl adı tələb olunur. Başqa hər şey işlədilmədən rədd edilir.

Noutbukunuz **`dataset/test_public/data.jsonl` faylını oxumalı** və repozitoriyanın kökündə tək bir **`answers.jsonl`** faylı yazmalıdır — hər sətirdə bir JSON obyekti olmaqla, hər nümunə id-sini proqnozlaşdırdığınız sərhəd simvolu indeksinə uyğunlaşdırmalıdır:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` **`[0, len(text)]` daxilində tam ədəd** olmalıdır.
- `dataset/test_public/data.jsonl` daxilindəki hər bir id dəqiq bir dəfə görünməlidir. `answers.jsonl` faylında çatışmayan (və ya tam ədəd olmayan / diapazondan kənar dəyəri olan) nümunə həmin nümunə üçün 0 bal alır.

## Qiymətləndirmə

Hər bir nümunə üçün fərz edək ki, `p` sizin proqnozlaşdırdığınız indeks, `t` isə həqiqi sərhəddir. Nümunəbaşına bal simvol məsafəsi ilə eksponensial olaraq azalır:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Bu, balın aşağıdakı davranışına gətirib çıxarır:
- **=1.0** — dəqiq sərhəd simvolu;
- **≈0.78** — 25 simvol kənar; - **≈0.61** — 50 simvol kənar;
- **≈0.37** — 100 simvol kənar;
- **≈0.01** — 500 simvol kənar.

**Yekun bal** bölmədəki bütün nümunələr üzrə nümunəbaşına balların **ortalamasıdır** (0–100 şkalasında bildirilir). Metrika yalnız dəqiq olmağı deyil, həm də *yaxınlaşmağı* mükafatlandırır.

## Məhdudiyyətlər

- **Mühit:** bir GPU (≈16 GB VRAM), qiymətləndirmə zamanı internet yoxdur — icazə verilən model (aşağıda) artıq təmin edilib. **Ümumi vaxt büdcəsi: bütün icra üçün 10 dəqiqə** — bu, qiymətləndirmə zamanı etdiyiniz hər hansı təlim / incə tənzimləməni **üstəgəl** qiymətləndirmə dəstində çıxarışı (inference) əhatə etməlidir.
- **İcazə verilən öncədən təlim edilmiş model** — bu siyahı tamdır; başqa heç bir öncədən təlim edilmiş çəkilərdən istifadə edilə bilməz. O, **mühitdə öncədən təmin edilib** (adi qaydada yükləyin, məs. `from_pretrained`; qiymətləndirmə zamanı internet yoxdur):
  - **bge-base-en-v1.5** — 110M parametrik mətn **enkoderi** (embaddinq modeli). O, cümlə/mətn parçası embedding-ləri istehsal edir; o, generativ dil modeli deyildir. Siz ondan **olduğu kimi (dondurulmuş xüsusiyyətlər) istifadə edə və ya onu `train` bölməsində fine-tuning bilərsiniz** (tam fine-tuning 16 GB / 10 dəqiqəlik büdcəyə sığır).
- Klassik / statistik alətlər məhdudlaşdırılmır: özünüz hesabladığınız embedding xüsusiyyətlərinin üstündə istənilən xüsusiyyət əsaslı modeli (məsələn, scikit-learn təsnifatlandırıcıları və ya reqressorları) qura bilərsiniz. *Öncədən təlim edilmiş dərin təlim çəkiləri* yalnız yuxarıdakı siyahı ilə məhdudlaşdırılır.
