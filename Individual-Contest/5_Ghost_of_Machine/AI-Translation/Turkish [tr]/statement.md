# Makinenin Hayaleti

- **Süre sınırı:** 10 dakika
- **Baseline puanı:** 28.6
- **Bilimsel Komite puanı:** 93.41
- **Ortam:** bir GPU (≈16 GB VRAM), internet yok
- **Çözüm boyutu:** `solution.ipynb` ≤ 20 MB
- **Depolama:** 5 GB
- **Önceden eğitilmiş modeller:** yalnızca **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — bir metin **kodlayıcısı** (embedding modeli).


## Görev

Kazakistan Ulusal Arşivi'nde tuhaf şeyler oluyor. Kütüphaneciler bazı kitapların eskiden farklı bittiğini söylüyor, ancak kimse bunu kanıtlayamıyor — her nüsha aynı ve her hikâye hâlâ anlamlı. Değişiklikleri tespit etmeniz için bir yapay zekâ araştırmacısı olarak davet ediliyorsunuz.
![Hayalet](../../ghost.jpg)

Bir metin parçası, insan tarafından yazılmış metin olarak başlar ve bir noktada sessizce
bir dil modeli tarafından üretilmiş devam metnine geçer. Bir bütün olarak okunduğunda,
tutarlı tek bir metin gibi görünür — ancak ortalarda bir yerde yazar bir insandan
bir makineye dönüşür. Göreviniz **bu geçişi, yani insan kısmının bittiği ve makine
kısmının başladığı karakter indisini bulmaktır**.

Her örnek tek bir `text` dizgesidir. Tam olarak bir sınır vardır. Ondan
önceki her şey insan tarafından yazılmıştır; ondan itibaren her şey makine tarafından üretilmiştir.

## Dataset

Her birinde bir sınır bulunan düz metin biçimindeki İngilizce pasajlar.

- **Bölüm A** (sınırdan önce): insan tarafından yazılmış bir metinden alıntı.
- **Bölüm B** (sınırdan itibaren): Bölüm A'ya koşullandırılmış olarak bir dil modeli
  tarafından üretilmiş devam metni.
- Her bölüm en az 180 kelimedir; toplam uzunluk ~500–800 kelimedir.
- **`boundary_char_index`**, Bölüm A'nın bittiği karakter ofsetidir:
  `text[:boundary_char_index]` insan kısmı,
  `text[boundary_char_index:].lstrip()` ise makine kısmıdır.

#### Size verilenler

**İki klasör** alırsınız:

| Klasör | Örnekler | `answers.jsonl`? | Kullanım amacı |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ dâhil | yönteminizi eğitmek / ince ayar yapmak |
| `dataset/test_public/`  | 380   | ✅ dâhil (dev kopyası) | işlem hattınızı çalıştırmak ve yerel olarak kendi puanınızı hesaplamak |

**Değerlendirme sırasında** `dataset/test_public/` klasörünüz **gizli bir
değerlendirme setiyle değiştirilir**. Bu set aynı biçimdedir, ancak **`answers.jsonl` içermez**.
Notebook'unuz bu set üzerinde yeniden çalıştırılır ve ürettiği `answers.jsonl` puanlanır.

- Herkese açık liderlik tablosu, gizli bir **test_leaderboard_a** seti (380 örnek) kullanır.

- Nihai sıralama, gizli bir **test_leaderboard_b** seti (380 örnek) kullanır.

Üç değerlendirme
seti de aynı boyuttadır ve `train` ile aynı dağılımdan alınmıştır; dolayısıyla yerel
`dataset/test_public/` puanınız, liderlik tablosu puanınız için makul bir tahmindir.

#### Disk üzerindeki biçim

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- `answers.jsonl` içindeki kimlikler, `data.jsonl` içindeki kimliklerle eşleşir.
- `dataset/train/` (cevaplarla birlikte), eğitim veya ince ayar yaptığınız her zaman kullanılabilir.

## Çıktı (gönderim biçimi)

**`solution.ipynb` olarak adlandırılması gereken tek bir notebook** gönderirsiniz. Tam olarak bu dosya adı zorunludur. Başka herhangi bir ad, çalıştırılmadan reddedilir.

