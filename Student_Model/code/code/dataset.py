"""
dataset.py — LOL Dataset with Heavy Augmentation
=================================================
Processing Order: #6 (loaded by training.py and testing.py)

Contains:
  - LOLDataset class with patch cropping, flips, rotations, and MixUp
"""

import os
import glob
import numpy as np
import torch
from torch.utils.data import Dataset
from PIL import Image


class LOLDataset(Dataset):
    def __init__(self, input_dir, target_dir, patch_size=None, augment=False):
        self.input_files = sorted(glob.glob(os.path.join(input_dir, "*.*")))
        self.target_files = sorted(glob.glob(os.path.join(target_dir, "*.*")))
        assert len(self.input_files) == len(self.target_files), \
            f"Mismatch: {len(self.input_files)} inputs vs {len(self.target_files)} targets"
        self.patch_size = patch_size
        self.augment = augment

    def __len__(self):
        return len(self.input_files)

    def __getitem__(self, idx):
        inp = np.array(Image.open(self.input_files[idx]).convert("RGB")).astype(np.float32) / 255.0
        tgt = np.array(Image.open(self.target_files[idx]).convert("RGB")).astype(np.float32) / 255.0

        # Resize if shapes don't match
        if inp.shape != tgt.shape:
            h = min(inp.shape[0], tgt.shape[0])
            w = min(inp.shape[1], tgt.shape[1])
            inp = inp[:h, :w]
            tgt = tgt[:h, :w]

        if self.patch_size:
            h, w, _ = inp.shape
            ps = self.patch_size
            if h < ps or w < ps:
                # Pad if image is smaller than patch
                pad_h = max(0, ps - h)
                pad_w = max(0, ps - w)
                inp = np.pad(inp, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')
                tgt = np.pad(tgt, ((0, pad_h), (0, pad_w), (0, 0)), mode='reflect')
                h, w = inp.shape[:2]
            rh = np.random.randint(0, h - ps + 1)
            rw = np.random.randint(0, w - ps + 1)
            inp = inp[rh:rh + ps, rw:rw + ps]
            tgt = tgt[rh:rh + ps, rw:rw + ps]

        if self.augment:
            # Horizontal flip
            if np.random.rand() > 0.5:
                inp, tgt = inp[:, ::-1].copy(), tgt[:, ::-1].copy()
            # Vertical flip
            if np.random.rand() > 0.5:
                inp, tgt = inp[::-1].copy(), tgt[::-1].copy()
            # Random 90° rotation
            k = np.random.randint(0, 4)
            inp, tgt = np.rot90(inp, k).copy(), np.rot90(tgt, k).copy()
            # MixUp augmentation (20% chance)
            if np.random.rand() < 0.2 and self.patch_size:
                idx2 = np.random.randint(0, len(self))
                inp2 = np.array(Image.open(self.input_files[idx2]).convert("RGB")).astype(np.float32) / 255.0
                tgt2 = np.array(Image.open(self.target_files[idx2]).convert("RGB")).astype(np.float32) / 255.0
                if inp2.shape != tgt2.shape:
                    h2 = min(inp2.shape[0], tgt2.shape[0])
                    w2 = min(inp2.shape[1], tgt2.shape[1])
                    inp2 = inp2[:h2, :w2]
                    tgt2 = tgt2[:h2, :w2]
                h2, w2, _ = inp2.shape
                ps = self.patch_size
                if h2 >= ps and w2 >= ps:
                    rh2 = np.random.randint(0, h2 - ps + 1)
                    rw2 = np.random.randint(0, w2 - ps + 1)
                    inp2 = inp2[rh2:rh2+ps, rw2:rw2+ps]
                    tgt2 = tgt2[rh2:rh2+ps, rw2:rw2+ps]
                    lam = np.random.beta(0.5, 0.5)
                    inp = lam * inp + (1 - lam) * inp2
                    tgt = lam * tgt + (1 - lam) * tgt2

        inp = torch.from_numpy(inp.copy()).permute(2, 0, 1).float()
        tgt = torch.from_numpy(tgt.copy()).permute(2, 0, 1).float()
        return inp, tgt
