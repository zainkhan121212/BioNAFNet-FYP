# BioNAFNet Teacher Model - Complete Code Flow Analysis

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture Summary](#architecture-summary)
3. [The 7 Biological Novelties](#the-7-biological-novelties)
4. [Complete Data Flow - Step by Step](#complete-data-flow---step-by-step)
5. [File-by-File Execution Guide](#file-by-file-execution-guide)
6. [Training Pipeline](#training-pipeline)
7. [Inference Pipeline](#inference-pipeline)
8. [Detailed Component Breakdown](#detailed-component-breakdown)

---

## Overview

**BioNAFNet** (Biologically-inspired NAFNet) is a low-light image enhancement model that integrates **7 biological novelties** inspired by human vision into the NAFNet backbone architecture.

### Key Files Location:
```
F:\low_light_enhancement\eye adaption\BioNAFNet\Teacher_Model\
├── code\
│   ├── train_bionafnet.py        # Main training script (ALL-IN-ONE)
│   ├── infer_bionafnet.py         # Standalone inference script
│   └── code\                      # Modular components folder
│       ├── model.py               # BioNAFNet model class
│       ├── losses.py              # Loss functions
│       ├── dataset.py             # Dataset loader
│       ├── nafnet_blocks.py       # Enhanced NAFNet blocks
│       ├── novels\                # 7 biological novelty modules
│       │   ├── novel1_rlin.py     # Retinal Lateral Inhibition
│       │   ├── novel2_faeb.py     # Frequency-Aware Branch
│       │   ├── novel3_arfp.py     # Adaptive Receptive Field
│       │   ├── novel4_prcm.py     # Photoreceptor Response Curve
│       │   ├── novel5_spdp.py     # Scotopic-Photopic Dual Pathway
│       │   └── novel6_tam.py      # Temporal Adaptation Memory
│       └── ...
└── checkpoints\
    └── best.pth                   # Best trained model weights
```

---

## Architecture Summary

### High-Level Pipeline:
```
Input Image → PRCM → SPDP → NAFNet Backbone → TAM → Output Image
                    (Novel 4)  (Novel 5)   (with Novel 1,2,3)  (Novel 6)
                                        ↓
                                    Loss Calculation (Novel 7)
```

### Network Configuration:
- **Width**: 64 channels
- **Encoder Blocks**: [2, 2, 4, 8] at 4 scales
- **Middle Blocks**: 12 BioNAFBlocks
- **Decoder Blocks**: [2, 2, 2, 2] at 4 scales
- **Total Parameters**: ~10-15 million (depending on configuration)
- **Multi-pass Refinement**: 2 passes by default

---

## The 7 Biological Novelties

### Novel 1: RLIN - Retinal Lateral Inhibition Network
**File**: `novels/novel1_rlin.py` (lines 21-36)  
**Inspiration**: Center-surround antagonism in retinal ganglion cells  
**Purpose**: Enhances local contrast and edge detection  
**Location in pipeline**: Inside each BioNAFBlock in encoder

### Novel 2: FAEB - Frequency-Aware Enhancement Branch  
**File**: `novels/novel2_faeb.py` (lines 22-52)  
**Inspiration**: Visual cortex processes spatial frequencies separately  
**Purpose**: Recovers high-frequency textures lost in low light  
**Location in pipeline**: At bottleneck of U-Net architecture

### Novel 3: ARFP - Adaptive Receptive Field Pooling
**File**: `novels/novel3_arfp.py` (lines 22-41)  
**Inspiration**: Rod cells have larger receptive fields in darkness  
**Purpose**: Dynamically adjusts kernel size based on luminance  
**Location in pipeline**: After decoder output, before final result

### Novel 4: PRCM - Photoreceptor Response Curve Modeling
**File**: `novels/novel4_prcm.py` (lines 25-39)  
**Inspiration**: Different gamma curves for rods vs cones  
**Purpose**: Simulates rod/cone response characteristics  
**Location in pipeline**: First preprocessing step (input stage)

### Novel 5: SPDP - Scotopic-Photopic Dual Pathway
**File**: `novels/novel5_spdp.py` (lines 23-54)  
**Inspiration**: Separate luminance (rod) and chrominance (cone) pathways  
**Purpose**: Processes brightness and color independently  
**Location in pipeline**: Second preprocessing step (after PRCM)

### Novel 6: TAM - Temporal Adaptation Memory
**File**: `novels/novel6_tam.py` (lines 23-42)  
**Inspiration**: Progressive dark adaptation over time  
**Purpose**: Multi-pass refinement using GRU memory  
**Location in pipeline**: Final aggregation stage

### Novel 7: WFPL - Weber-Fechner Perceptual Loss
**File**: `code/losses.py` (lines 85-98)  
**Inspiration**: Human perception more sensitive in darker regions  
**Purpose**: Weights loss function to prioritize dark region quality  
**Location in pipeline**: During training loss calculation only

---

## Complete Data Flow - Step by Step

### When You Input an Image During INFERENCE:

#### **STEP 1: Image Loading & Preprocessing**
**File**: `infer_bionafnet.py`  
**Lines**: 617-624

```python
# Line 618-619: Load image from disk
img = Image.open(fpath).convert("RGB")

# Line 622-624: Convert to tensor [B, C, H, W]
inp = torch.from_numpy(
    np.array(img).astype(np.float32) / 255.0
).permute(2, 0, 1).unsqueeze(0).to(device)
```

**What happens**:
- Image loaded as PIL Image (H×W×3, uint8, 0-255)
- Converted to numpy array, normalized to float32 (0-1)
- Permuted to PyTorch format: (C×H×W)
- Batch dimension added: (1×C×H×W)
- Moved to GPU/CPU device

---

#### **STEP 2: Forward Pass Through BioNAFNet**
**File**: `infer_bionafnet.py` or `train_bionafnet.py`  
**Class**: `BioNAFNet`  
**Method**: `forward()`  
**Lines**: 417-441 (in infer_bionafnet.py) or 429-453 (in train_bionafnet.py)

```python
def forward(self, x):
    # NOVEL 4: Photoreceptor response curve
    x_prcm = self.prcm(x)                    # ← STEP 2a
    
    # NOVEL 5: Scotopic-Photopic dual pathway
    x_spdp = self.spdp(x_prcm)               # ← STEP 2b
    
    lum_map = luminance(x)                   # ← Compute luminance map
    
    # Multi-pass refinement for TAM
    pass_outputs = []
    current = x_spdp
    for p in range(self.n_passes):           # ← Usually 2 passes
        out = self.forward_single(current, lum_map)  # ← STEP 2c
        out = out.clamp(0, 1)
        pass_outputs.append(out)
        current = out
    
    # NOVEL 6: TAM aggregates multi-pass results
    if self.n_passes > 1:
        final = self.tam(pass_outputs)       # ← STEP 2d
    else:
        final = pass_outputs[-1]
    
    return final.clamp(0, 1)
```

---

#### **STEP 2a: Photoreceptor Response Curve (PRCM)**
**File**: `novels/novel4_prcm.py`  
**Lines**: 34-39

```python
def forward(self, x):
    lum = luminance(x)  # Compute luminance: 0.299*R + 0.587*G + 0.114*B
    
    # Sigmoid gate: transitions from rod to cone dominance
    cone_weight = torch.sigmoid((lum - self.threshold) * 12)
    
    # Apply different gamma curves
    x_rod = torch.pow(x.clamp(1e-5, 1), self.rod_gamma)   # gamma ≈ 0.45
    x_cone = torch.pow(x.clamp(1e-5, 1), self.cone_gamma) # gamma ≈ 0.95
    
    # Blend based on luminance
    return x_rod * (1 - cone_weight) + x_cone * cone_weight
```

**What happens**:
- Dark pixels → rod_gamma (0.45) → brightens significantly
- Bright pixels → cone_gamma (0.95) → minimal change
- Smooth transition controlled by threshold parameter
- **Output**: Same shape as input, but with non-linear tone mapping

---

#### **STEP 2b: Scotopic-Photopic Dual Pathway (SPDP)**
**File**: `novels/novel5_spdp.py`  
**Lines**: 41-47

```python
def forward(self, x):
    # Convert RGB to YUV color space
    y, u, v = self.rgb_to_yuv(x)
    
    # Scotopic pathway: process luminance only
    lum_feat = self.scotopic(y)  # 2 conv layers with PReLU
    
    # Photopic pathway: process chrominance
    col_feat = self.photopic(torch.cat([u, v], dim=1))  # 2 conv layers
    
    # Fuse both pathways
    combined = torch.cat([lum_feat, col_feat], dim=1)
    residual = self.fuse(combined) * 0.2  # Small residual connection
    return x + residual
```

**What happens**:
- RGB → YUV conversion (separates brightness from color)
- Y channel (luminance) processed by "scotopic" network (2 convs)
- UV channels (chrominance) processed by "photopic" network (2 convs)
- Features concatenated and fused back to RGB residual
- **Output**: Same shape, enhanced luminance-color separation

---

#### **STEP 2c: NAFNet Backbone (Single Pass)**
**File**: `train_bionafnet.py` or `model.py`  
**Method**: `forward_single()`  
**Lines**: 391-415 (infer) or 402-427 (train)

This is the **core U-Net architecture** with encoder-decoder structure:

```python
def forward_single(self, inp, lum_map):
    B, C, H, W = inp.shape
    inp_padded = self.check_image_size(inp)  # Pad to multiple of 16
    
    # === ENCODER (Downsampling) ===
    x = self.intro(inp_padded)  # Initial conv: 3→64 channels
    encs = []
    for encoder, down in zip(self.encoders, self.downs):
        x = encoder(x)          # Process at this scale
        encs.append(x)          # Save for skip connection
        x = down(x)             # Downsample 2x
    
    # === BOTTLENECK ===
    x = self.middle_blks(x)     # 12 BioNAFBlocks
    x = self.faeb(x)            # NOVEL 2: Frequency enhancement
    
    # === DECODER (Upsampling) ===
    for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
        x = up(x)               # Upsample 2x
        x = x + enc_skip        # Add skip connection
        x = decoder(x)          # Process at this scale
    
    # === OUTPUT STAGE ===
    x = self.arfp(x, lum_map)   # NOVEL 3: Adaptive receptive field
    x = self.ending(x)          # Final conv: 64→3 channels
    x = x + inp_padded          # Residual learning
    return x[:, :, :H, :W]      # Crop padding
```

**Detailed breakdown**:

**Encoder path** (4 scales):
- Scale 1: 64 ch, 2 BioNAFBlocks → downsample to 128 ch
- Scale 2: 128 ch, 2 BioNAFBlocks → downsample to 256 ch
- Scale 3: 256 ch, 4 BioNAFBlocks → downsample to 512 ch
- Scale 4: 512 ch, 8 BioNAFBlocks → downsample to 1024 ch

**Bottleneck**:
- 1024 channels, 12 BioNAFBlocks
- **NOVEL 2 (FAEB)**: FFT-based frequency enhancement

**Decoder path** (4 scales):
- Scale 4: 1024→512 ch (upsample) + skip connection → 2 BioNAFBlocks
- Scale 3: 512→256 ch (upsample) + skip connection → 2 BioNAFBlocks
- Scale 2: 256→128 ch (upsample) + skip connection → 2 BioNAFBlocks
- Scale 1: 128→64 ch (upsample) + skip connection → 2 BioNAFBlocks

**Output**:
- **NOVEL 3 (ARFP)**: Luminance-guided adaptive pooling
- Final conv: 64→3 channels
- Residual connection: add original padded input
- Crop to original size

---

#### **Inside Each BioNAFBlock**
**File**: `nafnet_blocks.py`  
**Lines**: 73-91

```python
def forward(self, inp):
    # === First half: Spatial gating branch ===
    x = self.norm1(inp)
    x = self.conv1(x)           # 1x1 conv: expand channels
    x = self.conv2(x)           # 3x3 depthwise conv
    x = self.sg(x)              # SimpleGate: split & multiply
    x = x * self.sca(x)         # Channel attention (Squeeze-and-Excitation)
    x = self.conv3(x)           # 1x1 conv: reduce channels
    x = self.dropout1(x)
    
    # NOVEL 1: RLIN lateral inhibition
    x = self.rlin(x)
    
    y = inp + x * self.beta     # Residual connection with learnable weight
    
    # === Second half: FFN branch ===
    x = self.conv4(self.norm2(y))  # 1x1 conv: expand
    x = self.sg(x)                 # SimpleGate
    x = self.conv5(x)              # 1x1 conv: reduce
    x = self.dropout2(x)
    
    return y + x * self.gamma      # Final residual connection
```

**Inside RLIN (Novel 1)**:
**File**: `novels/novel1_rlin.py`  
**Lines**: 33-36

```python
def forward(self, x):
    c = self.center(x)      # 1x1 conv: fine detail
    s = self.surround(x)    # 5x5 avg pool + 1x1: broad context
    return x + self.alpha * (c - s)  # Center-surround difference
```

---

#### **STEP 2d: Temporal Adaptation Memory (TAM)**
**File**: `novels/novel6_tam.py`  
**Lines**: 32-42

After 2 forward passes, TAM aggregates them:

```python
def forward(self, pass_outputs):  # List of 2 outputs
    B, _, H, W = pass_outputs[0].shape
    
    # Initialize GRU hidden state
    hidden = torch.zeros(B * H * W, self.gru.hidden_size, device=...)
    
    # Process each pass through GRU
    for out in pass_outputs:
        feat = self.proj_in(out)  # Project 3 ch → 32 ch
        feat = feat.permute(0, 2, 3, 1).reshape(B * H * W, -1)
        hidden = self.gru(feat, hidden)  # GRU update
    
    # Project back to image space
    out = hidden.reshape(B, H, W, -1).permute(0, 3, 1, 2)
    residual = self.proj_out(out) * 0.15  # 32 ch → 3 ch
    return pass_outputs[-1] + residual
```

**What happens**:
- Treats spatial pixels as sequence for GRU
- Accumulates information across passes
- Produces refined output combining temporal memory
- **Output**: Final enhanced image (1×3×H×W)

---

#### **STEP 3: Post-Processing (Optional)**
**File**: `infer_bionafnet.py`  
**Function**: `post_process()`  
**Lines**: 496-511

If enabled during inference:

```python
def post_process(img_np, denoise_strength=5, sharpen_strength=0.4):
    # Step 1: Adaptive denoising (stronger in dark regions)
    if denoise_strength > 0:
        img_np = adaptive_denoise(img_np, strength=denoise_strength)
    
    # Step 2: Unsharp masking for edge enhancement
    if sharpen_strength > 0:
        img_np = unsharp_mask(img_np, sigma=1.0, strength=sharpen_strength)
    
    return img_np
```

---

#### **STEP 4: Save Output**
**File**: `infer_bionafnet.py`  
**Lines**: 639-651

```python
# Convert tensor to numpy image
out_np = (out.squeeze().permute(1, 2, 0).cpu().numpy() * 255.0
          ).clip(0, 255).astype(np.uint8)

# Apply post-processing if enabled
if use_postprocess:
    out_np = post_process(out_np, denoise_strength=denoise, 
                          sharpen_strength=sharpen)

# Save to disk
Image.fromarray(out_np).save(os.path.join(output_dir, fname))
```

---

### When You Run TRAINING:

#### **Training Data Flow:**

**File**: `train_bionafnet.py`  
**Function**: `train()`  
**Lines**: 721-902

**Main training loop** (lines 769-898):

```python
for epoch in range(start_epoch, EPOCHS):
    # Get progressive patch size
    ps = get_patch_size(epoch)
    
    # Build training datasets
    train_datasets = [
        LOLDataset(LOLv1_TRAIN_IN, LOLv1_TRAIN_GT, patch_size=ps, augment=True),
        LOLDataset(LOLv2R_TRAIN_IN, LOLv2R_TRAIN_GT, patch_size=ps, augment=True),
        LOLDataset(LOLv2S_TRAIN_IN, LOLv2S_TRAIN_GT, patch_size=ps, augment=True),
    ]
    train_loader = DataLoader(ConcatDataset(train_datasets), ...)
    
    model.train()
    for step, (low, high) in enumerate(train_loader):
        low = low.to(device)   # Low-light input
        high = high.to(device) # Normal-light ground truth
        
        # Forward pass through BioNAFNet
        with torch.amp.autocast(device_type=device.type, enabled=USE_AMP):
            out = model(low)                    # ← Same forward() as inference
            loss, loss_dict = criterion(out, high)  # ← Calculate all losses
            loss = loss / ACCUM_STEPS
        
        # Backward pass with gradient scaling
        scaler.scale(loss).backward()
        
        if step % ACCUM_STEPS == 0:
            # Check for NaN gradients
            # Clip gradients
            # Update optimizer
            # Update EMA (Exponential Moving Average)
    
    # Validation
    validate with EMA model
    save best checkpoint if PSNR improved
```

---

#### **Loss Calculation (Novel 7)**
**File**: `losses.py`  
**Class**: `TotalLoss`  
**Lines**: 119-154

```python
def forward(self, out, target):
    # Calculate 6 different loss components
    l_charb = self.charb(out, target)    # Charbonnier (robust L1)
    l_ssim = self.ssim(out, target)      # Structural similarity
    l_perc = self.perc(out, target)      # VGG perceptual loss
    l_edge = self.edge(out, target)      # Edge preservation
    l_color = self.color(out, target)    # Color accuracy (YUV)
    l_weber = self.weber(out, target)    # NOVEL 7: Weber-Fechner
    
    # Weighted combination
    total = (
        1.0 * l_charb +   # Base reconstruction
        0.8 * l_ssim +    # Structural quality
        0.2 * l_perc +    # Perceptual realism
        0.25 * l_edge +   # Edge sharpness
        0.1 * l_color +   # Color fidelity
        0.3 * l_weber     # Dark region emphasis
    )
    
    return total, {individual loss values for logging}
```

**Weber-Fechner Loss** (Novel 7):
**Lines**: 85-98

```python
def forward(self, pred, target):
    lum = luminance(target)              # Compute luminance
    weight = 1.0 / (lum + self.eps)      # Inverse luminance weighting
    weight = weight / (weight.mean() + 1e-6)  # Normalize
    diff = torch.abs(pred - target)
    return (diff * weight).mean()        # Weighted MAE
```

**Key insight**: Errors in dark regions are penalized MORE than errors in bright regions, matching human visual sensitivity.

---

## File-by-File Execution Guide

### For INFERENCE (Running the model):

**Entry Point**: `infer_bionafnet.py`

1. **Line 656-689**: Parse command-line arguments
2. **Line 558**: Create BioNAFNet model instance
3. **Line 562-577**: Load checkpoint weights (.pth file)
4. **Line 579**: Set model to eval mode
5. **Line 594-597**: Find all images in input folder
6. **Line 616-651**: Loop through each image:
   - **Line 618-624**: Load and preprocess image
   - **Line 630**: Call `model(inp)` → executes `forward()` method
   - **Line 639-640**: Convert output tensor to numpy
   - **Line 643-648**: Apply post-processing (optional)
   - **Line 651**: Save enhanced image

**Execution order when you call `model(inp)`**:
1. `BioNAFNet.forward()` - line 417
2. `PhotoreceptorCurve.forward()` - line 419
3. `DualPathway.forward()` - line 422
4. Loop for n_passes (usually 2):
   - `BioNAFNet.forward_single()` - line 430
     - Encoder blocks (with RLIN)
     - Middle blocks + FAEB
     - Decoder blocks
     - ARFP at output
5. `TemporalAdaptation.forward()` - line 437
6. Return clamped output

---

### For TRAINING:

**Entry Point**: `train_bionafnet.py`

1. **Line 976-1002**: Parse arguments, create model
2. **Line 998-999**: Call `train(model, device)`
3. **Inside `train()` function** (line 721):
   - **Line 722-733**: Log configuration
   - **Line 736-738**: Create validation dataloader
   - **Line 740-749**: Setup optimizer, scheduler, EMA
   - **Line 756-767**: Resume from checkpoint if exists
   - **Line 769-898**: Main training loop:
     - **Line 771-788**: Build datasets with current patch size
     - **Line 794-839**: Inner training loop:
       - **Line 802-808**: Forward pass + loss calculation
       - **Line 810-831**: Backward pass + optimizer step
       - **Line 833-839**: Update progress bar
     - **Line 841**: Learning rate scheduler step
     - **Line 844-862**: Validation with EMA model
     - **Line 869-897**: Save checkpoints

**Execution order for each batch**:
1. Load low-light and normal-light image pair
2. Move to GPU
3. Enable mixed precision (AMP)
4. Call `model(low)` → same forward() as inference
5. Call `criterion(out, high)` → calculate TotalLoss
6. Backpropagate gradients
7. Gradient clipping
8. Optimizer step
9. EMA update
10. Logging

---

## Detailed Component Breakdown

### 1. BioNAFBlock Structure

**Purpose**: Core building block of NAFNet, enhanced with RLIN

**Components**:
- LayerNorm2d: Normalization (like BatchNorm but per-sample)
- SimpleGate: Splits channels, multiplies halves (non-linearity)
- Depthwise convolutions: Efficient spatial processing
- Squeeze-and-Excitation Attention: Channel-wise feature selection
- RLIN: Lateral inhibition for edge enhancement
- Learnable skip weights (beta, gamma): Adaptive residual connections

**Data flow inside block**:
```
Input → Norm1 → Conv1 (expand) → Conv2 (depthwise) → SimpleGate 
    → SCA (attention) → Conv3 (reduce) → Dropout1 → RLIN 
    → + Input (scaled by beta)
    → Norm2 → Conv4 (expand) → SimpleGate → Conv5 (reduce) → Dropout2 
    → + Previous (scaled by gamma) → Output
```

---

### 2. Frequency Branch (FAEB)

**Purpose**: Recover high-frequency textures via Fourier domain processing

**How it works**:
1. Input: Feature map (B×C×H×W)
2. Apply 2D FFT → Complex spectrum
3. Split into amplitude and phase
4. Process each with separate CNNs
5. Recombine: new_complex = amp_out * exp(i * phase_out)
6. Inverse FFT → Enhanced features
7. Add residual connection

**Why it helps**: Low-light degradation primarily affects high frequencies. FFT makes these explicit and easier to recover.

---

### 3. Adaptive Receptive Field (ARFP)

**Purpose**: Dynamic kernel selection based on local brightness

**Mechanism**:
- Three parallel depthwise convolutions: 3×3, 5×5, 7×7
- Gate network takes luminance map → produces 3 weights (softmax)
- Dark regions → higher weight on 7×7 (large receptive field)
- Bright regions → higher weight on 3×3 (small receptive field)

**Biological basis**: Matches how rod cells pool over larger areas in peripheral/dark vision.

---

### 4. Temporal Adaptation (TAM)

**Purpose**: Iterative refinement simulating dark adaptation

**Process**:
1. Run forward pass → output1
2. Feed output1 as input to second pass → output2
3. Project both to feature space
4. Process through GRU cell (accumulates information)
5. Project back to image space
6. Add residual to last output

**Why 2 passes?**: First pass does coarse enhancement, second pass refines details. GRU learns what to keep from each pass.

---

## Training Configuration

**Hyperparameters** (from `train_bionafnet.py`):
```python
EPOCHS = 1000
BATCH_SIZE = 4
ACCUM_STEPS = 2              # Effective batch = 8
INIT_LR = 2e-4
MIN_LR = 1e-6
WEIGHT_DECAY = 1e-4
GRAD_CLIP = 0.5
EMA_DECAY = 0.9995
PATCH_SIZE = 128 (fixed)
WIDTH = 64 channels
ENC_BLKS = [2, 2, 4, 8]
MIDDLE_BLK_NUM = 12
DEC_BLKS = [2, 2, 2, 2]
N_PASSES = 2
```

**Datasets**:
- LOLv1 Train/Test
- LOLv2 Real-captured Train
- LOLv2 Synthetic Train

**Augmentations**:
- Random cropping (128×128 patches)
- Horizontal/vertical flips
- 90° rotations
- MixUp (20% probability)

**Optimizer**: AdamW with Cosine Annealing Warm Restarts

**Loss weights**:
- Charbonnier: 1.0
- SSIM: 0.8
- Perceptual (VGG): 0.2
- Edge: 0.25
- Color: 0.1
- Weber-Fechner: 0.3

---

## Key Differences: Training vs Inference

| Aspect | Training | Inference |
|--------|----------|-----------|
| Input size | 128×128 patches | Full resolution |
| Batch size | 4 | 1 |
| Mixed precision | Enabled (AMP) | Disabled (full precision for cuFFT) |
| Augmentation | Yes | No |
| Loss calculation | Yes | No |
| Gradient updates | Yes | No |
| EMA tracking | Yes | Uses EMA weights |
| Self-ensemble | No | Optional (8x TTA) |
| Post-processing | No | Optional |

---

## Common Questions Answered

### Q: Where does the image enter the model?
**A**: 
- **Inference**: `infer_bionafnet.py` line 630: `out = model(inp)`
- **Training**: `train_bionafnet.py` line 806: `out = model(low)`
- Both call `BioNAFNet.forward()` at line 417/429

### Q: What is the exact execution order?
**A**: 
```
Input → PRCM → SPDP → [Pass 1: Encoder→Bottleneck→Decoder→ARFP] 
    → [Pass 2: Encoder→Bottleneck→Decoder→ARFP] 
    → TAM → Output
```

### Q: Where are the 7 novelties applied?
**A**:
1. **RLIN**: Inside each encoder BioNAFBlock (line 331 in train_bionafnet.py)
2. **FAEB**: At bottleneck after middle blocks (line 404/415)
3. **ARFP**: After decoder before final output (line 411/423)
4. **PRCM**: First preprocessing step (line 419/431)
5. **SPDP**: Second preprocessing step (line 422/434)
6. **TAM**: Final aggregation after all passes (line 437/449)
7. **WFPL**: Only during training loss calculation (losses.py line 93)

### Q: How many times does an image go through the backbone?
**A**: `n_passes` times (default = 2). Each pass refines the previous output.

### Q: What is EMA and why use it?
**A**: Exponential Moving Average of model weights. Updated every training step with decay=0.9995. Provides more stable, better-generalizing weights. Used for validation and final inference.

### Q: Why is inference slower than training per image?
**A**: 
- Training uses 128×128 patches
- Inference uses full-resolution images (e.g., 600×400)
- Larger spatial dimensions = more computation
- cuFFT in FAEB is slower on non-power-of-2 dimensions

---

## Debugging Tips

### To trace execution:
Add print statements in `forward()`:
```python
def forward(self, x):
    print(f"Input shape: {x.shape}")
    x_prcm = self.prcm(x)
    print(f"After PRCM: {x_prcm.shape}")
    x_spdp = self.spdp(x_prcm)
    print(f"After SPDP: {x_spdp.shape}")
    # ... etc
```

### To check which file/line is executing:
```python
import inspect
print(f"Current file: {inspect.getfile(self.__class__)}")
print(f"Current method: {inspect.currentframe().f_code.co_name}")
```

### To verify model architecture:
```python
model = BioNAFNet()
print(model)  # Prints all layers
print(f"Total parameters: {sum(p.numel() for p in model.parameters()):,}")
```

---

## Summary

**BioNAFNet Teacher Model** is a sophisticated low-light enhancement system that:

1. **Preprocesses** input with biologically-inspired modules (PRCM, SPDP)
2. **Processes** through enhanced U-Net with 7 novelties integrated
3. **Refines** via multi-pass temporal adaptation (TAM)
4. **Optimizes** with perceptually-motivated loss (WFPL + 5 others)

The complete data flow for a single image during inference:
```
Load Image → Normalize → PRCM → SPDP → 
  [Forward Pass 1: Encoder→FAEB→Decoder→ARFP] → 
  [Forward Pass 2: Encoder→FAEB→Decoder→ARFP] → 
TAM → Clamp → [Post-process] → Save
```

**Total execution time**: ~0.1-0.5 seconds per image (depending on resolution and GPU)

**Best practices**:
- Use EMA weights for inference (automatically done)
- Enable self-ensemble for critical applications (8x slower, better quality)
- Tune post-processing parameters based on noise level
- Use patch_size=128 for fast training, increase for better quality

---

*Document generated for BioNAFNet Teacher Model analysis*
*Date: 2026-04-12*
*Files analyzed: train_bionafnet.py, infer_bionafnet.py, model.py, losses.py, nafnet_blocks.py, novels/*.py*
