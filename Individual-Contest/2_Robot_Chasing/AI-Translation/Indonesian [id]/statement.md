# Robot Chasing

- **Batas waktu:** 5 menit
- **Lingkungan:** satu GPU (≈16 GB VRAM), tanpa internet
- **Ukuran solusi:** `solution.ipynb` ≤ 1 MB
- **Penyimpanan:** 5 GB

## Tugas

Terdapat enam robot. Setiap robot beroperasi di sebuah ruangan kecil yang direpresentasikan sebagai grid. Setiap ruangan memiliki area bermain `6×6` yang dikelilingi tembok, sehingga array `image` lengkap berukuran `8×8` (area bermain + tembok).

Setiap robot menerima instruksi dalam bahasa Inggris yang menjelaskan suatu tugas. Snapshot dapat diambil pada titik mana pun ketika robot sedang menjalankannya. Tujuan Anda adalah memprediksi aksi berikutnya dari robot tersebut.

Robot tidak selalu mengikuti jalur terpendek. Robot 0 dapat berperilaku berbeda dari Robot 1, tetapi setiap robot mengikuti polanya sendiri yang konsisten. Gunakan contoh-contoh pelatihan, yang mencakup aksi berikutnya yang benar, untuk mempelajari pola-pola ini.

![Robot](../../robot.jpg)

Terdapat tiga jenis misi:

- **pergi ke** suatu objek, misalnya `"approach the red ball"`;
- **mengambil** suatu objek, misalnya `"grab the blue key"`;
- **meletakkan satu objek di samping objek lain**, misalnya
  `"place the red box beside the green ball"`.

Instruksi yang sama dapat dituliskan dengan beberapa cara. Test set dapat memuat kombinasi baru dari frasa, warna, dan jenis objek yang sudah dikenal. Namun, setiap kata, pola frasa, warna, jenis objek, dan jenis misi yang digunakan dalam test set juga muncul dalam training set.

Setiap sampel memiliki field berikut:

| Field | Makna |
|---|---|
| `robot_id` | robot yang mana di antara 6 robot (`0`–`5`) |
| `image` | ruangan, sebuah array bilangan bulat `8×8×2` dengan kanal 0 memuat object_idx kategorikal (mis., 1=kosong, 2=tembok, 10=robot) dan kanal 1 memuat colour_idx kategorikal (0–5). |
| `direction` | arah yang sedang dihadapi robot |
| `mission` | instruksi bahasa alami yang terlihat |
| `carrying` | `null` atau `[object_idx, colour_idx]` untuk objek yang dibawa |

Baris-baris merupakan snapshot independen dalam urutan acak. Baris-baris tersebut tidak membentuk episode, dan tidak ada observasi atau aksi sebelumnya yang tersedia pada saat evaluasi.

`visualize_dataset.ipynb` yang disediakan memungkinkan Anda memeriksa observasi yang tersedia bagi model dalam berbagai situasi.

## Pengodean grid

`image[row][column] = [object_idx, colour_idx]`. Indeks pertama adalah baris dari atas ke bawah, dan indeks kedua adalah kolom dari kiri ke kanan. Array tersebut mencakup batas tembok terluar, sehingga bagian dalam yang dapat dilalui berukuran `6×6`.

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

Citra tersebut hanya memiliki dua kanal di atas. Arah robot diberikan satu kali, pada field `direction` di tingkat teratas; arah tersebut tidak diduplikasi di dalam `image`.

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

Sebuah aksi pergerakan pertama-tama memutar robot ke arah absolut tersebut dan kemudian mencoba menggerakkannya sejauh satu sel. Tembok atau objek dapat menghalangi pergerakan, tetapi arahnya tetap berubah. `pick up` dan `drop` bekerja secara eksklusif pada sel target yang bersebelahan yang ditentukan oleh direction (mis., jika direction=0, aksi bekerja pada (row - 1, col)).

## Dataset

Anda menerima dua folder:

| Folder | Baris | `labels.json`? | Gunakan untuk |
|---|---:|---|---|
| `dataset/train/` | 60,000 | disertakan | melatih model Anda |
| `dataset/test_public/` | 3,600 | disertakan pada salinan pengembangan | menjalankan dan menilai sendiri pipeline Anda |

Setiap folder berisi `observations.json`, sebuah daftar JSON berisi sampel-sampel yang dijelaskan
di atas. `labels.json` adalah daftar JSON aksi yang selaras (`0`–`5`).

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
