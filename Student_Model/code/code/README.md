# BioNAFNet — Student Model (Knowledge Distilled)

**Lightweight BioNAFNet for Fast Low-Light Image Enhancement**

A compressed student model (~24M params) distilled from the full BioNAFNet teacher (~154M params), retaining all 7 biological mechanisms while being 6x smaller and faster.

## 7 Biological Novel Contributions

| # | Name | File | Inspired By |
|---|------|------|-------------|
| 1 | **RLIN** — Retinal Lateral Inhibition Network | `novels/novel1_rlin.py` | Retinal ganglion center-surround antagonism |
| 2 | **FAEB** — Frequency-Aware Enhancement Branch | `novels/novel2_faeb.py` | Visual cortex spatial frequency processing |
| 3 | **ARFP** — Adaptive Receptive Field Pooling | `novels/novel3_arfp.py` | Rod/cone receptive field size differences |
| 4 | **PRCM** — Photoreceptor Response Curve Modeling | `novels/novel4_prcm.py` | Rod/cone gamma response curves |
| 5 | **SPDP** — Scotopic-Photopic Dual Pathway | `novels/novel5_spdp.py` | Separate luminance/chrominance pathways |
| 6 | **TAM** — Temporal Adaptation Memory | `novels/novel6_tam.py` | Dark adaptation progressive refinement |
| 7 | **Weber-Fechner Loss** | `losses.py` | Weber-Fechner law of perception |

## Student vs Teacher

| Property | Teacher | Student |
|----------|---------|---------|
| Width | 64 | 32 |
| Middle Blocks | 12 | 4 |
| Passes | 2 | 1 |
| Parameters | ~154M | ~24M |
| Training | Standard GT loss | Knowledge distillation |

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Edit config.py — set DATA_ROOT and TEACHER_CKPT paths

# 3. Train the student model (distillation)
python train.py

# 4. Test the student model
python test.py

# 5. Or train + test in one go
python train_and_test.py
```

## Dataset

Trained on **LOLv1 + LOLv2** (Real + Synthetic) datasets.
Set the `DATA_ROOT` path in `config.py` to point to your data:

```
DATA_ROOT/
├── LOLv1/
│   ├── Train/  (input/ + target/)
│   └── Test/   (input/ + target/)
└── LOLv2/
    ├── Real_captured/Train/  (Low/ + Normal/)
    └── Synthetic/Train/      (Low/ + Normal/)
```

## File Structure

See `PROCESSING_ORDER.txt` for the complete dependency graph and execution order.

```
code/
├── train.py              ← Run this to TRAIN (distillation)
├── test.py               ← Run this to TEST
├── train_and_test.py     ← Train + Test combined
├── config.py             ← Configuration & hyperparameters
├── model.py              ← BioNAFNet architecture
├── nafnet_blocks.py      ← NAFNet building blocks
├── losses.py             ← Loss functions (7 components)
├── dataset.py            ← LOL dataset loader
├── train_loop.py         ← Distillation training loop (used by train.py)
├── test_loop.py          ← Evaluation loop engine (used by test.py)
├── ema.py                ← EMA helper
├── novels/               ← 7 biological novel components
│   ├── novel1_rlin.py
│   ├── novel2_faeb.py
│   ├── novel3_arfp.py
│   ├── novel4_prcm.py
│   ├── novel5_spdp.py
│   ├── novel6_tam.py
│   └── luminance_utils.py
├── requirements.txt
└── PROCESSING_ORDER.txt
```

## Model Pipeline

```
Input → PRCM → SPDP → NAFNet Encoder [RLIN] → Bottleneck + FAEB → Decoder + ARFP → TAM → Output
```
