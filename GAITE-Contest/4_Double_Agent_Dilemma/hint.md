# 5 Progressive Hints for the Double Agent Dilemma

---

## Before You Start — The Image Processing Pipeline

Before writing any attack, you must understand how images flow through the system.
This pipeline is fixed and used by the grader — your perturbation must survive it.

### Step-by-step

```python
# 1. Load the raw image (varies in size, e.g. 500x375)
img = TF.to_tensor(Image.open(path).convert("RGB"))   # shape: (3, H, W)

# 2. Add your perturbation BEFORE any processing
adv = torch.clamp(img + delta, 0, 1)                   # keep pixels in [0, 1]

# 3. The grader then applies this EXACT pipeline:
#    Resize(256) -> CenterCrop(224) -> Normalize
x = TF.resize(adv, size=256)
x = TF.center_crop(x, 224)
x = (x - mean) / std
#    mean = [0.485, 0.456, 0.406], std = [0.229, 0.224, 0.225]

# 4. Feed to both models
out_r = resnet(x.unsqueeze(0))
out_v = vit(x.unsqueeze(0))
```

### Why this matters

- **Perturbation at original resolution**: `delta` must be `(3, H, W)` — the raw image size, not 224x224. The resize/crop happens *after* the perturbation is added.
- **Pixel range**: Perturbed image must stay in `[0, 1]`. Always `clamp` after adding delta.
- **TF.resize keeps aspect ratio**: Unlike `F.interpolate`, `TF.resize` preserves proportions. A 500x375 image becomes 341x256 (not 256x256).
- **Normalization is fixed**: You don't change it. The models were trained with these exact values.

> **Where to look**: The full pipeline code is in `solution.ipynb`, **Section 3** ("The Image Processing Process"). The `preprocess()` function there is exactly what the grader runs.

### Data layout

```
train/images/0000.png ... 0099.png    # 100 images, varying resolutions
train/labels.json                      # { "0": 160, "1": 439, ... }
test/images/0000.png ... 0099.png      # 100 images
test/labels.json
```

> **Where to look**: Data loading is in `solution.ipynb`, **Section 2** ("Load the data"). The `load_split()` function handles the folder structure.

---

## Hint 1 — Read, Mask, Test, Repeat

**Key idea:** Before writing any optimizer, try the simplest thing — just *hide* part of the image and see what happens.

CNN and ViT look at images very differently. If you zero out (black out) a region, one model may become confused while the other stays correct. This is the core insight behind all mask-based attacks.

**Basic workflow for one image:**

```python
img = TF.to_tensor(Image.open(path).convert("RGB"))   # shape: (3, H, W)
mask = torch.ones_like(img)                            # start all-white
mask[:, y0:y0+h, x0:x0+w] = 0                         # black-out a rectangle
delta = img * mask - img                                # perturbation = what we removed
adv = torch.clamp(img + delta, 0, 1)                  # apply & clamp
```

Feed `adv` through `preprocess()` → both models. If ResNet is still correct but ViT is wrong — you just found a Type A perturbation.

**To search efficiently**, slide the mask across the image at different positions and sizes. Try square masks (e.g., 64x64, 90x90, 128x128) near the center, edges, and corners. The `for` loop is your friend here — no gradients needed yet.

> **Why it works:** CNN uses local features; masking a small region can disrupt ViT's global attention without destroying CNN's local patterns (or vice versa).
>
> **In `solution.ipynb`**: See **Section 5** for how the Solution class is structured. Your mask search replaces the `_attack()` method.

---

## Hint 2 — Target the Right Model

**Key idea:** Not all mask positions work equally well. You need to find positions where the *fool* model breaks but the *keep* model survives.

For **Type A** (keep CNN, fool ViT), you want regions where ViT depends heavily but CNN does not. A simple heuristic: try larger masks for ViT (it needs global context) and smaller masks for CNN (it relies on local texture).

```python
# Type A: fool ViT, keep CNN
for y0, x0, size in candidate_positions:
    mask[:, y0:y0+size, x0:x0+size] = 0
    delta = img * mask - img          # perturbation = what we removed
    if cnn_correct(img+delta) and not vit_correct(img+delta):
        return delta                  # success!
```

**Pro tips:**
- Pre-compute both model predictions on the clean image once.
- If a mask breaks *both* models, try a smaller mask or a different position.
- If nothing works with pure black, try replacing the masked region with the image mean color or random noise instead of zero.

> **Why this matters:** Before moving to gradient-based attacks (Hints 3–5), understanding mask search builds intuition about *where* each model is vulnerable.
>
> **In `solution.ipynb`**: After modifying Section 5, run the train smoke test in **Section 6** to quickly check your score on 20 images.

---

## Hint 3 — Replace the Loop with a Loss Function

**Key idea:** Instead of brute-force searching mask positions, let gradients guide you. Make the perturbation a *trainable tensor* and use `torch.optim`.

The loss has two parts pulling in opposite directions:

```python
delta = torch.zeros_like(img, requires_grad=True)
optimizer = torch.optim.Adam([delta], lr=0.01)

loss = CE(keep_model(img + delta), true_label)    # make keep model stay correct
     - CE(fool_model(img + delta), true_label)    # make fool model get wrong
```

`CE` is `F.cross_entropy`. The first term *minimizes* cross-entropy for the keep model (help it stay correct). The second term *maximizes* cross-entropy for the fool model (push it toward wrong predictions) — notice the minus sign.

