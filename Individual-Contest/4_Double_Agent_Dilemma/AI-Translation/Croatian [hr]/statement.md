# Dilema dvostrukog agenta

- **Vremensko ograničenje:** 12 minutes.
- **Pohrana:** 5 GB
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Početni rezultat:** 0 
- **Rezultat Znanstvenog odbora:** 96.99 

U nacionalnom centru za umjetnu inteligenciju u Astani dva računalna modela — Model R (ResNet-18) i Model V (ViT-Tiny) — analiziraju fotografije. Trenutačno oba modela rade savršeno, postižući točnost od 100% i slažući se oko svake pojedine slike. Kako bi ispitao koliko su njihovi pametni „mozgovi” doista različiti, glavni znanstvenik daje vam izazov: napravite sitne, gotovo nevidljive promjene piksela na svakoj fotografiji tako da se Model R i Model V u potpunosti ne slažu.

![slika](../../dilemma.jpg)

## 1. Zadatak

Dva prethodno istrenirana klasifikatora slika promatraju istu sliku. Na slikama danima u ovom zadatku oba klasifikatora postižu točnost od 100%.

- **Model R**: `torchvision.models.resnet18` (CNN, ResNet18).
- **Model V**: `timm`ov `vit_tiny_patch16_224` (Transformer, ViT-Tiny).

Vaš je zadatak napraviti malu promjenu („perturbaciju”) za svaku sliku tako da se dva modela ne slažu. Za svaku sliku morate napraviti **dvije različite** perturbacije:

- **Tip A**: nakon njezina dodavanja Model R i dalje ispravno klasificira sliku, ali Model V klasificira je pogrešno.
- **Tip B**: nakon njezina dodavanja Model V i dalje ispravno klasificira sliku, ali Model R klasificira je pogrešno.

Svaka perturbacija mora biti dovoljno *mala* da ju je teško primijetiti. Manje perturbacije donose viši rezultat (vidjeti odjeljak 5). Perturbacija se primjenjuje izravno na izvornu sliku na razini piksela.

## 2. Javni podaci

Uz zadatak je dan skup slika organiziran u dva podskupa — `train` (100 images) i
`test_public` (100 images) — od kojih svaki sadrži slike različitih razlučivosti. Sve su slike iz 1000 klasa skupa ImageNet-1K, a i Model R i Model V postižu točnost od 100% na oba podskupa.

Dane su sljedeće datoteke:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Tijekom ocjenjivanja vaša mapa `dataset/test_public/` transparentno se zamjenjuje dvama skrivenim skupovima slika (`test_leaderboard_a` i `test_leaderboard_b`) za službeno bodovanje. Svaki od njih sadrži **100 images** u formatu PNG i datoteku s oznakama. 

**Napomena: Za ovaj su zadatak oznake u testnim skupovima podataka dostupne.**

## 3. Izlazni format

Za svaku sliku morate proizvesti dvije datoteke:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), odgovara nazivu slike u skupovima podataka.
- Svaka je datoteka jedan tenzor spremljen pomoću `torch.save`. Njegov oblik mora biti`3 x H x W`, pri čemu `H` i `W` odgovaraju **izvornoj** razlučivosti te slike (ne `224 x 224`).
- Kôd treba proizvesti samo jednu ZIP datoteku, `submission.zip`. Sve datoteke `.pt` smjestite na najvišu razinu ZIP arhive, bez obuhvatne mape ili poddirektorija. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Bilježnica će vas upozoriti ako postoje bilo kakvi problemi s izlaznim formatom.

## 4. Ograničenja

- **Modeli:** Morate upotrebljavati `torchvision.models.resnet18(pretrained=True)` i `timm.create_model('vit_tiny_patch16_224', pretrained=True)`. Nisu dopušteni drugi prethodno istrenirani modeli.
- **Slijed transformacija (primjenjuje se pri evaluaciji):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` za pojedinosti. 
- **Razlučivost perturbacije:** Mora odgovarati **izvornoj** razlučivosti neobrađene slike (ne 224×224). Tenzor se
  dodaje neobrađenoj slici *prije* slijeda transformacija.
- **Izlazni format:** samo datoteke `.pt` — bez PNG/JPG . Tenzori se dodaju neobrađenoj slici, a vrijednosti piksela ograničavaju se na `[0, 1]` prije predobrade.
- **Imenovanje datoteka:** Sve datoteke na jednoj razini, strogi format `{index}_a.pt` / `{index}_b.pt`. Bez poddirektorija unutar zip arhive.
- **Biblioteke:** `torch`, `torchvision`, `timm`. 

## 5. Bodovanje

Konačni rezultat računa se na sljedeći način. Neka je `M` broj slika u podskupu, $Score_A$ broj uspješnih perturbacija tipa A, a $Score_B$ broj uspješnih perturbacija tipa B:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF je funkcija osmišljena za penaliziranje perturbacija s velikom normom i vrlo je osjetljiva blizu gornje granice performansi. Ona je je ograničena na raspon od 0.5 do 1. Potpuna implementacija može se vidjeti u odjeljku  8 datoteke `solution.ipynb`. 

![slika](../../curves.jpeg)
Slika: Krivulja funkcije penalizacije.

## 6. Provjera predaje

U bilježnici postoje provjere koje vas upozoravaju ako postoje problemi s formatiranjem, u odjeljku 7 bilježnice `solution.ipynb`.

## 7. Lokalno testiranje

`solution.ipynb` sadrži potpun, funkcionalan primjer. Učitava javne podatke, oba modela i službeni sustav bodovanja te zapisuje ZIP datoteku za predaju. Pročitajte ga prije nego što počnete.

## 8. Kako predati

- Spremite svoje promjene u `solution.ipynb`.
- Otvorite karticu Git na liječnoj bočnoj traci sučelja JupyterLab.
- Označite `solution.ipynb` za pripremu (**Stage**) (ikona + pokraj njega).
- Unesite poruku commita i kliknite **Commit**.
- Kliknite ikonu oblaka sa strelicom prema gore kako biste izvršili push.
- Vratite se na ovu stranicu natjecanja i kliknite **Submit**.

Predajte točno jednu datoteku nazvanu `solution.ipynb`.
