# Robot Chasing

- **Batas waktu:** 5 menit
- **Lingkungan:** satu GPU (≈16 GB VRAM), tanpa internet
- **Ukuran solusi:** `solution.ipynb` ≤ 1 MB
- **Penyimpanan:** 5 GB

## Tugas

Terdapat enam robot. Setiap robot beroperasi di sebuah ruangan kecil yang direpresentasikan sebagai grid. Setiap ruangan memiliki area bermain `6×6` yang dikelilingi tembok, sehingga array `image` lengkap berukuran `8×8` (area bermain + tembok).

Setiap robot menerima instruksi dalam bahasa Inggris yang menjelaskan suatu tugas. Snapshot dapat diambil pada titik mana pun ketika robot sedang menjalankan instruksi tersebut. Tujuan Anda adalah memprediksi aksi berikutnya dari robot tersebut.

Robot tidak selalu mengikuti jalur terpendek. Robot 0 dapat berperilaku berbeda dari Robot 1, tetapi setiap robot mengikuti polanya sendiri yang konsisten. Gunakan contoh-contoh pelatihan, yang mencakup aksi berikutnya yang benar, untuk mempelajari pola-pola ini.

![Robot](../robot.jpg)

Terdapat tiga jenis misi:

- **pergi ke** suatu objek, misalnya `"approach the red ball"`;
- **mengambil** suatu objek, misalnya `"grab the blue key"`;
- **meletakkan satu objek di samping objek lain**, misalnya
  `"place the red box beside the green ball"`.

Instruksi yang sama dapat dituliskan dengan beberapa cara. *Test set* dapat memuat kombinasi baru dari kata, frasa, pola, warna, dan jenis objek yang sudah dikenal dari *training set*. Namun, setiap kata, frasa, pola, warna, jenis objek, dan jenis misi yang muncul di dalam *test set* juga muncul di dalam *training set*.

Setiap sampel memiliki field berikut:

| Field | Makna |
|---|---|
| `robot_id` | robot yang mana di antara 6 robot (`0`–`5`) |
| `image` | ruangan, sebuah array bilangan bulat `8×8×2` dengan kanal 0 memuat `object_idx` yang bersifat kategorikal (mis., `1=kosong`, `2=tembok`, `10=robot`) dan kanal 1 memuat `colour_idx` yang juga bersifat kategorikal (0–5). |
| `direction` | arah yang sedang dihadapi robot |
| `mission` | instruksi bahasa alami (*natural language*) eksplisit |
| `carrying` | `null` atau `[object_idx, colour_idx]` untuk objek yang dibawa |

Baris-baris merupakan *snapshot-snapshot* yang bersifat independen dan dalam urutan acak. Baris-baris tersebut tidak membentuk episode. Tidak ada observasi atau aksi pada *step* sebelumnya yang tersedia pada saat evaluasi.

Dokumen `visualize_dataset.ipynb` yang disediakan memungkinkan Anda untuk memeriksa observasi yang tersedia bagi model dalam berbagai situasi.

## *Grid Encoding*

`image[row][column] = [object_idx, colour_idx]`. Indeks pertama (*row*) adalah indeks untuk baris dari atas ke bawah, dan indeks kedua (*column*) adalah indeks kolom dari kiri ke kanan. *Array* yang diberikan mencakup batas tembok terluar dengan ukuran `8×8`, sehingga bagian yang dapat dilalui adalah bagian dalam *array* berukuran `6×6`.

Id objek:

| id | objek |
|---:|---|
| 1 | sel kosong |
| 2 | tembok |
| 5 | key |
| 6 | ball |
| 7 | box |
| 10 | robot |
| 11 | token |

Token dapat muncul di dalam ruangan tetapi tidak pernah disebutkan dalam misi.

Id warna adalah `0` merah, `1` hijau, `2` biru, `3` ungu, `4` kuning, dan `5` abu-abu. Kanal warna tidak memiliki makna untuk sel kosong dan tembok.

Citra hanya memiliki dua kanal yang sudah dijelaskan di atas. Arah robot diberikan satu kali, yakni pada field `direction` di tingkat teratas; dimana arah tersebut tidak diduplikasi (tidak terlihat) di dalam `image`.