```python
for step in range(50):
    optimizer.zero_grad()
    adv = torch.clamp(img + delta, 0, 1)           # keep pixels valid
    out_keep = keep_model(preprocess(adv))
    out_fool = fool_model(preprocess(adv))
    
    if out_keep.argmax() == label and out_fool.argmax() != label:
        break                                       # early stop on success!
    
    loss = F.cross_entropy(out_keep, target) - F.cross_entropy(out_fool, target)
    loss.backward()
    optimizer.step()
```

> **Why it's better:** Adam finds a perturbation in milliseconds that might take thousands of random mask guesses. The gradient tells you *exactly* which pixels to change and in which direction.
>
> **In `solution.ipynb`**: The `preprocess()` function you call is defined in **Section 3**. The models (`resnet`, `vit`) are loaded there too — reuse them, don't reload.

---

## Hint 4 — Tune the Loss: Separation is Everything

**Key idea:** The core challenge is *differential* fooling — you need one model to break while the other stays intact. The loss function is your main lever for controlling this balance.

**Loss design options:**

| Strategy | Loss formula | When to use |
|----------|-------------|-------------|
| Balanced | `CE(keep) - CE(fool)` | Default, works well for most images |
| Keep-heavy | `2*CE(keep) - CE(fool)` | When keep model also starts getting wrong |
| Fool-heavy | `CE(keep) - 2*CE(fool)` | When fool model is hard to break |
| Margin | `max(0, CE(keep) - CE(fool) + margin)` | When you want a minimum confidence gap |

**Learning rate matters.** Start with `lr=0.01`. If the loss oscillates (goes up and down), halve it. If it barely moves, double it.

**Early stopping is critical.** The moment both conditions are met (keep correct AND fool wrong), save `delta` and stop. Continuing further only increases the perturbation size without benefit:

```python
if keep_correct and fool_wrong:
    return delta.detach()    # stop immediately — it's already good!
```

> **Why this matters:** The perfect loss function finds a perturbation at the exact boundary between the two models' decision regions. This minimizes L2 norm naturally because you stop as soon as you cross the boundary.
>
> **In `solution.ipynb`**: Run **Section 6** on the train split to tune your parameters. When ready, run on the full test split to see your leaderboard-equivalent score.

---

## Hint 5 — Constrain the Perturbation Size

**Key idea:** Pure Score measures *whether* you succeed. The Penalty Factor (PF) measures *how small* your perturbation is. A successful attack with a large perturbation gets a low final score. You need to win AND stay quiet.

**Method 1: L-infinity clamping (simplest)**

After each optimizer step, clip delta to a small range:

```python
with torch.no_grad():
    delta.clamp_(-epsilon, epsilon)     # e.g., epsilon = 0.002 to 0.005
```

This guarantees every pixel changes by at most `epsilon`. Smaller epsilon = lower L2 but harder to succeed. Try ε = 0.005 first, then reduce to 0.002 if your Pure Score is already high.

**Method 2: L2 penalty in the loss (more controllable)**

Add an L2 term that pushes the perturbation toward zero:

```python
loss = CE(keep) - CE(fool) + lambda_l2 * delta.norm(p=2)
```

Start with `lambda_l2 = 5.0`. This adds a "cost" for large perturbations. The gradient from `delta.norm(p=2)` is `delta / ||delta||_2` — it pulls every pixel proportionally toward zero.

**Method 3: Post-success compression (advanced)**

After you find a successful perturbation, continue optimizing with *only* the L2 term:

```python
if success_found:
    loss = delta.norm(p=2)    # ignore CE, just shrink
```

Record the smallest-L2 delta that still works. This is how the best solutions squeeze out every last bit of PF.

**How the math connects:** Your PF uses `μ_norm = mean(||δ||₂ / N_pixels)`. With ε=0.005, a fully saturated perturbation has μ_norm ≈ 0.003 → PF ≈ 0.5 (half score). With good L2 control, μ_norm ≈ 1e-6 → PF ≈ 0.98. That's the difference between a score of 0.50 and 0.98 — entirely from managing perturbation size.

> **In `solution.ipynb`**: Before submitting, run **Section 8** ("Evaluate locally") to see your exact Pure Score, L2/px, PF, and Final Score. Then run **Section 9** to build `submission.zip`.

---

## Summary: Your Progression Path

| Hint | What you learn | Typical score | Key `solution.ipynb` section |
|------|---------------|---------------|------------------------------|
| 1–2 | Mask search — brute-force grid | ~0.15–0.30 | §3 (preprocess), §5 (attack), §6 (run) |
| 3 | Adam optimization — gradient-guided | ~0.50–0.70 | §3 (models), §5 (attack), §6 (run) |
| 4 | Loss tuning — separation control | ~0.80–0.87 | §6 (tune), §7 (check) |
| 5 | Norm control — clamping + L2 penalty | ~0.90–0.97 | §8 (evaluate), §9 (zip) |

### solution.ipynb structure reference

| Section | What's inside | Use it to... |
|---------|--------------|--------------|
| §1 | Setup, imports, DEVICE | — |
| §2 | `load_split()`, train/test data | Load your images |
| §3 | `preprocess()`, ResNet18, ViT-Tiny | Understand the pipeline, get models |
| §4 | Scoring formula | Understand how PF works |
| **§5** | **`Solution` class** | **Replace `_attack()` with YOUR method** |
| §6 | Run on train subset + test split | Test your solution |
| §7 | `check()` — format validation | Verify .pt files before zip |
| §8 | `compute_score()` — local scoring | See your exact Pure/L2/PF/Final |
| §9 | `make_submission_zip()` | Package for submission |

Start with Hint 1 on a single image. Once you can reliably find Type A and Type B perturbations, scale up to all 100 training images. Then iterate through Hints 3–5 to climb the leaderboard. Good luck!
