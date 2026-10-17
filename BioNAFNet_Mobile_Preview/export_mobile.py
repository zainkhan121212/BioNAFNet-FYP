import os
import torch
import torch.nn as nn
from realtime_preview import BioNAFNet  # Import from the sibling script

def export_model():
    print("--- Exporting BioNAFNet-Lite for Mobile/Edge ---")
    
    device = torch.device("cpu") # Exporting usually done against CPU inference graph
    print("Initializing architecture...")
    model = BioNAFNet(width=32, middle_blk_num=4, enc_blk_nums=[2, 2, 4, 8], dec_blk_nums=[2, 2, 2, 2], n_passes=1).to(device)

    # Load weights
    ckpt_path = "best_student.pth"
    if not os.path.exists(ckpt_path):
        print(f"Error: Target weights '{ckpt_path}' not found.")
        return
        
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt.get("ema", ckpt.get("model")))
    model.eval()
    
    # Create Dummy Input
    # Typical mobile preview resolutions
    H, W = 480, 640
    print(f"Generating dummy input tensor [1, 3, {H}, {W}] for tracing...")
    dummy_input = torch.randn(1, 3, H, W).to(device)

    # --- TorchScript Export (Best for PyTorch Mobile - Android/iOS) ---
    ts_path = "BioNAFNet_Lite_Mobile.pt"
    print(f"\n1. Exporting TorchScript model to '{ts_path}'...")
    try:
        # We use tracing over scripting because of the complex RLIN/TAM branches
        traced_script_module = torch.jit.trace(model, dummy_input)
        
        # Optimize for mobile
        from torch.utils.mobile_optimizer import optimize_for_mobile
        optimized_traced_model = optimize_for_mobile(traced_script_module)
        
        optimized_traced_model._save_for_lite_interpreter(ts_path)
        print("   [OK] TorchScript Mobile Ready export successful!")
    except Exception as e:
        print(f"   [FAIL] TorchScript export failed: {e}")

    # --- ONNX Export (Best for browsers, edge TPUs, generic C++) ---
    onnx_path = "BioNAFNet_Lite.onnx"
    print(f"\n2. Exporting ONNX model to '{onnx_path}'...")
    try:
        torch.onnx.export(
            model, 
            dummy_input, 
            onnx_path, 
            export_params=True, 
            opset_version=16, # Use modern opset
            do_constant_folding=True, 
            input_names=['input_image'], 
            output_names=['enhanced_image'],
            dynamic_axes={'input_image': {0: 'batch_size', 2: 'height', 3: 'width'},
                          'enhanced_image': {0: 'batch_size', 2: 'height', 3: 'width'}}
        )
        print("   [OK] ONNX export successful!")
    except Exception as e:
        print(f"   [FAIL] ONNX export failed: {e}")
        
    print("\n--- Export Complete ---")
    print(f"Find files in: {os.getcwd()}")

if __name__ == "__main__":
    export_model()
