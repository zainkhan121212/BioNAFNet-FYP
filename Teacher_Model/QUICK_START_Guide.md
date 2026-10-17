# BioNAFNet Teacher Model - Quick Start Guide (2-Day Crash Course)

## 📚 What You Need to Know in 2 Days

### DAY 1: Understand the Architecture

#### Morning (3 hours): Core Concepts

**1. What is BioNAFNet?**
- A low-light image enhancement model
- Based on NAFNet (U-Net architecture)
- Adds 7 biological innovations inspired by human vision
- Trained on LOLv1 and LOLv2 datasets

**2. The 7 Novelties (MUST KNOW):**

| # | Name | What It Does | Where |
|---|------|--------------|-------|
| 1 | RLIN | Edge enhancement via center-surround inhibition | Inside encoder blocks |
| 2 | FAEB | Recovers textures using FFT | At bottleneck |
| 3 | ARFP | Adaptive kernel size based on brightness | At decoder output |
| 4 | PRCM | Different gamma for dark/bright regions | Input preprocessing |
| 5 | SPDP | Separate luminance/color processing | After PRCM |
| 6 | TAM | Multi-pass refinement with GRU | Final aggregation |
| 7 | WFPL | Weights errors more in dark regions | Training loss only |

**3. Data Flow (Simplified):**
```
Input → PRCM → SPDP → [Pass 1: U-Net] → [Pass 2: U-Net] → TAM → Output
                         ↑                    ↑
                      Same network, same weights
```

#### Afternoon (3 hours): Code Walkthrough

**Key Files to Read:**

1. **`train_bionafnet.py`** (main file, contains everything)
   - Lines 103-117: RLIN implementation
   - Lines 123-152: FAEB (FFT-based enhancement)
   - Lines 158-176: ARFP (adaptive pooling)
   - Lines 182-195: PRCM (photoreceptor curves)
   - Lines 201-231: SPDP (dual pathway)
   - Lines 237-255: TAM (temporal adaptation)
   - Lines 286-339: BioNAFBlock (core building block)
   - Lines 342-460: BioNAFNet (main model class)
   - Lines 467-599: Loss functions
   - Lines 606-677: Dataset loader
   - Lines 721-902: Training loop
   - Lines 909-969: Testing function

2. **Study order:**
   - First: Look at `BioNAFNet.forward()` (line 429)
   - Then: Follow one pass through `forward_single()` (line 402)
   - Then: Check how each novelty is implemented
   - Finally: Understand training loop (line 769)

**What to ignore for now:**
- EMA implementation
- Progressive resizing
- Mixed precision details
- Gradient accumulation
- Checkpoint resumption

---

### DAY 2: Hands-On Practice

#### Morning (3 hours): Run the Code

**Step 1: Test Inference**
```bash
cd "F:\low_light_enhancement\eye adaption\BioNAFNet\Teacher_Model\code"
python infer_bionafnet.py --input <path_to_test_images> --output ./results --weights ../checkpoints/best.pth
```

**Step 2: Monitor Training** (optional, takes too long)
```bash
python train_bionafnet.py
```

**Step 3: Add Debug Prints**
Open `train_bionafnet.py` and add prints in `forward()`:
```python
def forward(self, x):
    print(f"Input shape: {x.shape}")
    x_prcm = self.prcm(x)
    print(f"After PRCM: {x_prcm.shape}")
    # ... continue adding prints
```

#### Afternoon (3 hours): Answer Common Questions

**Q1: How does an image flow through the network?**
```
1. Load image (H×W×3)
2. Normalize to [0,1], convert to tensor (1×3×H×W)
3. PRCM: Apply gamma correction
4. SPDP: Convert RGB→YUV, process separately
5. Pass 1 through U-Net
6. Pass 2 through U-Net (using output of Pass 1)
7. TAM: Combine both passes with GRU
8. Clamp to [0,1]
9. Save as enhanced image
```

**Q2: What happens during training?**
```
1. Load low-light image + normal-light ground truth
2. Forward pass through model (same as inference)
3. Calculate loss (6 components weighted sum)
4. Backpropagate gradients
5. Update weights with AdamW
6. Update EMA weights
7. Repeat for 1000 epochs
```

**Q3: Where are the 7 novelties in code?**
- Novel 1 (RLIN): Line 103-117, used in line 331
- Novel 2 (FAEB): Line 123-152, used in line 404
- Novel 3 (ARFP): Line 158-176, used in line 423
- Novel 4 (PRCM): Line 182-195, used in line 431
- Novel 5 (SPDP): Line 201-231, used in line 434
- Novel 6 (TAM): Line 237-255, used in line 449
- Novel 7 (WFPL): Line 530-543, used in line 581

**Q4: What's the most important function?**
`BioNAFNet.forward()` at line 429 - this is where all novelties come together.

