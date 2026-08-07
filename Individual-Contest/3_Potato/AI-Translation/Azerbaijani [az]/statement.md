# Kartof

- **Vaxt limiti:** 10 dəqiqə
- **Mühit:** bir GPU (≈16 GB VRAM), internet yoxdur
- **Həllin ölçüsü:** `solution.ipynb` ≤ 1 MB
- **Yaddaş:** 5 GB 

## Tapşırıq
 
Dostunuz təxmin oyunu oynamağı təklif edir.
O, hakim kimi, sabit lüğətdən bir gizli söz seçir və siz onu ən çox 30 gedişdə tapmalısınız.
Hər gedişdə hakim iki sözü müqayisə edir və hansının gizli sözə semantik olaraq daha yaxın olduğunu bildirir.
Hər oyun sabit `lamp vs potato` cütündən başlayır, çünki bunlar dostunuzun ən sevdiyi şeylərdən ikisidir.
Daha sonra proqramınız bir yeni söz təklif edir. Müqayisənin qalibi saxlanılır və növbəti təklifinizlə müqayisə olunur. 
Gizli sözü dəqiq təklif etdiyiniz anda oyunu qazanırsınız. Müqayisə registrdən asılı deyildir (case-insensitive). Təklif etdiyiniz hər bir söz `dataset/vocabulary.json` daxilində olmalıdır.

`solution.ipynb` faylında protokol və məlumatların yüklənməsi ilə birlikdə tam bir nümunə verilmişdir. 
Siz PublicEmbeddingPlayer sinfini dəyişə bilərsiniz. Proqramınız bir dəfə inisializasiya olunur və hər oyunu tək bir icra zamanı oynayır;
protokol hər oyunun əvvəlində yeni bir PublicEmbeddingPlayer yaradır.

## Hakim

Proqramınız Hakimə bir JSON obyekti göndərir və Hakim bir JSON obyekti ilə cavab verir. 

Yalnız protokolu izah etmək üçün gizli sözün göstərildiyi işlənilmiş bir nümunə:

```text
Hidden word: shovel          Fixed opening: lamp vs potato

<- {"turn": 1, "winner_word": "potato", "verdict": "second", "word1": "lamp",   "word2": "potato"}
-> {"new_word": "rock"}
<- {"turn": 2, "winner_word": "rock",   "verdict": "second", "word1": "potato", "word2": "rock"}
-> {"new_word": "hammer"}
<- {"turn": 3, "winner_word": "hammer", "verdict": "second", "word1": "rock",   "word2": "hammer"}
-> {"new_word": "shovel"}                                    <- matches: game won
-> {"status": "win"}
```

Gedişlər 1-dən 30-a qədər indekslənir.

`verdict` seçimləri: `first` söz1-in daha yaxın olduğu, `second` söz2-nin daha yaxın olduğu və ya
`same` hər iki sözün gizli sözə bərabər dərəcədə yaxın olduğu mənasını verir. 

`winner_word` növbəti müqayisə üçün saxlanılan sözdür. `same` qərarında birinci söz qalır.

## Məlumat dəsti (Dataset)

Bütün bölgülər (splits) tərəfindən paylaşılan:

- `dataset/vocabulary.json` — 1602 unikal kiçik hərflə yazılmış söz. Gizli söz həmişə
  bunlardan biridir.
- `dataset/public_embeddings.npy` — `float32`, forması (shape) `(1602, 2560)`. `i` sətiri
  lüğətdəki `i` sözünə uyğun gəlir. Bunlar *ictimai* (public) embaddinqlərdir;
  hakim fərqli, məxfi (private) təsvirdən istifadə edir.

Bölgülər gizli sözlər dəstləridir:

| Bölgü | Sözlər | Cavablar | İstifadə məqsədi |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | həllinizi icra etmək və özünüzü qiymətləndirmək üçün |
| `test_leaderboard_a` | 120 | gizli | canlı liderlər lövhəsi |
| `test_leaderboard_b` | 120 | gizli | yekun sıralama |

Heç bir `train` bölgüsü yoxdur — etiketlənmiş sətirlərdən heç nə uyğunlaşdırılmır (fit edilmir).

### Təqdim olunan modellər

Tapşırıqla birlikdə öncədən təlimatlandırılmış (pretrained) iki embaddinq modeli təqdim olunur və istifadə edilə bilər:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Hər ikisi öz lokal yolundan yüklənməlidir;
`"BAAI/bge-m3"` kimi bir Hugging Face hub ID-si yükləməni işə salır və qiymətləndirmə oflayn olduğu üçün xəta verir. Hər bir
qovluqda oflayn çağırışı göstərən icra oluna bilən `example.py` var.

Əlçatan kitabxanalar: `numpy`, `torch`, `sentence-transformers`. İnternet yoxdur, yükləmələr
yoxdur, başqa paketlər yoxdur.

## Çıxış

Yoxdur. Bu interaktiv tapşırıqdır: həlliniz heç bir cavab faylı yazmır;
yuxarıda təsvir edildiyi kimi stdin/stdout vasitəsilə hakim ilə əlaqə saxlayır.

## Metrika

`t` gedişində tapılan oyun `1.0 - 0.02 × max(0, t - 10)` xal qazandırır; 30 gediş
ərzində həll olunmayan oyun `0` xal verir. Beləliklə, 1–10-cu gedişlər `1.00` xal, 20-ci gediş `0.80` xal, 30-cu
gediş `0.60` xal verir.

Sizin tapşırıq xalınız `0.00` və `100.00` arasında olan, orta oyun xalı × 100 şəklindədir.

10 dəqiqəlik limit işə düşmə, hazırlıq və test dəstindəki bütün 120
oyunu əhatə edən vahid büdcədir. 

## Təqdim etmə qaydası

1. `solution.ipynb` faylını açın, `PublicEmbeddingPlayer` faylını redaktə edin və işlədiyindən əmin olmaq üçün bütün xanaları (cells) icra edin.
2. İstəyə bağlı olaraq, onu lokal şəkildə yoxlayın: `python local_test.py solution.ipynb --limit 5`.
   Lokal hakim *ictimai* (public) embaddinqlərdən istifadə edir, buna görə də onun xalı yalnız orientir xarakteri daşıyır.
3. `solution.ipynb` faylını saxlayın.
4. JupyterLab-ın sol panelində Git nişanını (tab) açın.
5. `solution.ipynb` faylını stage edin (yanındakı **+** işarəsi).
6. Commit mesajı daxil edin və Commit düyməsini sıxın.
7. Göndərmək (push etmək) üçün yuxarı oxlu bulud işarəsinə sıxın.
8. Bu Yarış (Contest) səhifəsinə qayıdın və təqdim etdiyiniz mesajla eyni olan commit mesajı ilə Submit düyməsini sıxın.

İstənilən zəruri hazırlıqları və çıxarışı (inference) əhatə edən, `solution.ipynb` adlı dəqiq bir fayl təqdim edin.
