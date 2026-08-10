# IOAI Field

- **Had masa:** 5 minit
- **Storan:** 5 GB
- **Saiz penyelesaian:** `solution.ipynb`, `custom_model.py` ≤ 1 MB secara keseluruhan
- **Model pralatih (pretrained):** tiada — latih dari kosong, tiada internet semasa pemarkahan
- **Skor Baseline**: 31.2187
- **Skor Jawatankuasa Saintifik:** 63.53


## Tugasan

Datuk Bandar Astana ingin menghiasi bandar itu dengan logo IOAI bergaya. Sebagai seorang ahli statistik, beliau melihat segala-galanya—termasuk logo tersebut—sebagai suatu fungsi ruang $F(x, y, \overline{W})$, di mana $x, y \in [0, 1]$ mewakili koordinat pada satah 2D dan $\overline{W}$ ialah satu set parameter tersembunyi yang menentukan atribut gaya seperti warna dan sudut huruf.

Oleh kerana $F$ terlalu kompleks untuk dinyatakan sebagai persamaan matematik yang eksplisit, tugasan anda ialah melatih rangkaian neural untuk menghampirinya. Rangkaian tersebut akan mengeluarkan nilai **IOAI field** bagi mana-mana pasangan koordinat $(x, y)$, menghasilkan visualisasi heatmap lengkap bagi logo itu merentasi satah. Berikut ialah contoh visualisasi heatmap bagi $F$ dengan beberapa parameter tersembunyi tertentu $\overline{W}$.

![f1](../../ioai1.png)

Apakah yang terkandung dalam IOAI field? Empat huruf dan latar belakang.

- Nilai dalam huruf `I` yang pertama adalah sangat besar (1e+10 dan lebih) dengan gradien linear
- Nilai dalam huruf `O` menunjukkan pola spiral
- Nilai dalam huruf `A` sentiasa -1
- Nilai dalam huruf `I` yang terakhir hendaklah nilai rawak daripada julat $[-2026,2026]$ walaupun dinilai pada titik yang sama dua kali
- Di luar huruf-huruf tersebut, nilainya sentiasa sifar

Fungsi ini mempunyai parameter tersembunyi $\overline{W}$, yang mempengaruhi skala dan kecondongan huruf, bersama-sama julat nilai dalam huruf `I` yang pertama. Namun, huruf-huruf tersebut tidak akan bersilang. Berikut ialah beberapa contoh ilustrasi bagaimana IOAI field kelihatan dengan $\overline{W}$ yang berbeza:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Apa yang diberikan kepada anda:**

Masalah ini TIDAK mengandungi dataset. Sebaliknya, anda diberikan fungsi penjana (generator) yang dikonfigurasikan oleh fail konfigurasi JSON di `data/train_config/field_config.json`.

Konfigurasi ujian adalah tersembunyi, tetapi ia bersifat serupa. Tugasan anda ialah memuatkan (fit) pada penjana yang diberikan menggunakan seberapa banyak data yang anda mahu. Distribusi "train" dan "test" anda dihasilkan daripada penjana yang sama - anda hanya tidak mengetahui pada titik $(x_i, y_i)$ yang mana anda akan dinilai.

Penyerahan anda hendaklah mengandungi:
- kelas model latihan yang disimpan sebagai `custom_model.py`. Model ini hendaklah mewarisi daripada kelas `torch.nn.Module` dan menggunakan hanya import `torch`. Ia hendaklah mengandungi kelas `CustomModel` yang digunakan dalam notebook `solution.ipynb`.
- notebook `solution.ipynb`, yang akan menghasilkan pemberat `model.pt`


## Pemarkahan

Bagi setiap kawasan, skor minimum ialah 0 dan skor maksimum ialah 1. Skor akhir dipuratakan merentasi kesemua lima kawasan (empat bagi setiap huruf dan latar belakang) dan digandakan dengan 100. Terdapat **penalti parameter:**

**Jika model anda mempunyai lebih daripada 20260 parameter, skor dibahagi dua.**

Bilangan parameter diukur oleh `sum(p.numel() for p in model.parameters())`. Kami menjangkakan model anda turut beroperasi dalam mod stokastik dengan PyTorch `nn.Dropout` menjadi sebahagian daripada model.

### Bagi Kawasan Standard

Bagi setiap kawasan $R$ (huruf `I` yang pertama, `O`, `A`, `Background`), kami menilai model pada $N_R = 512$ titik ujian $(x_i, y_i)$ dengan nilai sebenar $v_i$ dan ramalan $\hat{v}_i$. Kami menggunakan Mean Absolute Error (MAE) ternormal sebagai metrik utama. MAE ditakrifkan sebagai:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

Dan normalisasi dilakukan sebagai

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

di mana $s_R > 0$ ialah pemalar skala.


### Bagi kawasan huruf `I` yang terakhir

Dalam kawasan ini, **dropout diaktifkan semasa penilaian**. Bagi setiap titik ujian $j$:

1. Kami menjalankan model $K = 10$ kali untuk memperoleh $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Jika mana-mana output berada di luar julat $[-2026, 2026]$, maka $\mathrm{pointScore}(j) = 0$.
3. Jika tidak, hitung sisihan piawai $\sigma_j$ bagi $K$ output tersebut dan tukarkannya kepada skor:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

di mana $s_E > 0$ ialah pemalar skala yang tetap.

Skor kawasan ialah purata merentasi semua titik dalam kawasan tersebut:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

di mana $N_E = K * N_R$.

Secara ringkasnya, semakin banyak kepelbagaian yang anda miliki, semakin besar skor anda bagi kawasan ini. **Anda tidak boleh menggunakan random dalam bentuk tulen, termasuk fungsi PyTorch `rand*` dan `_uniform`, kerawakan hendaklah datang daripada inferens dengan dropout diaktifkan.**

## Cara menyerahkan

1. Buka `solution.ipynb` dan jalankan semua sel.
2. Perbaiki model `CustomModel` dalam `custom_model.py`
3. Pastikan sel terakhir anda menyimpan model anda ke fail `model.pt`.
4. Dalam tab Git JupyterLab, stage, komen dan commit `solution.ipynb` dan `custom_model.py`, kemudian push.
5. Kembali ke halaman Contest dan klik **Submit**. Komen penyerahan hendaklah sama dengan komen daripada langkah sebelumnya.
