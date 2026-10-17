import matplotlib.pyplot as plt
import re
import os

def create_convergence_chart():
    log_path = r'f:/low_light_enhancement/eye adaption/BioNAFNet/training_log.txt'
    if not os.path.exists(log_path):
        print("Could not find training_log.txt")
        return
        
    psnr_vals = []
    with open(log_path, 'r') as f:
        for line in f:
            m = re.search(r'PSNR[:\s]*([0-9]+\.[0-9]+)', line, re.IGNORECASE)
            if m:
                psnr_vals.append(float(m.group(1)))
                
    if not psnr_vals:
        print("No PSNR values extracted.")
        return
        
    # Assume 1 epoch per recorded value for simplicity, though log might have multiple validations.
    # usually we can just plot them sequentially
    epochs = list(range(1, len(psnr_vals) + 1))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot line
    ax.plot(epochs, psnr_vals, color='#b829dd', linewidth=2, label='Teacher Model PSNR')
    
    # Highlight the best PSNR
    best_psnr = max(psnr_vals)
    best_epoch = psnr_vals.index(best_psnr) + 1
    
    ax.scatter(best_epoch, best_psnr, color='#ff006e', s=80, zorder=5, label=f'Peak: {best_psnr:.2f} dB')
    ax.annotate(f'Max: {best_psnr:.2f}', 
                xy=(best_epoch, best_psnr), 
                xytext=(10, -15), 
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.3))

    ax.set_title('Teacher Model PSNR Convergence Detail', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Validation Step / Epoch', fontsize=12, fontweight='bold')
    ax.set_ylabel('PSNR (dB)', fontsize=12, fontweight='bold')
    
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='lower right', fontsize=12)
    
    out_dir = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig_teacher_convergence.png")
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    print(f"Chart saved to {out_path}")

create_convergence_chart()
