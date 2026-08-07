# Potato

- **Batas waktu:** 10 menit
- **Lingkungan:** satu GPU (≈16 GB VRAM), tanpa internet
- **Ukuran solusi:** `solution.ipynb` ≤ 1 MB
- **Penyimpanan:** 5 GB

## Tugas

Teman Anda mengusulkan untuk memainkan permainan tebak-tebakan.
Ia, sebagai juri, memilih satu kata tersembunyi dari kosakata tetap, dan Anda harus menemukannya dalam paling banyak 30 giliran.
Pada setiap giliran, juri membandingkan dua kata dan melaporkan mana yang secara semantik lebih dekat dengan kata tersembunyi. Setiap permainan dimulai dari
pasangan tetap `lamp vs potato`, karena keduanya adalah dua hal favorit teman Anda. Program Anda kemudian
mengusulkan satu kata baru. Pemenang perbandingan tersebut dipertahankan
dan dibandingkan dengan usulan Anda berikutnya.
Anda memenangkan sebuah permainan pada saat Anda mengusulkan kata tersembunyi secara persis. Pencocokan
tidak membedakan huruf besar/kecil. Setiap kata yang Anda usulkan harus ada di `dataset/vocabulary.json`.

Terdapat contoh lengkap di `solution.ipynb` beserta protokol dan pemuatan data.
Anda dapat mengubah kelas PublicEmbeddingPlayer. Program Anda diinisialisasi satu kali dan memainkan setiap permainan dalam satu kali eksekusi;
protokol membuat PublicEmbeddingPlayer yang baru pada awal setiap permainan.

## Juri

Program Anda mengirimkan satu objek JSON kepada Juri dan Juri merespons dengan satu objek JSON.

Sebuah contoh terperinci, dengan kata tersembunyi ditampilkan hanya untuk menjelaskan protokolnya:

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

Giliran diindeks dari 1 sampai 30.

Opsi `verdict` adalah `first` yang berarti word1 lebih dekat, `second` yang berarti word2 lebih dekat, atau
`same` yang berarti kedua kata sama dekatnya dengan kata tersembunyi.

`winner_word` adalah kata yang dipertahankan untuk perbandingan berikutnya. Pada putusan `same`, kata pertama yang bertahan.

## Dataset

Digunakan bersama oleh setiap split:

- `dataset/vocabulary.json` — 1602 kata huruf kecil yang unik. Kata tersembunyi selalu
  salah satu dari kata-kata ini.
- `dataset/public_embeddings.npy` — `float32`, berbentuk `(1602, 2560)`. Baris `i`
  berkorespondensi dengan kata `i` dalam kosakata. Ini adalah embedding *publik*; juri
  menggunakan representasi privat yang berbeda.

Split-split tersebut adalah himpunan kata tersembunyi:

| Split | Kata | Jawaban | Gunakan untuk |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | menjalankan solusi Anda dan menilai sendiri |
| `test_leaderboard_a` | 120 | tersembunyi | leaderboard langsung |
| `test_leaderboard_b` | 120 | tersembunyi | peringkat akhir |

Tidak ada split `train` — tidak ada yang dilatih dari baris berlabel.

### Model yang disediakan

Dua model embedding terlatih (pretrained) disertakan bersama tugas ini dan boleh digunakan:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Keduanya harus dimuat dari path lokalnya; id hub Hugging Face seperti
`"BAAI/bge-m3"` akan memicu unduhan dan gagal, karena penjurian dilakukan secara offline. Setiap
direktori berisi `example.py` yang dapat dijalankan dan menunjukkan pemanggilan offline.

Pustaka yang tersedia: `numpy`, `torch`, `sentence-transformers`. Tanpa internet, tanpa
unduhan, tanpa paket lain.

## Keluaran

Tidak ada. Ini adalah tugas interaktif: solusi Anda tidak menulis berkas jawaban; solusi Anda berkomunikasi dengan
juri melalui stdin/stdout seperti dijelaskan di atas.

## Metrik

Permainan yang ditemukan pada giliran `t` memperoleh skor `1.0 - 0.02 × max(0, t - 10)`; permainan yang tidak terselesaikan
dalam 30 giliran memperoleh skor `0`. Jadi giliran 1–10 memperoleh skor `1.00`, giliran 20 memperoleh skor `0.80`, giliran
30 memperoleh skor `0.60`.

Skor tugas Anda adalah rata-rata skor permainan × 100, antara `0.00` dan `100.00`.

Batas 10 menit adalah satu anggaran tunggal yang mencakup start-up, persiapan, dan seluruh 120
permainan dalam test set.

## Cara mengirimkan

1. Buka `solution.ipynb`, sunting `PublicEmbeddingPlayer`, dan jalankan semua sel untuk memastikan semuanya berfungsi.
2. Secara opsional, periksa secara lokal: `python local_test.py solution.ipynb --limit 5`.
   Juri lokal menggunakan embedding *publik*, sehingga skornya
   hanya sebagai panduan.
3. Simpan `solution.ipynb`.
4. Buka tab Git di bilah sisi kiri JupyterLab.
5. Stage `solution.ipynb` (ikon **+** di sebelahnya).
6. Masukkan pesan commit dan klik Commit.
7. Klik ikon awan dengan panah ke atas untuk melakukan push.
8. Kembali ke halaman Contest ini dan klik Submit, dengan pesan commit yang sesuai dengan yang telah Anda berikan.

Kirimkan tepat satu berkas, bernama `solution.ipynb`, yang mencakup segala persiapan yang diperlukan dan inferensi.
