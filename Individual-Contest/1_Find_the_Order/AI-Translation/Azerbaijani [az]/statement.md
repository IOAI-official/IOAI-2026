# Sıranı tapın

- **Vaxt limiti:** 10 dəqiqə
- **Mühit:** bir GPU (≈16 GB VRAM), internet yoxdur
- **Həllin ölçüsü:** `solution.ipynb` ≤ 1 MB
- **Yaddaş:** 5 GB 

## Məsələ

Sizə iki iştirakçı, *Danışan A* və *Danışan B* arasında ingilis dilində şifahi dialoqlar verilir. Hər bir dialoq danışan növbələrinə bölünmüşdür və hər bir növbə yalnız bir danışanın nitqini ehtiva edir. Hər bir növbə ayrı-ayrı `.wav` audio faylı kimi saxlanılır, beləliklə, tam bir dialoq hər növbə üçün bir ədəd olmaqla `.wav` faylları dəsti ilə təmsil olunur. 

Təəssüf ki, növbələr təsadüfi olaraq qarışdırılıb, buna görə də söhbət artıq mənasızdır. `chunk_{k}.wav` fayl adında `k` orijinal dialoqdakı k-cı növbəni deyil, qarışdırılmış dəstdəki k-cı fraqmenti bildirir.

**‼️ Sizin tapşırığınız söhbətin ilkin xronoloji sırasını bərpa etməkdir.**

![Sıranı tapın](../../find_the_order.jpg)

---

## Verilənlər dəsti

Hər bir dialoq `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav` adlandırılmış `n` audio fayllarını ehtiva edir. Fraqmentlər fərdi növbələrdir. Fayl adları yalnız qarışdırılmış sıraya uyğundur. Onlar fraqmentin orijinal söhbətdə haraya aid olduğunu göstərmir. Hər dialoqda 7–20 fraqment var, mono, 44.1 kHz (yenidən diskretləşdirə bilərsiniz).

**`prefix.json` hər bir dialoqdakı ilk iki fraqmentin fayl adı indekslərini ehtiva edir.** Bu, dialoqun həqiqi başlanğıcını müəyyənləşdirir və söhbəti irəliyə və ya geriyə oxumaq arasındakı qeyri-müəyyənliyi aradan qaldırır.

Məsələn: `11: [7, 12]` o deməkdir ki, 11-ci dialoqun birinci və ikinci növbələri uyğun olaraq `chunk_7.wav` və `chunk_12.wav`-dir.

### Nə əldə edirsiniz

Siz **eynitipli formatda iki qovluq** alırsınız:

| Qovluq | Dialoqlar | `answers.json`? | Bunlar üçün istifadə edin |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ daxil edilib | modelinizi öyrətmək / fine-tune etmək |
| `dataset/test_public/`  | 100   | ✅ daxil edilib | pipeline-ınızı işlətmək və lokal olaraq özünüzü qiymətləndirmək |

Qiymətləndirmə zamanı `dataset/test_public/` qovluğunuz şəffaf şəkildə `hidden evaluation set` (ictimai liderlər lövhəsi üçün `test_leaderboard_a` və yekun liderlər lövhəsi üçün `test_leaderboard_b`) ilə əvəz olunur — bunlar `dataset/test_public/` ilə eyni ölçüyə və formata malikdir, lakin `answers.json` olmadan.

Dəftərçəniz həmin verilənlər üzərində yenidən icra olunur və onun istehsal etdiyi `answers.json` faylı qiymətləndirmə üçün istifadə olunur. Gizli saxlanılan sınaq dialoqları `train` ilə eyni paylanmadan gəlir, buna görə də lokal `test_public` xalınız dürüst bir önbaxışdır.

### Kataloq strukturu

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

## Çıxış

Hər bir dialoq üçün onun audio fraqmentlərinin ilkin xronoloji sırasını müəyyənləşdirin. Sizin proqnozunuz `{0, 1, …, n−1}`-nin bir `P` permutasiyası olmalıdır, burada `P[i]` `chunk_i.wav`-in proqnozlaşdırılan xronoloji mövqeyidir (0 = birinci).

Sizin çıxış faylınız `answers.json` hər bir dialoq ID-sini onun proqnozlaşdırılan permutasiyasına eşləşdirməlidir:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Nümunə

