"""Portable inference entry point using the project's unchanged model architecture."""
import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=['student', 'teacher'], default='student')
    parser.add_argument('--weights', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    args = parser.parse_args()
    if not args.weights.is_file():
        parser.error('Checkpoint missing: download the release weights first.')
    if not args.input.is_file():
        parser.error('--input must be an image file.')
    if args.input.resolve() == args.output.resolve():
        parser.error('Choose a different output path to preserve the original image.')
    import numpy as np
    import torch
    from PIL import Image
    root = Path(__file__).resolve().parent
    folder = 'Student_Model' if args.model == 'student' else 'Teacher_Model'
    sys.path.insert(0, str(root / folder / 'code' / 'code'))
    from model import BioNAFNet
    if args.device == 'cuda' and not torch.cuda.is_available():
        parser.error('CUDA is unavailable; use --device cpu or install a matching CUDA PyTorch build.')
    student = args.model == 'student'
    model = BioNAFNet(width=32 if student else 64,
                      middle_blk_num=4 if student else 12,
                      n_passes=1 if student else 2)
    checkpoint = torch.load(args.weights, map_location='cpu', weights_only=True)
    model.load_state_dict(checkpoint.get('ema', checkpoint.get('model', checkpoint)), strict=True)
    model = model.to(args.device).eval()
    with Image.open(args.input) as source:
        rgb = np.asarray(source.convert('RGB'), dtype=np.float32) / 255.0
    tensor = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0).to(args.device)
    with torch.inference_mode():
        result = model(tensor).clamp(0, 1)[0].permute(1, 2, 0).cpu().numpy()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((result * 255).round().astype(np.uint8)).save(args.output)
    print(f'Saved {args.output}')


if __name__ == '__main__':
    main()