**Q5: If you only read 50 lines, which ones?**
Lines 429-453 in `train_bionafnet.py` - the `forward()` method.

---

## 🎯 Exam Preparation Cheat Sheet

### Architecture Numbers to Memorize:
- **Width**: 64 channels
- **Encoder**: [2, 2, 4, 8] blocks at 4 scales
- **Middle**: 12 blocks
- **Decoder**: [2, 2, 2, 2] blocks at 4 scales
- **Passes**: 2 (multi-pass refinement)
- **Patch size**: 128×128 (training)
- **Epochs**: 1000
- **Batch size**: 4 (effective 8 with accumulation)
- **Learning rate**: 2e-4

### Key Formulas:
```python
# Luminance calculation
lum = 0.299*R + 0.587*G + 0.114*B

# PRCM blending
cone_weight = sigmoid((lum - threshold) * 12)
output = rod_gamma * (1 - cone_weight) + cone_gamma * cone_weight

# RLIN
output = x + alpha * (center(x) - surround(x))

# Weber-Fechner Loss
weight = 1 / (luminance + eps)
loss = mean(|pred - target| * weight)
```

### Biological Inspirations:
- **RLIN**: Retinal ganglion cells have center-surround receptive fields
- **FAEB**: Visual cortex processes frequencies separately
- **ARFP**: Rod cells pool over larger areas in darkness
- **PRCM**: Rods and cones have different response curves
- **SPDP**: Separate pathways for luminance (rods) and color (cones)
- **TAM**: Dark adaptation takes time (progressive refinement)
- **WFPL**: Human vision more sensitive to changes in dark regions

---

## 🔥 Last-Minute Study Tips

### If you have 6 hours:
1. Read `BioNAFNet.forward()` (lines 429-453) - 30 min
2. Read each novelty implementation - 2 hours
3. Draw the architecture diagram from memory - 30 min
4. Trace one image through the network on paper - 1 hour
5. Review loss function components - 30 min
6. Practice explaining each novelty in 2 sentences - 1 hour

### If you have 2 hours:
1. Memorize the 7 novelties (names + what they do) - 30 min
2. Understand the high-level pipeline - 30 min
3. Know the key numbers (width, blocks, epochs) - 15 min
4. Be able to explain U-Net architecture - 15 min
5. Review biological inspirations - 30 min

### If you have 30 minutes:
Read ONLY these sections:
- Lines 1-18 of `train_bionafnet.py` (overview comments)
- Lines 429-453 (`forward()` method)
- This cheat sheet!

---

## 📝 Common Exam Questions & Answers

**Q: Explain the role of PRCM.**
A: PRCM simulates different photoreceptor response curves for rods (dark) and cones (bright). It applies a lower gamma (~0.45) to dark regions to brighten them significantly, and a higher gamma (~0.95) to bright regions with minimal change. This mimics how human vision adapts to different light levels.

**Q: Why is FAEB placed at the bottleneck?**
A: FAEB uses FFT to recover high-frequency textures. The bottleneck has the deepest semantic features at the lowest spatial resolution, making it computationally efficient to apply FFT there. Also, by that point, the network has extracted all necessary features, so frequency enhancement is most effective.

**Q: How does TAM achieve multi-pass refinement?**
A: TAM runs the backbone network multiple times (n_passes=2), feeding each output back as input. It then uses a GRU cell to accumulate information across passes, treating spatial pixels as a sequence. The GRU learns what to keep from each pass, producing a refined final output.

**Q: What makes Weber-Fechner Loss special?**
A: Unlike standard losses that treat all pixels equally, WFPL weights errors inversely proportional to luminance. Errors in dark regions are penalized more heavily because human vision is more sensitive to changes in darkness (Weber-Fechner law). This produces perceptually better results.

**Q: Why use residual connections throughout?**
A: Residual connections help with gradient flow during training (prevents vanishing gradients), allow the network to learn identity mappings easily, and stabilize training. In BioNAFNet, every major component uses residuals: BioNAFBlocks, TAM, SPDP, etc.

---

## ✅ Final Checklist

Before your presentation/exam, make sure you can:

- [ ] Name all 7 novelties
- [ ] Explain what each novelty does (1-2 sentences)
- [ ] Draw the high-level architecture
- [ ] Trace an image through the network
- [ ] Explain the training loop
- [ ] List the key hyperparameters
- [ ] Describe the U-Net structure
- [ ] Explain why residual connections are used
- [ ] Describe what FAEB does and why FFT is helpful
- [ ] Explain the biological inspiration behind at least 3 novelties

---

**Good luck! You've got this! 🚀**

Remember: Focus on understanding the DATA FLOW and the 7 NOVELTIES. Everything else is implementation details.
