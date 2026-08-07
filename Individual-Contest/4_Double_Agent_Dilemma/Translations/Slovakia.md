# Dilema dvojitého agenta

- **Časový limit:** 12 minút
- **Úložisko:** 5 GB
- **Prostredie:** jedna GPU (≈16 GB VRAM), bez internetu
- **Veľkosť riešenia:** `solution.ipynb` ≤ 1 MB
- **Baseline skóre:** 0 

V národnom centre AI v Astane analyzujú fotografie dva počítačové modely — Model R (ResNet-18) a Model V (ViT-Tiny). V súčasnosti oba modely pracujú bezchybne, dosahujú presnosť 100% a zhodujú sa pri každom jednom obrázku. Aby hlavný vedec otestoval, nakoľko sa ich inteligentné „mozgy“ skutočne líšia, zadá vám výzvu: vykonajte v každej fotografii nepatrné, takmer neviditeľné zmeny pixelov tak, aby sa Model R a Model V vôbec nezhodovali.

![obrázok](../dilemma.jpg)

## 1. Úloha

Dva predtrénované klasifikátory obrázkov posudzujú rovnaký obrázok. Na obrázkoch poskytnutých v tejto úlohe dosahujú oba klasifikátory presnosť 100%.

- **Model R**: `torchvision.models.resnet18` (CNN, ResNet18).
- **Model V**: `timm`-ov `vit_tiny_patch16_224` (Transformer, ViT-Tiny).

Vašou úlohou je vytvoriť pre každý obrázok malú zmenu („perturbáciu“) tak, aby sa tieto dva modely nezhodovali. Pre každý obrázok musíte vytvoriť **dve rôzne** perturbácie:

- **Typ A**: po jej pridaní Model R naďalej klasifikuje obrázok správne, ale Model V ho klasifikuje nesprávne.
- **Typ B**: po jej pridaní Model V naďalej klasifikuje obrázok správne, ale Model R ho klasifikuje nesprávne.

Každá perturbácia musí byť dostatočne *malá*, aby ju bolo ťažké postrehnúť. Menšie perturbácie získajú vyššie skóre (pozri časť 5). Perturbácia sa aplikuje priamo na pôvodný obrázok na úrovni pixelov.

## 2. Verejné dáta

S úlohou je poskytnutá množina obrázkov rozdelená na dve časti — `train` (100 obrázkov) a
`test_public` (100 obrázkov) — pričom obsahuje obrázky s rôznym rozlíšením. Všetky obrázky pochádzajú z 1000 tried ImageNet-1K a Model R aj Model V dosahujú v oboch častiach presnosť 100%.

Poskytnuté sú tieto súbory:

```text
train/images/*.png         # 100 images in PNG format
train/labels.json          # maps each image index to its correct class
test_public/images/*.png   # 100 images in PNG format
test_public/labels.json    # maps each image index to its correct class
```

Počas vyhodnocovania sa váš priečinok `dataset/test_public/` transparentne nahradí dvoma skrytými množinami obrázkov (`test_leaderboard_a` a `test_leaderboard_b`) určenými na oficiálne bodovanie. Každá z nich obsahuje **100 obrázkov** vo formáte PNG a súbor s anotáciami. 

**Poznámka: V tejto úlohe sú anotácie v testovacích datasetoch prístupné.**

## 3. Výstupný formát

Pre každý obrázok musíte vytvoriť dva súbory:

```text
{index}_a.pt   # Type A perturbation
{index}_b.pt   # Type B perturbation
```

- `{index}` (`0`, `1`, `2`, ...), zodpovedá názvu obrázka v datasetoch.
- Každý súbor je jeden tenzor uložený pomocou `torch.save`. Jeho tvar musí byť`3 x H x W`, pričom `H` a `W` zodpovedajú **pôvodnému** rozlíšeniu daného obrázka (nie `224 x 224`).
- Kód má vytvoriť iba jeden súbor ZIP, `submission.zip`. Všetky súbory `.pt` umiestnite na najvyššiu úroveň archívu ZIP bez nadradeného priečinka alebo podpriečinkov. 

```text
submission.zip
├── 0_a.pt
├── 0_b.pt
└── 1_a.pt
└── ...
```

Notebook vás upozorní, ak sa vo výstupnom formáte vyskytnú akékoľvek problémy.

## 4. Obmedzenia

- **Modely:** Musíte použiť `torchvision.models.resnet18(pretrained=True)` a `timm.create_model('vit_tiny_patch16_224', pretrained=True)`. Žiadne iné predtrénované modely nie sú povolené.
- **Transformačný pipeline (vynútený pri vyhodnocovaní):** `Resize(256) → CenterCrop(224) →
  Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])`. Časť 3 súboru `baseline.ipynb` obsahuje podrobnosti. 
- **Rozlíšenie perturbácie:** Musí zodpovedať **pôvodnému** rozlíšeniu nespracovaného obrázka (nie 224×224). Tenzor sa
  pridá k nespracovanému obrázku *pred* transformačným pipeline.
- **Výstupný formát:** Iba súbory `.pt` — žiadne PNG/JPG . Tenzory sa pridajú k obrázku (normalizovanému do rozsahu `[0,1]`) a potom sa hodnoty pixelov pred predspracovaním orežú na `[0, 1]`.
- **Názvy súborov:** Uložené len súbory s názvami `{index}_a.pt` / `{index}_b.pt`. V súbore zip nesmú byť žiadne podpriečinky.
- **Knižnice:** `torch`, `torchvision`, `timm`. 

## 5. Bodovanie

Konečné skóre sa vypočíta takto. Nech `M` je počet obrázkov v danej časti, $Score_A$ počet úspešných perturbácií typu A a $Score_B$ počet úspešných perturbácií typu B:
$$
S_{final} = \frac{Score_A + Score_B}{2M} \times PF
$$

PF je funkcia navrhnutá tak, aby penalizovala perturbácie s vysokou normou a bola veľmi citlivá v blízkosti maxima výkonu. Je ohraničená na rozsah 0.5 až 1. Úplnú implementáciu možno nájsť v časti  8 súboru `solution.ipynb`. 

![obrázok](../curves.jpeg)
Obrázok: Krivka penalizačnej funkcie.

## 6. Kontrola odovzdania

Notebook obsahuje kontroly, ktoré vás upozornia na problémy s formátovaním, v časti 7 notebooku `solution.ipynb`.

## 7. Lokálne testovanie

Súbor `solution.ipynb` obsahuje úplný a funkčný príklad. Načíta verejné dáta, oba modely a oficiálny hodnotiaci nástroj a zapíše súbor ZIP na odovzdanie. Pred začatím si ho prečítajte.

## 8. Ako odovzdať riešenie

- Uložte svoje zmeny do `solution.ipynb`.
- Otvorte kartu Git v ľavom bočnom paneli JupyterLab.
- **Pridajte do stage** `solution.ipynb` (ikona + vedľa neho).
- Zadajte označenie commitu a kliknite na **Commit**.
- Kliknutím na ikonu oblaku so šípkou nahor vykonajte push.
- Vráťte sa na túto stránku súťaže a kliknite na **Submit**.

Odovzdajte presne jeden súbor s názvom `solution.ipynb`.
