import os
import glob
import math
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from skimage.metrics import structural_similarity as calc_ssim
from skimage.metrics import peak_signal_noise_ratio as calc_psnr
from tqdm import tqdm

# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════
BEST_PATH = r"f:\low_light_enhancement\eye adaption\BioNAFNet\checkpoints\best.pth"
SID_SHORT = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data\SID\sid_processed\short_sid2"
SID_LONG  = r"c:\Users\GNG\Desktop\retinex former\Retinexformer-master\data\SID\sid_processed\long_sid2"
RESULTS_DIR = r"f:\low_light_enhancement\eye adaption\BioNAFNet\results_sid"
os.makedirs(RESULTS_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# Model Components (BioNAFNet)
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
        c = self.center(x)
        s = self.surround(x)
        return x + self.alpha * (c - s)

class FrequencyBranch(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.conv_amp = nn.Sequential(
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1),
        )
        self.conv_phase = nn.Sequential(
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1),
        )
        self.blend = nn.Parameter(torch.ones(1) * 0.15)

    def forward(self, x):
        B, C, H, W = x.shape
        with torch.amp.autocast(device_type='cuda', enabled=False):
            x_fp32 = x.float()
            fft = torch.fft.rfft2(x_fp32, norm="ortho")
            amp = torch.abs(fft)
            phase = torch.angle(fft)
            amp_out = self.conv_amp(amp)
            phase_out = self.conv_phase(phase)
            real = amp_out * torch.cos(phase_out)
            imag = amp_out * torch.sin(phase_out)
            fft_out = torch.complex(real, imag)
            out = torch.fft.irfft2(fft_out, s=(H, W), norm="ortho")
        return x + self.blend * out.to(x.dtype)

class AdaptiveReceptiveField(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.small = nn.Conv2d(ch, ch, 3, padding=1, groups=ch, bias=True)
        self.medium = nn.Conv2d(ch, ch, 5, padding=2, groups=ch, bias=True)
        self.large = nn.Conv2d(ch, ch, 7, padding=3, groups=ch, bias=True)
        self.gate = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.PReLU(16),
            nn.Conv2d(16, 3, 1), nn.Softmax(dim=1),
        )

    def forward(self, x, lum_map):
        lum = F.interpolate(lum_map, size=x.shape[-2:], mode="bilinear", align_corners=False)
        weights = self.gate(lum)
        s = self.small(x)
        m = self.medium(x)
        l = self.large(x)
        return weights[:, 0:1] * s + weights[:, 1:2] * m + weights[:, 2:3] * l

class PhotoreceptorCurve(nn.Module):
    def __init__(self):
        super().__init__()
        self.rod_gamma = nn.Parameter(torch.tensor([0.45]))
        self.cone_gamma = nn.Parameter(torch.tensor([0.95]))
        self.threshold = nn.Parameter(torch.tensor([0.25]))

    def forward(self, x):
        lum = luminance(x)
        cone_weight = torch.sigmoid((lum - self.threshold) * 12)
        x_rod = torch.pow(x.clamp(1e-5, 1), self.rod_gamma)
        x_cone = torch.pow(x.clamp(1e-5, 1), self.cone_gamma)
        return x_rod * (1 - cone_weight) + x_cone * cone_weight

