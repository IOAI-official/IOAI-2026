# IOAI polje

- **Vremensko ograničenje:** 5 minuta
- **Prostor za pohranu:** 5 GB
- **Veličina rješenja:** `solution.ipynb`, `custom_model.py` ≤ 1 MB zajedno
- **Unaprijed istrenirani modeli:** nisu dopušteni — treniranje od početka, bez interneta tijekom ocjenjivanja
- **Referentni rezultat**: 31.2187
- **Rezultat Znanstvenog odbora:** 63.53


## Zadatak

Gradonačelnik Astane želi ukrasiti grad stiliziranim logotipima IOAI-ja. Kao statističar, sve — uključujući logotip — promatra kao prostornu funkciju $F(x, y, \overline{W})$, gdje $x, y \in [0, 1]$ predstavljaju koordinate u 2D ravnini, a $\overline{W}$ skup je skrivenih parametara koji definiraju stilska svojstva poput boja i kutova slova.

Budući da je $F$ previše složena da bi se izrazila eksplicitnom matematičkom jednadžbom, vaš je zadatak istrenirati neuronsku mrežu koja će je aproksimirati. Mreža će za svaki par koordinata $(x, y)$ davati vrijednost **IOAI polja**, stvarajući potpunu vizualizaciju logotipa toplinskom kartom preko cijele ravnine. Slijedi primjer vizualizacije $F$ toplinskom kartom s određenim skrivenim parametrima $\overline{W}$.

![f1](../../ioai1.png)

Od čega se sastoji IOAI polje? Od četiriju slova i pozadine.

- Vrijednosti unutar prvog slova `I` vrlo su velike (1e+10 i više) te imaju linearni gradijent
- Vrijednosti u slovu `O` tvore spiralni uzorak
- Vrijednost unutar slova `A` uvijek je -1
- Vrijednosti unutar posljednjeg slova `I` trebaju biti slučajne vrijednosti iz raspona $[-2026,2026]$ čak i ako se ista točka evaluira dvaput
- Izvan slova vrijednost je uvijek nula

Funkcija ima skrivene parametre $\overline{W}$, koji utječu na veličinu i nagib slova, kao i na raspon vrijednosti unutar prvog slova `I`. Međutim, slova se neće presijecati. Slijedi nekoliko ilustrativnih primjera izgleda IOAI polja za različite $\overline{W}$:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Što vam je zadano:**

Ovaj zadatak NE sadržava skupove podataka. Umjesto toga, zadana vam je funkcija generatora koja se konfigurira JSON konfiguracijskom datotekom na `data/train_config/field_config.json`. 

Testna konfiguracija je skrivena, ali slične je prirode. Vaš je zadatak prilagoditi model zadanom generatoru koristeći onoliko podataka koliko želite. Vaše distribucije za „treniranje” i „testiranje” generiraju se istim generatorom — samo ne znate na kojim ćete točkama $(x_i, y_i)$ biti evaluirani.

Vaša predaja treba sadržavati:
- klasu modela za treniranje spremljenu kao `custom_model.py`. Ovaj model treba nasljeđivati klasu `torch.nn.Module` i koristiti samo importe iz `torch`. Treba sadržavati klasu `CustomModel` koja se koristi u bilježnici `solution.ipynb`. 
- bilježnicu `solution.ipynb`, koja će proizvesti težine `model.pt`


## Bodovanje

Za svaku regiju najmanji je rezultat 0, a najveći 1. Konačni rezultat dobiva se izračunavanjem prosjeka za svih pet regija (četiri za pojedina slova i jedna za pozadinu) i množenjem sa 100. Primjenjuje se **kazna za broj parametara:**

**Ako vaš model ima više od 20260 parametara, rezultat se prepolovljuje.**

Broj parametara mjeri se pomoću `sum(p.numel() for p in model.parameters())`. Očekujemo da vaš model radi i u stohastičkom načinu, pri čemu je PyTorch `nn.Dropout` dio modela.

### Za standardne regije

Za svaku regiju $R$ (prvo slovo `I`, `O`, `A`, `Background`) evaluiramo model na $N_R = 512$ testnih točaka $(x_i, y_i)$ sa stvarnim vrijednostima $v_i$ i predikcijama $\hat{v}_i$. Kao glavnu metriku koristimo normaliziranu srednju apsolutnu pogrešku (MAE). MAE je definirana kao:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

A normalizacija se provodi kao 

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

gdje je $s_R > 0$ konstanta skaliranja.


### Za regiju posljednjeg slova `I`

U ovoj je regiji **dropout omogućen tijekom evaluacije**. Za svaku testnu točku $j$:

1. Pokrećemo model $K = 10$ puta kako bismo dobili $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Ako je bilo koji izlaz izvan raspona $[-2026, 2026]$, tada $\mathrm{pointScore}(j) = 0$.
3. U suprotnom izračunavamo standardnu devijaciju $\sigma_j$ od $K$ izlaza i pretvaramo je u rezultat:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

gdje je $s_E > 0$ fiksna konstanta skaliranja.

Rezultat regije prosjek je po svim točkama u regiji:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

gdje $N_E = K * N_R$. 

Jednostavno rečeno, što je raznolikost veća, to će vaš rezultat za ovu regiju biti veći. **Ne smijete koristiti slučajnost u čistom obliku, uključujući PyTorch funkcije `rand*` i `_uniform`; slučajnost treba proizlaziti iz inferencije s omogućenim dropoutom.**

## Kako predati

1. Otvorite `solution.ipynb` i pokrenite sve ćelije.
2. Poboljšajte model `CustomModel` u `custom_model.py`
3. Pobrinite se da vaša posljednja ćelija spremi model u datoteku `model.pt`.
4. U Git kartici JupyterLaba dodajte `solution.ipynb` i `custom_model.py` u staging, unesite komentar i napravite commit, a zatim ih pushajte.
5. Vratite se na stranicu natjecanja i kliknite **Predaj**. Komentar predaje treba biti jednak komentaru iz prethodnog koraka.
