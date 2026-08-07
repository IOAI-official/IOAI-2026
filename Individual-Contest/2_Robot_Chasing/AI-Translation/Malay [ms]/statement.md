# Robot Memburu

- **Had masa:** 5 minit
- **Persekitaran:** satu GPU (≈16 GB VRAM), tanpa internet
- **Saiz penyelesaian:** `solution.ipynb` ≤ 1 MB
- **Storan:** 5 GB

## Tugasan

Terdapat enam robot. Setiap robot beroperasi di dalam sebuah bilik kecil yang diwakili oleh satu grid. Setiap bilik mempunyai kawasan boleh dimainkan `6×6` yang dikelilingi oleh dinding, jadi keseluruhan tatasusunan `image` mempunyai saiz `8×8` (kawasan boleh dimainkan + dinding).

Setiap robot menerima satu arahan dalam bahasa Inggeris yang menerangkan sesuatu tugasan. Petikan keadaan (snapshot) itu boleh diambil pada bila-bila titik semasa robot sedang melaksanakannya. Matlamat anda adalah untuk meramal tindakan seterusnya robot tersebut.

Robot tidak semestinya mengikut laluan terpendek. Robot 0 mungkin bertingkah laku berbeza daripada Robot 1, tetapi setiap robot mengikut polanya sendiri yang konsisten. Gunakan contoh latihan, yang merangkumi tindakan seterusnya yang betul, untuk mempelajari pola-pola ini.

![Robot](../../robot.jpg)

Terdapat tiga jenis misi:

- **go to** sesuatu objek, contohnya `"approach the red ball"`;
- **pick up** sesuatu objek, contohnya `"grab the blue key"`;
- **put one object next to another**, contohnya
  `"place the red box beside the green ball"`.

Arahan yang sama boleh ditulis dalam beberapa cara. Set ujian mungkin mengandungi gabungan baharu bagi frasa, warna dan jenis objek yang sudah dikenali. Namun, setiap perkataan, pola frasa, warna, jenis objek dan jenis misi yang digunakan dalam set ujian juga muncul dalam set latihan.

Setiap sampel mempunyai medan berikut:

| Medan | Maksud |
|---|---|
| `robot_id` | robot yang mana antara 6 robot (`0`–`5`) |
| `image` | bilik tersebut, satu tatasusunan integer `8×8×2` di mana saluran 0 menyimpan object_idx berkategori (cth., 1=empty, 2=wall, 10=robot) dan saluran 1 menyimpan colour_idx berkategori (0–5). |
| `direction` | arah yang sedang dihadapi oleh robot |
| `mission` | arahan bahasa tabii yang kelihatan |
| `carrying` | `null` atau `[object_idx, colour_idx]` bagi objek yang dibawa |

Baris-baris ialah petikan keadaan bebas dalam susunan rawak. Ia tidak membentuk episod, dan tiada pemerhatian atau tindakan sebelumnya yang tersedia semasa penilaian.

`visualize_dataset.ipynb` yang disediakan membolehkan anda memeriksa pemerhatian yang tersedia kepada model dalam situasi yang berbeza.

## Pengekodan grid

`image[row][column] = [object_idx, colour_idx]`. Indeks pertama ialah baris dari atas ke bawah, dan yang kedua ialah lajur dari kiri ke kanan. Tatasusunan itu merangkumi sempadan dinding luar, jadi bahagian dalam yang boleh dilalui ialah `6×6`.

Id objek:

| id | objek |
|---:|---|
| 1 | sel kosong |
| 2 | dinding |
| 5 | kunci |
| 6 | bola |
| 7 | kotak |
| 10 | robot |
| 11 | token |

Token mungkin muncul di dalam bilik tetapi tidak sesekali dinamakan dalam misi.

Id warna ialah `0` merah, `1` hijau, `2` biru, `3` ungu, `4` kuning dan `5` kelabu. Saluran warna tidak mempunyai maksud bagi sel kosong dan dinding.

