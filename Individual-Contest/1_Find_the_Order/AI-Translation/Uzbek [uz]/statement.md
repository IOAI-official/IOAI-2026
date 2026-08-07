# Tartibni toping

- **Vaqt cheklovi:** 10 daqiqa
- **Muhit:** bitta GPU (≈16 GB VRAM), internetsiz
- **Yechim hajmi:** `solution.ipynb` ≤ 1 MB
- **Saqlash joyi:** 5 GB 

## Masala

Sizga ikki ishtirokchi, *Speaker A* va *Speaker B* o‘rtasidagi ingliz tilidagi og‘zaki dialoglar beriladi. Har bir dialog so‘zlovchi replikalariga segmentlangan bo‘lib, har bir replikada faqat bitta so‘zlovchining nutqi mavjud. Har bir replika alohida `.wav` audiofayl sifatida saqlanadi, shuning uchun to‘liq dialog har bir replikaga bittadan `.wav` fayllar to‘plami bilan ifodalanadi. 

Afsuski, replikalar tasodifiy ravishda aralashtirib yuborilgan, shu sababli suhbat endi mantiqiy emas. `chunk_{k}.wav` fayl nomidagi `k` asl dialogdagi k-replikani emas, aralashtirilgan to‘plamdagi k-bo‘lakni bildiradi.

**‼️ Sizning vazifangiz suhbatning asl xronologik tartibini tiklashdir.**

![Tartibni toping](../../find_the_order.jpg)

---

## Dataset

Har bir dialog `chunk_0.wav`, `chunk_1.wav`, …, `chunk_{n-1}.wav` deb nomlangan `n` audiofayldan iborat. Bo‘laklar alohida replikalardir. Fayl nomlari faqat aralashtirilgan tartibga mos keladi. Ular bo‘lakning asl suhbatdagi o‘rnini ko‘rsatmaydi. Har bir dialogda 7–20 ta bir kanalli, 44.1 kHz bo‘lak mavjud (qayta
diskretlashingiz mumkin).

**`prefix.json` har bir dialogdagi dastlabki ikki bo‘lakning fayl nomi indekslarini o‘z ichiga oladi.** Bu dialogning haqiqiy boshlanishini aniqlaydi va suhbatni oldinga yoki orqaga qarab o‘qish orasidagi noaniqlikni bartaraf etadi.

Masalan: `11: [7, 12]` 11-dialogning birinchi va ikkinchi replikalari mos ravishda `chunk_7.wav` va `chunk_12.wav` ekanini anglatadi.

### Sizga beriladigan ma’lumotlar

Siz **bir xil formatdagi ikkita papka** olasiz:

| Papka | Dialoglar | `answers.json`? | Undan quyidagilar uchun foydalaning |
|--------|-----------|-----------------|-----------|
| `dataset/train/` | 1,288 | ✅ kiritilgan | modelingizni o‘qitish / nozik sozlash |
| `dataset/test_public/`  | 100   | ✅ kiritilgan | pipeline’ingizni ishga tushirish va natijani lokal baholash |

Baholash vaqtida `dataset/test_public/` papkangiz avtomatik ravishda
`hidden evaluation set` bilan almashtiriladi (ommaviy reyting jadvali uchun `test_leaderboard_a` va yakuniy reyting jadvali uchun `test_leaderboard_b`) — ular `dataset/test_public/` bilan bir xil hajm va formatga ega, ammo `answers.json` mavjud emas.

Notebook’ingiz ushbu ma’lumotlarda qayta bajariladi va u yaratgan `answers.json` fayli baholash uchun ishlatiladi. Ajratib qo‘yilgan test dialoglari `train` bilan bir xil taqsimotdan olingan, shuning uchun lokal `test_public` natijangiz ishonchli dastlabki ko‘rsatkichdir.

### Katalog tuzilishi

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

## Chiqish

Har bir dialog uchun uning audio bo‘laklarining asl xronologik tartibini aniqlang. Bashoratingiz `{0, 1, …, n−1}` ning `P` permutatsiyasi bo‘lishi kerak, bunda `P[i]` — `chunk_i.wav` ning bashorat qilingan xronologik o‘rni (0 = birinchi).

`answers.json` chiqish faylingiz har bir dialog ID’sini uning bashorat qilingan permutatsiyasiga moslashi kerak:

```json
{
  "17": [2, 0, 1],
  "42": [0, 1],
  "108": [3, 1, 0, 4, 2, 5]
}
```

### Misol

Dialogda aralashtirilgan 3 ta `chunk_0, chunk_1, chunk_2` bo‘lagi mavjud:

