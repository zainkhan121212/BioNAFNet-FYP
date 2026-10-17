import os
import glob
import numpy as np
from PIL import Image
from tqdm import tqdm

def convert_sdsd_dataset():
    input_dir = r"G:\bankai\retinex former_TRANSFORMER\Retinexformer-master\data\SDSD"
    output_dir = r"G:\bankai\retinex former_TRANSFORMER\Retinexformer-master\data\SDSD_PNG"

    print(f"Searching for .npy files in: {input_dir}")
    npy_files = glob.glob(os.path.join(input_dir, "**", "*.npy"), recursive=True)

    if not npy_files:
        print("No .npy files found.")
        return

    print(f"Found {len(npy_files)} numpy files. Converting to PNG...")
    
    success = 0
    for npy_path in tqdm(npy_files):
        try:
            # Recreate directory structure
            rel_path = os.path.relpath(npy_path, input_dir)
            out_file = os.path.join(output_dir, os.path.splitext(rel_path)[0] + ".png")
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            
            # Load and save to png (the arrays are already 1080x1920x3 uint8)
            arr = np.load(npy_path)
            
            # If for some reason it's [C,H,W], permute to [H,W,C]
            if arr.shape[0] == 3:
                arr = np.transpose(arr, (1, 2, 0))
                
            img = Image.fromarray(arr)
            img.save(out_file)
            success += 1
        except Exception as e:
            print(f"Error converting {npy_path}: {e}")

    print(f"\nDone! Successfully converted {success}/{len(npy_files)} files.")
    print(f"All converted PNGs are safely saved in: {output_dir}")

if __name__ == "__main__":
    convert_sdsd_dataset()
