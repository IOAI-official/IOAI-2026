# Robot Kovalama

- **Süre sınırı:** 5 dakika
- **Ortam:** bir GPU (≈16 GB VRAM), internet yok
- **Çözüm boyutu:** `solution.ipynb` ≤ 1 MB
- **Depolama:** 5 GB 

## Görev

Altı robot vardır. Her robot, bir ızgarayla temsil edilen küçük bir odada çalışır. Her odanın duvarlarla çevrili `6×6` boyutunda oynanabilir bir alanı vardır; dolayısıyla tam `image` dizisinin boyutu `8×8` olur (oynanabilir alan + duvarlar).

Her robot, bir görevi açıklayan İngilizce bir talimat alır. Anlık görüntü, robot görevi yerine getirirken herhangi bir anda alınmış olabilir. Amacınız robotun bir sonraki eylemini tahmin etmektir.

Robotlar her zaman en kısa yolu izlemez. Robot 0, Robot 1'den farklı davranabilir; ancak her robot kendine özgü tutarlı bir örüntüyü izler. Bu örüntüleri öğrenmek için doğru sonraki eylemleri içeren eğitim örneklerini kullanın.

![Robot](../../robot.jpg)

Üç tür görev vardır:

- bir nesneye **gitmek**, örneğin `"approach the red ball"`;
- bir nesneyi **almak**, örneğin `"grab the blue key"`;
- **bir nesneyi başka bir nesnenin yanına koymak**, örneğin
  `"place the red box beside the green ball"`.

Aynı talimat birkaç farklı şekilde yazılabilir. Test seti, bilinen ifadelerin, renklerin ve nesne türlerinin yeni birleşimlerini içerebilir. Bununla birlikte, test setinde kullanılan her sözcük, ifade örüntüsü, renk, nesne türü ve görev türü eğitim setinde de yer alır.

Her örnek aşağıdaki alanlara sahiptir:

| Alan | Anlamı |
|---|---|
| `robot_id` | bunun 6 robottan hangisi olduğu (`0`–`5`) |
| `image` | oda; kanal 0'ın kategorik object_idx değerini (ör. 1=boş, 2=duvar, 10=robot), kanal 1'in ise kategorik colour_idx değerini (0–5) tuttuğu bir `8×8×2` tamsayı dizisi. |
| `direction` | robotun şu anda baktığı yön |
| `mission` | görünür doğal dil talimatı |
| `carrying` | taşınan nesne için `null` veya `[object_idx, colour_idx]` |

Satırlar rastgele sıradaki bağımsız anlık görüntülerdir. Bölümler oluşturmazlar ve değerlendirme sırasında önceki hiçbir gözlem veya eylem mevcut değildir.

Sağlanan `visualize_dataset.ipynb`, farklı durumlarda modelin erişebildiği gözlemleri incelemenize olanak tanır.

## Izgara kodlaması

`image[row][column] = [object_idx, colour_idx]`. İlk indeks yukarıdan aşağıya satırı, ikinci indeks ise soldan sağa sütunu belirtir. Dizi dış duvar sınırını içerir; dolayısıyla gezilebilir iç alan `6×6` olur.

Nesne kimlikleri:

| id | nesne |
|---:|---|
| 1 | boş hücre |
| 2 | duvar |
| 5 | anahtar |
| 6 | top |
| 7 | kutu |
| 10 | robot |
| 11 | token |

Tokenlar odada görünebilir, ancak görevlerde hiçbir zaman adları belirtilmez.

Renk kimlikleri `0` kırmızı, `1` yeşil, `2` mavi, `3` mor, `4` sarı ve `5` gridir. Boş hücreler ve duvarlar için renk kanalının bir anlamı yoktur.

Görüntü yalnızca yukarıdaki iki kanala sahiptir. Robotun yönü, üst düzey `direction` alanında bir kez sağlanır; `image` içinde tekrarlanmaz.

## Eylemler

`0`–`3` kodları için hareket eylemleri aşağıdaki mutlak eşlemeyi kullanır:

