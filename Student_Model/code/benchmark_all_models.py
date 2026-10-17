"""
BioNAFNet — Comprehensive Model Benchmark
==========================================
Tests Teacher (154M), Student-350 (24M), and Student-693 (24M) on LOLv1/v2.
Reports PSNR, SSIM, inference speed, and model size.
"""

import os, sys, time, math, glob, argparse
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr

# ═══════════════════════════════════════════════════════════════════════════════
# Architecture (shared between teacher and student, only hyperparams differ)
# ═══════════════════════════════════════════════════════════════════════════════

def luminance(x):
    return 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]

class LateralInhibition(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.center = nn.Conv2d(ch, ch, 1, bias=True)
        self.surround = nn.Sequential(nn.AvgPool2d(5, stride=1, padding=2), nn.Conv2d(ch, ch, 1, bias=True))
        self.alpha = nn.Parameter(torch.ones(1) * 0.3)
    def forward(self, x):
        return x + self.alpha * (self.center(x) - self.surround(x))

class FrequencyBranch(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.conv_amp = nn.Sequential(nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1))
        self.conv_phase = nn.Sequential(nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1))
        self.blend = nn.Parameter(torch.ones(1) * 0.15)
    def forward(self, x):
        B, C, H, W = x.shape
        with torch.amp.autocast(device_type='cuda', enabled=False):
            x_fp32 = x.float()
            fft = torch.fft.rfft2(x_fp32, norm="ortho")
            amp, phase = torch.abs(fft), torch.angle(fft)
            amp_out, phase_out = self.conv_amp(amp), self.conv_phase(phase)
            real, imag = amp_out * torch.cos(phase_out), amp_out * torch.sin(phase_out)
            out = torch.fft.irfft2(torch.complex(real, imag), s=(H, W), norm="ortho")
        return x + self.blend * out.to(x.dtype)

class AdaptiveReceptiveField(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.small = nn.Conv2d(ch, ch, 3, padding=1, groups=ch, bias=True)
        self.medium = nn.Conv2d(ch, ch, 5, padding=2, groups=ch, bias=True)
        self.large = nn.Conv2d(ch, ch, 7, padding=3, groups=ch, bias=True)
        self.gate = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.PReLU(16), nn.Conv2d(16, 3, 1), nn.Softmax(dim=1))
    def forward(self, x, lum_map):
        lum = F.interpolate(lum_map, size=x.shape[-2:], mode="bilinear", align_corners=False)
        w = self.gate(lum)
        return w[:, 0:1] * self.small(x) + w[:, 1:2] * self.medium(x) + w[:, 2:3] * self.large(x)

class PhotoreceptorCurve(nn.Module):
    def __init__(self):
        super().__init__()
        self.rod_gamma = nn.Parameter(torch.tensor([0.45]))
        self.cone_gamma = nn.Parameter(torch.tensor([0.95]))
        self.threshold = nn.Parameter(torch.tensor([0.25]))
    def forward(self, x):
        lum = luminance(x)
        cone_weight = torch.sigmoid((lum - self.threshold) * 12)
        return torch.pow(x.clamp(1e-5, 1), self.rod_gamma) * (1 - cone_weight) + \
               torch.pow(x.clamp(1e-5, 1), self.cone_gamma) * cone_weight

