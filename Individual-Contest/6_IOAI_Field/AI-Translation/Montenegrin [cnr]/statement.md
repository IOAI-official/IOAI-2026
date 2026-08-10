# IOAI polje

- **Vremensko ograničenje:** 5 minuta
- **Prostor za skladištenje:** 5 GB
- **Veličina rješenja:** `solution.ipynb`, `custom_model.py` ≤ 1 MB zajedno
- **Prethodno trenirani modeli:** nijedan — trenirati od početka, bez interneta tokom ocjenjivanja
- **Baseline rezultat**: 31.2187
- **Rezultat Naučnog komiteta:** 63.53


## Zadatak

Gradonačelnik Astane želi da ukrasi grad stilizovanim IOAI logotipima. Kao statističar, on sve — uključujući i logotip — posmatra kao prostornu funkciju $F(x, y, \overline{W})$, gdje $x, y \in [0, 1]$ predstavljaju koordinate u 2D ravni, a $\overline{W}$ je skup skrivenih parametara koji definišu stilska svojstva kao što su boje i uglovi slova.

Pošto je $F$ previše složena da bi se izrazila eksplicitnom matematičkom jednačinom, vaš zadatak je da istrenirate neuronsku mrežu koja će je aproksimirati. Mreža će za svaki par koordinata $(x, y)$ kao izlaz dati vrijednost **IOAI polja**, generišući potpunu vizuelizaciju logotipa u vidu toplotne mape preko ravni. Ovdje je primjer vizuelizacije $F$ u vidu toplotne mape, sa nekim konkretnim skrivenim parametrima $\overline{W}$.

![f1](../../ioai1.png)

Od čega se sastoji IOAI polje? Od četiri slova i pozadine.

- Vrijednosti unutar prvog slova `I` veoma su velike (1e+10 i više), sa linearnim gradijentom
- Vrijednosti u slovu `O` obrazuju spiralni obrazac
- Vrijednost unutar slova `A` uvijek je -1
- Vrijednosti unutar posljednjeg slova `I` treba da budu slučajne vrijednosti iz opsega $[-2026,2026]$, čak i ako se ista tačka evaluira dva puta
- Van slova vrijednost je uvijek nula

Funkcija ima skrivene parametre $\overline{W}$, koji utiču na veličinu i nagib slova, zajedno sa opsegom vrijednosti unutar prvog slova `I`. Međutim, slova se neće presijecati. Ovdje je nekoliko ilustrativnih primjera kako IOAI polje izgleda sa različitim $\overline{W}$:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Šta vam je dato:**

Ovaj problem NE sadrži datasetove. Umjesto toga, data vam je funkcija generatora koja se konfiguriše pomoću JSON konfiguracione datoteke na putanji `data/train_config/field_config.json`. 

Test konfiguracija je skrivena, ali je slične prirode. Vaš zadatak je da prilagodite model datom generatoru koristeći onoliko podataka koliko želite. Vaše „train“ i „test“ distribucije generišu se iz istog generatora — samo ne znate na kojim tačkama $(x_i, y_i)$ ćete biti evaluirani.

Vaša prijava treba da se sastoji od:
- klase modela za treniranje sačuvane kao `custom_model.py`. Ovaj model treba da nasljeđuje klasu `torch.nn.Module` i koristi samo `torch` importe. Treba da sadrži klasu `CustomModel` koja se koristi u notebooku `solution.ipynb`. 
- notebooka `solution.ipynb`, koji će proizvesti težine `model.pt`


## Bodovanje

Za svaku oblast minimalni rezultat je 0, a maksimalni rezultat je 1. Konačni rezultat je prosjek za svih pet oblasti (četiri za svako slovo i jedna za pozadinu) pomnožen sa 100. Postoji **kazna za broj parametara:**

**Ako vaš model ima više od 20260 parametara, rezultat se prepolovljava.**

Broj parametara mjeri se pomoću `sum(p.numel() for p in model.parameters())`. Očekujemo da vaš model radi i u stohastičkom režimu, pri čemu je PyTorch `nn.Dropout` dio modela.

### Za standardne oblasti

Za svaku oblast $R$ (prvo slovo `I`, `O`, `A`, `Background`), evaluiramo model na $N_R = 512$ testnih tačaka $(x_i, y_i)$ sa stvarnim vrijednostima $v_i$ i predikcijama $\hat{v}_i$. Kao glavnu metriku koristimo normalizovanu srednju apsolutnu grešku (MAE). MAE je definisana kao:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

A normalizacija se izvodi kao 

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

gdje je $s_R > 0$ konstanta skaliranja.


### Za oblast posljednjeg slova `I`

U ovoj oblasti, **dropout je omogućen tokom evaluacije**. Za svaku testnu tačku $j$:

1. Pokrećemo model $K = 10$ puta da bismo dobili $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Ako je bilo koji izlaz van opsega $[-2026, 2026]$, onda $\mathrm{pointScore}(j) = 0$.
3. U suprotnom, izračunavamo standardnu devijaciju $\sigma_j$ za $K$ izlaza i pretvaramo je u rezultat:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

gdje je $s_E > 0$ fiksna konstanta skaliranja.

Rezultat za oblast je prosjek preko svih tačaka u toj oblasti:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

gdje $N_E = K * N_R$. 

Jednostavno rečeno, što je raznovrsnost veća, to će vaš rezultat za ovu oblast biti veći. **Ne možete koristiti slučajnost u čistom obliku, uključujući PyTorch funkcije `rand*` i `_uniform`; slučajnost treba da potiče od inferencije sa omogućenim dropoutom.**

## Kako predati rješenje

1. Otvorite `solution.ipynb` i pokrenite sve ćelije.
2. Poboljšajte model `CustomModel` u `custom_model.py`
3. Uvjerite se da vaša posljednja ćelija čuva model u datoteku `model.pt`.
4. U Git kartici JupyterLaba, postavite `solution.ipynb` i `custom_model.py` u staging, unesite komentar i napravite commit, a zatim ih pushujte.
5. Vratite se na stranicu takmičenja i kliknite na **Predaj**. Komentar prijave treba da bude isti kao komentar iz prethodnog koraka.
