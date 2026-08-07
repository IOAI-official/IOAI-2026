# Dilema Ejen Berkembar

- **Had masa:** 12 minit.
- **Storan:** 5 GB
- **Persekitaran:** satu GPU (≈16 GB VRAM), tiada internet
- **Saiz penyelesaian:** `solution.ipynb` ≤ 1 MB
- **Skor baseline:** 0 
- **Skor Jawatankuasa Saintifik:** 96.99 

Di pusat AI kebangsaan di Astana, dua model komputer — Model R (sebuah ResNet-18) dan Model V (sebuah ViT-Tiny) — sedang menganalisis foto. Pada masa ini, kedua-dua model melakukan tugas dengan sempurna, mencatat ketepatan 100% dan bersetuju pada setiap imej. Untuk menguji sejauh mana "otak" pintar mereka sebenarnya berbeza, ketua saintis memberikan anda satu cabaran: buat perubahan piksel yang kecil dan hampir tidak kelihatan pada setiap foto supaya Model R dan Model V tidak bersetuju sama sekali.

![img](../../dilemma.jpg)

## 1. Tugasan

Dua pengelas imej pralatih melihat imej yang sama. Pada imej yang disediakan dalam tugasan ini, kedua-dua pengelas mencapai ketepatan 100%.

- **Model R**: `torchvision.models.resnet18` (sebuah CNN, ResNet18).
- **Model V**: `vit_tiny_patch16_224` daripada `timm` (sebuah Transformer, ViT-Tiny).

Tugasan anda adalah untuk mencipta satu perubahan kecil ("perturbation") bagi setiap imej supaya kedua-dua model tidak bersetuju. Bagi setiap imej, anda mesti mencipta **dua** perturbation yang **berbeza**:

- **Jenis A**: selepas ditambah, Model R masih mengelaskan imej dengan betul, tetapi Model V mengelaskannya dengan salah.
- **Jenis B**: selepas ditambah, Model V masih mengelaskan imej dengan betul, tetapi Model R mengelaskannya dengan salah.

Setiap perturbation mesti *kecil* secukupnya sehingga sukar disedari. Perturbation yang lebih kecil mendapat skor lebih tinggi (lihat Seksyen 5). Perturbation dikenakan pada imej asal secara langsung pada peringkat piksel.

## 2. Data awam

Satu set imej disediakan bersama tugasan ini, disusun kepada dua bahagian (split) — `train` (100 imej) dan
`test_public` (100 imej) — masing-masing dengan imej pada resolusi yang berbeza-beza. Semua imej adalah daripada 1000 kelas ImageNet-1K dan kedua-dua Model R dan Model V mencapai ketepatan 100% pada kedua-dua split.

Fail berikut disediakan:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Semasa pemarkahan, folder `dataset/test_public/` anda digantikan secara telus dengan dua set imej tersembunyi (`test_leaderboard_a` dan `test_leaderboard_b`) untuk pemarkahan rasmi. Setiap satu daripadanya mengandungi **100 imej** dalam format PNG dan satu fail label. 

**Nota: Untuk tugasan ini, label dalam set data ujian boleh diakses.**

## 3. Format output

Bagi setiap imej, anda mesti menghasilkan dua fail:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), sepadan dengan nama imej dalam set data.
- Setiap fail ialah satu tensor tunggal yang disimpan dengan `torch.save`. Bentuknya mesti`3 x H x W`, di mana `H` dan `W` sepadan dengan resolusi **asal** imej tersebut (bukan `224 x 224`).
- Kod tersebut hendaklah menghasilkan hanya satu fail ZIP, `submission.zip`. Letakkan semua fail `.pt` pada aras teratas arkib ZIP, tanpa folder pembalut atau subdirektori. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Notebook tersebut akan memberi amaran kepada anda jika terdapat apa-apa isu dengan format output.

## 4. Kekangan

- **Model:** Anda mesti menggunakan `torchvision.models.resnet18(pretrained=True)` dan `timm.create_model('vit_tiny_patch16_224', pretrained=True)`. Tiada model pralatih lain dibenarkan.
- **Talian paip transform (dikuatkuasakan semasa penilaian):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` untuk butiran. 
- **Resolusi perturbation:** Mesti sepadan dengan resolusi imej mentah **asal** (bukan 224×224). Tensor tersebut
  ditambah kepada imej mentah *sebelum* talian paip transform.
- **Format output:** Fail `.pt` sahaja — tiada PNG/JPG . Tensor ditambah kepada imej mentah dan nilai piksel dikepit (clip) kepada `[0, 1]` sebelum prapemprosesan.
- **Penamaan fail:** Disenaraikan rata (flat-listed), format `{index}_a.pt` / `{index}_b.pt` yang ketat. Tiada subdirektori di dalam zip.
- **Pustaka:** `torch`, `torchvision`, `timm`. 

## 5. Pemarkahan

Skor akhir dikira seperti berikut. Biar `M` ialah bilangan imej dalam split tersebut, $Score_A$ bilangan perturbation Jenis A yang berjaya, dan $Score_B$ bilangan perturbation Jenis B yang berjaya:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF ialah satu fungsi yang direka untuk menghukum perturbation yang mempunyai norm tinggi dan supaya sangat sensitif berhampiran siling prestasi. Ia terbatas dalam julat 0.5 hingga 1. Pelaksanaan penuh boleh dilihat dalam Seksyen 8 `solution.ipynb`. 

![img](../../curves.jpeg)
Rajah: Lengkung fungsi penalti.

## 6. Semak Penghantaran

Terdapat pemeriksaan dalam notebook yang memberi amaran kepada anda jika terdapat isu pemformatan, pada Seksyen 7 dalam notebook `solution.ipynb`.

## 7. Ujian setempat

`solution.ipynb` mengandungi satu contoh yang lengkap dan berfungsi. Ia memuatkan data awam, kedua-dua model, dan pemberi skor rasmi, serta menulis satu fail ZIP penghantaran. Bacalah ia sebelum anda mula.

## 8. Cara menghantar

- Simpan perubahan anda ke `solution.ipynb`.
- Buka tab Git di bar sisi kiri JupyterLab.
- **Stage** `solution.ipynb` (ikon + di sebelahnya).
- Masukkan mesej commit dan klik **Commit**.
- Klik ikon awan-dengan-anak-panah-ke-atas untuk push.
- Kembali ke halaman Contest ini dan klik **Submit**.

Hantar tepat satu fail, dinamakan `solution.ipynb`.
