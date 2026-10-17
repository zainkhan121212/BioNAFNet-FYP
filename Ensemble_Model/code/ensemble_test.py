"""
BioNAFNet — Teacher + Student Ensemble
=======================================
Combines the Teacher (154M) and Student-693 (24M) models' outputs
using multiple fusion strategies:
  1. Simple Average (50/50)
  2. Weighted Average (Teacher-heavy: 60/40)
  3. Weighted Average (Student-heavy: 40/60)

Tests on LOLv1, LOLv2 Real, LOLv2 Synthetic and saves results
to separate folders for each dataset and strategy.
"""

import os, sys, time, math, glob
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr

# ═══════════════════════════════════════════════════════════════════════════════
# Architecture (identical to benchmark script)
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
# Ensemble Evaluation
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

# Ensemble fusion strategies
STRATEGIES = {
    "ensemble_avg":       (0.50, 0.50),   # Simple average
    "ensemble_teacher60": (0.60, 0.40),   # Teacher-biased
    "ensemble_student60": (0.40, 0.60),   # Student-biased
}

RESULTS_BASE = r"F:\low_light_enhancement\eye adaption\BioNAFNet\results_ensemble"

class LOLDataset(Dataset):
    def __init__(self, input_dir, target_dir):
        self.input_files = sorted(glob.glob(os.path.join(input_dir, "*.*")))
        self.target_files = sorted(glob.glob(os.path.join(target_dir, "*.*")))
    def __len__(self): return len(self.input_files)
    def __getitem__(self, idx):
        low = torch.from_numpy(np.array(Image.open(self.input_files[idx]).convert("RGB")).astype(np.float32) / 255.0).permute(2, 0, 1)
        high = torch.from_numpy(np.array(Image.open(self.target_files[idx]).convert("RGB")).astype(np.float32) / 255.0).permute(2, 0, 1)
        return low, high, os.path.basename(self.input_files[idx])


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    # ── Load Teacher ────────────────────────────────────────────────────────
    teacher_ckpt = r"F:\low_light_enhancement\eye adaption\BioNAFNet\checkpoints\best.pth"
    print("Loading Teacher Model (154M, 2-pass)...")
    teacher = BioNAFNet(width=64, middle_blk_num=12,
                        enc_blk_nums=[2,2,4,8], dec_blk_nums=[2,2,2,2], n_passes=2).to(device)
    ckpt = torch.load(teacher_ckpt, map_location=device, weights_only=False)
    teacher.load_state_dict(ckpt.get("ema", ckpt.get("model")))
    teacher.eval()
    print("  [OK] Teacher loaded.")

    # ── Load Student-693 ────────────────────────────────────────────────────
    student_ckpt = r"F:\low_light_enhancement\eye adaption\BioNAFNet\checkpoints_student\best.pth"
    print("Loading Student-693 Model (24M, 1-pass)...")
    student = BioNAFNet(width=32, middle_blk_num=4,
                        enc_blk_nums=[2,2,4,8], dec_blk_nums=[2,2,2,2], n_passes=1).to(device)
    ckpt = torch.load(student_ckpt, map_location=device, weights_only=False)
    student.load_state_dict(ckpt.get("ema", ckpt.get("model")))
    student.eval()
    print("  [OK] Student-693 loaded.")

    # ── Also benchmark individual models for comparison ─────────────────────
    all_results = {}

    for strat_name, (w_teacher, w_student) in STRATEGIES.items():
        print(f"\n{'='*70}")
        print(f"  STRATEGY: {strat_name} (Teacher={w_teacher:.0%}, Student={w_student:.0%})")
        print(f"{'='*70}")

        strat_results = {}

        for d_name, d_paths in DATASETS.items():
            if not os.path.exists(d_paths["in"]):
                print(f"  Skipping {d_name}")
                continue

            # Create output directory for this strategy + dataset
            out_dir = os.path.join(RESULTS_BASE, strat_name, d_name)
            os.makedirs(out_dir, exist_ok=True)

            ds = LOLDataset(d_paths["in"], d_paths["gt"])
            loader = DataLoader(ds, batch_size=1, shuffle=False)

            psnrs, ssims, times = [], [], []

            with torch.no_grad():
                for i, (low, high, fname) in enumerate(loader):
                    if low.shape != high.shape:
                        continue
                    low, high = low.to(device), high.to(device)

                    start = time.time()
                    out_teacher = teacher(low)
                    out_student = student(low)
                    
                    # Fusion: weighted average
                    out_ensemble = (w_teacher * out_teacher + w_student * out_student).clamp(0, 1)
                    torch.cuda.synchronize()
                    elapsed = time.time() - start
                    times.append(elapsed)

                    out_np = out_ensemble.squeeze().permute(1, 2, 0).cpu().numpy()
                    high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()

                    p = calc_psnr(high_np, out_np, data_range=1.0)
                    s = calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)
                    psnrs.append(p)
                    ssims.append(s)

                    # Save the ensemble image
                    out_img = (out_np * 255).clip(0, 255).astype(np.uint8)
                    Image.fromarray(out_img).save(os.path.join(out_dir, fname[0]))

            avg_psnr = np.mean(psnrs)
            avg_ssim = np.mean(ssims)
            avg_time = np.mean(times) * 1000

            strat_results[d_name] = {"psnr": avg_psnr, "ssim": avg_ssim, "time_ms": avg_time}

            print(f"\n  {d_name} ({len(psnrs)} images):")
            print(f"    PSNR: {avg_psnr:.2f} dB  |  SSIM: {avg_ssim:.4f}")
            print(f"    Speed: {avg_time:.1f} ms/img")
            print(f"    Saved to: {out_dir}")

        all_results[strat_name] = strat_results

    # ── Final Summary Table ─────────────────────────────────────────────────
    print("\n\n" + "="*95)
    print("  ENSEMBLE RESULTS COMPARISON")
    print("="*95)

    # Also show individual model results for reference
    print(f"\n  {'Strategy':<30} {'LOLv1 PSNR':>12} {'LOLv2R PSNR':>12} {'LOLv2S PSNR':>12} {'ms/img':>10}")
    print("-"*95)
    
    # Reference lines (from earlier benchmark)
    print(f"  {'Teacher (solo)':<30} {'24.94':>12} {'28.67':>12} {'26.22':>12} {'188.7':>10}")
    print(f"  {'Student-693 (solo)':<30} {'25.23':>12} {'28.48':>12} {'25.75':>12} {'48.9':>10}")
    print("-"*95)

    for strat_name, strat_res in all_results.items():
        lolv1 = strat_res.get("LOLv1", {}).get("psnr", 0)
        lolv2r = strat_res.get("LOLv2_Real", {}).get("psnr", 0)
        lolv2s = strat_res.get("LOLv2_Synthetic", {}).get("psnr", 0)
        avg_t = np.mean([strat_res.get(d, {}).get("time_ms", 0) for d in ["LOLv1", "LOLv2_Real", "LOLv2_Synthetic"] if d in strat_res])
        tw, sw = STRATEGIES[strat_name]
        label = f"{strat_name} (T{tw:.0%}/S{sw:.0%})"
        print(f"  {label:<30} {lolv1:>12.2f} {lolv2r:>12.2f} {lolv2s:>12.2f} {avg_t:>10.1f}")

    print("="*95)
    print(f"\nAll ensemble results saved to: {RESULTS_BASE}")
    print("Done!")


if __name__ == "__main__":
    main()
