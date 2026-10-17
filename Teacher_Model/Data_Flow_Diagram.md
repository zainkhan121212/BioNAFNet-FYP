# BioNAFNet Data Flow Visualization

## 🎯 Complete Execution Path - Visual Guide

### HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                     INPUT IMAGE (Low-Light)                      │
│                    Shape: [1, 3, H, W]                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              NOVEL 4: PRCM (Photoreceptor Curve)                │
│  File: novels/novel4_prcm.py                                    │
│  What: Applies different gamma curves for dark/bright regions   │
│  Code: rod_gamma≈0.45 (dark), cone_gamma≈0.95 (bright)         │
│  Output: [1, 3, H, W] - Tone-mapped image                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│          NOVEL 5: SPDP (Dual Pathway Y/U/V Processing)          │
│  File: novels/novel5_spdp.py                                    │
│  What: Separates luminance (Y) from chrominance (U,V)           │
│  Process: RGB→YUV → separate convs → fuse back to RGB          │
│  Output: [1, 3, H, W] - Enhanced luminance-color separation    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│            Compute Luminance Map (for ARFP later)               │
│  Function: luminance(x) = 0.299*R + 0.587*G + 0.114*B         │
│  Output: [1, 1, H, W] - Single channel luminance map           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌═════════════════════════════════════════════════════════════════┐
║           MULTI-PASS REFINEMENT LOOP (n_passes=2)              ║
╚══════════════╦══════════════════════════════════════════════════╝
               │
               │  ┌──────────────────────────────────────┐
               │  │  PASS 1 (current = x_spdp)           │
               │  └──────────────┬───────────────────────┘
               │                 │
               │                 ▼
               │  ┌──────────────────────────────────────────────┐
               │  │     forward_single(current, lum_map)         │
               │  │     This is the NAFNet U-Net Backbone        │
               │  └──────────────┬───────────────────────────────┘
               │                 │
               │                 ├──► ENCODER PATH ──────────────┐
               │                 │                               │
               │                 │  Intro Conv: 3→64 ch          │
               │                 │       ↓                        │
               │                 │  Encoder Block 1: 64 ch       │
               │                 │  [BioNAFBlock × 2]            │
               │                 │  Each block has RLIN!         │
               │                 │       ↓ Downsample 2×         │
               │                 │  Encoder Block 2: 128 ch      │
               │                 │  [BioNAFBlock × 2]            │
               │                 │       ↓ Downsample 2×         │
               │                 │  Encoder Block 3: 256 ch      │
               │                 │  [BioNAFBlock × 4]            │
               │                 │       ↓ Downsample 2×         │
               │                 │  Encoder Block 4: 512 ch      │
               │                 │  [BioNAFBlock × 8]            │
               │                 │       ↓ Downsample 2×         │
               │                 │                               │
               │                 ├──► BOTTLENECK ────────────────┤
               │                 │                               │
               │                 │  Middle Blocks: 1024 ch       │
               │                 │  [BioNAFBlock × 12]           │
               │                 │       ↓                        │
               │                 │  NOVEL 2: FAEB                 │
               │                 │  (Frequency Enhancement)      │
               │                 │  FFT → process amp/phase      │
               │                 │  → inverse FFT                 │
               │                 │                               │
               │                 ├──► DECODER PATH ──────────────┤
               │                 │                               │
               │                 │  Upsample 2× + Skip Connect   │
               │                 │  Decoder Block 1: 512 ch      │
               │                 │  [BioNAFBlock × 2]            │
               │                 │       ↓                        │
               │                 │  Upsample 2× + Skip Connect   │
               │                 │  Decoder Block 2: 256 ch      │
               │                 │  [BioNAFBlock × 2]            │
               │                 │       ↓                        │
               │                 │  Upsample 2× + Skip Connect   │
               │                 │  Decoder Block 3: 128 ch      │
               │                 │  [BioNAFBlock × 2]            │
               │                 │       ↓                        │
               │                 │  Upsample 2× + Skip Connect   │
               │                 │  Decoder Block 4: 64 ch       │
               │                 │  [BioNAFBlock × 2]            │
               │                 │       ↓                        │
               │                 │  NOVEL 3: ARFP                 │
               │                 │  (Adaptive Receptive Field)   │
               │                 │  Uses lum_map to blend        │
               │                 │  3×3, 5×5, 7×7 kernels        │
               │                 │       ↓                        │
               │                 │  Ending Conv: 64→3 ch         │
               │                 │       ↓                        │
               │                 │  + Residual (add input)       │
               │                 │       ↓                        │
               │                 │  Crop padding                  │
               │                 │                               │
               │                 ▼
               │  ┌──────────────────────────────────────────────┐
               │  │  Clamp to [0, 1]                             │
               │  │  Save to pass_outputs list                   │
               │  └──────────────────────────────────────────────┘
               │
               │  ┌──────────────────────────────────────┐
               │  │  PASS 2 (current = output of Pass 1) │
               │  └──────────────┬───────────────────────┘
               │                 │
               │                 ▼
               │  ┌──────────────────────────────────────────────┐
               │  │     forward_single(current, lum_map)         │
               │  │     Same U-Net backbone, refined input       │
               │  └──────────────┬───────────────────────────────┘
               │                 │
               │                 ▼
               │  ┌──────────────────────────────────────────────┐
               │  │  Clamp to [0, 1]                             │
               │  │  Append to pass_outputs list                 │
               │  └──────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│              NOVEL 6: TAM (Temporal Adaptation Memory)          │
