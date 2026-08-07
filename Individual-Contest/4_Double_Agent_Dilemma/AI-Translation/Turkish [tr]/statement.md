# Çifte Ajan İkilemi

- **Süre sınırı:** 12 dakika.
- **Depolama:** 5 GB
- **Ortam:** bir GPU (≈16 GB VRAM), internet yok
- **Çözüm boyutu:** `solution.ipynb` ≤ 1 MB
- **Baseline puanı:** 0 
- **Bilimsel Komite puanı:** 96.99 

Astana'daki ulusal yapay zekâ merkezinde, iki bilgisayar modeli — Model R (bir ResNet-18) ve Model V (bir ViT-Tiny) — fotoğrafları analiz ediyor. Şu anda her iki model de kusursuz çalışıyor; 100% doğruluk elde ediyor ve her bir görüntü üzerinde aynı kararı veriyor. Baş bilim insanı, akıllı "beyinlerinin" gerçekte ne kadar farklı olduğunu sınamak için size bir görev veriyor: her fotoğraftaki piksellerde küçük, neredeyse görünmez değişiklikler yaparak Model R ile Model V'nin tamamen farklı kararlar vermesini sağlayın.

![görsel](../../dilemma.jpg)

## 1. Görev

Önceden eğitilmiş iki görüntü sınıflandırıcı aynı görüntüye bakmaktadır. Bu görevde sağlanan görüntüler üzerinde her iki sınıflandırıcı da 100% doğrulukla çalışmaktadır.

- **Model R**: `torchvision.models.resnet18` (bir CNN, ResNet18).
- **Model V**: `timm`'s `vit_tiny_patch16_224` (bir Transformer, ViT-Tiny).

Göreviniz, iki modelin farklı kararlar vermesi için her görüntüye yönelik küçük bir değişiklik ("pertürbasyon") oluşturmaktır. Her görüntü için **iki farklı** pertürbasyon oluşturmalısınız:

- **Tip A**: eklendikten sonra Model R görüntüyü hâlâ doğru sınıflandırır, ancak Model V yanlış sınıflandırır.
- **Tip B**: eklendikten sonra Model V görüntüyü hâlâ doğru sınıflandırır, ancak Model R yanlış sınıflandırır.

Her pertürbasyon, fark edilmesi zor olacak kadar *küçük* olmalıdır. Daha küçük pertürbasyonlar daha yüksek puan alır (bkz. Bölüm 5). Pertürbasyon, doğrudan piksel düzeyinde özgün görüntüye uygulanır.

## 2. Açık veri

Görevle birlikte, farklı çözünürlüklerde görüntüler içeren iki bölüme — `train` (100 görüntü) ve
`test_public` (100 görüntü) — ayrılmış bir görüntü kümesi sağlanmaktadır. Tüm görüntüler ImageNet-1K'nin 1000 sınıfından alınmıştır ve hem Model R hem de Model V, her iki bölümde de 100% doğruluk elde etmektedir.

Aşağıdaki dosyalar sağlanmaktadır:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Değerlendirme sırasında `dataset/test_public/` klasörünüz, resmî puanlama için görünmez biçimde iki gizli görüntü kümesiyle (`test_leaderboard_a` ve `test_leaderboard_b`) değiştirilir. Bunların her biri PNG biçiminde **100 görüntü** ve bir etiket dosyası içerir. 

**Not: Bu görevde test datasetlerindeki etiketlere erişilebilir.**

## 3. Çıktı biçimi

Her görüntü için iki dosya üretmelisiniz:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), datasetlerdeki görüntü adıyla eşleşir.
- Her dosya, `torch.save` ile kaydedilmiş tek bir tensördür. Şekli`3 x H x W` olmalıdır; burada `H` ve `W`, söz konusu görüntünün **özgün** çözünürlüğüyle (`224 x 224` ile değil) eşleşir.
- Kod yalnızca bir ZIP dosyası, `submission.zip`, üretmelidir. Tüm `.pt` dosyalarını, herhangi bir kapsayıcı klasör veya alt dizin olmadan ZIP arşivinin en üst düzeyine yerleştirin. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Çıktı biçimiyle ilgili herhangi bir sorun varsa notebook sizi uyaracaktır.

## 4. Kısıtlar

- **Modeller:** `torchvision.models.resnet18(pretrained=True)` ve `timm.create_model('vit_tiny_patch16_224', pretrained=True)` kullanmalısınız. Önceden eğitilmiş başka hiçbir modele izin verilmez.
- **Dönüşüm işlem hattı (değerlendirme sırasında zorunlu tutulur):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` ayrıntılar için. 
- **Pertürbasyon çözünürlüğü:** **Özgün** ham görüntü çözünürlüğüyle eşleşmelidir (224×224 ile değil). Tensör, dönüşüm işlem hattından *önce* ham görüntüye eklenir.
- **Çıktı biçimi:** Yalnızca `.pt` dosyaları — PNG/JPG yok. Tensörler ham görüntüye eklenir ve piksel değerleri ön işlemeden önce `[0, 1]` aralığına kırpılır.
- **Dosya adlandırma:** Düz listelenmiş, katı `{index}_a.pt` / `{index}_b.pt` biçimi. Zip içinde alt dizin bulunmamalıdır.
- **Kütüphaneler:** `torch`, `torchvision`, `timm`. 

## 5. Puanlama

Nihai puan aşağıdaki şekilde hesaplanır. `M` bölümdeki görüntü sayısı, $Score_A$ başarılı Tip A pertürbasyonlarının sayısı ve $Score_B$ başarılı Tip B pertürbasyonlarının sayısı olsun:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF, yüksek norma sahip pertürbasyonları cezalandırmak ve performans tavanına yakın değerlerde çok hassas olmak üzere tasarlanmış bir fonksiyondur. 0.5 ile 1 aralığında sınırlıdır. Tam uygulama `solution.ipynb` belgesinin Bölüm  8'inde görülebilir. 

![görsel](../../curves.jpeg)
Şekil: Ceza fonksiyonunun eğrisi.

## 6. Gönderimi Kontrol Etme

Notebook'ta, `solution.ipynb` notebook'unun Bölüm 7'sinde, biçimlendirme sorunları varsa sizi uyaran kontroller bulunmaktadır.

## 7. Yerel test

`solution.ipynb` eksiksiz ve çalışan bir örnek içerir. Açık veriyi, her iki modeli ve resmî puanlayıcıyı yükler ve bir gönderim ZIP dosyası oluşturur. Başlamadan önce bunu okuyun.

## 8. Nasıl gönderilir

- Değişikliklerinizi `solution.ipynb` dosyasına kaydedin.
- JupyterLab'ın sol kenar çubuğundaki Git sekmesini açın.
- `solution.ipynb` dosyasını **Stage** edin (yanındaki + simgesi).
- Bir commit mesajı girin ve **Commit** düğmesine tıklayın.
- Push işlemi için yukarı ok bulunan bulut simgesine tıklayın.
- Bu Yarışma sayfasına dönün ve **Submit** düğmesine tıklayın.

Tam olarak `solution.ipynb` adlı tek bir dosya gönderin.
