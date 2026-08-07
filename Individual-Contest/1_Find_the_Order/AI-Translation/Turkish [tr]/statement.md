# Sırayı Bulun

- **Süre sınırı:** 10 dakika
- **Ortam:** bir GPU (≈16 GB VRAM), internet yok
- **Çözüm boyutu:** `solution.ipynb` ≤ 1 MB
- **Depolama:** 5 GB 

## Problem

Size, *Konuşmacı A* ve *Konuşmacı B* adlı iki katılımcı arasındaki sözlü İngilizce diyaloglar verilmektedir. Her diyalog, konuşmacı sıralarına bölünmüştür ve her sıra yalnızca bir konuşmacının konuşmasını içerir. Her sıra ayrı bir `.wav` ses dosyası olarak saklanır; dolayısıyla eksiksiz bir diyalog, her sıra için bir tane olmak üzere bir `.wav` dosyaları kümesiyle temsil edilir. 

Ne yazık ki sıralar rastgele karıştırılmıştır, bu nedenle konuşma artık anlamlı değildir. `chunk_{k}.wav` dosya adında `k`, özgün diyalogdaki k'ıncı sırayı değil, karıştırılmış kümedeki k'ıncı parçayı ifade eder.

**‼️ Göreviniz, konuşmanın özgün kronolojik sırasını yeniden oluşturmaktır.**

![Sırayı bulun](../../find_the_order.jpg)

---

## Dataset

Her diyalog; `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav` olarak adlandırılan `n` ses dosyası içerir. Parçaların her biri ayrı bir konuşmacı sırasıdır. Dosya adları yalnızca karıştırılmış sıraya karşılık gelir. Bir parçanın özgün konuşmada nereye ait olduğunu göstermezler. Her diyalogda 7–20 parça bulunur; bunlar mono, 44.1 kHz'dir (yeniden
örnekleyebilirsiniz).

**`prefix.json`, her diyalogdaki ilk iki parçanın dosya adı indekslerini içerir.** Bu, diyaloğun gerçek başlangıcını belirler ve konuşmayı ileriye veya geriye doğru okuma arasındaki belirsizliği ortadan kaldırır.

Örneğin: `11: [7, 12]`, 11 numaralı diyaloğun birinci ve ikinci sıralarının sırasıyla `chunk_7.wav` ve `chunk_12.wav` olduğu anlamına gelir.

### Size verilenler

**Aynı formatta iki klasör** alırsınız:

| Klasör | Diyaloglar | `answers.json`? | Kullanım amacı |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ dâhil | modelinizi eğitmek / modelinize ince ayar yapmak |
| `dataset/test_public/`  | 100   | ✅ dâhil | pipeline'ınızı çalıştırmak ve puanınızı yerel olarak hesaplamak |

Değerlendirme sırasında `dataset/test_public/` klasörünüz şeffaf bir şekilde
bir `hidden evaluation set` ile değiştirilir (herkese açık liderlik tablosu için `test_leaderboard_a` ve final liderlik tablosu için `test_leaderboard_b`) — bunlar `dataset/test_public/` ile aynı boyut ve formata sahiptir, ancak `answers.json` içermez.

Notebook'unuz bu veri üzerinde yeniden yürütülür ve ürettiği `answers.json` dosyası puanlama için kullanılır. Ayrılmış test diyalogları `train` ile aynı dağılımdan gelir, dolayısıyla yerel `test_public` puanınız gerçeğe uygun bir ön gösterimdir.

### Dizin yapısı

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

## Çıktı

Her diyalog için ses parçalarının özgün kronolojik sırasını belirleyin. Tahmininiz, `{0, 1, …, n−1}` öğelerinin bir `P` permütasyonu olmalıdır; burada `P[i]`, `chunk_i.wav` öğesinin tahmin edilen kronolojik konumudur (0 = ilk).

`answers.json` çıktı dosyanız, her diyalog kimliğini tahmin edilen permütasyonuyla eşlemelidir:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Örnek