class DualPathway(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.scotopic = nn.Sequential(nn.Conv2d(1, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch))
        self.photopic = nn.Sequential(nn.Conv2d(2, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch))
        self.fuse = nn.Sequential(nn.Conv2d(ch * 2, ch, 1), nn.PReLU(ch), nn.Conv2d(ch, 3, 1), nn.Tanh())
    def forward(self, x):
        r, g, b = x[:, 0:1], x[:, 1:2], x[:, 2:3]
        y = 0.299*r+0.587*g+0.114*b
        u = -0.147*r-0.289*g+0.436*b
        v = 0.615*r-0.515*g-0.100*b
        feat = torch.cat([self.scotopic(y), self.photopic(torch.cat([u, v], dim=1))], dim=1)
        return x + self.fuse(feat) * 0.2

class TemporalAdaptation(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.gru = nn.GRUCell(ch, ch)
        self.proj_in = nn.Conv2d(3, ch, 1)
        self.proj_out = nn.Conv2d(ch, 3, 1)
    def forward(self, pass_outputs):
        B, _, H, W = pass_outputs[0].shape
        h = torch.zeros(B * H * W, self.gru.hidden_size, device=pass_outputs[0].device)
        for out in pass_outputs:
            feat = self.proj_in(out).permute(0, 2, 3, 1).reshape(B * H * W, -1)
            h = self.gru(feat, h)
        return pass_outputs[-1] + self.proj_out(h.reshape(B, H, W, -1).permute(0, 3, 1, 2)) * 0.15

class LayerNorm2d(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(channels))
        self.bias = nn.Parameter(torch.zeros(channels))
    def forward(self, x):
        u = x.mean(1, keepdim=True)
        s = (x - u).pow(2).mean(1, keepdim=True)
        x = (x - u) / torch.sqrt(s + 1e-6)
        return self.weight[None, :, None, None] * x + self.bias[None, :, None, None]

class SimpleGate(nn.Module):
    def forward(self, x):
        x1, x2 = x.chunk(2, dim=1)
        return x1 * x2

class BioNAFBlock(nn.Module):
    def __init__(self, c, DW_Expand=2, FFN_Expand=2, use_rlin=True):
        super().__init__()
        dw = c * DW_Expand
        self.conv1 = nn.Conv2d(c, dw, 1)
        self.conv2 = nn.Conv2d(dw, dw, 3, padding=1, groups=dw)
        self.conv3 = nn.Conv2d(dw // 2, c, 1)
        self.sca = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Conv2d(dw // 2, dw // 2, 1))
        self.conv4 = nn.Conv2d(c, c * FFN_Expand, 1)
        self.conv5 = nn.Conv2d(c * FFN_Expand // 2, c, 1)
        self.norm1 = LayerNorm2d(c)
        self.norm2 = LayerNorm2d(c)
        self.sg = SimpleGate()
        self.beta = nn.Parameter(torch.zeros((1, c, 1, 1)))
        self.gamma = nn.Parameter(torch.zeros((1, c, 1, 1)))
        self.rlin = LateralInhibition(c) if use_rlin else nn.Identity()
    def forward(self, inp):
        x = self.norm1(inp)
        x = self.conv1(x); x = self.conv2(x); x = self.sg(x)
        x = x * self.sca(x); x = self.conv3(x); x = self.rlin(x)
        y = inp + x * self.beta
        x = self.norm2(y); x = self.conv4(x); x = self.sg(x); x = self.conv5(x)
        return y + x * self.gamma

class BioNAFNet(nn.Module):
    def __init__(self, img_channel=3, width=64, middle_blk_num=12,
                 enc_blk_nums=[2,2,4,8], dec_blk_nums=[2,2,2,2], n_passes=2):
        super().__init__()
        self.n_passes = n_passes
        self.prcm = PhotoreceptorCurve()
        self.spdp = DualPathway(ch=32)
        self.intro = nn.Conv2d(img_channel, width, 3, padding=1)
        self.ending = nn.Conv2d(width, img_channel, 3, padding=1)
        self.encoders, self.decoders, self.ups, self.downs = nn.ModuleList(), nn.ModuleList(), nn.ModuleList(), nn.ModuleList()
        chan = width
        for i, num in enumerate(enc_blk_nums):
            self.encoders.append(nn.Sequential(*[BioNAFBlock(chan, use_rlin=(i < len(enc_blk_nums)-1)) for _ in range(num)]))
            self.downs.append(nn.Conv2d(chan, 2 * chan, 2, 2)); chan *= 2
        self.middle_blks = nn.Sequential(*[BioNAFBlock(chan, use_rlin=False) for _ in range(middle_blk_num)])
        self.faeb = FrequencyBranch(chan)
        for num in dec_blk_nums:
            self.ups.append(nn.Sequential(nn.Conv2d(chan, chan * 2, 1, bias=False), nn.PixelShuffle(2))); chan //= 2
            self.decoders.append(nn.Sequential(*[BioNAFBlock(chan, use_rlin=False) for _ in range(num)]))
        self.arfp = AdaptiveReceptiveField(chan)
        self.tam = TemporalAdaptation(ch=32)
        self.padder_size = 2 ** len(self.encoders)

    def forward_single(self, inp, lum_map):
        B, C, H, W = inp.shape
        mod_h = (self.padder_size - H % self.padder_size) % self.padder_size
        mod_w = (self.padder_size - W % self.padder_size) % self.padder_size
        x = self.intro(F.pad(inp, (0, mod_w, 0, mod_h), mode='reflect'))
        encs = []
        for enc, down in zip(self.encoders, self.downs):
            x = enc(x); encs.append(x); x = down(x)
        x = self.middle_blks(x); x = self.faeb(x)
        for dec, up, skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x); x = x + skip; x = dec(x)
        x = self.arfp(x, lum_map); x = self.ending(x)
        x = x + F.pad(inp, (0, mod_w, 0, mod_h), mode='reflect')
        return x[:, :, :H, :W]

    def forward(self, x):
        x_in = self.spdp(self.prcm(x))
        lum_map = luminance(x)
        pass_outputs, curr = [], x_in
        for _ in range(self.n_passes):
            out = self.forward_single(curr, lum_map).clamp(0, 1)
            pass_outputs.append(out); curr = out
        return self.tam(pass_outputs).clamp(0, 1) if self.n_passes > 1 else pass_outputs[-1]


# ═══════════════════════════════════════════════════════════════════════════════
# Benchmark Logic
# ═══════════════════════════════════════════════════════════════════════════════

DATA_ROOT = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data"
DATASETS = {
    "LOLv1": {
        "in": os.path.join(DATA_ROOT, "LOLv1", "Test", "input"),
        "gt": os.path.join(DATA_ROOT, "LOLv1", "Test", "target")
    },
    "LOLv2_Real": {
        "in": os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Test", "Low"),
        "gt": os.path.join(DATA_ROOT, "LOLv2", "Real_captured", "Test", "Normal")
    },
    "LOLv2_Synthetic": {
        "in": os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Test", "Low"),
        "gt": os.path.join(DATA_ROOT, "LOLv2", "Synthetic", "Test", "Normal")
    }
}

class LOLDataset(Dataset):
    def __init__(self, input_dir, target_dir):
        self.input_files = sorted(glob.glob(os.path.join(input_dir, "*.*")))
        self.target_files = sorted(glob.glob(os.path.join(target_dir, "*.*")))
    def __len__(self): return len(self.input_files)
    def __getitem__(self, idx):
        low = torch.from_numpy(np.array(Image.open(self.input_files[idx]).convert("RGB")).astype(np.float32) / 255.0).permute(2, 0, 1)
        high = torch.from_numpy(np.array(Image.open(self.target_files[idx]).convert("RGB")).astype(np.float32) / 255.0).permute(2, 0, 1)
        return low, high


def benchmark_model(model, model_name, device):
    """Test a single model on all datasets."""
    model.eval()
    total_params = sum(p.numel() for p in model.parameters())
    size_mb = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024**2)
    
    print(f"\n{'='*70}")
    print(f"  MODEL: {model_name}")
    print(f"  Parameters: {total_params:,}  |  Size: {size_mb:.1f} MB")
    print(f"{'='*70}")
    
    results = {}
    
    for d_name, d_paths in DATASETS.items():
        if not os.path.exists(d_paths["in"]):
            print(f"  Skipping {d_name}: path not found.")
            continue
        
        ds = LOLDataset(d_paths["in"], d_paths["gt"])
        loader = DataLoader(ds, batch_size=1, shuffle=False)
        
        psnrs, ssims, times = [], [], []
        
        with torch.no_grad():
            for i, (low, high) in enumerate(loader):
                if low.shape != high.shape:
                    continue
                low, high = low.to(device), high.to(device)
                
                # Warmup on first image
                if i == 0:
                    _ = model(low)
                    torch.cuda.synchronize()
                
                start = time.time()
                out = model(low)
                torch.cuda.synchronize()
                elapsed = time.time() - start
                times.append(elapsed)
                
                out_np = out.squeeze().permute(1, 2, 0).cpu().numpy()
                high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()
                p = calc_psnr(high_np, out_np, data_range=1.0)
                s = calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)
                psnrs.append(p)
                ssims.append(s)
        
        avg_psnr = np.mean(psnrs)
        avg_ssim = np.mean(ssims)
        avg_time = np.mean(times)
        fps = 1.0 / avg_time if avg_time > 0 else 0
        
        results[d_name] = {
            "psnr": avg_psnr, "ssim": avg_ssim,
            "time_ms": avg_time * 1000, "fps": fps,
            "num_images": len(psnrs)
        }
        
        print(f"\n  {d_name} ({len(psnrs)} images):")
        print(f"    PSNR: {avg_psnr:.2f} dB  |  SSIM: {avg_ssim:.4f}")
        print(f"    Speed: {avg_time*1000:.1f} ms/img  |  {fps:.1f} FPS")
    
    results["params"] = total_params
    results["size_mb"] = size_mb
    return results


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    
    all_results = {}
    
    # ── 1. Teacher Model (154M params) ──────────────────────────────────────
    teacher_ckpt = r"F:\low_light_enhancement\eye adaption\BioNAFNet\checkpoints\best.pth"
    if os.path.exists(teacher_ckpt):
        print("\n\nLoading Teacher Model...")
        teacher = BioNAFNet(width=64, middle_blk_num=12,
                            enc_blk_nums=[2,2,4,8], dec_blk_nums=[2,2,2,2], n_passes=2).to(device)
        ckpt = torch.load(teacher_ckpt, map_location=device, weights_only=False)
        teacher.load_state_dict(ckpt.get("ema", ckpt.get("model")))
        print(f"  Loaded from epoch {ckpt.get('epoch', '?')}, train best_psnr: {ckpt.get('best_psnr', 0):.2f}")
        all_results["Teacher (154M, n_passes=2)"] = benchmark_model(teacher, "Teacher BioNAFNet (154M, 2-pass)", device)
        del teacher; torch.cuda.empty_cache()
    
    # ── 2. Student Model - Epoch 350 (GOOD checkpoint) ──────────────────────
    student_ckpt_good = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Distilled_Test\weights\best_student.pth"
    if os.path.exists(student_ckpt_good):
        print("\n\nLoading Student Model (Epoch 350 - GOOD)...")
        student_good = BioNAFNet(width=32, middle_blk_num=4,
                                  enc_blk_nums=[2,2,4,8], dec_blk_nums=[2,2,2,2], n_passes=1).to(device)
        ckpt = torch.load(student_ckpt_good, map_location=device, weights_only=False)
        student_good.load_state_dict(ckpt.get("ema", ckpt.get("model")))
        print(f"  Loaded from epoch {ckpt.get('epoch', '?')}, train best_psnr: {ckpt.get('best_psnr', 0):.2f}")
        all_results["Student-350 (24M, n_passes=1)"] = benchmark_model(student_good, "Student BioNAFNet-Lite Epoch 350 (24M, 1-pass)", device)
        del student_good; torch.cuda.empty_cache()
    
    # ── 3. Student Model - Epoch 693 (overfit checkpoint) ───────────────────
    student_ckpt_new = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Distilled_Test\New folder\best.pth"
    if os.path.exists(student_ckpt_new):
        print("\n\nLoading Student Model (Epoch 693 - Overfit)...")
        student_new = BioNAFNet(width=32, middle_blk_num=4,
                                 enc_blk_nums=[2,2,4,8], dec_blk_nums=[2,2,2,2], n_passes=1).to(device)
        ckpt = torch.load(student_ckpt_new, map_location=device, weights_only=False)
        student_new.load_state_dict(ckpt.get("ema", ckpt.get("model")))
        print(f"  Loaded from epoch {ckpt.get('epoch', '?')}, train best_psnr: {ckpt.get('best_psnr', 0):.2f}")
        all_results["Student-693 (24M, overfit)"] = benchmark_model(student_new, "Student BioNAFNet-Lite Epoch 693 (24M, 1-pass, OVERFIT)", device)
        del student_new; torch.cuda.empty_cache()
    
    # ── Summary Table ───────────────────────────────────────────────────────
    print("\n\n" + "="*90)
    print("  COMPREHENSIVE COMPARISON TABLE")
    print("="*90)
    header = f"{'Model':<35} {'Params':>10} {'Size':>8} {'LOLv1':>8} {'LOLv2R':>8} {'LOLv2S':>8} {'ms/img':>8} {'FPS':>6}"
    print(header)
    print("-"*90)
    
    for name, res in all_results.items():
        lolv1 = res.get("LOLv1", {}).get("psnr", 0)
        lolv2r = res.get("LOLv2_Real", {}).get("psnr", 0)
        lolv2s = res.get("LOLv2_Synthetic", {}).get("psnr", 0)
        avg_time = np.mean([res.get(d, {}).get("time_ms", 0) for d in ["LOLv1", "LOLv2_Real", "LOLv2_Synthetic"] if d in res])
        avg_fps = 1000.0 / avg_time if avg_time > 0 else 0
        params_str = f"{res['params']/1e6:.1f}M"
        size_str = f"{res['size_mb']:.0f}MB"
        print(f"{name:<35} {params_str:>10} {size_str:>8} {lolv1:>7.2f}  {lolv2r:>7.2f}  {lolv2s:>7.2f}  {avg_time:>7.1f} {avg_fps:>6.1f}")
    
    print("="*90)
    print("\nDone! All benchmarks complete.")


if __name__ == "__main__":
    main()
