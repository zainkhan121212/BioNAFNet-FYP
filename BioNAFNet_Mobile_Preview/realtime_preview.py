import os
import cv2
import time
import torch
import numpy as np

# Import the Student model class
# Note: Since the BioNAFNet class is complex, we'll keep its definition here for portability,
# identical to how it was set up in `test_distilled.py`.
import torch.nn as nn
import torch.nn.functional as F

# ══════════════════════════════════════════════════════════════════════════════
# Student Architecture (24M parameters)
# ══════════════════════════════════════════════════════════════════════════════

def luminance(x): return 0.299 * x[:, 0:1] + 0.587 * x[:, 1:2] + 0.114 * x[:, 2:3]

class LateralInhibition(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.center = nn.Conv2d(ch, ch, 1, bias=True)
        self.surround = nn.Sequential(nn.AvgPool2d(5, stride=1, padding=2), nn.Conv2d(ch, ch, 1, bias=True))
        self.alpha = nn.Parameter(torch.ones(1) * 0.3)
    def forward(self, x): return x + self.alpha * (self.center(x) - self.surround(x))

class FrequencyBranch(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.conv_amp = nn.Sequential(nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1))
        self.conv_phase = nn.Sequential(nn.Conv2d(ch, ch, 3, padding=1), nn.PReLU(ch), nn.Conv2d(ch, ch, 3, padding=1))
        self.blend = nn.Parameter(torch.ones(1) * 0.15)
    def forward(self, x):
        B, C, H, W = x.shape
        fft = torch.fft.rfft2(x.float(), norm="ortho")
        amp_out = self.conv_amp(torch.abs(fft))
        phase_out = self.conv_phase(torch.angle(fft))
        out = torch.fft.irfft2(torch.complex(amp_out * torch.cos(phase_out), amp_out * torch.sin(phase_out)), s=(H, W), norm="ortho")
        return x + self.blend * out.to(x.dtype)

class AdaptiveReceptiveField(nn.Module):
    def __init__(self, ch):
        super().__init__()
        self.small = nn.Conv2d(ch, ch, 3, padding=1, groups=ch, bias=True)
        self.medium = nn.Conv2d(ch, ch, 5, padding=2, groups=ch, bias=True)
        self.large = nn.Conv2d(ch, ch, 7, padding=3, groups=ch, bias=True)
        self.gate = nn.Sequential(nn.Conv2d(1, 16, 3, padding=1), nn.PReLU(16), nn.Conv2d(16, 3, 1), nn.Softmax(dim=1))
    def forward(self, x, lum_map):
        w = self.gate(F.interpolate(lum_map, size=x.shape[-2:], mode="bilinear", align_corners=False))
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
        return x + self.fuse(torch.cat([self.scotopic(y), self.photopic(torch.cat([u, v], dim=1))], dim=1)) * 0.2

class TemporalAdaptation(nn.Module):
    def __init__(self, ch=32):
        super().__init__()
        self.gru = nn.GRUCell(ch, ch)
        self.proj_in, self.proj_out = nn.Conv2d(3, ch, 1), nn.Conv2d(ch, 3, 1)
    def forward(self, pass_outputs):
        B, _, H, W = pass_outputs[0].shape
        h = torch.zeros(B * H * W, self.gru.hidden_size, device=pass_outputs[0].device)
        for out in pass_outputs:
            h = self.gru(self.proj_in(out).permute(0, 2, 3, 1).reshape(B * H * W, -1), h)
        return pass_outputs[-1] + self.proj_out(h.reshape(B, H, W, -1).permute(0, 3, 1, 2)) * 0.15

class LayerNorm2d(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.weight, self.bias = nn.Parameter(torch.ones(channels)), nn.Parameter(torch.zeros(channels))
    def forward(self, x):
        u, s = x.mean(1, keepdim=True), (x - x.mean(1, keepdim=True)).pow(2).mean(1, keepdim=True)
        return self.weight[None, :, None, None] * (x - u) / torch.sqrt(s + 1e-6) + self.bias[None, :, None, None]

class SimpleGate(nn.Module):
    def forward(self, x): return x.chunk(2, dim=1)[0] * x.chunk(2, dim=1)[1]

class BioNAFBlock(nn.Module):
    def __init__(self, c, use_rlin=True):
        super().__init__()
        self.conv1, self.conv2, self.conv3 = nn.Conv2d(c, c*2, 1), nn.Conv2d(c*2, c*2, 3, padding=1, groups=c*2), nn.Conv2d(c, c, 1)
        self.sca, self.conv4, self.conv5 = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Conv2d(c, c, 1)), nn.Conv2d(c, c*2, 1), nn.Conv2d(c, c, 1)
        self.norm1, self.norm2, self.sg = LayerNorm2d(c), LayerNorm2d(c), SimpleGate()
        self.beta, self.gamma = nn.Parameter(torch.zeros((1, c, 1, 1))), nn.Parameter(torch.zeros((1, c, 1, 1)))
        self.rlin = LateralInhibition(c) if use_rlin else nn.Identity()
    def forward(self, inp):
        x = self.conv3(self.sg(self.conv2(self.conv1(self.norm1(inp))))) * self.sca(self.sg(self.conv2(self.conv1(self.norm1(inp))))) # Approximation for brevity
        x = self.norm1(inp)
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.sg(x)
        x = x * self.sca(x)
        x = self.conv3(x)
        x = self.rlin(x)
        y = inp + x * self.beta
        out = self.conv5(self.sg(self.conv4(self.norm2(y))))
        return y + out * self.gamma

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
        for enc, down in zip(self.encoders, self.downs): x = enc(x); encs.append(x); x = down(x)
        x = self.faeb(self.middle_blks(x))
        for dec, up, skip in zip(self.decoders, self.ups, encs[::-1]): x = dec(up(x) + skip)
        return (self.ending(self.arfp(x, lum_map)) + F.pad(inp, (0, mod_w, 0, mod_h), mode='reflect'))[:, :, :H, :W]

    def forward(self, x):
        x_in, lum_map = self.spdp(self.prcm(x)), luminance(x)
        pass_outputs = []
        curr = x_in
        for _ in range(self.n_passes):
            out = self.forward_single(curr, lum_map).clamp(0, 1)
            pass_outputs.append(out); curr = out
        return self.tam(pass_outputs).clamp(0, 1) if self.n_passes > 1 else pass_outputs[-1]

# ══════════════════════════════════════════════════════════════════════════════
# Real-Time Webcam Preview Loop
# ══════════════════════════════════════════════════════════════════════════════

def run_realtime():
    print("Loading BioNAFNet-Lite for Real-Time Execution...")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 1. Initialize Network
    model = BioNAFNet(width=32, middle_blk_num=4, enc_blk_nums=[2, 2, 4, 8], dec_blk_nums=[2, 2, 2, 2], n_passes=1).to(device)
    
    # 2. Load Weights 
    ckpt_path = "best_student.pth"
    if not os.path.exists(ckpt_path):
        print(f"Error: {ckpt_path} not found. Please place the model weights in the same folder.")
        return
        
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt.get("ema", ckpt.get("model")))
    model.eval()
    print("Model loaded successfully. Starting webcam...")

    # 3. Setup Webcam
    # 0 is usually the default built-in laptop webcam or primary USB cam.
    cap = cv2.VideoCapture(0)
    
    # Lower resolution makes it faster for real-time mobile/laptop preview
    CAPTURE_WIDTH = 640
    CAPTURE_HEIGHT = 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    frames_processed = 0
    start_time = time.time()
    
    print("\n--- Controls ---")
    print("Press 'q' to quit.")
    print("Press 's' to save the current frame.")
    print("----------------\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # Simulate a low-light environment computationally if the webcam is naturally bright
        # (Comment this out if testing in an actual dark room)
        # frame = cv2.convertScaleAbs(frame, alpha=0.15, beta=0)

        # Pre-process frame for PyTorch
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor_in = torch.from_numpy(frame_rgb.astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)

        # Model Inference
        with torch.no_grad():
            t0 = time.time()
            tensor_out = model(tensor_in)
            inference_time = time.time() - t0

        # Post-process PyTorch output to OpenCV format
        out_rgb = tensor_out.squeeze(0).permute(1, 2, 0).cpu().numpy()
        out_bgr = cv2.cvtColor((out_rgb * 255).clip(0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

        # FPS Calculation
        fps = 1.0 / (inference_time + 0.001)

        # UI Overlay - Build Side-by-Side View
        # Stack horizontal (Original | Enhanced)
        combined = np.hstack((frame, out_bgr))
        
        cv2.putText(combined, "ORIGINAL WEBCAM", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(combined, "BioNAFNet-Lite ENHANCED", (CAPTURE_WIDTH + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(combined, f"Inf FPS: {fps:.1f}", (CAPTURE_WIDTH + 10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        cv2.imshow("BioNAFNet Real-Time Preview", combined)

        frames_processed += 1
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"capture_{int(time.time())}.png"
            cv2.imwrite(filename, combined)
            print(f"Saved {filename}")

    cap.release()
    cv2.destroyAllWindows()
    print("Preview Closed.")

if __name__ == "__main__":
    run_realtime()
