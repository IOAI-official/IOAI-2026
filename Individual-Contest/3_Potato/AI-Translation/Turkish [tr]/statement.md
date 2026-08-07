# Patates

- **Süre sınırı:** 10 dakika
- **Ortam:** bir GPU (≈16 GB VRAM), internet yok
- **Çözüm boyutu:** `solution.ipynb` ≤ 1 MB
- **Depolama:** 5 GB 

## Görev
 
Arkadaşınız bir tahmin oyunu oynamayı öneriyor.
Hakem olarak sabit bir söz dağarcığından gizli bir kelime seçiyor ve sizin bu kelimeyi en fazla 30 turda bulmanız gerekiyor.
Her turda hakem iki kelimeyi karşılaştırır ve hangisinin anlamsal olarak gizli kelimeye daha yakın olduğunu bildirir. Her oyun, arkadaşınızın en sevdiği şeylerden ikisi oldukları için sabit `lamp vs potato` çiftiyle başlar. Ardından programınız yeni bir kelime önerir. Karşılaştırmanın kazananı tutulur ve bir sonraki önerinizle karşılaştırılır. 
Gizli kelimeyi tam olarak önerdiğiniz anda oyunu kazanırsınız. Eşleştirme büyük/küçük harfe duyarsızdır. Önerdiğiniz her kelime `dataset/vocabulary.json` içinde bulunmalıdır.

Protokolü ve veri yüklemeyi içeren eksiksiz bir örnek `solution.ipynb` içinde bulunmaktadır. 
PublicEmbeddingPlayer sınıfını değiştirebilirsiniz. Programınız bir kez başlatılır ve her oyunu tek bir çalıştırmada oynar;
protokol her oyunun başında yeni bir PublicEmbeddingPlayer oluşturur.

## Hakem

Programınız Hakeme bir JSON nesnesi gönderir ve Hakem bir JSON nesnesiyle yanıt verir. 

Yalnızca protokolü açıklamak amacıyla gizli kelimenin gösterildiği tamamlanmış bir örnek:

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

Turlar 1 ile 30 arasında numaralandırılır.

`verdict` seçenekleri; word1 kelimesinin daha yakın olduğu anlamına gelen `first`, word2 kelimesinin daha yakın olduğu anlamına gelen `second` veya
iki kelimenin de gizli kelimeye eşit derecede yakın olduğu anlamına gelen `same` seçenekleridir. 

`winner_word`, bir sonraki karşılaştırma için tutulan kelimedir. `same` kararı verildiğinde ilk kelime kalır.

## Veri Kümesi

Her bölüm tarafından paylaşılır:

- `dataset/vocabulary.json` — 1602 benzersiz küçük harfli kelime. Gizli kelime her zaman
  bunlardan biridir.
- `dataset/public_embeddings.npy` — `float32`, şekli `(1602, 2560)`. `i` satırı,
  söz dağarcığındaki `i` kelimesine karşılık gelir. Bunlar *herkese açık* gömme vektörleridir (embeddings);
  hakem farklı, özel bir temsil kullanır.

Bölümler, gizli kelime kümeleridir:

| Bölüm | Kelimeler | Yanıtlar | Kullanım amacı |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | çözümünüzü çalıştırmak ve kendi puanınızı hesaplamak |
| `test_leaderboard_a` | 120 | gizli | canlı skor tablosu |
| `test_leaderboard_b` | 120 | gizli | nihai sıralama |

`train` bölümü yoktur — etiketli satırlardan hiçbir şey fit edilmez.

### Sağlanan modeller

Görevle birlikte iki önceden eğitilmiş gömme modeli sunulur ve bunlar kullanılabilir:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Her ikisi de yerel yollarından yüklenmelidir; `"BAAI/bge-m3"` gibi bir Hugging Face hub kimliği
indirme işlemini tetikler ve değerlendirme çevrimdışı olduğu için başarısız olur. Her
dizinde çevrimdışı çağrıyı gösteren, çalıştırılabilir bir `example.py` bulunur.

Kullanılabilir kütüphaneler: `numpy`, `torch`, `sentence-transformers`. İnternet yok, indirme yok,
başka paket yok.

## Çıktı

Yok. Bu etkileşimli bir görevdir: çözümünüz bir yanıt dosyası yazmaz; yukarıda açıklandığı şekilde
stdin/stdout üzerinden hakemle iletişim kurar.

## Metrik

`t` turunda bulunan bir oyun `1.0 - 0.02 × max(0, t - 10)` puan alır; 30 tur içinde çözülemeyen bir oyun
`0` puan alır. Dolayısıyla 1–10 turları `1.00`, 20. tur `0.80`,
30. tur ise `0.60` puan alır.

Görev puanınız, ortalama oyun puanı × 100 olup `0.00` ile `100.00` arasındadır.

10 dakikalık sınır; başlatma, hazırlık ve test kümesindeki tüm 120
oyunu kapsayan tek bir bütçedir. 

## Nasıl gönderilir

1. `solution.ipynb` dosyasını açın, `PublicEmbeddingPlayer` dosyasını düzenleyin ve çalıştığından emin olmak için tüm hücreleri çalıştırın.
2. İsteğe bağlı olarak yerel ortamda kontrol edin: `python local_test.py solution.ipynb --limit 5`.
   Yerel hakem *herkese açık* gömme vektörlerini kullandığından puanı
   yalnızca yol göstericidir.
3. `solution.ipynb` dosyasını kaydedin.
4. JupyterLab'in sol kenar çubuğundaki Git sekmesini açın.
5. `solution.ipynb` dosyasını hazırlama alanına ekleyin (yanındaki **+** simgesi).
6. Bir commit mesajı girin ve Commit düğmesine tıklayın.
7. Göndermek için üzerinde yukarı ok bulunan bulut simgesine tıklayın.
8. Bu Yarışma sayfasına dönün ve sağladığınız commit mesajıyla eşleşen mesajı kullanarak Submit düğmesine tıklayın.

Gerekli tüm hazırlıkları ve çıkarımı içeren, adı tam olarak `solution.ipynb` olan tek bir dosya gönderin.
