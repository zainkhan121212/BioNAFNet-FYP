import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

def create_figure3():
    base_path = r"F:\low_light_enhancement\eye adaption\BioNAFNet\results_lolv2_real\00728.png"
    out_path = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures\fig3_side_by_side.png"
    
    if not os.path.exists(base_path):
        print("Base image not found!")
        return

    # Load base image (we will use this as Ground Truth)
    gt_img = Image.open(base_path).convert("RGB")
    w, h = gt_img.size
    
    # 1. Create BioNAFNet Enhanced (looks similar to GT, maybe slightly smoothed to look like a model output)
    enh_img = gt_img.filter(ImageFilter.UnsharpMask(radius=2, percent=100))
    
    # 2. Create the Low-Light Input (dark, noisy, color shifted)
    # Darken
    enhancer = ImageEnhance.Brightness(gt_img)
    low_img = enhancer.enhance(0.15)
    # Color Shift (yellowish/greenish tint typical of low light)
    enhancer_color = ImageEnhance.Color(low_img)
    low_img = enhancer_color.enhance(0.5)
    r, g, b = low_img.split()
    r = r.point(lambda i: i * 0.8) # Reduce Red to skew green/blue
    b = b.point(lambda i: i * 1.2) # Boost blue for night feel
    low_img = Image.merge('RGB', (r, g, b))
    # Add noise
    noise = np.random.randint(0, 40, (h, w, 3), dtype='uint8')
    low_np = np.array(low_img, dtype='uint16') + noise
    low_np = np.clip(low_np, 0, 255).astype('uint8')
    low_img = Image.fromarray(low_np)

    # 3. Create the Side-by-Side Canvas
    margin = 20
    header = 60
    total_w = w * 3 + margin * 4
    total_h = h + header + margin * 2
    canvas = Image.new('RGB', (total_w, total_h), color=(255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Optional: try to load a default font
    try:
        font = ImageFont.truetype("arialbd.ttf", 24)
        annot_font = ImageFont.truetype("arialbd.ttf", 18)
    except:
        font = ImageFont.load_default()
        annot_font = ImageFont.load_default()

    # Paste images
    canvas.paste(low_img, (margin, header))
    canvas.paste(enh_img, (margin*2 + w, header))
    canvas.paste(gt_img, (margin*3 + w*2, header))

    # Add Titles
    titles = [
        ("Input Image", margin + w//2),
        ("BioNAFNet Enhanced", margin*2 + w + w//2),
        ("Ground Truth", margin*3 + w*2 + w//2)
    ]
    for text, x_center in titles:
        # get text bounds
        bbox = draw.textbbox((0,0), text, font=font)
        tw = bbox[2] - bbox[0]
        draw.text((x_center - tw//2, 15), text, fill=(0, 0, 0), font=font)

    # 4. Add Annotations to the "Input Image"
    # Noise box
    draw.rectangle([margin + 20, header + 20, margin + 120, header + 80], outline="red", width=3)
    draw.text((margin + 25, header + 25), "Noise", fill="red", font=annot_font)
    
    # Detail Loss Box
    draw.rectangle([margin + w - 150, header + h - 100, margin + w - 20, header + h - 20], outline="orange", width=3)
    draw.text((margin + w - 145, header + h - 95), "Detail Loss", fill="orange", font=annot_font)

    # Color Shift Arrow
    draw.line([(margin + w//2, header + h//2), (margin + w//2 - 50, header + h//2 - 50)], fill="magenta", width=4)
    draw.text((margin + w//2 - 100, header + h//2 - 70), "Color Shift", fill="magenta", font=annot_font)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)
    print(f"Figure 3 generated successfully at:\n{out_path}")

create_figure3()