## Aksi

Untuk kode `0`–`3`, aksi pergerakan menggunakan pemetaan absolut berikut:

| aksi | makna |
|---:|---|
| 0 | bergerak ke atas |
| 1 | bergerak ke bawah |
| 2 | bergerak ke kiri |
| 3 | bergerak ke kanan |
| 4 | mengambil |
| 5 | menjatuhkan |


Field `direction` menunjukkan orientasi hadap saat ini dengan: 0 = Atas (row - 1), 1 = Bawah (row + 1), 2 = Kiri (col - 1), 3 = Kanan (col + 1).

Sebuah aksi pergerakan robot dilakukan dalam dua tahap, dimana robot akan berputar ke arah absolut yang diminta terlebih dahulu (atas, bawah, kiri, atau kanan) dan lalu kemudian mencoba bergerak sejauh satu sel. Tembok atau objek dapat menghalangi pergerakan robot, tetapi arahnya tetap berubah. Aksi `pick up` dan `drop` bekerja secara eksklusif pada sel target di depan robot yang ditentukan oleh *direction* (mis., jika `direction=0` yang menandakan pergerakan ke atas oleh robot, maka aksi bekerja pada (row - 1, col)).

## Dataset

Anda menerima dua folder:

| Folder | Baris | `labels.json`? | Gunakan untuk |
|---|---:|---|---|
| `dataset/train/` | 60,000 | disertakan | Melatih model Anda |
| `dataset/test_public/` | 3,600 | Disertakan pada salinan pengembangan | menjalankan dan menilai sendiri pipeline Anda |

Setiap folder berisi `observations.json`, sebuah dokumen JSON berisi daftar sampel-sampel yang dijelaskan di atas. `labels.json` adalah daftar JSON aksi yang selaras (`0`–`5`).

Training set berisi tepat 10,000 baris per robot dan 20,000 baris dari setiap
keluarga tugas. Test publik berisi 600 baris per robot. Bungkus `image` dengan
`numpy.asarray(...)` jika Anda memerlukan sebuah array.

Pada saat penilaian, `dataset/test_public/` diganti secara transparan dengan sebuah himpunan tersembunyi berisi
3,600 observasi dalam format yang sama, tetapi tanpa `labels.json`. Papan peringkat publik
menggunakan `test_leaderboard_a`; peringkat akhir menggunakan
`test_leaderboard_b`. Notebook yang membaca label test tanpa syarat akan gagal.
Bacalah label hanya dari `dataset/train/`.

## Keluaran

Tuliskan `predictions.json` pada direktori kerja notebook. File tersebut harus berupa daftar JSON
yang berisi satu aksi bilangan bulat (`0`–`5`) per baris dari
`dataset/test_public/observations.json`, dalam urutan yang sama. Untuk suatu test set hipotetis yang berisi enam sampel, keluaran yang valid adalah:

```json
[0, 3, 2, 2, 5, 4]
```

File JSON yang hilang atau tidak valid, jumlah prediksi yang salah, nilai yang bukan bilangan bulat,
atau aksi di luar `{0,1,2,3,4,5}` akan ditolak tanpa skor.

## Penilaian

Penilaian adalah **rata-rata akurasi per robot** pada skala `0`–`100`. Akurasi pertama-tama
dihitung secara independen untuk setiap robot, lalu dirata-ratakan atas keenam robot. Karena itu, setiap
robot memiliki bobot yang sama.

## Cara mengumpulkan

1. Buka `solution.ipynb` dan jalankan semua sel.
2. Pastikan notebook menuliskan `predictions.json` dengan 3,600 prediksi untuk test set
   publik.
3. Perbaiki model jika Anda mau; baseline yang disediakan hanya menunjukkan
   format masukan dan keluaran yang diperlukan.
4. Pada tab Git di JupyterLab, lakukan stage dan commit terhadap `solution.ipynb`, lalu push.
5. Kembali ke halaman Contest dan klik **Submit**.

Kumpulkan tepat satu file bernama `solution.ipynb`.
