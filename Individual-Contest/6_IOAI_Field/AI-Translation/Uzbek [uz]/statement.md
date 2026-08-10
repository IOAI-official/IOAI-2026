# IOAI maydoni

- **Vaqt chegarasi:** 5 minutes
- **Xotira:** 5 GB
- **Yechim hajmi:** `solution.ipynb`, `custom_model.py` birgalikda ≤ 1 MB
- **Oldindan o‘qitilgan modellar:** yo‘q — noldan o‘qiting, baholash vaqtida internet mavjud emas
- **Baseline natijasi**: 31.2187
- **Ilmiy qo‘mita natijasi:** 63.53


## Vazifa

Astana meri shaharni stilizatsiya qilingan IOAI logotiplari bilan bezatmoqchi. Statistika mutaxassisi sifatida u hamma narsani, jumladan logotipni ham, $F(x, y, \overline{W})$ fazoviy funksiya deb qaraydi, bunda $x, y \in [0, 1]$ 2D tekislikdagi koordinatalarni ifodalaydi, $\overline{W}$ esa harflarning ranglari va burchaklari kabi uslubiy xususiyatlarni belgilovchi yashirin parametrlar to‘plamidir.

$F$ ni aniq matematik tenglama ko‘rinishida ifodalash uchun u juda murakkab bo‘lgani sababli, vazifangiz uni approksimatsiya qilish uchun neyron tarmoqni (neural network) o‘qitishdan iborat. Tarmoq istalgan $(x, y)$ koordinatalar juftligi uchun **IOAI maydoni** qiymatini chiqarib, butun tekislik bo‘ylab logotipning to‘liq issiqlik xaritasi (heatmap) vizualizatsiyasini yaratadi. Quyida muayyan $\overline{W}$ yashirin parametrlarga ega $F$ ning issiqlik xaritasi vizualizatsiyasiga misol keltirilgan.

![f1](../../ioai1.png)

IOAI maydoni nimalardan iborat? To‘rtta harf va fon.

- Birinchi `I` harfi ichidagi qiymatlar juda katta (1e+10 va undan katta) bo‘lib, chiziqli gradientga ega
- `O` harfidagi qiymatlar spiral naqshni namoyish etadi
- `A` harfi ichidagi qiymat har doim -1
- Oxirgi `I` harfi ichidagi qiymatlar, hatto ayni nuqtada ikki marta hisoblanganda ham, $[-2026,2026]$ oraliqdagi tasodifiy qiymatlar bo‘lishi kerak
- Harflardan tashqaridagi qiymat har doim nol

Funksiya $\overline{W}$ yashirin parametrlarga ega bo‘lib, ular harflarning masshtabi va qiyaligiga, shuningdek birinchi `I` harfi ichidagi qiymatlar oralig‘iga ta’sir qiladi. Biroq, harflar kesishmaydi. Quyida IOAI maydoni turli $\overline{W}$ bilan qanday ko‘rinishiga oid bir nechta ko‘rgazmali misol keltirilgan:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Sizga beriladiganlar:**

Bu masalada HECH QANDAY dataset mavjud emas. Buning o‘rniga sizga `data/train_config/field_config.json` manzilidagi JSON konfiguratsiya fayli orqali sozlanadigan generator funksiya beriladi. 

Test konfiguratsiyasi yashirin, ammo u o‘xshash xususiyatga ega. Vazifangiz berilgan generatordan istalgancha ko‘p ma’lumot olib, ularga moslashishdan iborat. Sizning «o‘qitish» va «test» taqsimotlaringiz ayni bir generatordan yaratiladi — faqat qaysi $(x_i, y_i)$ nuqtalarda baholanishingizni bilmaysiz.

Topshirig‘ingiz quyidagilardan iborat bo‘lishi kerak:
- `custom_model.py` sifatida saqlangan o‘qitish modeli klassi. Bu model `torch.nn.Module` klassidan voris olishi va faqat `torch` importlaridan foydalanishi kerak. U `solution.ipynb` notebookida ishlatiladigan `CustomModel` klassini o‘z ichiga olishi kerak. 
- `model.pt` vaznlarini hosil qiladigan `solution.ipynb` notebooki


## Baholash

Har bir hudud uchun eng kichik natija 0, eng katta natija esa 1. Yakuniy natija barcha beshta hudud (har bir harf uchun to‘rtta va fon) bo‘yicha o‘rtachalanadi va 100 ga ko‘paytiriladi. **Parametrlar uchun jarima mavjud:**

**Agar modelingizda 20260 tadan ko‘p parametr bo‘lsa, natija ikki baravar kamaytiriladi.**

Parametrlar soni `sum(p.numel() for p in model.parameters())` orqali o‘lchanadi. Modelingiz stoxastik rejimda ham ishlashi va PyTorch `nn.Dropout` modelning bir qismi bo‘lishi kutiladi.

### Standart hududlar uchun

Har bir $R$ hudud (birinchi `I` harfi, `O`, `A`, `Background`) uchun biz modelni haqiqiy qiymatlari $v_i$ va bashoratlari $\hat{v}_i$ bo‘lgan $(x_i, y_i)$ test nuqtalarida $N_R = 512$ baholaymiz. Asosiy metrika sifatida normallashtirilgan o‘rtacha mutlaq xatolikdan (Mean Absolute Error, MAE) foydalanamiz. MAE quyidagicha aniqlanadi:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

Normallashtirish esa quyidagicha amalga oshiriladi:

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

bunda $s_R > 0$ masshtab konstantasidir.


### Oxirgi `I` harfi hududi uchun

Bu hududda **baholash vaqtida dropout yoqiladi**. Har bir $j$ test nuqtasi uchun:

1. $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$ ni olish maqsadida modelni $K = 10$ marta ishga tushiramiz.
2. Agar biror natija $[-2026, 2026]$ oraliqdan tashqarida bo‘lsa, u holda $\mathrm{pointScore}(j) = 0$.
3. Aks holda, $K$ natijalarning $\sigma_j$ standart og‘ishini hisoblang va uni natijaga aylantiring:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

bunda $s_E > 0$ o‘zgarmas masshtab konstantasidir.

Hudud natijasi hududdagi barcha nuqtalar bo‘yicha o‘rtacha qiymatdir:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

bunda $N_E = K * N_R$. 

Sodda qilib aytganda, xilma-xillik qancha ko‘p bo‘lsa, bu hudud uchun natijangiz shuncha yuqori bo‘ladi. **Tasodifiylikdan sof ko‘rinishda, jumladan PyTorch `rand*` va `_uniform` funksiyalaridan foydalana olmaysiz; tasodifiylik dropout yoqilgan inferensiyadan (inference) kelib chiqishi kerak.**

## Qanday topshirish kerak

1. `solution.ipynb` ni oching va barcha kataklarni ishga tushiring.
2. `custom_model.py` ichidagi `CustomModel` modelini yaxshilang
3. Oxirgi katagingiz modelingizni `model.pt` fayliga saqlashiga ishonch hosil qiling.
4. JupyterLab Git ichki oynasida `solution.ipynb` va `custom_model.py` ni stage qiling, izoh yozing va commit qiling, so‘ng push qiling.
5. Tanlov sahifasiga qayting va **Submit** tugmasini bosing. Topshirish izohi oldingi bosqichdagi izoh bilan bir xil bo‘lishi kerak.
