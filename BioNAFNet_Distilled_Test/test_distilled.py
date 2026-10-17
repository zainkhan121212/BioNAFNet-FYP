import os
import math
import glob
import time
import argparse
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr

# ══════════════════════════════════════════════════════════════════════════════
# Student Configuration
# ══════════════════════════════════════════════════════════════════════════════
WIDTH           = 32
ENC_BLKS        = [2, 2, 4, 8]
MIDDLE_BLK_NUM  = 4
DEC_BLKS        = [2, 2, 2, 2]
STUDENT_PASSES  = 2

DATA_ROOT       = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data"
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

# ══════════════════════════════════════════════════════════════════════════════
# Architecture Classes (Exact Copy from train_distillation.py)
# ══════════════════════════════════════════════════════════════════════════════

def luminance(x):
    return 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]

class LateralInhibition(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.center = nn.Conv2d(ch, ch, 1, bias=True)
        self.surround = nn.Sequential(
            nn.AvgPool2d(5, stride=1, padding=2),
            nn.Conv2d(ch, ch, 1, bias=True),
        )
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
        x_fp32 = x.float()
        fft = torch.fft.rfft2(x_fp32, norm="ortho")
        amp, phase = torch.abs(fft), torch.angle(fft)
        amp_out = self.conv_amp(amp)
        phase_out = self.conv_phase(phase)
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
        self.rod_gamma, self.cone_gamma, self.threshold = nn.Parameter(torch.tensor([0.45])), nn.Parameter(torch.tensor([0.95])), nn.Parameter(torch.tensor([0.25]))
    def forward(self, x):
        lum = luminance(x)
        cone_weight = torch.sigmoid((lum - self.threshold) * 12)
        return torch.pow(x.clamp(1e-5, 1), self.rod_gamma) * (1 - cone_weight) + torch.pow(x.clamp(1e-5, 1), self.cone_gamma) * cone_weight

class DualPathway(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.scotopic = nn.Sequential(nn.Conv2d(1, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch))
        self.photopic = nn.Sequential(nn.Conv2d(2, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch))
        self.fuse = nn.Sequential(nn.Conv2d(ch * 2, ch, 1), nn.PReLU(ch), nn.Conv2d(ch, 3, 1), nn.Tanh())
    def forward(self, x):
        r, g, b = x[:, 0:1], x[:, 1:2], x[:, 2:3]
        y, u, v = 0.299*r+0.587*g+0.114*b, -0.147*r-0.289*g+0.436*b, 0.615*r-0.515*g-0.100*b
        feat = torch.cat([self.scotopic(y), self.photopic(torch.cat([u, v], dim=1))], dim=1)
        return x + self.fuse(feat) * 0.2

class TemporalAdaptation(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.gru = nn.GRUCell(ch, ch)
        self.proj_in, self.proj_out = nn.Conv2d(3, ch, 1), nn.Conv2d(ch, 3, 1)
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
        self.weight, self.bias = nn.Parameter(torch.ones(channels)), nn.Parameter(torch.zeros(channels))
    def forward(self, x):
        u, s = x.mean(1, keepdim=True), (x - x.mean(1, keepdim=True)).pow(2).mean(1, keepdim=True)
        x = (x - u) / torch.sqrt(s + 1e-6)
        return self.weight[None, :, None, None] * x + self.bias[None, :, None, None]

class SimpleGate(nn.Module):
    def forward(self, x):
        x1, x2 = x.chunk(2, dim=1)
        return x1 * x2

class BioNAFBlock(nn.Module):
    def __init__(self, c, use_rlin=True):
        super().__init__()
        self.conv1, self.conv2, self.conv3 = nn.Conv2d(c, c*2, 1), nn.Conv2d(c*2, c*2, 3, padding=1, groups=c*2), nn.Conv2d(c, c, 1)
        self.sca = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Conv2d(c, c, 1))
        self.conv4, self.conv5 = nn.Conv2d(c, c*2, 1), nn.Conv2d(c, c, 1)
        self.norm1, self.norm2 = LayerNorm2d(c), LayerNorm2d(c)
        self.sg = SimpleGate()
        self.beta, self.gamma = nn.Parameter(torch.zeros((1, c, 1, 1))), nn.Parameter(torch.zeros((1, c, 1, 1)))
        self.rlin = LateralInhibition(c) if use_rlin else nn.Identity()

    def forward(self, inp):
        x = self.norm1(inp)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.sg(x)
        x = x * self.sca(x)
        x = self.conv3(x)
        x = self.rlin(x)
        y = inp + x * self.beta
        x = self.norm2(y)
        x = self.conv4(x)
        x = self.sg(x)
        x = self.conv5(x)
        return y + x * self.gamma

class BioNAFNet(nn.Module):
    def __init__(self, img_channel=3, width=32, middle_blk_num=4, enc_blk_nums=[2, 2, 4, 8], dec_blk_nums=[2, 2, 2, 2], n_passes=1):
        super().__init__()
        self.n_passes, self.prcm, self.spdp = n_passes, PhotoreceptorCurve(), DualPathway(ch=32)
        self.intro, self.ending = nn.Conv2d(3, width, 3, padding=1), nn.Conv2d(width, 3, 3, padding=1)
        self.encoders, self.decoders, self.ups, self.downs = nn.ModuleList(), nn.ModuleList(), nn.ModuleList(), nn.ModuleList()
        chan = width
        for i, num in enumerate(enc_blk_nums):
            self.encoders.append(nn.Sequential(*[BioNAFBlock(chan, use_rlin=(i < len(enc_blk_nums)-1)) for _ in range(num)]))
            self.downs.append(nn.Conv2d(chan, 2 * chan, 2, 2)); chan *= 2
        self.middle_blks, self.faeb = nn.Sequential(*[BioNAFBlock(chan, use_rlin=False) for _ in range(middle_blk_num)]), FrequencyBranch(chan)
        for num in dec_blk_nums:
            self.ups.append(nn.Sequential(nn.Conv2d(chan, chan * 2, 1, bias=False), nn.PixelShuffle(2))); chan //= 2
            self.decoders.append(nn.Sequential(*[BioNAFBlock(chan, use_rlin=False) for _ in range(num)]))
        self.arfp, self.tam, self.padder_size = AdaptiveReceptiveField(chan), TemporalAdaptation(ch=32), 2 ** len(self.encoders)

    def forward_single(self, inp, lum_map):
        B, C, H, W = inp.shape
        mod_h, mod_w = (self.padder_size - H % self.padder_size) % self.padder_size, (self.padder_size - W % self.padder_size) % self.padder_size
        x = self.intro(F.pad(inp, (0, mod_w, 0, mod_h), mode='reflect'))
        encs = []
        for enc, down in zip(self.encoders, self.downs):
            x = enc(x); encs.append(x); x = down(x)
        x = self.middle_blks(x)
        x = self.faeb(x)
        for dec, up, skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x); x = x + skip; x = dec(x)
        out = self.arfp(x, lum_map)
        out = self.ending(out)
        out = out + F.pad(inp, (0, mod_w, 0, mod_h), mode='reflect')
        return out[:, :, :H, :W]

    def forward(self, x):
        x_in, lum_map = self.spdp(self.prcm(x)), luminance(x)
        pass_outputs = []
        curr = x_in
        for _ in range(self.n_passes):
            out = self.forward_single(curr, lum_map).clamp(0, 1)
            pass_outputs.append(out); curr = out
        return self.tam(pass_outputs).clamp(0, 1) if self.n_passes > 1 else pass_outputs[-1]

# ══════════════════════════════════════════════════════════════════════════════
# Execution
# ══════════════════════════════════════════════════════════════════════════════

class LOLDataset(Dataset):
    def __init__(self, input_dir, target_dir):
        self.input_files = sorted(glob.glob(os.path.join(input_dir, "*.*")))
        self.target_files = sorted(glob.glob(os.path.join(target_dir, "*.*")))
    def __len__(self): return len(self.input_files)
    def __getitem__(self, idx):
        low = torch.from_numpy(np.array(Image.open(self.input_files[idx]).convert("RGB")).astype(np.float32) / 255.0).permute(2, 0, 1)
        high = torch.from_numpy(np.array(Image.open(self.target_files[idx]).convert("RGB")).astype(np.float32) / 255.0).permute(2, 0, 1)
        return low, high

def run_test():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = BioNAFNet(width=WIDTH, middle_blk_num=MIDDLE_BLK_NUM, enc_blk_nums=ENC_BLKS, dec_blk_nums=DEC_BLKS, n_passes=STUDENT_PASSES).to(device)
    
    ckpt_path = "New folder/best.pth"
    if os.path.exists(ckpt_path):
        ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
        model.load_state_dict(ckpt.get("ema", ckpt.get("model")))
        print(f"Loaded checkpoint from {ckpt_path} (Best PSNR: {ckpt.get('best_psnr', 0):.2f})")
    else:
        print(f"ERROR: Checkpoint not found at {ckpt_path}")
        return

    model.eval()

    for d_name, d_paths in DATASETS.items():
        if not os.path.exists(d_paths["in"]):
            print(f"Skipping {d_name}: path not found.")
            continue
            
        print(f"\nTesting on {d_name}...")
        results_dir = os.path.join("resultsneww", d_name)
        os.makedirs(results_dir, exist_ok=True)

        test_ds = LOLDataset(d_paths["in"], d_paths["gt"])
        loader = DataLoader(test_ds, batch_size=1, shuffle=False)

        psnrs, ssims = [], []
        start_time = time.time()
        with torch.no_grad():
            for i, (low, high) in enumerate(loader):
                if low.shape != high.shape:
                    continue # Safety check for mismatched datasets
                low, high = low.to(device), high.to(device)
                out = model(low)
                out_np = out.squeeze().permute(1, 2, 0).cpu().numpy()
                high_np = high.squeeze().permute(1, 2, 0).cpu().numpy()
                p = calc_psnr(high_np, out_np, data_range=1.0)
                s = calc_ssim(high_np, out_np, data_range=1.0, channel_axis=2)
                psnrs.append(p); ssims.append(s)
                Image.fromarray((out_np * 255).clip(0, 255).astype(np.uint8)).save(os.path.join(results_dir, os.path.basename(test_ds.input_files[i])))
                if (i+1) % 20 == 0 or i == 0:
                    print(f"  [{i+1}/{len(test_ds)}] PSNR: {p:.2f} dB, SSIM: {s:.4f}")

        total_time = time.time() - start_time
        print("-" * 30)
        print(f"RESULTS for {d_name}")
        print(f"Avg PSNR: {np.mean(psnrs):.2f} dB")
        print(f"Avg SSIM: {np.mean(ssims):.4f}")
        print(f"Time: {total_time:.2f}s ({total_time/len(test_ds):.3f}s/img)")
        print("-" * 30)

if __name__ == "__main__":
    run_test()
