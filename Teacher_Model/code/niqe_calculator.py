import cv2
import math
import numpy as np
import os
import glob
from scipy.ndimage import convolve
from scipy.special import gamma
from tqdm import tqdm

# ══════════════════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════════════════
IMAGE_DIR = r"f:\low_light_enhancement\eye adaption\BioNAFNet\enhanced_real_test"
PARAMS_PATH = r"f:\low_light_enhancement\eye adaption\NAFNet\basicsr\metrics\niqe_pris_params.npz"

# ══════════════════════════════════════════════════════════════════════════════
# MATLAB-Style Color Conversion (BasicSR/NAFNet logic)
# ══════════════════════════════════════════════════════════════════════════════

def _convert_input_type_range(img):
    img_type = img.dtype
    img = img.astype(np.float32)
    if img_type == np.uint8:
        img /= 255.
    return img

def _convert_output_type_range(img, dst_type):
    if dst_type == np.uint8:
        img = img.round()
    else:
        img /= 255.
    return img.astype(dst_type)

def bgr2ycbcr(img, y_only=False):
    img_type = img.dtype
    img = _convert_input_type_range(img)
    if y_only:
        out_img = np.dot(img, [24.966, 128.553, 65.481]) + 16.0
    else:
        out_img = np.matmul(
                    img, [[24.966, 112.0, -18.214], [128.553, -74.203, -93.786],
                          [65.481, -37.797, 112.0]]) + [16, 128, 128]
    out_img = _convert_output_type_range(out_img, img_type)
    return out_img

def reorder_image(img, input_order='HWC'):
    if len(img.shape) == 2:
        img = img[..., None]
    if input_order == 'CHW':
        img = img.transpose(1, 2, 0)
    return img

def to_y_channel(img):
    img = img.astype(np.float32) / 255.
    if img.ndim == 3 and img.shape[2] == 3:
        img = bgr2ycbcr(img, y_only=True)
        img = img[..., None]
    return img * 255.

# ══════════════════════════════════════════════════════════════════════════════
# NIQE Logic
# ══════════════════════════════════════════════════════════════════════════════

def estimate_aggd_param(block):
    block = block.flatten()
    gam = np.arange(0.2, 10.001, 0.001)
    gam_reciprocal = np.reciprocal(gam)
    r_gam = np.square(gamma(gam_reciprocal * 2)) / (gamma(gam_reciprocal) * gamma(gam_reciprocal * 3))

    left_std = np.sqrt(np.mean(block[block < 0]**2))
    right_std = np.sqrt(np.mean(block[block > 0]**2))
    gammahat = (left_std / right_std) if right_std != 0 else 1.0
    rhat = (np.mean(np.abs(block)))**2 / np.mean(block**2) if np.mean(block**2) != 0 else 0
    rhatnorm = (rhat * (gammahat**3 + 1) * (gammahat + 1)) / ((gammahat**2 + 1)**2)
    array_position = np.argmin((r_gam - rhatnorm)**2)

    alpha = gam[array_position]
    beta_l = left_std * np.sqrt(gamma(1 / alpha) / gamma(3 / alpha))
    beta_r = right_std * np.sqrt(gamma(1 / alpha) / gamma(3 / alpha))
    return (alpha, beta_l, beta_r)

def compute_feature(block):
    feat = []
    alpha, beta_l, beta_r = estimate_aggd_param(block)
    feat.extend([alpha, (beta_l + beta_r) / 2])
    shifts = [[0, 1], [1, 0], [1, 1], [1, -1]]
    for i in range(len(shifts)):
        shifted_block = np.roll(block, shifts[i], axis=(0, 1))
        alpha, beta_l, beta_r = estimate_aggd_param(block * shifted_block)
        mean = (beta_r - beta_l) * (gamma(2 / alpha) / gamma(1 / alpha))
        feat.extend([alpha, mean, beta_l, beta_r])
    return feat

def niqe(img, mu_pris_param, cov_pris_param, gaussian_window, block_size_h=96, block_size_w=96):
    h, w = img.shape
    num_block_h = math.floor(h / block_size_h)
    num_block_w = math.floor(w / block_size_w)
    img = img[0:num_block_h * block_size_h, 0:num_block_w * block_size_w]

    distparam = []
    for scale in (1, 2):
        mu = convolve(img, gaussian_window, mode='nearest')
        sigma = np.sqrt(np.abs(convolve(np.square(img), gaussian_window, mode='nearest') - np.square(mu)))
        img_nomalized = (img - mu) / (sigma + 1)

        feat = []
        for idx_w in range(num_block_w):
            for idx_h in range(num_block_h):
                block = img_nomalized[idx_h * block_size_h // scale:(idx_h + 1) * block_size_h // scale,
                                      idx_w * block_size_w // scale:(idx_w + 1) * block_size_w // scale]
                feat.append(compute_feature(block))
        distparam.append(np.array(feat))
        if scale == 1:
            h, w = img.shape
            img = cv2.resize(img / 255., (w // 2, h // 2), interpolation=cv2.INTER_LINEAR) * 255.

    distparam = np.concatenate(distparam, axis=1)
    mu_distparam = np.nanmean(distparam, axis=0)
    distparam_no_nan = distparam[~np.isnan(distparam).any(axis=1)]
    cov_distparam = np.cov(distparam_no_nan, rowvar=False)

    invcov_param = np.linalg.pinv((cov_pris_param + cov_distparam) / 2)
    quality = np.matmul(np.matmul((mu_pris_param - mu_distparam), invcov_param), np.transpose((mu_pris_param - mu_distparam)))
    return np.sqrt(quality)

def calculate_niqe(img, crop_border=0, input_order='HWC', convert_to='y'):
    niqe_pris_params = np.load(PARAMS_PATH)
    mu_pris_param = niqe_pris_params['mu_pris_param']
    cov_pris_param = niqe_pris_params['cov_pris_param']
    gaussian_window = niqe_pris_params['gaussian_window']

    img = img.astype(np.float32)
    if input_order != 'HW':
        img = reorder_image(img, input_order=input_order)
        if convert_to == 'y':
            img = to_y_channel(img)
        img = np.squeeze(img)

    if crop_border != 0:
        img = img[crop_border:-crop_border, crop_border:-crop_border]

    return niqe(img, mu_pris_param, cov_pris_param, gaussian_window)

# ══════════════════════════════════════════════════════════════════════════════
# Main Execution
# ══════════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NIQE Calculator for Enhanced Images")
    parser.add_argument("--input", type=str, default=IMAGE_DIR, help="Path to folder containing images")
    args = parser.parse_args()

    active_dir = args.input

    if not os.path.exists(PARAMS_PATH):
        print(f"Error: NIQE parameters not found at {PARAMS_PATH}")
        exit(1)

    images = sorted(glob.glob(os.path.join(active_dir, "*.png")) + glob.glob(os.path.join(active_dir, "*.jpg")) + glob.glob(os.path.join(active_dir, "*.jpeg")))
    if not images:
        print(f"No images found in {active_dir}")
        exit(1)

    print(f"Calculating NIQE for {len(images)} images in {active_dir}...")
    scores = []
    for img_path in tqdm(images):
        img = cv2.imread(img_path)
        if img is None:
            continue
        try:
            score = calculate_niqe(img, crop_border=0)
            scores.append(score)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    if scores:
        print("=" * 40)
        print(f"Average NIQE: {np.mean(scores):.4f}")
        print("=" * 40)
    else:
        print("No scores calculated.")
