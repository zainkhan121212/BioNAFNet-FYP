# BioNAFNet — Google Colab Setup Guide

## Step 1: Open Colab & Enable GPU

1. Go to [Google Colab](https://colab.research.google.com)
2. Click **Runtime → Change runtime type → GPU** (select **T4** or **A100** if available)

---

## Step 2: Upload Dataset to Google Drive

Upload your LOLv1 (and optionally LOLv2) dataset to Google Drive with this folder structure:

```
MyDrive/
└── datasets/
    ├── LOLv1/
    │   ├── Train/
    │   │   ├── input/     ← 485 low-light images
    │   │   └── target/    ← 485 normal-light images
    │   └── Test/
    │       ├── input/     ← 15 test images
    │       └── target/    ← 15 test ground truths
    │
    └── LOLv2/             ← OPTIONAL (for better results)
        ├── Real_captured/
        │   └── Train/
        │       ├── Low/
        │       └── Normal/
        └── Synthetic/
            └── Train/
                ├── Low/
                └── Normal/
```

> **Tip:** You can zip the dataset, upload to Drive, and unzip in Colab:
> ```python
> !unzip /content/drive/MyDrive/LOL-v1.zip -d /content/drive/MyDrive/datasets/
> ```

---

## Step 3: Upload the Training Script

Upload `train_bionafnet_colab.py` to Google Drive at:
```
MyDrive/train_bionafnet_colab.py
```

---

## Step 4: Run These Cells in Colab

### Cell 1: Mount Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```

### Cell 2: Install Dependencies
```python
!pip install scikit-image tqdm torchvision
```

### Cell 3: Copy Script to Colab
```python
!cp /content/drive/MyDrive/train_bionafnet_colab.py /content/
```

### Cell 4: Start Training
```python
!python /content/train_bionafnet_colab.py
```

Training will:
- Auto-detect LOLv1 + LOLv2 data
- Save checkpoints to `MyDrive/BioNAFNet_output/checkpoints/`
- Save logs to `MyDrive/BioNAFNet_output/training_log.txt`
- Save enhanced images to `MyDrive/BioNAFNet_output/results/`

---

## Step 5: Resume After Timeout

Colab sessions timeout after ~12 hours. Training **auto-resumes** from `latest.pth`:

```python
# Just run the same command again — it picks up where it left off!
!python /content/train_bionafnet_colab.py
```

---

## Step 6: Test Best Model

```python
!python /content/train_bionafnet_colab.py --test_only
```

---

## Monitoring Training

### View the log:
```python
!tail -20 /content/drive/MyDrive/BioNAFNet_output/training_log.txt
```

### Plot PSNR curve:
```python
import matplotlib.pyplot as plt
import re

with open('/content/drive/MyDrive/BioNAFNet_output/training_log.txt') as f:
    lines = f.readlines()

epochs, val_psnrs = [], []
for line in lines:
    m = re.search(r'Epoch (\d+)/\d+ .* Val PSNR: ([\d.]+)', line)
    if m:
        epochs.append(int(m.group(1)))
        val_psnrs.append(float(m.group(2)))

plt.figure(figsize=(10, 5))
plt.plot(epochs, val_psnrs, 'b-', linewidth=2)
plt.xlabel('Epoch')
plt.ylabel('Val PSNR (dB)')
plt.title('BioNAFNet Training Progress')
plt.grid(True)
plt.show()
```

---

## Estimated Training Time

| GPU | Time per Epoch | Total (500 epochs) |
|-----|----------------|---------------------|
| T4 (free tier) | ~5-6 min | ~50 hours (5 sessions) |
| A100 (Pro) | ~2 min | ~17 hours (2 sessions) |
| V100 (Pro) | ~3 min | ~25 hours (3 sessions) |

> Each Colab Pro session lasts ~24 hours. Free tier lasts ~12 hours.
> The auto-resume feature ensures no progress is lost between sessions.