Notebook'unuz **`dataset/test_public/data.jsonl` dosyasını okumalı** ve repository kök dizinine
**`answers.jsonl`** adlı tek bir dosya yazmalıdır — her satırda, her örnek kimliğini
tahmin ettiğiniz sınır karakter indisine eşleyen bir JSON nesnesi:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index`, **`[0, len(text)]` içinde bir tam sayı** olmalıdır.
- `dataset/test_public/data.jsonl` içindeki her kimlik tam olarak bir kez yer almalıdır. `answers.jsonl`
  içinde bulunmayan (veya tam sayı olmayan / aralık dışında bir değere sahip olan) bir örnek,
  o örnek için 0 puan alır.

## Puanlama

Her örnek için `p` tahmin ettiğiniz indis ve `t` gerçek sınır olsun. Örnek başına puan, karakter uzaklığıyla üstel olarak azalır:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Bu, puanın aşağıdaki gibi davranmasına yol açar:
- **=1.0** — sınır karakteri tam olarak doğru;
- **≈0.78** — 25 karakter sapma; - **≈0.61** — 50 karakter sapma;
- **≈0.37** — 100 karakter sapma;
- **≈0.01** — 500 karakter sapma.

**Nihai puan**, split içindeki tüm örneklerin örnek başına puanlarının ortalamasıdır
(0–100 ölçeğinde raporlanır). Metrik, yalnızca tam isabeti değil, *yaklaşmayı* da ödüllendirir.

## Kısıtlar

- **Ortam:** bir GPU (≈16 GB VRAM), değerlendirme sırasında internet yok — izin verilen
  model (aşağıda) önceden sağlanmıştır. Tüm çalıştırma için **duvar saati bütçesi: 10 dakika** —
  bu süre, değerlendirme sırasında yaptığınız tüm eğitim / ince ayar işlemlerini
  **ve** değerlendirme seti üzerindeki çıkarımı kapsamalıdır.
- **İzin verilen önceden eğitilmiş model** — bu liste kapsamlıdır; önceden eğitilmiş başka hiçbir ağırlık
  kullanılamaz. Model **ortamda önceden sağlanmıştır** (normal biçimde yükleyin; ör.
  `from_pretrained`; değerlendirme sırasında internet yoktur):
  - **bge-base-en-v1.5** — 110M parametreli bir metin **kodlayıcısı** (embedding modeli). Cümle/pasaj
    embedding'leri üretir; üretici bir dil modeli değildir. Modeli **olduğu gibi (dondurulmuş özellikler olarak)
    kullanabilir veya `train` split'i üzerinde ince ayar yapabilirsiniz**
    (tam ince ayar, 16 GB / 10 dakika bütçesine sığar).
- Klasik / istatistiksel araçlar kısıtlanmamıştır: kendiniz hesapladığınız embedding özelliklerinin
  üzerine herhangi bir özellik tabanlı model (ör. scikit-learn sınıflandırıcıları veya regresyon modelleri)
  oluşturabilirsiniz. *Önceden eğitilmiş derin öğrenme ağırlıkları* yalnızca yukarıdaki listeyle kısıtlanmıştır.

## Baseline

Sağlanan `solution.ipynb` basit bir referanstır: `dataset/train/` üzerinden tek bir
“ortalama sınır oranı” tahmin eder ve her test pasajı için uzunluğun aynı oranını
öngörür. Gizli **test_leaderboard_a** split'inde **28.6** puan alır ve yalnızca
`dataset/test_public/` okuma → `answers.jsonl` yazma döngüsü için çalıştırılabilir bir şablon olarak bulunur.

Aynı split ve aynı 10 dakika bütçesiyle ölçülen **93.41 Bilimsel Komite puanı**,
izin verilen kodlayıcıya `train` üzerinde ince ayar yapılmasından ve geçişin
cümleler üzerindeki bir değişim noktası olarak belirlenmesinden elde edilir. Bu bir üst sınır değildir —
bu metrikte alınabilecek en yüksek puan 100'dür.