Imej itu hanya mempunyai dua saluran di atas. Arah robot diberikan sekali sahaja, dalam medan peringkat atas `direction`; ia tidak diduplikasi di dalam `image`.

## Tindakan

Bagi kod `0`–`3`, tindakan pergerakan menggunakan pemetaan mutlak berikut:

| tindakan | maksud |
|---:|---|
| 0 | bergerak ke atas |
| 1 | bergerak ke bawah |
| 2 | bergerak ke kiri |
| 3 | bergerak ke kanan |
| 4 | ambil |
| 5 | lepas |


Medan `direction` menunjukkan orientasi hadapan semasa menggunakan: 0 = Atas (row - 1), 1 = Bawah (row + 1), 2 = Kiri (col - 1), 3 = Kanan (col + 1).

Satu tindakan pergerakan mula-mula memutarkan robot ke arah mutlak tersebut dan kemudian mencuba menggerakkannya sebanyak satu sel. Dinding atau objek mungkin menghalang pergerakan itu, tetapi arahnya tetap berubah. `pick up` dan `drop` bertindak secara eksklusif pada sel sasaran bersebelahan yang ditentukan oleh arah (cth., jika direction=0, ia bertindak pada (row - 1, col)).

## Set data

Anda menerima dua folder:

| Folder | Baris | `labels.json`? | Gunakannya untuk |
|---|---:|---|---|
| `dataset/train/` | 60,000 | disertakan | melatih model anda |
| `dataset/test_public/` | 3,600 | disertakan dalam salinan pembangunan | menjalankan dan menilai sendiri saluran kerja anda |

Setiap folder mengandungi `observations.json`, satu senarai JSON bagi sampel-sampel yang diterangkan
di atas. `labels.json` ialah satu senarai JSON tindakan yang sejajar (`0`–`5`).

Set latihan mengandungi tepat 10,000 baris bagi setiap robot dan 20,000 baris daripada setiap
keluarga tugasan. Ujian awam mengandungi 600 baris bagi setiap robot. Balut `image` dengan
`numpy.asarray(...)` jika anda memerlukan satu tatasusunan.

Semasa pemarkahan, `dataset/test_public/` digantikan secara telus dengan satu set tersembunyi berisi
3,600 pemerhatian dalam format yang sama, tetapi tanpa `labels.json`. Papan pendahulu awam
menggunakan `test_leaderboard_a`; kedudukan akhir menggunakan
`test_leaderboard_b`. Sebuah notebook yang membaca label ujian tanpa syarat akan gagal.
Baca label hanya daripada `dataset/train/`.

## Output

Tulis `predictions.json` dalam direktori kerja notebook. Ia mestilah satu senarai JSON
yang mengandungi satu tindakan integer (`0`–`5`) bagi setiap baris
`dataset/test_public/observations.json`, dalam susunan yang sama. Bagi satu set ujian hipotetikal yang mengandungi enam sampel, output yang sah adalah:

```json
[0, 3, 2, 2, 5, 4]
```

Fail JSON yang hilang atau tidak sah, bilangan ramalan yang salah, nilai bukan integer,
atau tindakan di luar `{0,1,2,3,4,5}` akan ditolak tanpa markah.

## Pemarkahan

Pemarkahan ialah **ketepatan min setiap robot** pada skala `0`–`100`. Ketepatan mula-mula
dihitung secara berasingan bagi setiap robot, kemudian dirata-ratakan ke atas kesemua enam robot. Oleh itu, setiap
robot mempunyai pemberat yang sama.

## Cara menghantar

1. Buka `solution.ipynb` dan jalankan semua sel.
2. Pastikan ia menulis `predictions.json` dengan 3,600 ramalan bagi set ujian
   awam.
3. Perbaiki model itu jika anda mahu; baseline yang disediakan hanya menunjukkan
   format input dan output yang diperlukan.
4. Dalam tab Git JupyterLab, stage dan commit `solution.ipynb`, kemudian push fail itu.
5. Kembali ke halaman Contest dan klik **Submit**.

Hantar tepat satu fail bernama `solution.ipynb`.
