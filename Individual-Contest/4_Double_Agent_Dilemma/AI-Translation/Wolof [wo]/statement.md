# Jafe-jafey Ajan bu Ñaari Kanam

- **Limitu waxtu:** 12 minutes.
- **Dencukaay:** 5 GB
- **Environnement:** benn GPU (≈16 GB VRAM), internet amul
- **Dayo solution bi:** `solution.ipynb` ≤ 1 MB
- **Baseline score:** 0 
- **Score bu Kurélu Xam-xam:** 96.99 

Ci AI center bu réew mi nekk Astana, ñaari computer model — Model R (ResNet-18) ak Model V (ViT-Tiny) — ñoo ngay seet ay nataal. Léegi, ñaari model yi ñoo ngi def liggéey bu mat sëkk, am 100% accuracy te dëppoo ci bépp nataal. Ngir seet ba xam ni seen “xel” yu muus yi wuute, kilifag xam-xam bi jox na la jafe-jafe bii: def ay coppite yu ndaw ci pixel yi, yu jege a bañ a feeñ, ci bépp nataal, ba Model R ak Model V dëppoo wuñu mukk.

![nataal](../../dilemma.jpg)

## 1. Liggéey bi

Ñaari image classifier yu ñu pretrained ñoo xool benn nataal bi. Ci nataal yi ñu joxe ci liggéey bii, ñaari classifier yi yépp dañuy liggéey ak 100% accuracy.

- **Model R**: `torchvision.models.resnet18` (CNN, ResNet18).
- **Model V**: `vit_tiny_patch16_224` bu `timm` (Transformer, ViT-Tiny).

Sa liggéey mooy sos coppite bu ndaw (“perturbation”) ci bépp nataal, ba ñaari model yi dëppoo wuñu. Ci bépp nataal, fàww nga sos **ñaari** perturbation yu wuute:

- **Xeetu A**: gannaaw bi ñu ko yokkee, Model R dafay wéy di classifie nataal bi ci anam gu jub, waaye Model V dafay classifie ko ci anam gu jubul.
- **Xeetu B**: gannaaw bi ñu ko yokkee, Model V dafay wéy di classifie nataal bi ci anam gu jub, waaye Model R dafay classifie ko ci anam gu jubul.

Fàww bépp perturbation *ndaw* doy ba mu jafe a gis. Perturbation yu gën a ndaw dañuy am score bu gën a kawe (xool Section 5). Ñuy jëfandikoo perturbation bi ci nataal bu njëkk bi, ci pixel level bi ci boppam.

## 2. Public data

Ñu joxe nañu ak liggéey bi ab kuréel nataal, te ñu séddale ko ci ñaari split — `train` (100 images) ak
`test_public` (100 images) — te ci bu nekk am na nataal yu resolution yi wuute. Nataal yépp jóge nañu ci 1000 classes yu ImageNet-1K, te Model R ak Model V yépp am nañu 100% accuracy ci ñaari split yi.

Fichier yii lañu joxe:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Bu grading di am, ñuy wuutal sa folder `dataset/test_public/` ci anam wu transparent ak ñaari kuréel nataal yu nëbbu (`test_leaderboard_a` ak `test_leaderboard_b`) ngir scoring bu ofisel bi. Bu nekk am na **100 images** ci format PNG ak ab label file. 

**Seetal: Ci liggéey bii, manees na jot labels yi nekk ci test datasets yi.**

## 3. Format génne gi

Ci bépp nataal, fàww nga génne ñaari fichier:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), dafay méngoo ak turu nataal bi ci datasets yi.
- Bépp fichier benn tensor la bu ñu denc ak `torch.save`. Shape-am war na doon`3 x H x W`, te `H` ak `W` dañu wara méngoo ak resolution **original** bu nataal boobu (du `224 x 224`).
- Code bi war na génne benn ZIP file rekk, `submission.zip`. Teg bépp fichier `.pt` ci top level bu ZIP archive bi, te bañ cee am folder buy ëmb fichier yi walla subdirectory. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Notebook bi dina la yëgal su amee benn jafe-jafe ci format génne gi.

## 4. Ay tënk

- **Models:** Fàww nga jëfandikoo `torchvision.models.resnet18(pretrained=True)` ak `timm.create_model('vit_tiny_patch16_224', pretrained=True)`. Duñu may benn pretrained model bu dul yooyu.
- **Transform pipeline (ñu koy enforce ci evaluation bi):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` ngir yeneen leeral. 
- **Resolution bu perturbation bi:** Fàww mu méngoo ak resolution **original** bu raw image bi (du 224×224). Ñuy yokk tensor bi ci raw image bi *laata* transform pipeline bi.
- **Format génne gi:** Fichier `.pt` rekk — du PNG/JPG . Ñuy yokk tensors yi ci raw image bi, te ñuy dagg pixel values yi ba ñu des ci `[0, 1]` laata preprocessing.
- **Tuddinu fichier yi:** Flat-listed, te topp bu baax format `{index}_a.pt` / `{index}_b.pt`. Benn subdirectory warul nekk ci biir zip bi.
- **Libraries:** `torch`, `torchvision`, `timm`. 

## 5. Scoring

Nii lañuy xayma score bu mujj bi. Na `M` doon limu nataal yi ci split bi, $Score_A$ doon limu perturbation yu Xeetu A yi jàll, te $Score_B$ doon limu perturbation yu Xeetu B yi jàll:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF ab function la bu ñu def ngir penalise perturbation yi am norm bu kawe, te mu am sensitivity bu réy jege digg bu gën a kawe ci performance. Moom moom, ñu tëj ko ci diggante 0.5 ba 1. Mën nga gis implementation bi yépp ci Section  8 bu `solution.ipynb`. 

![nataal](../../curves.jpeg)
Nataal: Curve bu penalty function bi.

## 6. Seetal Submission bi

Am na ay checks ci notebook bi yuy la yëgal su amee jafe-jafe ci format bi, ci Section 7 bu notebook `solution.ipynb` bi.

## 7. Test ci sa ordinatëër

`solution.ipynb` am na misaal bu mat sëkk te di liggéey. Dafay load public data bi, ñaari model yi, ak official scorer bi, ba noppi bind ab submission ZIP file. Jàngal ko laata ngay tàmbali.

## 8. Naka lañuy submit

- Dencal say coppite ci `solution.ipynb`.
- Ubbi Git tab bi ci sidebar bu càmmooñ bu JupyterLab.
- **Stage** `solution.ipynb` (màndarga + bi nekk ci wetam).
- Bind ab commit message te bës **Commit**.
- Bës cloud bi ànd ak fitt buy jëm kaw ngir push.
- Dellu ci xëtu Contest bii te bës **Submit**.

Submit benn fichier rekk, bu tudd `solution.ipynb`.