│  File: novels/novel6_tam.py                                     │
│  Input: List of 2 outputs from passes                           │
│  Process:                                                       │
│    - Initialize GRU hidden state                                │
│    - For each pass output:                                      │
│      * Project 3→32 channels                                    │
│      * Flatten spatial dims                                     │
│      * GRU update (accumulates temporal info)                   │
│    - Project back: 32→3 channels                                │
│    - Add residual to last pass output                           │
│  Output: [1, 3, H, W] - Final refined enhancement              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FINAL CLAMP [0, 1]                            │
│  Output shape: [1, 3, H, W]                                     │
│  Range: 0.0 to 1.0                                              │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│              OPTIONAL POST-PROCESSING                           │
│  If enabled:                                                    │
│    1. Adaptive Denoising (stronger in dark regions)             │
│    2. Unsharp Masking (edge enhancement)                        │
│  Output: numpy array [H, W, 3], uint8, 0-255                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SAVE TO DISK                                 │
│  Convert: tensor → numpy → PIL Image                            │
│  Format: PNG/JPG                                                │
│  Location: output folder                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 DETAILED VIEW: Inside BioNAFBlock

```
Input [B, C, H, W]
       │
       ▼
┌──────────────────────────────────┐
│  First Half: Spatial Branch      │
├──────────────────────────────────┤
│  1. LayerNorm2d                  │
│  2. Conv1: 1×1, C→C*2           │
│  3. Conv2: 3×3 depthwise        │
│  4. SimpleGate: split & multiply│
│     [x1, x2] = chunk(2)         │
│     return x1 * x2              │
│  5. SCA (Squeeze & Excite)      │
│     GlobalAvgPool → Conv → ×    │
│  6. Conv3: 1×1, C*2→C           │
│  7. Dropout                      │
│  8. ★ NOVEL 1: RLIN ★           │
│     Center: 1×1 conv            │
│     Surround: 5×5 avgpool + 1×1 │
│     return x + α*(center-surround)│
│  9. + Residual (input × beta)   │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  Second Half: FFN Branch         │
├──────────────────────────────────┤
│  1. LayerNorm2d                  │
│  2. Conv4: 1×1, C→C*FFN_Expand  │
│  3. SimpleGate                   │
│  4. Conv5: 1×1, C*2→C           │
│  5. Dropout                      │
│  6. + Residual (previous × gamma)│
└──────────────┬───────────────────┘
               │
               ▼
          Output [B, C, H, W]
```

---

## 🔬 DETAILED VIEW: Inside FAEB (Novel 2)

```
Input features [B, C, H, W] at bottleneck
       │
       ▼
┌──────────────────────────────────────┐
│  Disable AMP (cuFFT needs float32)   │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  2D Real FFT                         │
│  torch.fft.rfft2()                   │
│  Output: Complex tensor [B, C, H, W//2+1] │
└──────────────┬───────────────────────┘
               │
               ├─────────────────┬─────────────────┐
               │                 │                 │
               ▼                 ▼                 │
        Amplitude           Phase                │
        torch.abs()      torch.angle()           │
        [B, C, H, W']   [B, C, H, W']           │
               │                 │                 │
               ▼                 ▼                 │
     Conv_Amp Network    Conv_Phase Network       │
     [Conv→PReLU→Conv]   [Conv→PReLU→Conv]       │
               │                 │                 │
               ▼                 ▼                 │
        amp_out            phase_out              │
        [B, C, H, W']     [B, C, H, W']          │
               │                 │                 │
               └────────┬────────┘                 │
                        │                          │
                        ▼                          │
     Recombine: complex = amp * exp(i*phase)      │
     torch.complex(real, imag)                     │
                        │                          │
                        ▼                          │
     Inverse FFT                                  │
     torch.fft.irfft2()                           │
     Output: [B, C, H, W]                         │
                        │                          │
                        ▼                          │
     + Residual (input × blend_param)             │
     blend ≈ 0.15 (learnable)                     │
└──────────────────────────────────────┘
               │
               ▼
      Enhanced features [B, C, H, W]
```

