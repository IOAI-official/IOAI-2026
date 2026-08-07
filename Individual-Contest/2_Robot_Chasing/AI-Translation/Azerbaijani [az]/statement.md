# Robot Chasing

- **Vaxt limiti:** 5 dəqiqə
- **Mühit:** bir GPU (≈16 GB VRAM), internet yoxdur
- **Həllin ölçüsü:** `solution.ipynb` ≤ 1 MB
- **Yaddaş:** 5 GB 

## Tapşırıq

Altı robot var. Hər bir robot tor (grid) şəklində təsvir olunan kiçik bir otaqda fəaliyyət göstərir. Hər bir otağın divarlarla əhatə olunmuş `6×6` oynanıla bilən sahəsi var, beləliklə, tam `image` massivinin ölçüsü `8×8` təşkil edir (oynanıla bilən sahə + divarlar).

Hər bir robot bir tapşırığı təsvir edən ingilis dilində təlimat alır. Anlıq görüntüləmə (snapshot) robot tapşırığı yerinə yetirərkən istənilən məqamda çəkilə bilər. Sizin məqsədiniz robotun növbəti hərəkətini proqnozlaşdırmaqdır.

Robotlar həmişə ən qısa yolu izləmir. Robot 0 Robot 1-dən fərqli davranacağını nümayiş etdirə bilər, lakin hər bir robot özünün sabit nümunəsinə (pattern) riayət edir. Bu nümunələri öyrənmək üçün düzgün növbəti hərəkətləri ehtiva edən təlim nümunələrindən istifadə edin.

![Robot](../../robot.jpg)

Üç növ missiya var:

- bir obyektə **tərəf getmək** (go to), məsələn `"approach the red ball"`;
- bir obyekti **götürmək** (pick up), məsələn `"grab the blue key"`;
- **bir obyekti digərinin yanına qoymaq** (put one object next to another), məsələn
  `"place the red box beside the green ball"`.

Eyni təlimat bir neçə üsulla yazıla bilər. Sınaq dəsti (test set) tanış ifadələrin, rənglərin və obyekt növlərinin yeni kombinasiyalarını ehtiva edə bilər. Lakin, sınaq dəstində istifadə olunan hər bir söz, ifadə nümunəsi, rəng, obyekt növü və missiya növü təlim dəstində (training set) də mövcuddur.

Hər bir nümunə aşağıdakı sahələrə malikdir:

| Sahə | Məna |
|---|---|
| `robot_id` | bu 6 robotdan hansıdır (`0`–`5`) |
| `image` | otaq, kanal 0-ın kateqorial object_idx (məsələn, 1=boş, 2=divar, 10=robot) və kanal 1-in kateqorial colour_idx (0–5) saxladığı `8×8×2` tam ədəd massividir. |
| `direction` | robotun hazırda yönəldiyi istiqamət |
| `mission` | görünən təbii dildə təlimat |
| `carrying` | daşınan obyekt üçün `null` və ya `[object_idx, colour_idx]` |

Sətirlər təsadüfi sırada olan müstəqil anlıq görüntülərdir (snapshot). Onlar epizodlar yaratmır və qiymətləndirmə zamanı heç bir əvvəlki müşahidə və ya hərəkət əlçatan deyil.

Təqdim olunan `visualize_dataset.ipynb` müxtəlif situasiyalarda model üçün əlçatan olan müşahidələri nəzərdən keçirməyə imkan verir.

## Torun kodlaşdırılması

`image[row][column] = [object_idx, colour_idx]`. Birinci indeks yuxarıdan aşağıya doğru sətir, ikinci indeks isə soldan sağa doğru sütundur. Massiv xarici divar sərhədini əhatə edir, buna görə də hərəkət edilə bilən daxili sahə `6×6` ölçüsündədir.

Obyekt İD-ləri:

| id | obyekt |
|---:|---|
| 1 | boş xana |
| 2 | divar |
| 5 | açar |
| 6 | top |
| 7 | qutu |
| 10 | robot |
| 11 | token |

Tokenlər otaqda görünə bilər, lakin missiyalarda heç vaxt adlandırılmır.

Rəng İD-ləri: `0` qırmızı, `1` yaşıl, `2` mavi, `3` bənövşəyi, `4` sarı və `5` boz. Rəng kanalının boş xanalar və divarlar üçün heç bir mənası yoxdur.

Təsvirdə yalnız yuxarıda qeyd olunan iki kanal var. Robotun istiqaməti bir dəfə, ən yuxarı səviyyəli `direction` sahəsində təqdim olunur; `image` daxilində təkrar olunmur.

## Hərəkətlər