class DualPathway(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.scotopic = nn.Sequential(
            nn.Conv2d(1, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
        )
        self.photopic = nn.Sequential(
            nn.Conv2d(2, ch, 3, padding=1), nn.PReLU(ch),
            nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch),
        )
        self.fuse = nn.Sequential(
            nn.Conv2d(ch * 2, ch, 1), nn.PReLU(ch),
            nn.Conv2d(ch, 3, 1), nn.Tanh(),
        )

    def forward(self, x):
        y, u, v = self.rgb_to_yuv(x)
        lum_feat = self.scotopic(y)
        col_feat = self.photopic(torch.cat([u, v], dim=1))
        combined = torch.cat([lum_feat, col_feat], dim=1)
        residual = self.fuse(combined) * 0.2
        return x + residual

    def rgb_to_yuv(self, rgb):
        r, g, b = rgb[:, 0:1], rgb[:, 1:2], rgb[:, 2:3]
        y = 0.299 * r + 0.587 * g + 0.114 * b
        u = -0.147 * r - 0.289 * g + 0.436 * b
        v = 0.615 * r - 0.515 * g - 0.100 * b
        return y, u, v

class TemporalAdaptation(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.gru = nn.GRUCell(ch, ch)
        self.proj_in = nn.Conv2d(3, ch, 1)
        self.proj_out = nn.Conv2d(ch, 3, 1)

    def forward(self, pass_outputs):
        B, _, H, W = pass_outputs[0].shape
        hidden = torch.zeros(B * H * W, self.gru.hidden_size, device=pass_outputs[0].device)
        for out in pass_outputs:
            feat = self.proj_in(out)
            feat = feat.permute(0, 2, 3, 1).reshape(B * H * W, -1)
            hidden = self.gru(feat, hidden)
        out = hidden.reshape(B, H, W, -1).permute(0, 3, 1, 2)
        residual = self.proj_out(out) * 0.15
        return pass_outputs[-1] + residual

class LayerNorm2d(nn.Module):
    def __init__(self, channels, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(channels))
        self.bias = nn.Parameter(torch.zeros(channels))
        self.eps = eps

    def forward(self, x):
        u = x.mean(1, keepdim=True)
        s = (x - u).pow(2).mean(1, keepdim=True)
        x = (x - u) / torch.sqrt(s + self.eps)
        return self.weight[None, :, None, None] * x + self.bias[None, :, None, None]

class SimpleGate(nn.Module):
    def forward(self, x):
        x1, x2 = x.chunk(2, dim=1)
        return x1 * x2

class BioNAFBlock(nn.Module):
    def __init__(self, c, DW_Expand=2, FFN_Expand=2, drop_out_rate=0., use_rlin=True):
        super().__init__()
        dw_channel = c * DW_Expand
        self.conv1 = nn.Conv2d(c, dw_channel, 1, bias=True)
        self.conv2 = nn.Conv2d(dw_channel, dw_channel, 3, padding=1, groups=dw_channel, bias=True)
        self.conv3 = nn.Conv2d(dw_channel // 2, c, 1, bias=True)
        self.sca = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(dw_channel // 2, dw_channel // 2, 1, bias=True),
        )
        self.sg = SimpleGate()
        ffn_channel = FFN_Expand * c
        self.conv4 = nn.Conv2d(c, ffn_channel, 1, bias=True)
        self.conv5 = nn.Conv2d(ffn_channel // 2, c, 1, bias=True)
        self.norm1 = LayerNorm2d(c)
        self.norm2 = LayerNorm2d(c)
        self.beta = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)
        self.gamma = nn.Parameter(torch.zeros((1, c, 1, 1)), requires_grad=True)
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
        x = self.conv4(self.norm2(y))
        x = self.sg(x)
        x = self.conv5(x)
        return y + x * self.gamma

class BioNAFNet(nn.Module):
    def __init__(self, img_channel=3, width=64, middle_blk_num=12,
                 enc_blk_nums=[2, 2, 4, 8], dec_blk_nums=[2, 2, 2, 2],
                 n_passes=2):
        super().__init__()
        self.n_passes = n_passes
        self.prcm = PhotoreceptorCurve()
        self.spdp = DualPathway(ch=32)
        self.intro = nn.Conv2d(img_channel, width, 3, padding=1, bias=True)
        self.ending = nn.Conv2d(width, img_channel, 3, padding=1, bias=True)
        self.encoders = nn.ModuleList()
        self.decoders = nn.ModuleList()
        self.ups = nn.ModuleList()
        self.downs = nn.ModuleList()
        chan = width
        for i, num in enumerate(enc_blk_nums):
            use_rlin = (i < len(enc_blk_nums) - 1)
            self.encoders.append(nn.Sequential(*[BioNAFBlock(chan, use_rlin=use_rlin) for _ in range(num)]))
            self.downs.append(nn.Conv2d(chan, 2 * chan, 2, 2))
            chan *= 2
        self.middle_blks = nn.Sequential(*[BioNAFBlock(chan, use_rlin=False) for _ in range(middle_blk_num)])
        self.faeb = FrequencyBranch(chan)
        for num in dec_blk_nums:
            self.ups.append(nn.Sequential(nn.Conv2d(chan, chan * 2, 1, bias=False), nn.PixelShuffle(2)))
            chan //= 2
            self.decoders.append(nn.Sequential(*[BioNAFBlock(chan, use_rlin=False) for _ in range(num)]))
        self.arfp = AdaptiveReceptiveField(chan)
        self.tam = TemporalAdaptation(ch=32)
        self.padder_size = 2 ** len(self.encoders)

    def forward_single(self, inp, lum_map):
        B, C, H, W = inp.shape
        inp_padded = self.check_image_size(inp)
        x = self.intro(inp_padded)
        encs = []
        for encoder, down in zip(self.encoders, self.downs):
            x = encoder(x)
            encs.append(x)
            x = down(x)
        x = self.middle_blks(x)
        x = self.faeb(x)
        for decoder, up, enc_skip in zip(self.decoders, self.ups, encs[::-1]):
            x = up(x)
            x = x + enc_skip
            x = decoder(x)
        x = self.arfp(x, lum_map)
        x = self.ending(x)
        x = x + inp_padded
        return x[:, :, :H, :W]

    def forward(self, x):
        x_prcm = self.prcm(x)
        x_spdp = self.spdp(x_prcm)
        lum_map = luminance(x)
        pass_outputs = []
        current = x_spdp
        for p in range(self.n_passes):
            out = self.forward_single(current, lum_map)
            out = out.clamp(0, 1)
            pass_outputs.append(out)
            current = out
        if self.n_passes > 1:
            final = self.tam(pass_outputs)
        else:
            final = pass_outputs[-1]
        return final.clamp(0, 1)

    def check_image_size(self, x):
        _, _, h, w = x.size()
        mod_pad_h = (self.padder_size - h % self.padder_size) % self.padder_size
        mod_pad_w = (self.padder_size - w % self.padder_size) % self.padder_size
        x = F.pad(x, (0, mod_pad_w, 0, mod_pad_h))
        return x

# ══════════════════════════════════════════════════════════════════════════════
# SID Dataset (npy)
# ══════════════════════════════════════════════════════════════════════════════

class SIDDataset(Dataset):
    def __init__(self, short_root, long_root):
        self.input_files = sorted(glob.glob(os.path.join(short_root, "*/*.npy")))
        self.long_root = long_root
        
    def __len__(self):
        return len(self.input_files)

    def __getitem__(self, idx):
        short_path = self.input_files[idx]
        # Scene name from folder structure: short_sid2/00001/00001_00_0.04s.npy
        folder_name = os.path.basename(os.path.dirname(short_path))
        file_name = os.path.basename(short_path)
        
        # Long path: long_sid2/00001/00001_00_10s.npy
        # Note: In SID, multiple shorts map to one long.
        long_folder = os.path.join(self.long_root, folder_name)
        long_files = glob.glob(os.path.join(long_folder, "*.npy"))
        if not long_files:
             raise FileNotFoundError(f"Target for {short_path} not found in {long_folder}")
        long_path = long_files[0] # Usually only one

        inp = np.load(short_path).astype(np.float32) / 255.0
        tgt = np.load(long_path).astype(np.float32) / 255.0

        inp = torch.from_numpy(inp).permute(2, 0, 1)
        tgt = torch.from_numpy(tgt).permute(2, 0, 1)
        
        return inp, tgt, file_name

# ══════════════════════════════════════════════════════════════════════════════
# Testing Logic
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = BioNAFNet(width=64, middle_blk_num=12, enc_blk_nums=[2, 2, 4, 8], dec_blk_nums=[2, 2, 2, 2], n_passes=2).to(device)
    
    if os.path.exists(BEST_PATH):
        ckpt = torch.load(BEST_PATH, map_location=device, weights_only=False)
        weights = ckpt["ema"] if "ema" in ckpt else ckpt["model"]
        model.load_state_dict(weights)
        print(f"Loaded checkpoint from epoch {ckpt.get('epoch', '?')}")
    else:
        print("ERROR: Checkpoint not found!")
        exit()

    dataset = SIDDataset(SID_SHORT, SID_LONG)
    # Test only a subset if too many images to be efficient for this request
    # but the user asked to "text on the SID folder", I'll test first 50.
    test_indices = list(range(min(50, len(dataset))))
    subset = torch.utils.data.Subset(dataset, test_indices)
    loader = DataLoader(subset, batch_size=1, shuffle=False)

    model.eval()
    all_psnr, all_ssim = [], []

    print(f"\nTesting BioNAFNet on SID (Sample of {len(subset)} images)...")
    print("=" * 70)

    with torch.no_grad():
        for inp, tgt, fname in tqdm(loader):
            inp = inp.to(device)
            tgt = tgt.to(device)
            fname = fname[0]

            out = model(inp)
            out = out.clamp(0, 1)

            out_np = out.squeeze().permute(1, 2, 0).cpu().numpy()
            tgt_np = tgt.squeeze().permute(1, 2, 0).cpu().numpy()

            p = calc_psnr(tgt_np, out_np, data_range=1.0)
            s = calc_ssim(tgt_np, out_np, data_range=1.0, channel_axis=2)
            all_psnr.append(p)
            all_ssim.append(s)

            # Save result as PNG
            res_img = (out_np * 255).astype(np.uint8)
            Image.fromarray(res_img).save(os.path.join(RESULTS_DIR, fname.replace(".npy", ".png")))

            print(f"  {fname:30s} PSNR: {p:.2f} dB  SSIM: {s:.4f}")

    print("=" * 70)
    print(f"Average PSNR: {np.mean(all_psnr):.2f} dB")
    print(f"Average SSIM: {np.mean(all_ssim):.4f}")
    print(f"Results saved to: {RESULTS_DIR}")
