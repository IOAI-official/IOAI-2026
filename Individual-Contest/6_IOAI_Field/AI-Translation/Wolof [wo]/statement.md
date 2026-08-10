# IOAI field

- **Diggante waxtu:** 5 minutes
- **Dencukaay:** 5 GB
- **Dayo solution bi:** `solution.ipynb`, `custom_model.py` ≤ 1 MB ñoom ñaar
- **Pretrained models:** amul — train ko dale ko ci dara, internet du am ci waxtu not bi
- **Baseline Score**: 31.2187
- **Score bu Scientific Committee bi:** 63.53


## Liggéey bi

Meeru Astana bëgg na rafetal dëkk bi ak ay logo IOAI yu ñu defare ci style. Ndegam statistician la, lépp—ba ci logo bi—daf koy jàppe ni fonction spatiale $F(x, y, \overline{W})$, féete bu $x, y \in [0, 1]$ di coordinates ci 2D plane te $\overline{W}$ di set bu hidden parameters yiy määnaale ay stylistic attributes yu mel ni melo yi ak angles yi.

Ndegam $F$ dafa jafee lool ba kenn mënu koo bind ci mathematical equation bu leer, sa liggéey mooy train neural network ngir mu approximater ko. Network bi dina génne valeur **IOAI field** ci bépp coordinate pair $(x, y)$, ba sos heatmap visualization bu mat sëkk bu logo bi ci plane bi bépp. Lii ab misaalu heatmap visualization la bu $F$ ak yenn hidden parameters $\overline{W}$ yuñu tànn.

![f1](../../ioai1.png)

Lan moo bokk ci IOAI field bi? Ñeenti araf ak background bi.

- Valeurs yi nekk ci araf `I` bu njëkk bi dañoo réy lool (1e+10 ak lu ko ëpp), te am gradient linéaire
- Valeurs yi nekk ci araf `O` dañuy wone motif spiral
- Valeur bi nekk ci araf `A` mooy -1 saa su nekk
- Valeurs yi nekk ci araf `I` bu mujj bi war nañu nekk random values yu jóge ci range $[-2026,2026]$, sax su ñu ko evaluate ci benn point bi ñaari yoon
- Ci biti araf yi, valeur bi mooy zero saa su nekk

Function bi am na hidden parameters $\overline{W}$, yuy soppi scale ak incline araf yi, ak it range bu valeurs yi ci araf `I` bu njëkk bi. Waaye araf yi duñu daje. Yii ay misaal lañu yuy wone ni IOAI field bi mel ak $\overline{W}$ yu wuute:

![f2](../../ioai2.png)
![f3](../../ioai3.png)

**Li ñu la jox:**

Problem bii amul benn dataset. Waaye, ñu jox nañu la generator function bi nga xam ne JSON config file bi nekk ci `data/train_config/field_config.json` moo ko configure. 

Test config bi nëbbu na, waaye melokaanam jege na bii. Sa liggéey mooy fit ci generator bi ñu la jox, te jëfandikoo data bu bare ni nga bëgge. Sa distributions yu "train" ak "test" dañuy jóge ci benn generator bi — xamuloo rekk ci ban points $(x_i, y_i)$ lañu lay evaluate.

Sa submission war na ëmb:
- training model class bu ñu save ni `custom_model.py`. Model bii war na inherit ci class `torch.nn.Module` te jëfandikoo rekk imports yu `torch`. War na ëmb class `CustomModel` bi ñuy jëfandikoo ci notebook `solution.ipynb`. 
- notebook `solution.ipynb`, buy génne weights `model.pt`


## Not bi

Ci bépp region, score bi gën a néew mooy 0 te score bi gën a kawe mooy 1. Score bu mujj bi mooy moyenne bu juróomi regions yépp (ñeent, benn ci bépp araf, ak background bi), ba noppi ñu multiply ko ak 100. Am na **parameter penalty:**

**Su sa model amee lu ëpp 20260 parameters, ñu dinañu xaaj score bi ñaar.**

Ñuy natt limu parameter yi ak `sum(p.numel() for p in model.parameters())`. Yaakaar nanu sa model bi dina dox itam ci stochastic mode, te PyTorch `nn.Dropout` bokk ci model bi.

### Ngir Standard Regions yi

Ci bépp region $R$ (araf `I` bu njëkk bi, `O`, `A`, `Background`), danuy evaluate model bi ci test points $N_R = 512$, maanaam $(x_i, y_i)$, ak true values $v_i$ ak predictions $\hat{v}_i$. Danuy jëfandikoo normalized Mean Absolute Error (MAE) ni metric bi gën a am solo. Ni ñuy définir MAE mooy:

$$
\mathrm{MAE}(R) = \frac{1}{N_R} \sum_{i=1}^{N_R} |\hat{v}_i - v_i|.
$$

Te normalization bi ñu koy def nii:

$$
\mathrm{score}(R) = 1 - \min\left(\frac{\mathrm{MAE}(R)}{s_R}, 1\right),
$$

féete bu $s_R > 0$ di scale constant.


### Ngir region bu araf `I` bu mujj bi

Ci region bii, **dropout bi enable nañu ko ci evaluation bi**. Ci bépp test point $j$:

1. Danuy doxal model bi $K = 10$ yoon ngir jot $\hat{v}_{j,1}, \ldots, \hat{v}_{j,K}$.
2. Su benn output génnee ci range $[-2026, 2026]$, kon $\mathrm{pointScore}(j) = 0$.
3. Lu ko moy, ñu compute standard deviation $\sigma_j$ bu outputs $K$ yi, ba noppi soppi ko score:

$$
\mathrm{pointScore}(j) = \min\left(\frac{\sigma_j}{s_E}, 1\right),
$$

féete bu $s_E > 0$ di fixed scale constant.

Score bu region bi mooy moyenne ci points yépp yu nekk ci region bi:

$$
\mathrm{score}(I_{last}) = \frac{1}{N_E} \sum_{j=1}^{N_E} \mathrm{pointScore}(j),
$$

féete bu $N_E = K * N_R$. 

Ci wax ju yomb, saa su diversity bi gënee bare, score bi nga am ci region bii dina gën a kawe. **Mënuloo jëfandikoo random ci anam gu sell, ba ci PyTorch functions `rand*` ak `_uniform`; randomness bi war na jóge ci inference bi dropout enable.**

## Ni ñuy submit

1. Ubbi `solution.ipynb` te doxal cells yépp.
2. Gënal model `CustomModel` bi ci `custom_model.py`
3. Wóorlu ne sa cell bu mujj bi dafay save sa model bi ci file `model.pt`.
4. Ci JupyterLab Git tab bi, stage, bind comment te commit `solution.ipynb` ak `custom_model.py`, ba noppi nga push ko.
5. Dellu ci Contest page bi te bës **Submit**. Submit comment bi war na doon benn ak comment bi ci jéego bi ko jiitu.
