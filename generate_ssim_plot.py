import matplotlib.pyplot as plt
import numpy as np
import os

# Create directory if it doesn't exist
output_dir = r"F:\low_light_enhancement\eye adaption\BioNAFNet\clean_plots"
os.makedirs(output_dir, exist_ok=True)

def set_style():
    plt.style.use('default')
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.alpha'] = 0.3
    plt.rcParams['grid.color'] = '#CCCCCC'

def plot_ssim_comparison():
    set_style()
    plt.figure(figsize=(10, 5))
    
    # Models to keep
    models = ['Teacher\n(154M)', 'Student-350\n(24M)', 'Student-693\n(24M)']
    
    # Data from Table 20
    lolv1_ssim = [0.8661, 0.8409, 0.8528]
    lolv2r_ssim = [0.9101, 0.8844, 0.8942]
    lolv2s_ssim = [0.9457, 0.9329, 0.9375]
    
    x = np.arange(len(models))
    bar_width = 0.25
    
    # Matching the colors from the user's image
    c_lolv1 = '#2196F3' # Bright Blue
    c_lolv2r = '#4CAF50' # Green
    c_lolv2s = '#FF9800' # Orange
    
    plt.bar(x - bar_width, lolv1_ssim, bar_width, label='LOLv1', color=c_lolv1, edgecolor='none')
    plt.bar(x, lolv2r_ssim, bar_width, label='LOLv2 Real', color=c_lolv2r, edgecolor='none')
    plt.bar(x + bar_width, lolv2s_ssim, bar_width, label='LOLv2 Synthetic', color=c_lolv2s, edgecolor='none')
    
    plt.xticks(x, models, fontsize=9)
    
    # Set y-axis to match the provided image
    plt.ylim(0.82, 0.96)
    plt.ylabel('SSIM', fontsize=10)
    plt.title('SSIM Comparison Across Model Variants', fontsize=12)
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.0), fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, '6_SSIM_Comparison.png')
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}")

if __name__ == "__main__":
    plot_ssim_comparison()
