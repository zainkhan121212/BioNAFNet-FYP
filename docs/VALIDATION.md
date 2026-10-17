# Publication validation

Validated on Windows on 2026-10-17 using the existing Python 3.12 installation, PyTorch `2.11.0+cu128`, and torchvision `0.26.0+cu128`.

- Python syntax parsing: 64 files across student, teacher, and the inference wrapper passed.
- Existing model unit suite: `python -m pytest Teacher_Model/code/code/tests -q` — **57 passed in 2.97 seconds**.
- Both exported EMA checkpoints loaded with `strict=True` and no missing/unexpected parameters.
- CPU forward checks passed for both models with finite outputs of shape `[1, 3, 32, 48]`.
- The documented `enhance.py` entry point produced PNG output for both models from a synthetic 48x32 RGB input.
- Checkpoint metadata and SHA-256 hashes are recorded in [weights_manifest.json](weights_manifest.json).

The original model architectures and training code are unchanged. Packaging adds documentation, dependency lists, Git ignore rules, and a portable inference wrapper. A fresh-environment install, full-resolution benchmarks, retraining, optional third-party integrations, and interactive GUI behavior were not validated. Smoke-test input is synthetic and is not evidence of enhancement quality.