Bir diyalogda karıştırılmış 3 parça `chunk_0, chunk_1, chunk_2` vardır:

| karıştırılmış parça | konuşulan içerik | gerçek konum (sıra) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (son) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (ilk) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Gerçek sıra **chunk_1 → chunk_2 → chunk_0** şeklindedir; dolayısıyla `P = [2, 0, 1]` olur ve `prefix.json`, `[1, 2]` değerini içerir.

⚠️ **P gerçek bir permütasyon olmalıdır:** uzunluğu n olmalı, 0'dan indekslenmeli ve her değer tam olarak bir kez bulunmalıdır. Yinelenen, eksik veya aralık dışı değerler (ör. 1'den indeksleme), dosyada bulunmayan bir diyalogda olduğu gibi, söz konusu diyalog için 0 puan alır. Hatalı biçimlendirilmiş veya JSON olmayan bir dosya reddedilir.

## Puanlama

Bu görev için puanlama, **ikili sıralama doğruluğudur**. Her parça çiftini kontrol eder ve şu soruyu sorar: _ikisinden hangisi önce gelmelidir?_ Tahmininiz, temel gerçekle aynı yanıtı veriyorsa çift doğrudur. `n` parçalı bir diyalog için $$M = n(n-1)/2$$ çift vardır; `I`, temel gerçekten farklı sıralanan çiftlerin, yani tersliklerin sayısı olsun:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Final puanı, bölmedeki tüm
diyalogların diyalog başına puanlarının ortalamasıdır.**

## İzin verilen modeller

Bu görevi çözmek için hem eğitim hem de değerlendirme sırasında yalnızca aşağıdaki önceden eğitilmiş modelleri kullanabilirsiniz. Bu modellerin tümü önceden indirilmiştir ve ortamda mevcuttur. Bunların nasıl kullanılacağına ilişkin örnekleri `solution.ipynb` baseline notebook'unda görebilirsiniz. Başka hiçbir modeli kullanamayacağınızı ve programınızın internet erişimi olmadığını lütfen unutmayın.

- **Konuşma temsilleri:** **wav2vec 2.0**. **Whisper encoder** da özellik çıkarıcı olarak kullanılabilir.
[wav2vec model kartı](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Otomatik konuşma tanıma (ASR):** **OpenAI Whisper** (herhangi bir boyut).
[Whisper model kartı](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Dil modeli:** **Qwen2.5-0.5B**; bu model, zero-shot olarak veya sağlanan `train` bölmesi üzerinde ince ayar yapılarak kullanılabilir.
[Qwen model kartı](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
10 dakikalık sınırın, değerlendirme sırasında yaptığınız her türlü eğitim veya ince ayarın yanı sıra değerlendirme kümesi üzerindeki çıkarımı da kapsaması gerektiğini unutmayın.

## Nasıl gönderilir

- `solution.ipynb` dosyasını açın ve tüm hücreleri çalıştırın. Çalışma dizinine, `dataset/test_public/` içindeki her diyalog (100 diyalog) için bir permütasyon içeren `answers.json` dosyasını yazdığını doğrulayın. Değerlendirme sırasında notebook gizli test kümesi üzerinde yeniden çalıştırılır ve orada ürettiği `answers.json` puanlanır.
- İsterseniz çözümü iyileştirin — ya da iyileştirmeyin; baseline tek başına pipeline'ı doğrular.
- JupyterLab'in sol kenar çubuğundaki Git sekmesini açın.
- `solution.ipynb` dosyasını **Stage** edin (yanındaki + simgesi).
- Bir commit mesajı girin ve **Commit** düğmesine tıklayın.
- Push etmek için yukarı oklu bulut simgesine tıklayın.
- Bu Yarışma sayfasına dönün ve **Submit** düğmesine tıklayın.

Tam olarak `solution.ipynb` adlı tek bir dosya gönderin.