---

## 🎨 DETAILED VIEW: Inside ARFP (Novel 3)

```
Input features [B, C, H, W]
Luminance map [B, 1, H, W]
       │
       ▼
┌──────────────────────────────────────┐
│  Interpolate lum_map to feature size │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  Gate Network                        │
│  Conv2d(1→16, 3×3) → PReLU          │
│  Conv2d(16→3, 1×1) → Softmax        │
│  Output: weights [B, 3, H, W]       │
│  (sums to 1.0 per pixel)             │
└──────────────┬───────────────────────┘
               │
       ┌───────┴───────┬───────────┐
       │               │           │
       ▼               ▼           ▼
  weight[:,0]      weight[:,1]  weight[:,2]
  (small)          (medium)     (large)
       │               │           │
       ▼               ▼           ▼
  Conv 3×3        Conv 5×5    Conv 7×7
  depthwise       depthwise   depthwise
       │               │           │
       ▼               ▼           ▼
    small_out       med_out     large_out
    [B,C,H,W]       [B,C,H,W]   [B,C,H,W]
       │               │           │
       └───────┬───────┴───────────┘
               │
               ▼
  Blend: w0*small + w1*med + w2*large
  Output: [B, C, H, W]
  
  Dark pixels → larger weights on 7×7
  Bright pixels → larger weights on 3×3
```

---

## ⚡ TRAINING LOOP EXECUTION ORDER

```
train_bionafnet.py executed
       │
       ▼
┌──────────────────────────────────────┐
│  1. Parse arguments                  │
│  2. Create BioNAFNet model           │
│  3. Move to GPU/CPU                  │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  4. Call train(model, device)        │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  5. Setup datasets & dataloaders     │
│     - LOLv1 Train/Test               │
│     - LOLv2 Real Train               │
│     - LOLv2 Synthetic Train          │
│     Patch size: 128×128              │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  6. Setup optimizer & loss           │
│     - AdamW (lr=2e-4)                │
│     - TotalLoss (6 components)       │
│     - GradScaler (AMP)               │
│     - EMA (decay=0.9995)             │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│  7. FOR each epoch (0 to 999):       │
└──────────────┬───────────────────────┘
               │
               ├──► A. Build train_loader with current patch_size
               │
               ├──► B. Training phase:
               │    │
               │    ├── FOR each batch (low, high):
               │    │    │
               │    │    ├── Forward: out = model(low)
               │    │    │              ↑ SAME as inference!
               │    │    │
               │    │    ├── Loss: total, dict = criterion(out, high)
               │    │    │              ↑ Calculates 6 loss components
               │    │    │
               │    │    ├── Backward: scaler.scale(loss).backward()
               │    │    │
               │    │    ├── Check for NaN gradients
               │    │    │
               │    │    ├── Clip gradients (max_norm=0.5)
               │    │    │
               │    │    ├── Optimizer step
               │    │    │
               │    │    └── EMA update
               │    │
               │    └── Scheduler step (cosine annealing)
               │
               ├──► C. Validation phase:
               │    │
               │    ├── Set EMA model to eval mode
               │    │
               │    ├── FOR each val image:
               │    │    ├── out = ema_model(low)
               │    │    ├── Calculate PSNR
               │    │    └── Calculate SSIM
               │    │
               │    └── Compute average metrics
               │
               └──► D. Checkpointing:
                    │
                    ├── If PSNR improved:
                    │    └── Save best.pth (with EMA weights)
                    │
                    ├── Save latest.pth (for resume)
                    │
                    └── Every 50 epochs:
                         └── Save ckpt_{epoch}.pth
```

---

## 📊 LOSS CALCULATION BREAKDOWN

