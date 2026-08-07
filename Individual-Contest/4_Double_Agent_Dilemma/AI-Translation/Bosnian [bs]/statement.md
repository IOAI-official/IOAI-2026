# Dilema dvostrukog agenta

- **Vremensko ograničenje:** 12 minuta.
- **Prostor za pohranu:** 5 GB
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Osnovni rezultat:** 0 
- **Rezultat Naučnog odbora:** 96.99 

U nacionalnom centru za AI u Astani, dva računarska modela — Model R (ResNet-18) i Model V (ViT-Tiny) —analiziraju fotografije. Trenutno oba modela savršeno obavljaju posao, postižući tačnost od 100% i slažući se za svaku pojedinačnu sliku. Kako bi ispitao koliko su njihovi pametni „mozgovi“ zaista različiti, glavni naučnik daje vam izazov: napravite sitne, gotovo nevidljive izmjene piksela na svakoj fotografiji tako da se Model R i Model V u potpunosti ne slažu.

![slika](../../dilemma.jpg)

## 1. Zadatak

Dva unaprijed obučena klasifikatora slika posmatraju istu sliku. Na slikama datim u ovom zadatku oba klasifikatora postižu tačnost od 100%.

- **Model R**: `torchvision.models.resnet18` (CNN, ResNet18).
- **Model V**: `timm`-ov `vit_tiny_patch16_224` (Transformer, ViT-Tiny).

Vaš je zadatak napraviti malu izmjenu („perturbaciju“) za svaku sliku tako da se dva modela ne slažu. Za svaku sliku morate napraviti **dvije različite** perturbacije:

- **Tip A**: nakon njenog dodavanja, Model R i dalje ispravno klasificira sliku, ali je Model V klasificira neispravno.
- **Tip B**: nakon njenog dodavanja, Model V i dalje ispravno klasificira sliku, ali je Model R klasificira neispravno.

Svaka perturbacija mora biti dovoljno *mala* da ju je teško primijetiti. Manje perturbacije donose veći rezultat (pogledajte Odjeljak 5). Perturbacija se primjenjuje direktno na originalnu sliku na nivou piksela.

## 2. Javni podaci

Uz zadatak je dat skup slika, organiziran u dva podskupa — `train` (100 slika) i
`test_public` (100 slika) — od kojih svaki sadrži slike različitih rezolucija. Sve slike pripadaju 1000 klasa skupa ImageNet-1K, a i Model R i Model V postižu tačnost od 100% na oba podskupa.

Date su sljedeće datoteke:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Tokom ocjenjivanja, vaša fascikla `dataset/test_public/` neprimjetno se zamjenjuje s dva skrivena skupa slika (`test_leaderboard_a` i `test_leaderboard_b`) radi službenog bodovanja. Svaki od njih sadrži **100 slika** u PNG formatu i datoteku s oznakama. 

**Napomena: Za ovaj zadatak oznake u testnim skupovima podataka su dostupne.**

## 3. Izlazni format

Za svaku sliku morate proizvesti dvije datoteke:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), odgovara nazivu slike u skupovima podataka.
- Svaka datoteka predstavlja jedan tenzor sačuvan pomoću `torch.save`. Njegov oblik mora biti`3 x H x W`, pri čemu `H` i `W` odgovaraju **originalnoj** rezoluciji te slike (ne `224 x 224`).
- Kod treba proizvesti samo jednu ZIP datoteku, `submission.zip`. Smjestite sve datoteke `.pt` na najviši nivo ZIP arhive, bez obuhvatne fascikle ili poddirektorija. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Bilježnica će vas upozoriti ako postoji bilo kakvi problemi s izlaznim formatom.

## 4. Ograničenja

- **Modeli:** Morate koristiti `torchvision.models.resnet18(pretrained=True)` i `timm.create_model('vit_tiny_patch16_224', pretrained=True)`. Nisu dozvoljeni drugi unaprijed obučeni modeli.
- **Lanac transformacija (primjenjuje se pri evaluaciji):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` za detalje. 
- **Rezolucija perturbacije:** Mora odgovarati **originalnoj** rezoluciji neobrađene slike (ne 224×224). Tenzor se
  dodaje neobrađenoj slici *prije* lanca transformacija.
- **Izlazni format:** samo datoteke `.pt` — bez PNG/JPG . Tenzori se dodaju neobrađenoj slici, a vrijednosti piksela ograničavaju se na `[0, 1]` prije predobrade.
- **Imenovanje datoteka:** Ravna lista, strogi format `{index}_a.pt` / `{index}_b.pt`. Bez poddirektorija unutar zip arhive.
- **Biblioteke:** `torch`, `torchvision`, `timm`. 

## 5. Bodovanje

Konačni rezultat izračunava se na sljedeći način. Neka je `M` broj slika u podskupu, $Score_A$ broj uspješnih perturbacija Tipa A, a $Score_B$ broj uspješnih perturbacija Tipa B:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF je funkcija osmišljena da penalizira perturbacije s visokom normom i da bude veoma osjetljiva blizu gornje granice performansi. Ona je je ograničena na raspon od 0.5 do 1. Potpuna implementacija može se vidjeti u Odjeljku  8 dokumenta `solution.ipynb`. 

![slika](../../curves.jpeg)
Slika: Kriva funkcije penalizacije.

## 6. Provjera predaje

U bilježnici postoje provjere koje vas upozoravaju ako postoje problemi s formatiranjem, u Odjeljku 7 bilježnice `solution.ipynb`.

## 7. Lokalno testiranje

`solution.ipynb` sadrži potpun, funkcionalan primjer. Učitava javne podatke, oba modela i službeni program za bodovanje te zapisuje ZIP datoteku za predaju. Pročitajte ga prije nego što počnete.

## 8. Kako predati

- Sačuvajte svoje izmjene u `solution.ipynb`.
- Otvorite karticu Git u lijevoj bočnoj traci JupyterLaba.
- **Dodajte u pripremno područje** `solution.ipynb` (ikona + pored njega).
- Unesite poruku commita i kliknite **Commit**.
- Kliknite oblak sa strelicom prema gore kako biste izvršili push.
- Vratite se na ovu stranicu takmičenja i kliknite **Submit**.

Predajte tačno jednu datoteku, nazvanu `solution.ipynb`.
