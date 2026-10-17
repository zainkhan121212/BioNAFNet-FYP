import matplotlib.pyplot as plt
import numpy as np
import os

def create_bar_chart():
    # Data from REWRITE_GUIDE.md
    methods = ['KinD\n(2019)', 'SNR-Aware\n(2022)', 'Teacher\n(Ours)', 'Retinexformer\n(2023)', 'Student\n(Ours)']
    psnr_values = [20.87, 24.61, 24.94, 25.16, 25.23]
    
    # Colors for the bars
    # 'Our' methods get a distinct color (e.g., deep blue or purple)
    colors = ['#8b8b9a', '#8b8b9a', '#6366f1', '#8b8b9a', '#00f5ff']
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bars
    bars = ax.bar(methods, psnr_values, color=colors, edgecolor='black', linewidth=1.2, width=0.6)
    
    # Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontweight='bold', fontsize=12)
    
    # Set y limit to make differences more visible (start from 15 instead of 0)
    ax.set_ylim(15, 27)
    
    # Styling
    ax.set_ylabel('PSNR (dB)', fontsize=14, fontweight='bold')
    ax.set_title('PSNR Comparison on LOLv1 Dataset', fontsize=16, fontweight='bold', pad=20)
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=11)
    
    # Grid lines for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True) # Put background grid behind bars
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Save the plot
    out_dir = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "fig_psnr_comparison_lolv1.png")
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {out_path}")

create_bar_chart()
