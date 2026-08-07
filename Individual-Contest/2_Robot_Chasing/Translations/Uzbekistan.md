# Robotni quvish

- **Vaqt cheklovi:** 5 minutes
- **Muhit:** bitta GPU (≈16 GB VRAM), internetsiz
- **Yechim hajmi:** `solution.ipynb` ≤ 1 MB
- **Xotira:** 5 GB 

## Vazifa

Oltita robot mavjud. Har bir robot panjara bilan ifodalangan kichik xonada ishlaydi. Har bir xonada devorlar bilan o‘ralgan `6×6` o‘yin maydoni mavjud, shuning uchun to‘liq `image` massivning o‘lchami `8×8` (o‘yin maydoni + devorlar).

Har bir robot vazifani tavsiflovchi ingliz tilidagi ko‘rsatmani oladi. Lahzaviy tasvir robot uni bajarayotgan istalgan paytda olinishi mumkin. Maqsadingiz robotning keyingi harakatini bashorat qilishdir.

Robotlar har doim ham eng qisqa yo‘ldan yurmaydi. Robot 0 o‘zini Robot 1 dan boshqacha tutishi mumkin, ammo har bir robot o‘zining izchil qonuniyatiga amal qiladi. Ushbu qonuniyatlarni o‘rganish uchun to‘g‘ri keyingi harakatlarni o‘z ichiga olgan o‘rgatish misollaridan foydalaning.

![Robot](../robot.jpg)

Missiyalarning uch turi mavjud:

- biror obyektga **borish**, masalan, `"approach the red ball"`;
- biror obyektni **olish**, masalan, `"grab the blue key"`;
- **bir obyektni boshqasining yoniga qo‘yish**, masalan,
  `"place the red box beside the green ball"`.

Ayni bir ko‘rsatma bir necha usulda yozilishi mumkin. Test to‘plamida tanish iboralar, ranglar va obyekt turlarining yangi kombinatsiyalari bo‘lishi mumkin. Biroq test to‘plamida ishlatiladigan har bir so‘z, ibora qolipi, rang, obyekt turi va missiya turi o‘rgatish to‘plamida ham uchraydi.

Har bir namunada quyidagi maydonlar mavjud:

| Maydon | Ma’nosi |
|---|---|
| `robot_id` | bu 6 ta robotdan qaysi biri ekanligi (`0`–`5`) |
| `image` | xona, `8×8×2` butun sonli massiv bo‘lib, unda 0-kanal kategoriyali object_idx ni (masalan, 1=bo‘sh, 2=devor, 10=robot), 1-kanal esa kategoriyali colour_idx ni (0–5) saqlaydi. |
| `direction` | robot hozir qarab turgan yo‘nalish |
| `mission` | ko‘rinadigan tabiiy tildagi ko‘rsatma |
| `carrying` | olib yurilayotgan obyekt uchun `null` yoki `[object_idx, colour_idx]` |

Qatorlar tasodifiy tartibdagi mustaqil lahzaviy tasvirlardir. Ular epizodlarni hosil qilmaydi va baholash vaqtida hech qanday oldingi kuzatuv yoki harakat mavjud bo‘lmaydi.

Taqdim etilgan `visualize_dataset.ipynb` turli vaziyatlarda model uchun mavjud kuzatuvlarni ko‘rib chiqish imkonini beradi.

## Panjarani kodlash

`image[row][column] = [object_idx, colour_idx]`. Birinchi indeks yuqoridan pastga qarab qatorni, ikkinchi indeks esa chapdan o‘ngga qarab ustunni bildiradi. Massiv tashqi devor chegarasini o‘z ichiga oladi, shuning uchun yurish mumkin bo‘lgan ichki qism `6×6`.

Obyekt id lari:

| id | obyekt |
|---:|---|
| 1 | bo‘sh katak |
| 2 | devor |
| 5 | kalit |
| 6 | to‘p |
| 7 | quti |
| 10 | robot |
| 11 | token |

Tokenlar xonada paydo bo‘lishi mumkin, ammo missiyalarda hech qachon tilga olinmaydi.

Rang id lari: `0` qizil, `1` yashil, `2` ko‘k, `3` binafsharang, `4` sariq va `5` kulrang. Rang kanali bo‘sh kataklar va devorlar uchun hech qanday ma’noga ega emas.

Tasvir faqat yuqoridagi ikkita kanalga ega. Robotning yo‘nalishi yuqori darajadagi `direction` maydonida bir marta beriladi; u `image` ichida takrorlanmaydi.

