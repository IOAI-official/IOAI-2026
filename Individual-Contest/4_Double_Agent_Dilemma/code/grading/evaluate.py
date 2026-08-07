"""Importable evaluation module for the Double Agent Dilemma problem.

Mirrors the scoring logic of updated-evaluation/evaluate.py but works
with in-memory tensors produced by a Solution, so no zip file is needed.

Usage
-----
from evaluate import compute_score

score = compute_score(preds, targets)

Where:
  preds   = list of (delta_a, delta_b) CPU tensors, one per image
  targets = list of {'idx': int, 'image_path': Path, 'label': int}
"""

from __future__ import annotations

import io
import os
import zipfile
from pathlib import Path

import torch
import torchvision.transforms as T
import torchvision.transforms.functional as TF
import numpy as np
from PIL import Image
from scipy.special import expit
from torchvision import models
import timm

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

MODELS_ROOT = Path(os.environ.get("MODELS_DIR", "models"))
_K = 50000  # sigmoid steepness for the L2 penalty

_resnet: torch.nn.Module | None = None
_vit: torch.nn.Module | None = None


def _get_models():
    global _resnet, _vit
    if _resnet is None:
        print(f"[evaluate] Loading models on {DEVICE}...")
        resnet_path = MODELS_ROOT / "resnet18.pth"
        vit_path = MODELS_ROOT / "vit_tiny_patch16_224.safetensors"

        # Match the notebook exactly and never consult the network or a mutable
        # framework cache for evaluator weights.
        _resnet = models.resnet18(weights=None)
        _resnet.load_state_dict(
            torch.load(resnet_path, map_location="cpu", weights_only=True)
        )
        _resnet = _resnet.to(DEVICE).eval()

        # timm's default cfg has custom_load=True because the original checkpoint
        # was JAX NPZ. The mounted artifact is safetensors, so this override is
        # required (and is the same one used by solution.ipynb).
        _vit = timm.create_model(
            "vit_tiny_patch16_224",
            pretrained=True,
            pretrained_cfg_overlay={
                "file": str(vit_path),
                "custom_load": False,
            },
        ).to(DEVICE).eval()
        for parameter in (*_resnet.parameters(), *_vit.parameters()):
            parameter.requires_grad_(False)
    return _resnet, _vit


def _preprocess(img_tensor: torch.Tensor) -> torch.Tensor:
    img = TF.resize(img_tensor, size=256, interpolation=T.InterpolationMode.BILINEAR)
    img = TF.center_crop(img, output_size=224)
    mean = torch.tensor([0.485, 0.456, 0.406]).to(DEVICE).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).to(DEVICE).view(3, 1, 1)
    return (img - mean) / std


def compute_score(preds, targets, verbose: bool = True) -> float:
    """Evaluate perturbations and return the final weighted score.

    Parameters
    ----------
    preds:
        List of ``(delta_a, delta_b)`` tensors (CPU).
        ``delta_a`` targets ResNet-keeps / ViT-fools.
        ``delta_b`` targets ViT-keeps  / ResNet-fools.
    targets:
        List of dicts with keys ``image_path`` and ``label``.
    verbose:
        Print per-metric breakdown.

    Returns
    -------
    float  final_score = pure_score * penalty_factor
    """
    resnet, vit = _get_models()

    score_a = score_b = 0
    l2_norms: list[float] = []
    total = len(targets)

    with torch.no_grad():
        for (delta_a, delta_b), item in zip(preds, targets):
            img = Image.open(item["image_path"]).convert("RGB")
            img_t = TF.to_tensor(img).to(DEVICE)
            label = item["label"]

            da = delta_a.to(DEVICE)
            db = delta_b.to(DEVICE)

            pixel_count = da.numel()
            l2_norms.append((da.norm(2).item() + db.norm(2).item()) / pixel_count)

            # Score A: ResNet correct, ViT wrong
            adv_a = torch.clamp(img_t + da, 0, 1)
            inp_a = _preprocess(adv_a).unsqueeze(0)
            if resnet(inp_a).argmax(1).item() == label and vit(inp_a).argmax(1).item() != label:
                score_a += 1

            # Score B: ViT correct, ResNet wrong
            adv_b = torch.clamp(img_t + db, 0, 1)
            inp_b = _preprocess(adv_b).unsqueeze(0)
            if resnet(inp_b).argmax(1).item() != label and vit(inp_b).argmax(1).item() == label:
                score_b += 1

    pure_score = (score_a + score_b) / (total * 2)
    mnorm = float(np.mean(l2_norms))
    pf = float(1.5 - expit(_K * mnorm))
    final_score = pure_score * pf

    if verbose:
        print(f"\n{'='*50}")
        print(f"Evaluation Results")
        print(f"{'='*50}")
        print(f"Total images       : {total}")
        print(f"Score A (R✓ / V✗)  : {score_a}/{total}  ({score_a/total:.1%})")
        print(f"Score B (V✓ / R✗)  : {score_b}/{total}  ({score_b/total:.1%})")
        print(f"Pure score         : {pure_score:.4f}  ({pure_score*100:.2f}%)")
        print(f"Mean L2/pixel      : {mnorm:.6f}")
        print(f"Penalty factor     : {pf:.4f}")
        print(f"Final score        : {final_score:.4f}  ({final_score*100:.2f}%)")
        print(f"{'='*50}")

    return final_score


def build_preds(zip_path: Path, targets: list) -> list:
    """Assemble (delta_a, delta_b) per target from the submission zip.

    Missing, mismatched-resolution, non-floating, sparse, or non-finite tensors
    are disqualified (zero delta) rather than crashing or poisoning the aggregate
    score, matching the statement's per-sample rule.
    """
    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        # The caller owns verdict/report handling. Keeping this helper independent
        # allows it to run inside the isolated scoring container.
        raise

    # Map basename -> raw bytes (ignore any accidental subdirectories/prefixes).
    members = {}
    with zf:
        for name in zf.namelist():
            base = os.path.basename(name)
            if base.endswith(".pt"):
                members[base] = zf.read(name)

    import torchvision.transforms.functional as TF
    from PIL import Image

    preds = []
    disqualified = 0
    for item in targets:
        idx = item["idx"]
        # Reference shape = raw image tensor shape (3, H, W).
        img = Image.open(item["image_path"]).convert("RGB")
        ref = TF.to_tensor(img)
        deltas = []
        for tag in ("a", "b"):
            data = members.get(f"{idx}_{tag}.pt")
            delta = None
            if data is not None:
                try:
                    delta = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
                except Exception:
                    delta = None
            valid = False
            if isinstance(delta, torch.Tensor) and delta.shape == ref.shape:
                try:
                    valid = (
                        delta.layout == torch.strided
                        and delta.is_floating_point()
                        and bool(torch.isfinite(delta).all().item())
                    )
                except Exception:
                    valid = False
            if not valid:
                delta = torch.zeros_like(ref)  # disqualified -> no fooling, no L2
                disqualified += 1
            deltas.append(delta.float())
        preds.append((deltas[0], deltas[1]))

    print(f"parsed {len(preds)} samples from {zip_path.name}  "
          f"(disqualified tensors: {disqualified}/{2 * len(preds)})")
    return preds
