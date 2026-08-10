# IOAI Alanı

- **Süre sınırı:** 5 dakika
- **Depolama:** 5 GB
- **Çözüm boyutu:** `solution.ipynb`, `custom_model.py` birlikte ≤ 1 MB
- **Önceden eğitilmiş modeller:** yok — sıfırdan eğitin, değerlendirme sırasında internet yok
- **Baseline Skoru**: 31.2187
- **Bilimsel Komite skoru:** 63.53


## Görev

Astana Belediye Başkanı, şehri stilize edilmiş IOAI logolarıyla süslemek istiyor. Bir istatistikçi olarak, logo da dâhil olmak üzere her şeyi bir uzamsal fonksiyon $F(x, y, \overline{W})$ olarak görmektedir; burada $x, y \in [0, 1]$, 2D düzlem üzerindeki koordinatları temsil eder ve $\overline{W}$, harf renkleri ve açıları gibi stilistik özellikleri tanımlayan gizli parametreler kümesidir.

$F$ açık bir matematiksel denklem olarak ifade edilemeyecek kadar karmaşık olduğundan, göreviniz ona yaklaşım sağlayacak bir sinir ağı eğitmektir. Ağ, herhangi bir $(x, y)$ koordinat çifti için bir **IOAI alanı** değeri üreterek logonun düzlem genelindeki eksiksiz bir ısı haritası görselleştirmesini oluşturacaktır. Aşağıda, belirli gizli parametreler $\overline{W}$ ile $F$ için bir ısı haritası görselleştirmesi örneği verilmiştir.

![f1](../../ioai1.png)

IOAI alanı nelerden oluşur? Dört harften ve arka plandan.

- İlk `I` harfinin içindeki değerler, doğrusal bir gradyanla birlikte çok büyüktür (1e+10 ve üzeri)
- `O` harfindeki değerler sarmal bir desen gösterir
- `A` harfinin içindeki değer her zaman -1'dir
- Son `I` harfinin içindeki değerler, aynı noktada iki kez değerlendirilse bile $[-2026,2026]$ aralığından rastgele değerler olmalıdır
- Harflerin dışında değer her zaman sıfırdır

Fonksiyon, harflerin ölçeğini ve eğimini, ayrıca ilk `I` harfinin içindeki değer aralığını etkileyen gizli parametrelere $\overline{W}$ sahiptir. Ancak harfler kesişmeyecektir. Aşağıda IOAI alanının farklı $\overline{W}$ değerleriyle nasıl göründüğüne ilişkin birkaç açıklayıcı örnek verilmiştir:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Size verilenler:**

Bu problem hiçbir dataset İÇERMEZ. Bunun yerine, `data/train_config/field_config.json` konumundaki JSON yapılandırma dosyası tarafından yapılandırılan üreteç fonksiyonu size verilir. 

Test yapılandırması gizlidir, ancak benzer niteliktedir. Göreviniz, istediğiniz kadar veri kullanarak verilen üreteç üzerinde uyum sağlamaktır. "Eğitim" ve "test" dağılımlarınız aynı üreteçten oluşturulur; yalnızca hangi $(x_i, y_i)$ noktalarında değerlendirileceğinizi bilmiyorsunuz.

Gönderiminiz şunlardan oluşmalıdır:
- `custom_model.py` olarak kaydedilmiş eğitim modeli sınıfı. Bu model, `torch.nn.Module` sınıfından kalıtım almalı ve yalnızca `torch` importlarını kullanmalıdır. `solution.ipynb` notebook'unda kullanılan `CustomModel` sınıfını içermelidir. 
- `model.pt` ağırlıklarını üretecek `solution.ipynb` notebook'u


## Puanlama

Her bölge için asgari skor 0, azami skor 1'dir. Nihai skor, beş bölgenin tamamı (her harf için dört bölge ve arka plan) üzerinden ortalanır ve 100 ile çarpılır. Bir **parametre cezası** vardır:

**Modeliniz 20260'tan fazla parametreye sahipse skor yarıya indirilir.**

Parametre sayısı `sum(p.numel() for p in model.parameters())` ile ölçülür. Modelinizin, PyTorch `nn.Dropout` modelin bir parçası olacak şekilde stokastik modda da çalışmasını bekliyoruz.

### Standart Bölgeler İçin

Her bir $R$ bölgesi (ilk `I` harfi, `O`, `A`, `Background`) için modeli, gerçek değerleri $v_i$ ve tahminleri $\hat{v}_i$ olan $N_R = 512$ test noktası $(x_i, y_i)$ üzerinde değerlendiririz. Ana metrik olarak normalize edilmiş Ortalama Mutlak Hata (MAE) kullanırız. MAE şu şekilde tanımlanır:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

Normalizasyon ise şu şekilde gerçekleştirilir:

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

burada $s_R > 0$ bir ölçek sabitidir.


### Son `I` harfinin bölgesi için

Bu bölgede, **değerlendirme sırasında dropout etkinleştirilir**. Her bir test noktası $j$ için:

1. $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$ elde etmek amacıyla modeli $K = 10$ kez çalıştırırız.
2. Herhangi bir çıktı $[-2026, 2026]$ aralığının dışındaysa $\mathrm{pointScore}(j) = 0$.
3. Aksi takdirde, $K$ çıktılarının standart sapması $\sigma_j$ hesaplanır ve bir skora dönüştürülür:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

burada $s_E > 0$ sabit bir ölçek sabitidir.

Bölge skoru, bölgedeki tüm noktalar üzerinden alınan ortalamadır:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

burada $N_E = K * N_R$. 

Basitçe ifade etmek gerekirse, ne kadar fazla çeşitliliğiniz olursa bu bölge için skorunuz o kadar yüksek olur. **PyTorch `rand*` ve `_uniform` fonksiyonları da dâhil olmak üzere rastgeleliği saf biçimde kullanamazsınız; rastgelelik, dropout etkinleştirilmiş çıkarımdan gelmelidir.**

## Nasıl gönderilir

1. `solution.ipynb` dosyasını açın ve tüm hücreleri çalıştırın.
2. `custom_model.py` içindeki `CustomModel` modelini iyileştirin
3. Son hücrenizin modelinizi `model.pt` dosyasına kaydettiğinden emin olun.
4. JupyterLab Git sekmesinde `solution.ipynb` ve `custom_model.py` dosyalarını stage'e alın, yorum yazın ve commit edin, ardından push edin.
5. Yarışma sayfasına dönün ve **Gönder** düğmesine tıklayın. Gönderim yorumu, önceki adımdaki yorumla aynı olmalıdır.