| aralashtirilgan bo‘lak | aytilgan mazmun | haqiqiy o‘rin (rang) |
|----------------|----------------|----------------------|
| `chunk_0.wav` | *"Muammo emas — keyinroq sizga qaydlarni yuboraman."* | 2 (oxirgi) |
| `chunk_1.wav` | *"Salom, soat uchdagi yig‘ilishga kelasizmi?"* | 0 (birinchi) |
| `chunk_2.wav` | *"Kela olmayman — o‘sha paytda tish shifokori qabuliga yozilganman."* | 1 |

Haqiqiy tartib **chunk_1 → chunk_2 → chunk_0**, demak, `P = [2, 0, 1]` va `prefix.json` qiymati `[1, 2]`.

⚠️ **P haqiqiy permutatsiya bo‘lishi shart:** uzunligi n, 0 dan indekslangan, har bir qiymat aynan bir martadan. Takroriy, yetishmayotgan yoki ruxsat etilgan oraliqdan tashqaridagi elementlar (masalan, 1 dan indekslangan elementlar), shuningdek, faylda mavjud bo‘lmagan dialog ushbu dialog uchun 0 ball oladi. Noto‘g‘ri shakllantirilgan yoki JSON bo‘lmagan fayl rad etiladi.

## Baholash

Ushbu vazifani baholash mezoni **juftliklar bo‘yicha tartiblash aniqligi**dir. U har bir bo‘laklar juftligini tekshiradi va quyidagini so‘raydi: _ikkalasidan qaysi biri avval kelishi kerak?_ Agar bashoratingiz haqiqiy etalon bilan bir xil javob bersa, juftlik to‘g‘ri hisoblanadi. `n` ta bo‘lakli dialogda $$M = n(n-1)/2$$ ta juftlik mavjud; `I` inversiyalar — haqiqiy etalondan boshqacha tartiblangan juftliklar soni bo‘lsin:

$$\text{score} = 1 - \frac{I}{M} \in [0, 1]$$

ℹ️ **Yakuniy natija splitdagi barcha
dialoglar bo‘yicha har bir dialog natijalarining o‘rtacha qiymatidir.**

## Ruxsat etilgan modellar

Ushbu vazifani yechish uchun ham o‘qitish, ham baholash davomida faqat quyidagi oldindan o‘qitilgan modellardan foydalanishingiz mumkin. Bu modellarning barchasi allaqachon yuklab olingan va muhitda mavjud. Ulardan qanday foydalanish misollarini `solution.ipynb` baseline notebook’ida ko‘rishingiz mumkin. Boshqa hech qanday modeldan foydalana olmasligingizni va dasturingiz internetga kira olmasligini yodda tuting.

- **Nutq reprezentatsiyalari:** **wav2vec 2.0**. **Whisper encoder**’idan xususiyatlar ekstraktori sifatida ham foydalanish mumkin.
[wav2vec model kartasi](https://yastatic.net/s3/contest/ioai/1/01_facebook_wav2vec2-base-960h_MODEL_CARD.html)

- **Nutqni avtomatik tanib olish (ASR):** **OpenAI Whisper** (istalgan hajm).
[Whisper model kartasi](https://yastatic.net/s3/contest/ioai/1/03_openai_whisper-small_MODEL_CARD.html)
- **Til modeli:** **Qwen2.5-0.5B**, undan zero-shot usulida yoki taqdim etilgan `train` splitida nozik sozlangan holda foydalanish mumkin.
[Qwen model kartasi](https://yastatic.net/s3/contest/ioai/1/02_Qwen_Qwen2.5-0.5B_MODEL_CARD.html)
10 daqiqalik cheklov baholash vaqtida bajaradigan har qanday o‘qitish yoki nozik sozlashni hamda baholash to‘plamida inferensiyani qamrab olishi kerakligini yodda tuting.

## Qanday topshirish kerak

- `solution.ipynb` ni oching va barcha kataklarni ishga tushiring. U ishchi katalogga `dataset/test_public/` dagi har bir dialog uchun permutatsiyani o‘z ichiga olgan `answers.json` faylini yozishini tasdiqlang (100 ta dialog). Baholash vaqtida notebook yashirin test to‘plamida qayta ishga tushiriladi va u yerda yaratgan `answers.json` fayli baholanadi.
- Istasangiz, yechimni yaxshilang — yoki yaxshilamang; baseline’ning o‘zi pipeline’ning to‘g‘ri ishlashini tasdiqlaydi.
- JupyterLab chap yon panelidagi Git tabini oching.
- `solution.ipynb` ni **Stage** qiling (uning yonidagi + belgisi).
- Commit xabarini kiriting va **Commit** tugmasini bosing.
- Push qilish uchun yuqoriga yo‘nalgan strelkali bulut belgisini bosing.
- Ushbu Contest sahifasiga qayting va **Submit** tugmasini bosing.

Aynan `solution.ipynb` deb nomlangan bitta faylni topshiring.