Dialoqun 3 qarışdırılmış `chunk_0, chunk_1, chunk_2` fraqmenti var:

| qarışdırılmış fraqment | şifahi məzmun | həqiqi mövqe (dərəcə) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (sonuncu) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (birinci) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Həqiqi sıra **chunk_1 → chunk_2 → chunk_0** şəklindədir, beləliklə `P = [2, 0, 1]`, və `prefix.json` `[1, 2]` dəyərini saxlayır.

⚠️ **P həqiqi permutasiya olmalıdır:** uzunluğu n, 0-indeksli, hər dəyər dəqiq bir dəfə olmalıdır. Dublikatlar, əskik dəyərlər və ya diapazondan kənar daxilolmalar (məsələn, 1-indeksli) həmin dialoq üçün 0 xal alır; faylda əskik olan dialoq da 0 xal alır. Yanlış formalaşdırılmış və ya JSON olmayan fayl rədd edilir.

## Qiymətləndirmə

Bu tapşırıq üçün qiymətləndirmə **cütlərlə sıralama dəqiqliyidir** (pairwise ordering accuracy). O, hər bir fraqment cütünü yoxlayır və soruşur: _bu ikisindən hansı birinci gəlməlidir?_ Əgər sizin proqnozunuz həqiqi cavabla (ground truth) eyni cavabı verərsə, cüt doğru hesab olunur. `n` fraqmenti olan dialoq üçün $$M = n(n-1)/2$$ cüt var; fərz edək ki, `I` inversiyaların sayıdır — yəni həqiqi cavabdan fərqli sırada yerləşdirilmiş cütlər:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Yekun xal bölmədəki (split) bütün dialoqlar üzrə hər dialoqa düşən xalların ədədi ortasıdır.**

## İcazə verilən modellər

Həm öyrətmə, həm də qiymətləndirmə zamanı bu tapşırığı həll etmək üçün yalnız aşağıdakı əvvəlcədən öyrədilmiş modellərdən istifadə edə bilərsiniz. Bu modellərin hamısı artıq yüklənib və mühitdə mövcuddur. Onlardan necə istifadə olunacağına dair nümunələri `solution.ipynb` bazis dəftərçəsində (baseline notebook) görə bilərsiniz. Nəzərə alın ki, başqa heç bir modeldən istifadə edə bilməzsiniz və proqramınızın internetə çıxışı yoxdur.

- **Nitq təmsilləri:** **wav2vec 2.0**. **Whisper enkoderi** də xüsusiyyət çıxarıcısı (feature extractor) kimi istifadə oluna bilər.
[wav2vec model kartı](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Avtomatik nitqin tanınması (ASR):** **OpenAI Whisper** (istənilən ölçüdə).
[Whisper model kartı](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Dil modeli:** **Qwen2.5-0.5B**, hansı ki, ya zero-shot rejimində, ya da təqdim olunan `train` bölməsində fine-tune edilərək istifadə oluna bilər.
[Qwen model kartı](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Nəzərə alın ki, 10 dəqiqəlik limit qiymətləndirmə zamanı etdiyiniz hər hansı öyrətmə və ya fine-tuning prosesini, üstəlik qiymətləndirmə dəsti üzərində çıxarışı (inference) əhatə etməlidir.

## Necə təqdim etməli

- `solution.ipynb` faylını açın və bütün xanaları (cells) işlədin. İşçi qovluqda `dataset/test_public/`-dəki hər bir dialoq üçün (100 dialoq) permutasiyası olan `answers.json` faylının yazıldığını təsdiqləyin. Qiymətləndirmə zamanı dəftərçə gizli test dəsti üzərində yenidən işlədilir və onun orada istehsal etdiyi `answers.json` qiymətləndirilir.
- İstəyirsinizsə həlli təkmilləşdirin — və ya etməyin; təkcə bazis (baseline) verilənlər zəncirini (pipeline) doğrulayır.
- JupyterLab-ın sol yan panelində Git sekmesini açın.
- `solution.ipynb` faylını **Stage** edin (yanındakı + ikonu).
- Commit mesajı daxil edin və **Commit** düyməsini sıxın.
- Push etmək üçün yuxarı oxlu bulud ikonuna sıxın.
- Bu Yarış (Contest) səhifəsinə qayıdın və **Submit** düyməsini sıxın.

Dəqiq bir fayl təqdim edin, `solution.ipynb` adında.
