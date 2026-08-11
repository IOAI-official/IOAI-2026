#!/usr/bin/env python3
"""Prefetch pretrained weights into a flat models/ directory.

Usage:
    ./download-models.py                  # writes ./models
    ./download-models.py /path/to/models

Produces two plain checkpoint files, no cache layout, no symlinks:
    models/resnet18.pth                        (torchvision IMAGENET1K_V1)
    models/vit_tiny_patch16_224.safetensors    (timm default pretrained tag)

Run it in the notebook image so the weights match the pinned torch/timm. Copy
it out of arcadia first -- docker cannot bind-mount the FUSE mount ("mkdir
/home/<user>/arcadia: file exists"):

    cp download-models.py /some/work/dir && cd /some/work/dir
    docker run --rm --user "$(id -u):$(id -g)" -e HOME=/work \\
        -v "$PWD:/work" -w /work \\
        cr.yandex/crpe6hs3eavcafkcisb5/ioai-notebook:20260805 \\
        python3 /work/download-models.py /work/models

Your own uid, not root, or the files land in the bind mount owned by root.
HOME must be writable because the image's /home/jovyan is not writable by an
arbitrary uid -- nothing is cached there, both downloads go straight to models/.
"""

import os
import shutil
import sys
from pathlib import Path

import timm
import torch
import torchvision
from huggingface_hub import hf_hub_download
from torchvision import models
from torchvision.models import ResNet18_Weights


def main(argv: list[str]) -> int:
    out = Path(argv[1] if len(argv) > 1 else "models").resolve()
    out.mkdir(parents=True, exist_ok=True)
    print(f"[models] Target: {out}")
    print(f"[models] torch={torch.__version__} "
          f"torchvision={torchvision.__version__} timm={timm.__version__}")

    resnet_path = fetch_resnet18(out)
    vit_path = fetch_vit_tiny(out)
    print(f"[models] wrote {resnet_path.name}, {vit_path.name}")

    verify(resnet_path, vit_path)

    for path in sorted(out.iterdir()):
        print(f"[models]   {path.stat().st_size:>12,}  {path.name}")
    print("[models] Done.")
    return 0


def fetch_resnet18(out: Path) -> Path:
    """Pull the state dict straight from the weights enum.

    Beats hardcoding the hashed filename: it tracks whatever torchvision is
    pinned in the image.
    """
    url = ResNet18_Weights.IMAGENET1K_V1.url
    print(f"[models] resnet18 <- {url}")
    # model_dir + file_name write straight into out/ under a stable name, so
    # nothing passes through ~/.cache/torch and HOME need not be writable.
    torch.hub.load_state_dict_from_url(
        url,
        model_dir=str(out),
        file_name="resnet18.pth",
        map_location="cpu",
        progress=True,
    )
    return out / "resnet18.pth"


def fetch_vit_tiny(out: Path) -> Path:
    """Download timm's default-tag checkpoint as a flat file.

    Re-serializing model.state_dict() would also work, but keeping the original
    checkpoint means timm's checkpoint filter sees the input it expects on the
    way back in. local_dir= gives a real file rather than the blobs/snapshots
    symlink tree, at the cost of a .cache/ bookkeeping dir we delete after.
    """
    cfg = timm.get_pretrained_cfg("vit_tiny_patch16_224")
    repo_id = cfg.hf_hub_id.rstrip("/")
    if repo_id == "timm":
        repo_id = f"timm/{cfg.tag}" if cfg.tag else "timm/vit_tiny_patch16_224"
    print(f"[models] vit_tiny_patch16_224 <- hf:{repo_id} (tag={cfg.tag})")

    for filename, suffix in (("model.safetensors", ".safetensors"),
                             ("pytorch_model.bin", ".bin")):
        try:
            downloaded = hf_hub_download(repo_id, filename, local_dir=str(out))
        except Exception as exc:  # noqa: BLE001 - fall through to the next candidate
            print(f"[models]   {filename}: {type(exc).__name__}: {exc}")
            continue
        path = out / f"vit_tiny_patch16_224{suffix}"
        shutil.move(downloaded, path)
        shutil.rmtree(out / ".cache", ignore_errors=True)
        return path

    raise SystemExit(f"[models] no downloadable weight file in {repo_id}")


def verify(resnet_path: Path, vit_path: Path) -> None:
    """Re-load both from disk the way the notebook does, with the hub cut off.

    A broken artifact then fails here rather than during scoring.
    """
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"

    resnet = models.resnet18(weights=None)
    resnet.load_state_dict(torch.load(resnet_path, map_location="cpu"))

    # custom_load=False is required, not cosmetic. This cfg carries
    # custom_load=True (the augreg weights were originally JAX .npz), and on the
    # file= path timm honours it unconditionally -- it would hand our
    # safetensors to np.load and die on "This file contains pickled data".
    # The hf-hub path only takes that branch for custom_load == 'hf', which is
    # why plain pretrained=True works and file= needs the override.
    vit = timm.create_model(
        "vit_tiny_patch16_224",
        pretrained=True,
        pretrained_cfg_overlay=dict(file=str(vit_path), custom_load=False),
    )

    print(f"[models] verified: resnet18 "
          f"({sum(p.numel() for p in resnet.parameters()):,} params), "
          f"vit_tiny_patch16_224 "
          f"({sum(p.numel() for p in vit.parameters()):,} params)")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