| eylem | anlamı |
|---:|---|
| 0 | yukarı hareket et |
| 1 | aşağı hareket et |
| 2 | sola hareket et |
| 3 | sağa hareket et |
| 4 | al |
| 5 | bırak |


`direction` alanı, mevcut bakış yönünü şu şekilde belirtir: 0 = Yukarı (satır - 1), 1 = Aşağı (satır + 1), 2 = Sol (sütun - 1), 3 = Sağ (sütun + 1).

Bir hareket eylemi önce robotu ilgili mutlak yöne döndürür, ardından onu bir hücre hareket ettirmeyi dener. Bir duvar veya nesne hareketi engelleyebilir, ancak yön yine de değişir. `pick up` ve `drop` yalnızca yön tarafından tanımlanan bitişik hedef hücre üzerinde işlem yapar (ör. direction=0 ise (row - 1, col) üzerinde işlem yapar).

## Dataset

İki klasör alırsınız:

| Klasör | Satır | `labels.json`? | Kullanım amacı |
|---|---:|---|---|
| `dataset/train/` | 60,000 | dâhil | modelinizi eğitmek |
| `dataset/test_public/` | 3,600 | geliştirme kopyasında dâhil | pipeline'ınızı çalıştırmak ve kendi puanınızı hesaplamak |

Her klasör, yukarıda açıklanan örneklerin bir JSON listesi olan `observations.json` dosyasını içerir. `labels.json`, bunlara karşılık gelecek şekilde hizalanmış bir eylemler JSON listesidir (`0`–`5`).

Eğitim seti, robot başına tam olarak 10,000 satır ve her görev
ailesinden 20,000 satır içerir. Açık test, robot başına 600 satır içerir. Bir diziye ihtiyacınız varsa `image` öğesini
`numpy.asarray(...)` ile sarmalayın.

Notlandırma sırasında `dataset/test_public/`, aynı biçimdeki ancak
`labels.json` içermeyen 3,600 gözlemden oluşan gizli bir setle şeffaf biçimde değiştirilir. Açık
liderlik tablosu `test_leaderboard_a` kullanır; nihai sıralama ise
`test_leaderboard_b` kullanır. Test etiketlerini koşulsuz olarak okuyan bir notebook başarısız olur.
Etiketleri yalnızca `dataset/train/` üzerinden okuyun.

## Çıktı

Notebook'un çalışma dizinine `predictions.json` yazın. Bu, `dataset/test_public/observations.json` içindeki
her satır için aynı sırada bir tamsayı eylem (`0`–`5`) içeren bir JSON
listesi olmalıdır. Altı örnek içeren varsayımsal bir test seti için geçerli bir çıktı şöyle olurdu:

```json
[0, 3, 2, 2, 5, 4]
```

Eksik veya geçersiz bir JSON dosyası, yanlış sayıda tahmin, tamsayı olmayan bir değer
veya `{0,1,2,3,4,5}` dışında bir eylem, puan verilmeden reddedilir.

## Puanlama

Puanlama, `0`–`100` ölçeğinde **robot başına ortalama doğruluk** değeridir. Doğruluk önce
her robot için bağımsız olarak hesaplanır, ardından altı robotun tamamı üzerinden ortalaması alınır. Bu nedenle her
robot eşit ağırlığa sahiptir.

## Nasıl gönderilir

1. `solution.ipynb` dosyasını açın ve tüm hücreleri çalıştırın.
2. Açık test seti için 3,600 tahmin içeren `predictions.json` dosyasını yazdığını
   doğrulayın.
3. İsterseniz modeli iyileştirin; sağlanan baseline yalnızca gerekli
   girdi ve çıktı biçimini gösterir.
4. JupyterLab Git sekmesinde `solution.ipynb` dosyasını stage edip commit edin, ardından push edin.
5. Yarışma sayfasına dönün ve **Gönder** düğmesine tıklayın.

Tam olarak `solution.ipynb` adlı tek bir dosya gönderin.
