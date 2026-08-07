# Kartoshka

- **Vaqt cheklovi:** 10 daqiqa
- **Muhit:** bitta GPU (≈16 GB VRAM), internetsiz
- **Yechim hajmi:** `solution.ipynb` ≤ 1 MB
- **Saqlash joyi:** 5 GB 

## Vazifa
 
Do‘stingiz taxmin qilish o‘yinini o‘ynashni taklif qiladi.
U hakam sifatida belgilangan lug‘atdan bitta yashirin so‘zni tanlaydi va siz uni ko‘pi bilan 30 yurishda topishingiz kerak.
Har bir yurishda hakam ikkita so‘zni taqqoslaydi va qaysi biri yashirin so‘zga semantik jihatdan yaqinroq ekanini
xabar qiladi. Har bir o‘yin
belgilangan `lamp vs potato` juftligidan boshlanadi, chunki ular do‘stingizning eng sevimli narsalaridan ikkitasidir. So‘ng dasturingiz
bitta yangi so‘zni taklif qiladi. Taqqoslash g‘olibi saqlab qolinadi
va keyingi taklifingiz bilan taqqoslanadi. 
Yashirin so‘zni aynan taklif qilgan zahotingiz o‘yinda g‘alaba qozonasiz. Moslik
harflarning katta-kichikligiga bog‘liq emas. Siz taklif qiladigan har bir so‘z `dataset/vocabulary.json` ichida bo‘lishi kerak.

Protokol va ma’lumotlarni yuklashni o‘z ichiga olgan to‘liq misol `solution.ipynb` ichida berilgan. 
PublicEmbeddingPlayer klassini o‘zgartirishingiz mumkin. Dasturingiz bir marta ishga tushiriladi va barcha o‘yinlarni bitta ishga tushirish davomida o‘ynaydi;
protokol har bir o‘yin boshida yangi PublicEmbeddingPlayer yaratadi.

## Hakam

Dasturingiz Hakamga bitta JSON obyektini yuboradi va Hakam bitta JSON obyekti bilan javob beradi. 

Protokolni tushuntirish uchungina yashirin so‘z ko‘rsatilgan batafsil misol:

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

Yurishlar 1 dan 30 gacha indekslanadi.

`verdict` variantlari: word1 yaqinroq ekanini anglatuvchi `first`, word2 yaqinroq ekanini anglatuvchi `second` yoki
ikkala so‘z ham yashirin so‘zga bir xil darajada yaqin ekanini anglatuvchi `same`. 

`winner_word` — keyingi taqqoslash uchun saqlab qolinadigan so‘z. `same` hukmi berilganda, birinchi so‘z qoladi.

## Dataset

Har bir split uchun umumiy:

- `dataset/vocabulary.json` — 1602 ta noyob kichik harfli so‘z. Yashirin so‘z har doim
  shulardan biri bo‘ladi.
- `dataset/public_embeddings.npy` — `float32`, shakli `(1602, 2560)`. `i`-qator
  lug‘atdagi `i` so‘ziga mos keladi. Bular *ochiq* embeddinglar;
  hakam boshqa, yopiq reprezentatsiyadan foydalanadi.

Splitlar yashirin so‘zlar to‘plamlaridir:

| Split | So‘zlar | Javoblar | Undan quyidagicha foydalaning |
|---|---|---|---|
| `test_public` | 120 | ✅ `dataset/test_public.json` | yechimingizni ishga tushirish va o‘zingiz baholash |
| `test_leaderboard_a` | 120 | yashirin | jonli reyting jadvali |
| `test_leaderboard_b` | 120 | yashirin | yakuniy reyting |

`train` spliti yo‘q — belgilangan qatorlardan hech narsa moslashtirilmaydi.

### Taqdim etilgan modellar

Vazifa bilan birga ikkita oldindan o‘qitilgan embedding modeli taqdim etiladi va ulardan foydalanish mumkin:

```text
models/Qwen/Qwen3-Embedding-0.6B
[Qwen Embedding model card](https://yastatic.net/s3/contest/ioai/3/01_Qwen_Qwen3-Embedding-0.6B_MODEL_CARD.html)
models/BAAI/bge-m3
[bge-m3 model card](https://yastatic.net/s3/contest/ioai/3/02_BAAI_bge-m3_MODEL_CARD.html)
```

Ikkalasi ham o‘zining lokal yo‘lidan yuklanishi kerak; masalan,
`"BAAI/bge-m3"` kabi Hugging Face hub id yuklab olishni ishga tushiradi va muvaffaqiyatsiz tugaydi, chunki baholash internetsiz amalga oshiriladi. Har bir
direktoriyada internetsiz chaqiruvni ko‘rsatuvchi, ishga tushirish mumkin bo‘lgan `example.py` mavjud.

Mavjud kutubxonalar: `numpy`, `torch`, `sentence-transformers`. Internet ham, yuklab olish ham,
boshqa paketlar ham mavjud emas.

## Chiqish

Yo‘q. Bu interaktiv vazifa: yechimingiz javob faylini yozmaydi; u
yuqorida tavsiflanganidek stdin/stdout orqali hakam bilan muloqot qiladi.

## Metrika

`t`-yurishda topilgan o‘yin `1.0 - 0.02 × max(0, t - 10)` ball oladi; 30 yurish
ichida yechilmagan o‘yin `0` ball oladi. Shunday qilib, 1–10-yurishlar `1.00`, 20-yurish `0.80`,
30-yurish esa `0.60` ball oladi.

Vazifa bo‘yicha ballingiz o‘yinlar o‘rtacha balli × 100 bo‘lib, `0.00` va `100.00` oralig‘ida bo‘ladi.

10 daqiqalik cheklov ishga tushirish, tayyorgarlik va test to‘plamidagi barcha 120
o‘yinni qamrab oluvchi yagona vaqt budjetidir. 

## Qanday topshirish kerak

1. `solution.ipynb` faylini oching, `PublicEmbeddingPlayer` faylini tahrirlang va uning ishlayotganiga ishonch hosil qilish uchun barcha kataklarni ishga tushiring.
2. Ixtiyoriy ravishda, uni lokal ravishda tekshiring: `python local_test.py solution.ipynb --limit 5`.
   Lokal hakam *ochiq* embeddinglardan foydalanadi, shuning uchun uning bali
   faqat yo‘l-yo‘riq sifatida xizmat qiladi.
3. `solution.ipynb` faylini saqlang.
4. JupyterLab chap yon panelidagi Git varag‘ini oching.
5. `solution.ipynb` faylini stage qiling (uning yonidagi **+** belgisi).
6. Commit xabarini kiriting va Commit tugmasini bosing.
7. Push qilish uchun yuqoriga yo‘nalgan strelkali bulut belgisini bosing.
8. Ushbu Contest sahifasiga qayting va siz kiritgan commit xabariga mos xabar bilan Submit tugmasini bosing.

Barcha zarur tayyorgarlik va inferensiyani qamrab oluvchi, `solution.ipynb` deb nomlangan aynan bitta faylni topshiring.
