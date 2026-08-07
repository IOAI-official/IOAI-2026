# Mashina arvohi

- **Vaqt cheklovi:** 10 daqiqa
- **Baseline natija:** 28.6
- **Ilmiy qo‘mita natijasi:** 93.41
- **Muhit:** bitta GPU (≈16 GB VRAM), internetsiz
- **Yechim hajmi:** `solution.ipynb` ≤ 20 MB
- **Xotira:** 5 GB
- **Oldindan o‘qitilgan modellar:** faqat **[bge-base-en-v1.5](https://yastatic.net/s3/contest/ioai/5/01_BAAI_bge-base-en-v1.5_MODEL_CARD.html)** — matn **enkoderi (encoder)** (embedding modeli).


## Vazifa

Qozog‘iston Milliy arxivida g‘alati voqealar yuz bermoqda. Kutubxonachilarning aytishicha, ayrim kitoblar ilgari boshqacha yakunlangan, ammo buni hech kim isbotlay olmaydi — barcha nusxalar bir xil va har bir hikoya hanuz mantiqan izchil. O‘zgarishlarni topish uchun siz sun’iy intellekt tadqiqotchisi sifatida taklif etildingiz.
![Arvoh](../../ghost.jpg)

Parcha inson yozgan matn sifatida boshlanadi va ma’lum bir nuqtada sezdirmasdan
til modeli yaratgan davomga o‘tadi. Yaxlit holda o‘qilganda, u bitta izchil
asar kabi ko‘rinadi — ammo o‘rtadagi qaysidir joyda muallif insondan
mashinaga almashadi. Sizning vazifangiz — **ushbu almashish nuqtasini: inson yozgan
qism tugab, mashina yozgan qism boshlanadigan belgi indeksini topish**.

Har bir namuna bitta `text` satridan iborat. Aynan bitta chegara mavjud. Undan
oldingi hamma narsa inson tomonidan yozilgan; undan boshlab keyingi hamma narsa mashina tomonidan yaratilgan.

## Dataset

Har birida bittadan chegara bo‘lgan oddiy matn formatidagi inglizcha parchalar.

- **A qism** (chegaradan oldin): inson yozgan matndan parcha.
- **B qism** (chegaradan boshlab): A qismga shartlangan holda til modeli tomonidan yaratilgan
  davom.
- Har bir qism kamida 180 so‘zdan iborat; umumiy uzunlik ~500–800 so‘z.
- **`boundary_char_index`** — A qism tugaydigan belgi ofseti:
  `text[:boundary_char_index]` — inson yozgan qism va
  `text[boundary_char_index:].lstrip()` — mashina yozgan qism.

#### Sizga beriladigan ma’lumotlar

Siz **ikkita papka** olasiz:

| Papka | Namunalar | `answers.jsonl`? | Undan quyidagilar uchun foydalaning |
|--------|---------|------------------|-----------|
| `dataset/train/` | 1,221 | ✅ kiritilgan | usulingizni o‘qitish / qo‘shimcha o‘qitish (fine-tune) |
| `dataset/test_public/`  | 380   | ✅ kiritilgan (dev nusxasi) | pipeline’ingizni ishga tushirish va natijani lokal hisoblash |

**Baholash vaqtida** `dataset/test_public/` papkangiz **yashirin
baholash to‘plami bilan almashtiriladi**. U xuddi shu formatda, ammo **`answers.jsonl`siz** bo‘ladi. Notebook’ingiz unda qayta ishga tushiriladi va u yaratgan `answers.jsonl` baholanadi.

- Ochiq leaderboard yashirin **test_leaderboard_a** to‘plamidan foydalanadi (380 namuna).

- Yakuniy reyting yashirin **test_leaderboard_b** to‘plamidan foydalanadi (380 namuna).

Uchala baholash
to‘plami ham bir xil hajmga ega va `train` bilan bir xil taqsimotdan olingan, shuning uchun lokal
`dataset/test_public/` natijangiz leaderboard natijangiz uchun oqilona bahodir.

#### Diskdagi format

```
dataset/train/data.jsonl      # one JSON object per line: {"id": "...", "text": "..."}
dataset/train/answers.jsonl   # {"id": "...", "boundary_char_index": 1842}
dataset/test_public/data.jsonl       # {"id": "...", "text": "..."}
dataset/test_public/answers.jsonl    # dev copy only — ABSENT in the hidden grading set
```

- `answers.jsonl` ichidagi IDlar `data.jsonl` ichidagi IDlarga mos keladi.
- `dataset/train/` (javoblari bilan) o‘qitish yoki qo‘shimcha o‘qitish vaqtida doimo mavjud bo‘ladi.

## Chiqish formati (yuborish formati)

Siz **nomi `solution.ipynb` bo‘lishi shart bo‘lgan bitta notebook yuborasiz**. Aynan shu fayl nomi talab qilinadi. Boshqa har qanday nomdagi fayl ishga tushirilmasdan rad etiladi.

Notebook’ingiz **`dataset/test_public/data.jsonl`ni o‘qishi** va repository ildiziga bitta
**`answers.jsonl`** faylini yozishi kerak — har bir satrda bittadan JSON obyekti bo‘lib, unda
har bir namuna IDsi siz bashorat qilgan chegara belgisi indeksiga moslanadi:

```json
{"id": "example_000123", "boundary_char_index": 1790}
{"id": "example_000124", "boundary_char_index": 2450}
```

- `boundary_char_index` **`[0, len(text)]` ichidagi butun son** bo‘lishi shart.
- `dataset/test_public/data.jsonl` ichidagi har bir ID aynan bir marta uchrashi kerak. `answers.jsonl` ichida mavjud bo‘lmagan namuna (yoki butun son bo‘lmagan / diapazondan tashqaridagi qiymat) shu namuna uchun 0
  ball oladi.

## Baholash

Har bir namuna uchun `p` siz bashorat qilgan indeks, `t` esa haqiqiy chegara bo‘lsin. Har bir namuna uchun ball belgilar masofasi ortishi bilan eksponensial ravishda kamayadi:

$$\text{score} = \exp\!\left(-\frac{|p - t|}{\tau}\right) \in (0, 1], 
~ \text{where} ~ \tau = 100.$$

Bu ballning quyidagi xatti-harakatiga olib keladi:
- **=1.0** — chegara belgisi aniq topilgan;
- **≈0.78** — 25 belgi xato; - **≈0.61** — 50 belgi xato;
- **≈0.37** — 100 belgi xato;
- **≈0.01** — 500 belgi xato.

**Yakuniy ball bo‘linmadagi barcha namunalar uchun ballarning o‘rtacha qiymatidir**
(0–100 shkalada taqdim etiladi). Metrika faqat aniq topishni emas, balki *yaqin* topishni ham rag‘batlantiradi.

## Cheklovlar

- **Muhit:** bitta GPU (≈16 GB VRAM), baholash vaqtida internet mavjud emas — ruxsat etilgan
  model (quyida) oldindan taqdim etilgan. Butun ishga tushirish uchun **umumiy vaqt cheklovi: 10 daqiqa** — bu baholash vaqtida bajaradigan har qanday o‘qitish / qo‘shimcha o‘qitish
  jarayonini **hamda** baholash to‘plamida inferensiyani qamrab olishi shart.
- **Ruxsat etilgan oldindan o‘qitilgan model** — bu ro‘yxat to‘liq; boshqa hech qanday oldindan o‘qitilgan vaznlardan
  foydalanish mumkin emas. U **muhitda oldindan taqdim etilgan** (uni odatdagidek yuklang, masalan,
  `from_pretrained`; baholash vaqtida internet mavjud emas):
  - **bge-base-en-v1.5** — 110M parametrli matn **enkoderi** (embedding modeli). U
    gap/parcha embeddinglarini yaratadi; u generativ til modeli emas. Undan
    **o‘z holicha (muzlatilgan belgilar sifatida) foydalanishingiz yoki uni `train` bo‘linmasida qo‘shimcha o‘qitishingiz mumkin**
    (to‘liq qo‘shimcha o‘qitish 16 GB / 10 daqiqalik cheklovga sig‘adi).
- Klassik / statistik vositalar cheklanmagan: o‘zingiz hisoblagan embedding belgilariga
  tayangan har qanday belgilar asosidagi modelni (masalan, scikit-learn klassifikatorlari yoki regressorlari) yaratishingiz mumkin. *Oldindan o‘qitilgan chuqur o‘rganish vaznlari* faqat yuqoridagi ro‘yxat bilan cheklangan.

## Baseline

Taqdim etilgan `solution.ipynb` sodda namuna yechimdir: u `dataset/train/`dan yagona
«o‘rtacha chegara ulushi»ni hisoblaydi va har bir test parchasi uchun uzunlikning aynan shu ulushini
bashorat qiladi. U yashirin **test_leaderboard_a** bo‘linmasida **28.6** ball oladi va faqat
`dataset/test_public/`ni o‘qish → `answers.jsonl`ni yozish sikli uchun ishga tushiriladigan shablon sifatida mavjud.

Xuddi shu bo‘linmada va xuddi shu
10 daqiqalik cheklov ostida o‘lchangan **Ilmiy qo‘mitaning 93.41 natijasi** ruxsat etilgan enkoderni `train`da qo‘shimcha o‘qitish va
almashish joyini gaplar bo‘yicha o‘zgarish nuqtasi (changepoint) sifatida aniqlash orqali olingan. Bu yuqori chegara emas — ushbu metrikadagi maksimal
natija 100.
