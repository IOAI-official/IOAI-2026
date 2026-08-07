# Ghost of the Machine

- **Had masa:** 10 minit
- **Skor baseline:** 28.6
- **Skor Jawatankuasa Saintifik:** 93.41
- **Persekitaran:** satu GPU (≈16 GB VRAM), tiada internet
- **Saiz penyelesaian:** `solution.ipynb` ≤ 20 MB
- **Storan:** 5 GB
- **Model pralatih:** hanya **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — sebuah **encoder** teks (model embedding).


## Tugasan

Perkara-perkara pelik sedang berlaku di Arkib Negara Kazakhstan. Pustakawan berkata bahawa sebahagian buku dahulunya berakhir dengan cara yang berbeza, tetapi tiada siapa dapat membuktikannya — setiap salinan adalah sama, dan setiap cerita masih masuk akal. Anda dijemput sebagai penyelidik AI untuk mengesan perubahan tersebut.
![Hantu](../../ghost.jpg)

Sebuah petikan bermula sebagai teks tulisan manusia dan, pada satu ketika, secara senyap bertukar
kepada sambungan yang dihasilkan oleh sebuah model bahasa. Apabila dibaca secara keseluruhan, ia kelihatan seperti
satu karya yang koheren — tetapi di suatu tempat di tengahnya penulisnya berubah daripada seorang manusia
kepada sebuah mesin. Tugasan anda ialah **mencari peralihan itu: indeks aksara di mana
bahagian manusia berakhir dan bahagian mesin bermula**.

Setiap sampel ialah satu rentetan tunggal `text`. Terdapat tepat satu sempadan. Segala-galanya
sebelum ia adalah manusia; segala-galanya daripada ia dan seterusnya dihasilkan oleh mesin.

## Set data

Petikan bahasa Inggeris dalam teks biasa, satu sempadan bagi setiap satu.

- **Bahagian A** (sebelum sempadan): satu cebisan teks tulisan manusia.
- **Bahagian B** (daripada sempadan dan seterusnya): satu sambungan yang dihasilkan oleh sebuah model bahasa,
  dikondisikan pada Bahagian A.
- Setiap belah adalah sekurang-kurangnya 180 perkataan; panjang keseluruhan ialah ~500–800 perkataan.
- **`boundary_char_index`** ialah ofset aksara di mana Bahagian A berakhir:
  `text[:boundary_char_index]` ialah bahagian manusia dan
  `text[boundary_char_index:].lstrip()` ialah bahagian mesin.

#### Apa yang anda terima

Anda menerima **dua folder**:

| Folder | Sampel | `answers.jsonl`? | Gunakan untuk |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ disertakan | melatih / fine-tune kaedah anda |
| `dataset/test_public/`  | 380   | ✅ disertakan (salinan dev) | menjalankan pipeline anda dan menilai skor sendiri secara setempat |

Pada **masa penilaian**, folder `dataset/test_public/` anda akan **digantikan dengan satu set
penilaian tersembunyi**. Ia mempunyai format yang sama tetapi **tanpa `answers.jsonl`**. Notebook
anda dijalankan semula padanya, dan `answers.jsonl` yang dihasilkannya akan diberi skor.

- Papan pendahulu awam menggunakan satu set tersembunyi **test_leaderboard_a** (380 sampel).

- Kedudukan akhir menggunakan satu set tersembunyi **test_leaderboard_b** (380 sampel).

Ketiga-tiga set penilaian
mempunyai saiz yang sama dan diambil daripada taburan yang sama seperti `train`, jadi skor
`dataset/test_public/` setempat anda merupakan penganggaran yang wajar bagi skor papan pendahulu anda.

#### Format pada cakera

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- Id dalam `answers.jsonl` sepadan dengan id dalam `data.jsonl`.
- `dataset/train/` (dengan jawapan) tersedia bila-bila masa anda melatih atau melakukan fine-tune.

## Output (format penyerahan)

