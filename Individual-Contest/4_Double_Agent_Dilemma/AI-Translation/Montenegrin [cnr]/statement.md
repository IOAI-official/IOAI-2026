# Dilema dvostrukog agenta

- **Vremensko ograničenje:** 12 minuta.
- **Prostor za skladištenje:** 5 GB
- **Okruženje:** jedan GPU (≈16 GB VRAM), bez interneta
- **Veličina rješenja:** `solution.ipynb` ≤ 1 MB
- **Baseline rezultat:** 0 
- **Rezultat Naučnog komiteta:** 96.99 

U nacionalnom centru za vještačku inteligenciju u Astani, dva računarska modela — Model R (ResNet-18) i Model V (ViT-Tiny) — analiziraju fotografije. Trenutno oba modela rade savršeno, ostvarujući tačnost od 100% i slažući se za svaku pojedinačnu sliku. Kako bi ispitao koliko se njihovi pametni „mozgovi“ zaista razlikuju, glavni naučnik vam zadaje izazov: napravite sitne, gotovo nevidljive izmjene piksela na svakoj fotografiji tako da se Model R i Model V u potpunosti ne slažu.

![slika](../../dilemma.jpg)

## 1. Zadatak

Dva pretrenirana klasifikatora slika posmatraju istu sliku. Na slikama datim u ovom zadatku oba klasifikatora postižu tačnost od 100%.

- **Model R**: `torchvision.models.resnet18` (CNN, ResNet18).
- **Model V**: `timm`-ov `vit_tiny_patch16_224` (Transformer, ViT-Tiny).

Vaš zadatak je da napravite malu izmjenu („perturbaciju“) za svaku sliku tako da se dva modela ne slažu. Za svaku sliku morate napraviti **dvije različite** perturbacije:

- **Tip A**: nakon njenog dodavanja, Model R i dalje ispravno klasifikuje sliku, ali je Model V klasifikuje pogrešno.
- **Tip B**: nakon njenog dodavanja, Model V i dalje ispravno klasifikuje sliku, ali je Model R klasifikuje pogrešno.

Svaka perturbacija mora biti dovoljno *mala* da ju je teško primijetiti. Manje perturbacije donose veći rezultat (vidjeti Odjeljak 5). Perturbacija se primjenjuje direktno na originalnu sliku, na nivou piksela.

## 2. Javni podaci

Uz zadatak je dat skup slika, organizovan u dva podskupa — `train` (100 slika) i
`test_public` (100 slika) — od kojih svaki sadrži slike različitih rezolucija. Sve slike pripadaju 1000 klasa dataseta ImageNet-1K, a Model R i Model V postižu tačnost od 100% na oba podskupa.

Date su sljedeće datoteke:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Tokom ocjenjivanja, vaš folder `dataset/test_public/` se automatski zamjenjuje sa dva skrivena skupa slika (`test_leaderboard_a` i `test_leaderboard_b`) radi zvaničnog bodovanja. Svaki od njih sadrži **100 slika** u PNG formatu i datoteku sa oznakama. 

**Napomena: Za ovaj zadatak oznake u testnim datasetima su dostupne.**

## 3. Format izlaza

Za svaku sliku morate proizvesti dvije datoteke:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), odgovara nazivu slike u datasetima.
- Svaka datoteka je jedan tenzor sačuvan pomoću `torch.save`. Njegov oblik mora biti`3 x H x W`, pri čemu `H` i `W` odgovaraju **originalnoj** rezoluciji te slike (ne `224 x 224`).
- Kod treba da proizvede samo jednu ZIP datoteku, `submission.zip`. Smjestite sve `.pt` datoteke na najviši nivo ZIP arhive, bez foldera koji ih obuhvata ili poddirektorijuma. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Notebook će vas upozoriti ako postoji bilo kakvi problemi sa formatom izlaza.

## 4. Ograničenja

- **Modeli:** Morate koristiti `torchvision.models.resnet18(pretrained=True)` i `timm.create_model('vit_tiny_patch16_224', pretrained=True)`. Nijedan drugi pretrenirani model nije dozvoljen.
- **Tok transformacija (primjenjuje se pri evaluaciji):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. See Section 3 of `baseline.ipynb` za detalje. 
- **Rezolucija perturbacije:** Mora odgovarati **originalnoj** rezoluciji neobrađene slike (ne 224×224). Tenzor se
  dodaje neobrađenoj slici *prije* toka transformacija.
- **Format izlaza:** Samo `.pt` datoteke — bez PNG/JPG . Tenzori se dodaju neobrađenoj slici, a vrijednosti piksela se ograničavaju na `[0, 1]` prije pretprocesiranja.
- **Imenovanje datoteka:** Sve datoteke na jednom nivou, u strogom formatu `{index}_a.pt` / `{index}_b.pt`. Bez poddirektorijuma unutar zip arhive.
- **Biblioteke:** `torch`, `torchvision`, `timm`. 

## 5. Bodovanje

Konačni rezultat se izračunava na sljedeći način. Neka je `M` broj slika u podskupu, $Score_A$ broj uspješnih perturbacija tipa A, a $Score_B$ broj uspješnih perturbacija tipa B:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF je funkcija osmišljena da penalizuje perturbacije sa velikom normom i da bude veoma osjetljiva blizu gornje granice performansi. Ona ona je ograničena na opseg od 0.5 do 1. Cjelokupna implementacija može se vidjeti u Odjeljku  8 dokumenta `solution.ipynb`. 

![slika](../../curves.jpeg)
Slika: Kriva funkcije penalizacije.

## 6. Provjera predaje

U notebooku postoje provjere koje vas upozoravaju ako postoje problemi sa formatiranjem, u Odjeljku 7 notebooka `solution.ipynb`.

## 7. Lokalno testiranje

`solution.ipynb` sadrži potpun primjer koji radi. Učitava javne podatke, oba modela i zvanični program za bodovanje i kreira ZIP datoteku za predaju. Pročitajte ga prije nego što počnete.

## 8. Kako predati

- Sačuvajte svoje izmjene u `solution.ipynb`.
- Otvorite karticu Git na lijevoj bočnoj traci u JupyterLab-u.
- Izvršite **Stage** za `solution.ipynb` (ikona + pored njega).
- Unesite poruku commita i kliknite na **Commit**.
- Kliknite na oblak sa strelicom nagore da biste izvršili push.
- Vratite se na ovu stranicu takmičenja i kliknite na **Submit**.

Predajte tačno jednu datoteku, nazvanu `solution.ipynb`.
