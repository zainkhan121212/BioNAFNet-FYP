# Installation, inference, training, and evaluation

## 1. Install and clone

Follow the root README's Windows instructions. Use Python 3.12, a virtual environment, and CPU PyTorch for the simplest setup. For CUDA, select the appropriate wheel using [PyTorch's official installation page](https://pytorch.org/get-started/locally/). Do not assume the CUDA version in an old training note matches your current driver.

Linux/macOS shell equivalents (not validated for the desktop GUI):

```bash
git clone https://github.com/zainkhan121212/BioNAFNet-FYP.git
cd BioNAFNet-FYP
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# Install torch/torchvision using the official selector for your operating system.
python -m pip install -r requirements.txt
```

The remaining `python` commands assume an activated environment. On Windows, use `.\.venv\Scripts\python.exe` in place of `python` if you prefer not to activate it.

## 2. Download trained weights

Open [release v1.0.0](https://github.com/zainkhan121212/BioNAFNet-FYP/releases/tag/v1.0.0) while signed in with repository access. Download:

| Release file | Save as | Purpose |
|---|---|---|
| `student_ema.pth` | `Student_Model/checkpoints/best.pth` | Single-pass student |
| `teacher_ema.pth` | `Teacher_Model/checkpoints/best.pth` | Two-pass teacher |
| `weights_manifest.json` | Any local folder | Source checkpoint, actual epoch, validation score, SHA-256 |
| `SHA256SUMS.txt` | Any local folder | Download verification |

Create the checkpoint folders first. `Get-FileHash -Algorithm SHA256 <file>` (PowerShell) or `sha256sum <file>` (Linux) should match the manifest. Assets contain EMA tensors and metadata, without optimizer state; they are for inference or initializing training, not exact optimizer-state resumption.

Optional GitHub CLI download, after `gh auth login`:

```powershell
New-Item -ItemType Directory -Force downloads, Student_Model/checkpoints, Teacher_Model/checkpoints
gh release download v1.0.0 --repo zainkhan121212/BioNAFNet-FYP --pattern '*_ema.pth' --dir downloads
Copy-Item downloads/student_ema.pth Student_Model/checkpoints/best.pth
Copy-Item downloads/teacher_ema.pth Teacher_Model/checkpoints/best.pth
```

## 3. Enhance an image

```bash
python enhance.py --model student --weights Student_Model/checkpoints/best.pth --input dark.png --output outputs/student.png
python enhance.py --model teacher --weights Teacher_Model/checkpoints/best.pth --input dark.png --output outputs/teacher.png --device cuda
```

The wrapper uses the unchanged modular architecture, strict checkpoint loading, RGB conversion, and no optional postprocessing. It stops if weights are missing. Start with a small image, especially on CPU. PNG output avoids JPEG compression affecting subsequent metrics.

## 4. Desktop application

```bash
python -m pip install -r requirements-gui.txt
python "Kimi_Agent_CustomTkinter Futuristic UI/neon_enhancer_pro.py"
```

Keep the student and teacher folders next to the UI folder. Download weights before selecting a BioNAFNet model: the original GUI can otherwise continue with untrained weights. Select CPU unless a working CUDA PyTorch build is installed. Retinexformer and Zero-DCE are optional integrations; their pretrained weights are not provided by this release. Their dependency stacks and the GUI itself have not been fully validated as part of packaging.

## 5. Paired datasets

Obtain LOL datasets separately under their original terms. No dataset or personal photograph is included. The original loaders expect:

```text
data/
  LOLv1/Train/input/       LOLv1/Train/target/
  LOLv1/Test/input/        LOLv1/Test/target/
  LOLv2/Real_captured/Train/Low/     .../Train/Normal/
  LOLv2/Real_captured/Test/Low/      .../Test/Normal/
  LOLv2/Synthetic/Train/Low/         .../Train/Normal/
  LOLv2/Synthetic/Test/Low/          .../Test/Normal/
```

Verify low/normal filename pairing before evaluation. The report uses 485 + 689 + 900 training pairs and 15 + 100 + 100 test pairs.

## 6. Train the teacher and distill the student

The original scripts contain author-specific paths. Edit `DATA_ROOT` in each model's `code/code/config.py` to an absolute local dataset path. Do this before running training.

```bash
python Teacher_Model/code/code/train.py
```

For distillation, set `TEACHER_CKPT` in `Student_Model/code/code/config.py` to the absolute teacher checkpoint path, then:

```bash
python Student_Model/code/code/train.py --n_passes 1
```

Review batch size, epochs, AMP, and patch size in the configs for your hardware. The teacher and student use different objectives; the student uses `0.5*L1 + 0.1*SSIM-loss + 0.4*teacher-mimic-MSE`. GPU training is recommended. The original trainer may fetch torchvision VGG weights on first use. Training was not rerun during packaging.

## 7. Evaluate

For student evaluation, set `BEST_PATH` in its `config.py` to the absolute downloaded student checkpoint path. Then:

```bash
python Student_Model/code/code/test.py --test_in /absolute/data/LOLv1/Test/input --test_gt /absolute/data/LOLv1/Test/target --test_name LOLv1 --results_dir outputs/student-lolv1
```

For teacher evaluation, set `BEST_PATH` in its `config.py`, and set `TEST_INPUT_PATH`, `TEST_GT_PATH`, and `OUTPUT_DIR` in `Teacher_Model/code/code/test.py`, then run:

```bash
python Teacher_Model/code/code/test.py
```

The original evaluators can fall back to random weights if the path is wrong: require a successful checkpoint-loaded message. Do not publish metrics from a missing-checkpoint run. The older standalone `Student_Model/code/test_distilled.py` uses two passes despite the one-pass student specification; use the modular evaluator above. Record checkpoint hash, passes, image sizes, dataset split, and postprocessing with every comparison.

## 8. Existing unit tests

```bash
python -m pip install pytest
python -m pytest Teacher_Model/code/code/tests -q
```

These test components and tensor behavior; they do not establish image-quality benchmarks or validate the estimated ablations.

## Troubleshooting

- Repository not found: sign in to an account invited to this private repository.
- Missing weights: download release assets and check the exact paths above.
- CUDA unavailable: install the matching PyTorch build, or use CPU.
- Out of memory: use the student, a smaller input, or CPU; resolution affects memory considerably.
- `No module named ...`: run pip through the same environment's Python used to launch the app.
- Legacy scripts fail on an `F:` or `C:` path: update their configuration; use `enhance.py` for portable inference.