Anda menyerahkan **satu notebook tunggal, yang mesti dinamakan `solution.ipynb`**. Nama fail yang tepat ini adalah wajib. Apa-apa selain daripadanya akan ditolak tanpa dijalankan.

Notebook anda mesti **membaca `dataset/test_public/data.jsonl`** dan menulis satu fail tunggal
**`answers.jsonl`** pada akar repositori — satu objek JSON setiap baris, memetakan
setiap id sampel kepada indeks aksara sempadan yang anda ramalkan:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` mesti merupakan satu **integer dalam `[0, len(text)]`**.
- Setiap id dalam `dataset/test_public/data.jsonl` patut muncul tepat sekali. Satu sampel yang tiada
  dalam `answers.jsonl` (atau dengan nilai bukan integer / di luar julat) mendapat skor 0
  bagi sampel tersebut.

## Pemberian skor

Bagi setiap sampel, biarlah `p` ialah indeks yang anda ramalkan dan `t` ialah sempadan yang benar. Skor bagi setiap sampel mereput secara eksponen dengan jarak aksara:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Ini membawa kepada kelakuan skor yang berikut:
- **=1.0** — aksara sempadan yang tepat;
- **≈0.78** — tersasar 25 aksara; - **≈0.61** — tersasar 50 aksara;
- **≈0.37** — tersasar 100 aksara;
- **≈0.01** — tersasar 500 aksara.

**Skor akhir ialah min** bagi skor setiap sampel merentas semua sampel dalam split tersebut
(dilaporkan pada skala 0–100). Metrik ini memberi ganjaran kepada ramalan yang *hampir*, bukan sekadar yang tepat.

## Kekangan

- **Persekitaran:** satu GPU (≈16 GB VRAM), tiada internet pada masa penilaian — model yang
  dibenarkan (di bawah) sudah pun disediakan. **Bajet masa wall-clock: 10 minit** untuk
  keseluruhan larian — ini mesti merangkumi apa-apa latihan / fine-tuning yang anda lakukan pada masa penilaian
  **serta** inferens pada set penilaian.
- **Model pralatih yang dibenarkan** — senarai ini adalah menyeluruh; tiada pemberat pralatih lain
  yang boleh digunakan. Ia **disediakan terlebih dahulu dalam persekitaran** (muatkannya seperti biasa, cth.
  `from_pretrained`; tiada internet pada masa penilaian):
  - **bge-base-en-v1.5** — sebuah **encoder** teks 110M parameter (model embedding). Ia
    menghasilkan embedding ayat/petikan; ia bukan model bahasa generatif. Anda
    boleh menggunakannya **sebagaimana adanya (ciri yang dibekukan) atau melakukan fine-tune padanya pada split `train`**
    (fine-tuning penuh sesuai dengan bajet 16 GB / 10 minit).
- Alat klasik / statistik tidak dihadkan: anda boleh membina apa-apa model berasaskan ciri
  (cth., pengelas atau pengregres scikit-learn) di atas ciri embedding yang anda
  hitung sendiri. *Pemberat pembelajaran mendalam pralatih* sahaja yang dihadkan kepada senarai di atas.

## Baseline

`solution.ipynb` yang disediakan ialah rujukan yang remeh: ia menganggarkan satu
"pecahan sempadan rata-rata" tunggal daripada `dataset/train/` dan meramalkan pecahan yang sama daripada
panjang bagi setiap petikan ujian. Ia mendapat skor **28.6** pada split tersembunyi
**test_leaderboard_a** dan wujud hanya sebagai templat boleh-larian bagi gelung
baca-`dataset/test_public/` → tulis-`answers.jsonl`.

**Skor Jawatankuasa Saintifik 93.41**, yang diukur pada split yang sama dan bajet
10 minit yang sama, diperoleh daripada melakukan fine-tune pada encoder yang dibenarkan pada `train` dan mengesan
peralihan itu sebagai satu titik perubahan (changepoint) merentas ayat-ayat. Ia bukan satu batas atas — nilai maksimum
bagi metrik ini ialah 100.
