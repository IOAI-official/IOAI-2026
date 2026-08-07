# Cari Susunan

- **Had masa:** 10 minit
- **Persekitaran:** satu GPU (≈16 GB VRAM), tiada internet
- **Saiz penyelesaian:** `solution.ipynb` ≤ 1 MB
- **Storan:** 5 GB 

## Masalah

Anda diberikan dialog bahasa Inggeris pertuturan antara dua peserta, *Speaker A* dan *Speaker B*. Setiap dialog disegmenkan kepada pusingan penutur (speaker turns), dengan setiap pusingan mengandungi pertuturan daripada seorang penutur sahaja. Setiap pusingan disimpan sebagai fail audio `.wav` yang berasingan, jadi satu dialog lengkap diwakili oleh satu set fail `.wav`, satu bagi setiap pusingan. 

Malangnya, pusingan-pusingan itu telah dikocok secara rawak, jadi perbualan itu tidak lagi masuk akal. Dalam nama fail `chunk_{k}.wav`, `k` merujuk kepada cebisan (chunk) ke-k dalam set yang dikocok, bukan pusingan ke-k dalam dialog asal.

**‼️ Tugas anda ialah membina semula susunan kronologi asal perbualan tersebut.**

![Cari susunan](../../find_the_order.jpg)

---

## Set data

Setiap dialog mengandungi `n` fail audio yang dinamakan `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav`. Cebisan-cebisan itu ialah pusingan individu. Nama fail hanya sepadan dengan susunan yang dikocok. Ia tidak menunjukkan di mana sesuatu cebisan berada dalam perbualan asal. Setiap dialog mempunyai 7–20 cebisan, mono, 44.1 kHz (anda boleh
melakukan pensampelan semula).

**`prefix.json` mengandungi indeks nama fail bagi dua cebisan pertama dalam setiap dialog.** Ini mengenal pasti permulaan sebenar dialog dan menghapuskan kekaburan antara membaca perbualan ke hadapan atau ke belakang.

Sebagai contoh: `11: [7, 12]` bermaksud bahawa pusingan pertama dan kedua bagi dialog 11 ialah `chunk_7.wav` dan `chunk_12.wav`, masing-masing.

### Apa yang anda dapat

Anda menerima **dua folder dalam format yang serupa**:

| Folder | Dialog | `answers.json`? | Gunakan untuk |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ disertakan | melatih / fine-tune model anda |
| `dataset/test_public/`  | 100   | ✅ disertakan | menjalankan pipeline anda dan menilai skor sendiri secara setempat |

Semasa masa pemarkahan, folder `dataset/test_public/` anda digantikan secara telus dengan
`hidden evaluation set` (`test_leaderboard_a` untuk papan pendahulu awam dan `test_leaderboard_b` untuk papan pendahulu akhir) — ini mempunyai saiz dan format yang sama seperti `dataset/test_public/` tetapi tanpa `answers.json`.

Notebook anda dilaksanakan semula pada data tersebut, dan fail `answers.json` yang dihasilkannya digunakan untuk pemarkahan. Dialog ujian yang dirahsiakan berasal daripada taburan yang sama seperti `train`, jadi skor `test_public` setempat anda merupakan pratonton yang tepat.

### Struktur direktori

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

## Output

Bagi setiap dialog, tentukan susunan kronologi asal cebisan audionya. Ramalan anda hendaklah suatu permutasi `P` bagi `{0, 1, …, n−1}`, di mana `P[i]` ialah kedudukan kronologi yang diramalkan bagi `chunk_i.wav` (0 = pertama).

Fail output anda `answers.json` hendaklah memetakan setiap ID dialog kepada permutasi yang diramalkannya:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Contoh

Sebuah dialog mempunyai 3 cebisan yang dikocok `chunk_0, chunk_1, chunk_2`:

| cebisan yang dikocok | kandungan pertuturan | kedudukan sebenar (rank) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"No worries — I'll send you the notes afterwards."* | 2 (terakhir) |
| `chunk_1.wav` | *"Hey, are you coming to the three o'clock meeting?"* | 0 (pertama) |
| `chunk_2.wav` | *"I can't — I've got a dentist appointment then."* | 1 |

Susunan sebenar ialah **chunk_1 → chunk_2 → chunk_0**, jadi `P = [2, 0, 1]`, dan `prefix.json` mengandungi `[1, 2]`.

⚠️ **P mestilah suatu permutasi yang sah:** panjang n, berindeks-0, setiap nilai tepat sekali. Nilai berulang, nilai yang tiada atau entri di luar julat (contohnya berindeks-1) mendapat skor 0 bagi dialog tersebut, begitu juga dialog yang tiada daripada fail. Fail yang cacat bentuk atau bukan JSON akan ditolak.

## Pemarkahan

Pemarkahan bagi tugas ini ialah **ketepatan susunan berpasangan (pairwise ordering accuracy)**. Ia memeriksa setiap pasangan cebisan dan bertanya: _antara kedua-duanya, yang mana patut datang dahulu?_ Suatu pasangan dianggap betul jika ramalan anda memberikan jawapan yang sama seperti kebenaran asas (ground truth). Bagi sebuah dialog dengan `n` cebisan terdapat $$M = n(n-1)/2$$ pasangan; biarkan `I` menjadi bilangan inversi — pasangan yang disusun berbeza daripada kebenaran asas:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Skor akhir ialah purata skor setiap dialog bagi semua
dialog dalam split tersebut.**

## Model yang dibenarkan

Anda hanya boleh menggunakan model pra-latih berikut untuk menyelesaikan tugas ini, baik semasa latihan maupun penilaian. Semua model ini telah pun dimuat turun dan tersedia dalam persekitaran. Anda boleh melihat contoh cara menggunakannya dalam notebook baseline `solution.ipynb`. Sila ambil perhatian bahawa anda tidak boleh menggunakan sebarang model lain, dan program anda tidak mempunyai akses internet.

- **Perwakilan pertuturan:** **wav2vec 2.0**. **Whisper encoder** juga boleh digunakan sebagai pengekstrak ciri.
[Kad model wav2vec](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Pengecaman pertuturan automatik (ASR):** **OpenAI Whisper** (mana-mana saiz).
[Kad model Whisper](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Model bahasa:** **Qwen2.5-0.5B**, yang boleh digunakan secara zero-shot atau di-fine-tune pada split `train` yang disediakan.
[Kad model Qwen](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
Ambil perhatian bahawa had 10 minit itu mesti merangkumi sebarang latihan atau fine-tuning yang anda lakukan pada masa pemarkahan berserta inferens pada set penilaian.

## Cara menghantar

- Buka `solution.ipynb` dan jalankan semua sel. Pastikan ia menulis `answers.json` dalam direktori kerja dengan satu permutasi bagi setiap dialog dalam `dataset/test_public/` (100 dialog). Pada masa pemarkahan, notebook itu dijalankan semula pada set ujian tersembunyi dan `answers.json` yang dihasilkannya di sana akan dimarkahkan.
- Perbaiki penyelesaian jika anda mahu — atau tidak perlu; baseline itu sendiri sudah mengesahkan pipeline.
- Buka tab Git di bar sisi kiri JupyterLab.
- **Stage** `solution.ipynb` (ikon + di sebelahnya).
- Masukkan mesej commit dan klik **Commit**.
- Klik ikon awan-dengan-anak-panah-ke-atas untuk push.
- Kembali ke halaman Contest ini dan klik **Submit**.

Hantar tepat satu fail, dinamakan `solution.ipynb`.