## Harakatlar

`0`–`3` kodlari uchun siljish harakatlari quyidagi mutlaq moslikdan foydalanadi:

| harakat | ma’nosi |
|---:|---|
| 0 | yuqoriga siljish |
| 1 | pastga siljish |
| 2 | chapga siljish |
| 3 | o‘ngga siljish |
| 4 | olish |
| 5 | tashlab qo‘yish |


`direction` maydoni joriy qarash yo‘nalishini quyidagicha bildiradi: 0 = Yuqori (row - 1), 1 = Past (row + 1), 2 = Chap (col - 1), 3 = O‘ng (col + 1).

Siljish harakati avval robotni ushbu mutlaq yo‘nalishga buradi, so‘ng uni bir katakka siljitishga urinadi. Devor yoki obyekt siljishni to‘sishi mumkin, ammo yo‘nalish baribir o‘zgaradi. `pick up` va `drop` faqat yo‘nalish belgilaydigan qo‘shni nishon katakka ta’sir qiladi (masalan, direction=0 bo‘lsa, u (row - 1, col) ga ta’sir qiladi).

## Dataset

Sizga ikkita papka beriladi:

| Papka | Qatorlar | `labels.json`? | Undan quyidagilar uchun foydalaning |
|---|---:|---|---|
| `dataset/train/` | 60,000 | kiritilgan | modelingizni o‘rgatish |
| `dataset/test_public/` | 3,600 | ishlab chiqish nusxasiga kiritilgan | pipeline’ingizni ishga tushirish va mustaqil baholash |

Har bir papkada yuqorida tavsiflangan namunalarning JSON ro‘yxati bo‘lgan `observations.json` mavjud. `labels.json` — harakatlarning (`0`–`5`) moslangan JSON ro‘yxati.

O‘rgatish to‘plami har bir robot uchun aynan 10,000 ta qatorni va har bir
vazifa oilasidan 20,000 ta qatorni o‘z ichiga oladi. Ochiq test har bir robot uchun 600 ta qatorni o‘z ichiga oladi. Agar massiv kerak bo‘lsa, `image` ni
`numpy.asarray(...)` bilan o‘rang.

Baholash vaqtida `dataset/test_public/` xuddi shu formatdagi, ammo `labels.json` siz
3,600 ta kuzatuvdan iborat yashirin to‘plam bilan shaffof tarzda almashtiriladi. Ochiq
reyting jadvali `test_leaderboard_a` dan foydalanadi; yakuniy reyting
`test_leaderboard_b` dan foydalanadi. Test belgilarini shartsiz o‘qiydigan notebook ishlamaydi.
Belgilarni faqat `dataset/train/` dan o‘qing.

## Chiqish

Notebook’ning ishchi katalogiga `predictions.json` ni yozing. U
`dataset/test_public/observations.json` ning har bir qatori uchun xuddi shu tartibda bittadan butun sonli harakatni (`0`–`5`) o‘z ichiga olgan JSON
ro‘yxat bo‘lishi kerak. Oltita namunani o‘z ichiga olgan faraziy test to‘plami uchun quyidagisi yaroqli chiqish bo‘ladi:

```json
[0, 3, 2, 2, 5, 4]
```

Yo‘q yoki yaroqsiz JSON fayl, noto‘g‘ri miqdordagi bashoratlar, butun son bo‘lmagan qiymat
yoki `{0,1,2,3,4,5}` dan tashqaridagi harakat bahosiz rad etiladi.

## Baholash

Baholash `0`–`100` shkalasidagi **har bir robot bo‘yicha o‘rtacha aniqlik** asosida amalga oshiriladi. Aniqlik avval
har bir robot uchun alohida hisoblanadi, keyin barcha oltita robot bo‘yicha o‘rtachasi olinadi. Shu sababli har bir
robot bir xil vaznga ega.

## Qanday topshirish kerak

1. `solution.ipynb` ni oching va barcha kataklarni ishga tushiring.
2. U ochiq test to‘plami uchun 3,600 ta bashorat bilan `predictions.json` ni yozishini
   tasdiqlang.
3. Istasangiz, modelni yaxshilang; taqdim etilgan baseline faqat talab qilinadigan
   kirish va chiqish formatini namoyish etadi.
4. JupyterLab Git ichki oynasida `solution.ipynb` ni stage qiling va commit qiling, so‘ng uni push qiling.
5. Contest sahifasiga qayting va **Submit** tugmasini bosing.

Aynan `solution.ipynb` nomli bitta faylni topshiring.