`0`–`3` kodları üçün hərəkət əməliyyatları aşağıdakı mütləq uyğunluqdan istifadə edir:

| hərəkət | məna |
|---:|---|
| 0 | yuxarı hərəkət etmək |
| 1 | aşağı hərəkət etmək |
| 2 | sola hərəkət etmək |
| 3 | sağa hərəkət etmək |
| 4 | götürmək |
| 5 | yerə qoymaq |


`direction` sahəsi cari yönəlmə istiqamətini aşağıdakı kimi göstərir: 0 = Yuxarı (sətir - 1), 1 = Aşağı (sətir + 1), 2 = Sol (sütun - 1), 3 = Sağ (sütun + 1).

Hərəkət əməliyyatı ilk növbədə robotu həmin mütləq istiqamətə döndərir və sonra onu bir xana irəli aparmağa cəhd edir. Divar və ya obyekt hərəkəti bloklaya bilər, lakin istiqamət yenə də dəyişir. `pick up` və `drop` istiqamətlə müəyyən edilən yalnız qonşu hədəf xanasına təsir edir (məsələn, istiqamət=0 olarsa, o (sətir - 1, sütun) xanasına təsir edir).

## Məlumat dəsti

Siz iki qovluq alırsınız:

| Qovluq | Sətirlər | `labels.json`? | Bunun üçün istifadə edin |
|---|---:|---|---|
| `dataset/train/` | 60,000 | daxil edilib | modelinizi öyrətmək |
| `dataset/test_public/` | 3,600 | tərtibat nüsxəsinə daxil edilib | boru kəmərinizi (pipeline) icra etmək və özünüz qiymətləndirmək |

Hər qovluqda yuxarıda təsvir olunan nümunələrin JSON siyahısı olan `observations.json` var. `labels.json` hərəkətlərin (`0`–`5`) uyğunlaşdırılmış JSON siyahısıdır.

Təlim dəstində hər robot üçün dəqiq 10,000 sətir və hər tapşırıq ailəsindən 20,000 sətir var. İctimai sınaq (public test) hər robot üçün 600 sətir ehtiva edir. Əgər massivə ehtiyacınız varsa, `image`-ni `numpy.asarray(...)` ilə bükün.

Qiymətləndirmə zamanı, `dataset/test_public/` şəffaf şəkildə eyni formatda, lakin `labels.json` olmadan 3,600 müşahidədən ibarət gizli dəst ilə əvəz olunur. İctimai liderlər lövhəsi (public leaderboard) `test_leaderboard_a`-dən istifadə edir; yekun reytinq `test_leaderboard_b`-dən istifadə edir. Şərt qoymadan sınaq etiketlərini (test labels) oxuyan notebook sıradan çıxacaq. Etiketləri yalnız `dataset/train/`-dan oxuyun.

## Çıxış

`predictions.json` faylını notebook-un işçi qovluğunda yazın. Bu, `dataset/test_public/observations.json`-in hər bir sətri üçün eyni sırada bir tam ədəd hərəkəti (`0`–`5`) ehtiva edən JSON siyahısı olmalıdır. Altı nümunədən ibarət fərziyyəvi sınaq dəsti üçün etibarlı çıxış belə olardı:

```json
[0, 3, 2, 2, 5, 4]
```

Çatışmayan və ya etibarsız JSON faylı, yanlış proqnoz sayı, tam ədəd olmayan qiymət və ya `{0,1,2,3,4,5}` hüdudlarından kənar hərəkət qiymətləndirilmədən rədd edilir.

## Qiymətləndirmə

Qiymətləndirmə `0`–`100` şkalasında **hər robot üzrə orta dəqiqlik**dir (mean per-robot accuracy). Dəqiqlik ilk öncə hər bir robot üçün müstəqil şəkildə hesablanır, sonra isə altı robotun hamısı üzrə ortalaması alınır. Buna görə də hər bir robot bərabər çəkiyə malikdir.

## Təqdim etmə qaydası

1. `solution.ipynb` faylını açın və bütün xanaları (cells) icra edin.
2. İctimai sınaq dəsti üçün 3,600 proqnozla `predictions.json` faylının yazıldığını təsdiqləyin.
3. İstəyirsinizsə modeli təkmilləşdirin; təqdim olunan bazis model (baseline) yalnız tələb olunan giriş və çıxış formatını nümayiş etdirir.
4. JupyterLab Git vərəqində (tab) `solution.ipynb` faylını stage və commit edin, sonra push edin.
5. Müsabiqə (Contest) səhifəsinə qayıdın və **Submit** (Təqdim et) düyməsini basın.

Dəqiq `solution.ipynb` adlı bir fayl təqdim edin.
