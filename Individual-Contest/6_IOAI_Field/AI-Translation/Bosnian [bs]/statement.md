# IOAI polje

- **Vremensko ograničenje:** 5 minutes
- **Prostor za pohranu:** 5 GB
- **Veličina rješenja:** `solution.ipynb`, `custom_model.py` ≤ 1 MB zajedno
- **Prethodno trenirani modeli:** nijedan — trenirajte od početka, bez interneta tokom ocjenjivanja
- **Rezultat baseline modela**: 31.2187
- **Rezultat Naučnog odbora:** 63.53


## Zadatak

Gradonačelnik Astane želi ukrasiti grad stiliziranim IOAI logotipima. Kao statističar, on sve — uključujući logotip — posmatra kao prostornu funkciju $F(x, y, \overline{W})$, gdje $x, y \in [0, 1]$ predstavljaju koordinate u 2D ravni, a $\overline{W}$ je skup skrivenih parametara koji definiraju stilska svojstva kao što su boje i uglovi slova.

Budući da je $F$ previše složena da bi se izrazila eksplicitnom matematičkom jednačinom, vaš je zadatak trenirati neuronsku mrežu koja će je aproksimirati. Mreža će za svaki par koordinata $(x, y)$ dati vrijednost **IOAI polja**, čime će se generirati potpuna vizualizacija logotipa u obliku toplotne mape preko cijele ravni. Ovo je primjer vizualizacije toplotne mape funkcije $F$ s određenim skrivenim parametrima $\overline{W}$.

![f1](../../ioai1.png)

Od čega se sastoji IOAI polje? Od četiri slova i pozadine.

- Vrijednosti unutar prvog slova `I` veoma su velike (1e+10 i više) i imaju linearni gradijent
- Vrijednosti u slovu `O` prikazuju spiralni obrazac
- Vrijednost unutar slova `A` uvijek je -1
- Vrijednosti unutar posljednjeg slova `I` trebaju biti slučajne vrijednosti iz raspona $[-2026,2026]$ čak i ako se ista tačka evaluira dva puta
- Izvan slova vrijednost je uvijek nula

Funkcija ima skrivene parametre $\overline{W}$, koji utječu na veličinu i nagib slova, zajedno s rasponom vrijednosti unutar prvog slova `I`. Međutim, slova se neće presijecati. Ovo je nekoliko ilustrativnih primjera izgleda IOAI polja s različitim vrijednostima $\overline{W}$:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Šta vam je dato:**

Ovaj problem NE sadrži datasetove. Umjesto toga, data vam je generatorska funkcija koja se konfigurira JSON konfiguracijskom datotekom na `data/train_config/field_config.json`. 

Testna konfiguracija je skrivena, ali je slične prirode. Vaš je zadatak prilagoditi model datom generatoru koristeći onoliko podataka koliko želite. Vaše distribucije za „treniranje“ i „testiranje“ generirane su iz istog generatora — samo ne znate na kojim ćete tačkama $(x_i, y_i)$ biti evaluirani.

Vaša predaja treba sadržavati:
- klasu modela za treniranje sačuvanu kao `custom_model.py`. Ovaj model treba naslijediti klasu `torch.nn.Module` i koristiti samo `torch` uvoze. Treba sadržavati klasu `CustomModel` koja se koristi u notebooku `solution.ipynb`. 
- notebook `solution.ipynb`, koji će proizvesti težine `model.pt`


## Bodovanje

Za svaku regiju minimalni rezultat je 0, a maksimalni rezultat je 1. Konačni rezultat je prosjek rezultata za svih pet regija (četiri za svako slovo i pozadinu) pomnožen sa 100. Postoji **kazna za broj parametara:**

**Ako vaš model ima više od 20260 parametara, rezultat se prepolovljava.**

Broj parametara mjeri se pomoću `sum(p.numel() for p in model.parameters())`. Očekujemo da vaš model radi i u stohastičkom režimu, pri čemu je PyTorch `nn.Dropout` dio modela.

### Za standardne regije

Za svaku regiju $R$ (prvo slovo `I`, `O`, `A`, `Background`), evaluiramo model na $N_R = 512$ testnih tačaka $(x_i, y_i)$ sa stvarnim vrijednostima $v_i$ i predikcijama $\hat{v}_i$. Kao glavnu metriku koristimo normaliziranu srednju apsolutnu grešku (MAE). MAE se definira kao:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

A normalizacija se izvodi kao 

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

gdje je $s_R > 0$ konstanta skaliranja.


### Za regiju posljednjeg slova `I`

U ovoj regiji **dropout je omogućen tokom evaluacije**. Za svaku testnu tačku $j$:

1. Pokrećemo model $K = 10$ puta kako bismo dobili $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Ako je bilo koji izlaz izvan raspona $[-2026, 2026]$, tada je $\mathrm{pointScore}(j) = 0$.
3. U suprotnom, izračunajte standardnu devijaciju $\sigma_j$ za $K$ izlaza i pretvorite je u rezultat:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

gdje je $s_E > 0$ fiksna konstanta skaliranja.

Rezultat regije je prosjek za sve tačke u regiji:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

gdje je $N_E = K * N_R$. 

Jednostavno rečeno, što je veća raznolikost, to će vaš rezultat za ovu regiju biti veći. **Ne možete koristiti slučajnost u čistom obliku, uključujući PyTorch funkcije `rand*` i `_uniform`; slučajnost treba proizlaziti iz inferencije s omogućenim dropoutom.**

## Kako predati rješenje

1. Otvorite `solution.ipynb` i pokrenite sve ćelije.
2. Poboljšajte model `CustomModel` u `custom_model.py`
3. Pobrinite se da vaša posljednja ćelija sačuva model u datoteku `model.pt`.
4. U Git kartici JupyterLaba označite `solution.ipynb` i `custom_model.py` za commit, unesite komentar i izvršite commit, a zatim ih pushajte.
5. Vratite se na stranicu takmičenja i kliknite **Predaj**. Komentar predaje treba biti isti kao komentar iz prethodnog koraka.