```
criterion(out, high) called
       │
       ▼
┌──────────────────────────────────────┐
│  TotalLoss.forward()                 │
│  File: losses.py, line 130           │
└──────────────┬───────────────────────┘
               │
               ├─────────────────────────────────────┬──────────────────┐
               │                                     │                  │
               ▼                                     ▼                  ▼
     CharbonnierLoss                        SSIMLoss          PerceptualLoss
     (robust L1)                        (structural sim)     (VGG features)
     eps=1e-3                             window=3×3        layers[:16]
               │                                     │                  │
               │                                     │                  │
               ▼                                     ▼                  ▼
          l_charb                              l_ssim            l_perc
          scalar                               scalar            scalar
               │                                     │                  │
               ├─────────────────────────────────────┼──────────────────┤
               │                                     │                  │
               ▼                                     ▼                  ▼
        EdgeLoss                             ColorLoss       WeberFechnerLoss
     (Sobel edges)                          (YUV space)      (NOVEL 7!)
     luminance-based                        U,V channels    1/(lum+eps) weight
               │                                     │                  │
               │                                     │                  │
               ▼                                     ▼                  ▼
          l_edge                               l_color           l_weber
          scalar                               scalar            scalar
               │                                     │                  │
               └─────────────────────────────────────┴──────────────────┘
                                                     │
                                                     ▼
                                          Weighted combination:
                                          
                                          total = 
                                            1.0  * l_charb +
                                            0.8  * l_ssim  +
                                            0.2  * l_perc  +
                                            0.25 * l_edge  +
                                            0.1  * l_color +
                                            0.3  * l_weber
                                            
                                                     │
                                                     ▼
                                          Return: total, {dict of losses}
```

---

## 🔄 COMPLETE END-TO-END EXAMPLE

**Scenario**: You run inference on a single low-light image

```bash
python infer_bionafnet.py --input ./test_images --output ./results --weights checkpoints/best.pth
```

**Execution trace**:

1. **Line 656-689**: Parse arguments
   - `args.input = "./test_images"`
   - `args.output = "./results"`
   - `args.weights = "checkpoints/best.pth"`

2. **Line 557**: Create device
   - `device = torch.device("cuda")` (if GPU available)

3. **Line 558**: Instantiate model
   - `model = BioNAFNet(n_passes=2)`
   - Creates all layers (~10M parameters)

4. **Line 562-577**: Load weights
   - `ckpt = torch.load("checkpoints/best.pth")`
   - `model.load_state_dict(ckpt["ema"])`
   - Loads EMA weights from training

5. **Line 579**: Set eval mode
   - `model.eval()` (disables dropout, uses running stats)

6. **Line 594-597**: Find images
   - Scans `./test_images` for .png, .jpg files
   - Suppose finds: `["img1.png", "img2.jpg"]`

7. **Line 617**: Start loop
   - `for fpath in tqdm(files):`

8. **First iteration** (`fpath = "img1.png"`):
   
   a. **Line 618-624**: Load image
      - `img = Image.open("img1.png")` → PIL Image, e.g., 600×400×3
      - Convert to numpy, normalize to [0,1]
      - `inp = tensor [1, 3, 400, 600]` on GPU
   
   b. **Line 630**: Forward pass
      - `out = model(inp)`
      - Calls `BioNAFNet.forward(inp)`
      
      **Inside forward()**:
      - Line 419: `x_prcm = self.prcm(inp)` → PRCM processing
      - Line 422: `x_spdp = self.spdp(x_prcm)` → Dual pathway
      - Line 424: `lum_map = luminance(inp)` → [1, 1, 400, 600]
      - Line 429-433: Loop for 2 passes:
        - Pass 1: `forward_single(x_spdp, lum_map)`
          * Encoder: 600×400 → 300×200 → 150×100 → 75×50 → 38×25
          * Bottleneck: 38×25 features, 1024 channels
          * FAEB: FFT enhancement at bottleneck
          * Decoder: 38×25 → 75×50 → 150×100 → 300×200 → 600×400
          * ARFP: Adaptive pooling using lum_map
          * Output: [1, 3, 400, 600]
        - Pass 2: `forward_single(output1, lum_map)`
          * Same architecture, refined input
          * Output: [1, 3, 400, 600]
      - Line 437: `final = self.tam([out1, out2])`
        * GRU aggregation of 2 passes
        * Output: [1, 3, 400, 600]
      - Line 441: `return final.clamp(0, 1)`
   
   c. **Line 639-640**: Convert to numpy
      - `out_np = out.squeeze().permute(1,2,0).cpu().numpy()`
      - Shape: [400, 600, 3]
      - Scale to [0, 255], clip, convert to uint8
   
   d. **Line 643-648**: Post-process (if enabled)
      - Denoise: adaptive strength based on luminance
      - Sharpen: unsharp masking
   
   e. **Line 651**: Save
      - `Image.fromarray(out_np).save("./results/img1.png")`

9. **Second iteration** (`fpath = "img2.jpg"`):
   - Repeat steps 8a-8e

