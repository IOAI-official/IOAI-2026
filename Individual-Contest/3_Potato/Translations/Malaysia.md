# Ubi

- **Had masa:** 10 minit
- **Persekitaran:** satu GPU (≈16 GB VRAM), tanpa internet
- **Saiz penyelesaian:** `solution.ipynb` ≤ 1 MB
- **Storan:** 5 GB

## Tugasan

Rakan anda mencadangkan supaya bermain permainan teka-teka. Dia akan memain watak pengadil dan memilih satu perkataan tersembunyi daripada suatu kosa kata tetap, dan anda mesti mencarinya dalam paling banyak 30 pusingan. Dalam setiap pusingan, pengadil membandingkan dua perkataan dan melaporkan yang mana lebih dekat secara semantik dengan perkataan tersembunyi itu. Setiap permainan bermula daripada pasangan tetap `lamp vs potato`, kerana kedua-duanya merupakan dua perkara kegemaran rakan anda. Program anda kemudian mencadangkan satu perkataan baharu. Pemenang perbandingan itu dikekalkan dan dibandingkan dengan cadangan anda yang seterusnya. Anda menang sebaik sahaja anda mencadangkan perkataan tersembunyi itu dengan tepat. Pemadanan tidak mengambil kira huruf besar/kecil. Setiap perkataan yang anda cadangkan mesti ada dalam `dataset/vocabulary.json`.

Terdapat contoh penuh dalam `solution.ipynb` berserta protokol dan pemuatan data. Anda boleh mengubah kelas PublicEmbeddingPlayer. Program anda dimulakan sekali sahaja dan memainkan setiap permainan dalam satu larian tunggal; protokol tersebut mencipta PublicEmbeddingPlayer yang baharu pada permulaan setiap permainan.

## Pengadil

Program anda menghantar satu objek JSON kepada Pengadil dan Pengadil membalas dengan satu objek JSON.

Satu contoh terperinci, dengan perkataan tersembunyi ditunjukkan hanya untuk menerangkan protokol:

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

Pusingan diindeks dari 1 hingga 30, bermula dari 1.

Pilihan `verdict` ialah `first` yang bermaksud word1 lebih dekat, `second` yang bermaksud word2 lebih dekat atau
`same` yang bermaksud kedua-dua perkataan sama dekat dengan perkataan tersembunyi.

`winner_word` ialah perkataan yang dikekalkan untuk perbandingan seterusnya. Pada keputusan `same`, perkataan pertama dikekalkan.

## Set data

Dikongsi oleh setiap split:

- `dataset/vocabulary.json` — 1602 perkataan unik, semua huruf kecil. Perkataan tersembunyi sentiasa
  salah satu daripadanya
- `dataset/public_embeddings.npy` — `float32`, bentuk `(1602, 2560)`. Baris `i`
  sepadan dengan perkataan `i` dalam kosa kata. Ini ialah embedding *awam*; pengadil
  menggunakan perwakilan lain yang bersifat peribadi

Split-split tersebut ialah set perkataan tersembunyi:

| Split | Perkataan | Jawapan | Gunakan untuk |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | menjalankan penyelesaian anda dan menilai sendiri |
| `test_leaderboard_a` | 120 | tersembunyi | papan pendahulu langsung |
| `test_leaderboard_b` | 120 | tersembunyi | kedudukan akhir |

Tiada split `train` — tiada apa-apa yang disuaikan daripada baris berlabel.

### Model yang disediakan

Dua model embedding pralatih disertakan bersama tugasan ini dan boleh digunakan:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Kedua-duanya mesti dimuatkan daripada laluan tempatannya; id hub Hugging Face seperti
`"BAAI/bge-m3"` akan mencetuskan muat turun dan gagal kerana pengadilan dilakukan secara luar talian. Setiap
direktori mengandungi `example.py` yang boleh dijalankan dan menunjukkan panggilan luar talian tersebut.

Pustaka yang tersedia: `numpy`, `torch`, `sentence-transformers`. Tiada internet, tiada
muat turun, tiada pakej lain.

## Output

Tiada. Ini ialah tugasan interaktif: penyelesaian anda tidak menulis apa-apa fail jawapan; ia berkomunikasi dengan
pengadil melalui stdin/stdout seperti yang diterangkan di atas.

## Metrik

Permainan yang dijumpai pada pusingan `t` mendapat skor `1.0 - 0.02 × max(0, t - 10)`; permainan yang tidak diselesaikan
dalam 30 pusingan mendapat skor `0`. Jadi pusingan 1–10 mendapat skor `1.00`, pusingan 20 mendapat skor `0.80`, pusingan 30 mendapat skor `0.60`.

Skor tugasan anda ialah purata skor permainan × 100, antara `0.00` dan `100.00`.

Had 10 minit merangkumi permulaan, penyediaan dan kesemua 120 permainan dalam set ujian.

## Cara menghantar

1. Buka `solution.ipynb`, edit `PublicEmbeddingPlayer`, dan jalankan semua sel untuk memastikan ia berfungsi.
2. Secara pilihan, periksa ia secara tempatan: `python local_test.py solution.ipynb --limit 5`.
   Pengadil tempatan menggunakan embedding *awam*, jadi skornya
   hanya sebagai panduan.
3. Simpan `solution.ipynb`.
4. Buka tab Git di bar sisi kiri JupyterLab.
5. Stage `solution.ipynb` (ikon **+** di sebelahnya).
6. Masukkan mesej commit dan klik Commit.
7. Klik ikon awan dengan anak panah ke atas untuk push.
8. Kembali ke halaman Contest ini dan klik Submit, dengan mesej commit yang sepadan dengan yang anda telah berikan.

Hantar tepat satu fail, bernama `solution.ipynb`, yang merangkumi apa-apa penyediaan yang diperlukan dan inferens.