10. **Line 653**: Print completion message

**Total time**: ~0.2-1.0 seconds per image (depending on GPU and resolution)

---

## 🎯 KEY CODE LOCATIONS REFERENCE

| Component | File | Lines | Function/Class |
|-----------|------|-------|----------------|
| Main entry (inference) | infer_bionafnet.py | 656-689 | `__main__` |
| Main entry (training) | train_bionafnet.py | 976-1002 | `__main__` |
| Model forward | train_bionafnet.py | 429-453 | `BioNAFNet.forward()` |
| Single pass | train_bionafnet.py | 402-427 | `BioNAFNet.forward_single()` |
| PRCM | novel4_prcm.py | 34-39 | `PhotoreceptorCurve.forward()` |
| SPDP | novel5_spdp.py | 41-47 | `DualPathway.forward()` |
| BioNAFBlock | nafnet_blocks.py | 73-91 | `BioNAFBlock.forward()` |
| RLIN | novel1_rlin.py | 33-36 | `LateralInhibition.forward()` |
| FAEB | novel2_faeb.py | 37-52 | `FrequencyBranch.forward()` |
| ARFP | novel3_arfp.py | 35-41 | `AdaptiveReceptiveField.forward()` |
| TAM | novel6_tam.py | 32-42 | `TemporalAdaptation.forward()` |
| Total Loss | losses.py | 130-154 | `TotalLoss.forward()` |
| Weber-Fechner | losses.py | 93-98 | `WeberFechnerLoss.forward()` |
| Training loop | train_bionafnet.py | 769-898 | `train()` function |
| Dataset loading | dataset.py | varies | `LOLDataset.__getitem__()` |

---

## 💡 UNDERSTANDING CHECK: Trace an Example

**Question**: If I input a 256×256 image, what are the tensor shapes at each stage?

**Answer**:

```
Input: [1, 3, 256, 256]

After PRCM: [1, 3, 256, 256]
After SPDP: [1, 3, 256, 256]
Lum_map: [1, 1, 256, 256]

PASS 1 - forward_single():
  After intro conv: [1, 64, 256, 256]
  
  Encoder 1 (64 ch, 2 blocks):
    After blocks: [1, 64, 256, 256]
    After downsample: [1, 128, 128, 128]
  
  Encoder 2 (128 ch, 2 blocks):
    After blocks: [1, 128, 128, 128]
    After downsample: [1, 256, 64, 64]
  
  Encoder 3 (256 ch, 4 blocks):
    After blocks: [1, 256, 64, 64]
    After downsample: [1, 512, 32, 32]
  
  Encoder 4 (512 ch, 8 blocks):
    After blocks: [1, 512, 32, 32]
    After downsample: [1, 1024, 16, 16]
  
  Middle (1024 ch, 12 blocks):
    After blocks: [1, 1024, 16, 16]
  
  FAEB:
    Input: [1, 1024, 16, 16]
    FFT → process → IFFT
    Output: [1, 1024, 16, 16]
  
  Decoder 1 (512 ch, 2 blocks):
    After upsample: [1, 512, 32, 32]
    + skip from Encoder 4
    After blocks: [1, 512, 32, 32]
  
  Decoder 2 (256 ch, 2 blocks):
    After upsample: [1, 256, 64, 64]
    + skip from Encoder 3
    After blocks: [1, 256, 64, 64]
  
  Decoder 3 (128 ch, 2 blocks):
    After upsample: [1, 128, 128, 128]
    + skip from Encoder 2
    After blocks: [1, 128, 128, 128]
  
  Decoder 4 (64 ch, 2 blocks):
    After upsample: [1, 64, 256, 256]
    + skip from Encoder 1
    After blocks: [1, 64, 256, 256]
  
  ARFP:
    Input: [1, 64, 256, 256] + lum_map [1, 1, 256, 256]
    Output: [1, 64, 256, 256]
  
  Ending conv:
    Input: [1, 64, 256, 256]
    Output: [1, 3, 256, 256]
  
  + Residual:
    [1, 3, 256, 256] + [1, 3, 256, 256]
    Output: [1, 3, 256, 256]

PASS 2 - forward_single():
  Same shapes, takes output of Pass 1 as input
  Final output: [1, 3, 256, 256]

TAM:
  Input: list of 2 tensors, each [1, 3, 256, 256]
  GRU processes flattened: [1*256*256, 32] hidden
  Output: [1, 3, 256, 256]

Final output: [1, 3, 256, 256]
Convert to numpy: [256, 256, 3]
```

This completes the comprehensive data flow visualization!
