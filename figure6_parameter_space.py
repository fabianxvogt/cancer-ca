"""
Figure 6: Parameter Space Analysis
===================================

Comprehensive sweep over parameter space showing global negative correlation.

Heatmaps of response and stability across:
- Tumor radius (size)
- Therapy intensity
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics
import pandas as pd
from scipy.stats import pearsonr
import seaborn as sns

print("Running parameter space sweep...")
print("This will take a few minutes...")

# Parameter grid
radii = [12, 15, 20, 25]
intensities = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]

results = []
total_configs = len(radii) * len(intensities)
config_num = 0

for radius in radii:
    for intensity in intensities:
        config_num += 1
        print(f"  [{config_num:2d}/{total_configs}] Radius={radius}, Intensity={intensity:.1f}")
        
        ca = AdvancedTumorCA(size=120, seed=42)
        ca.initialize_tumor(radius=radius, normal_cells=False)
        
        duration = 100  # Fixed duration
        
        for step in range(500):
            if step >= 200 and step < 200 + duration:
                ca.therapy = np.ones((120, 120)) * intensity
            else:
                ca.therapy = np.zeros((120, 120))
            ca.step()
        
        total = np.array(ca.history['sensitive']) + np.array(ca.history['resistant'])
        baseline = total[200]
        nadir = np.min(total[200:200+duration])
        response = (baseline - nadir) / (baseline + 1) * 100
        
        metrics = StabilityMetrics.compute_all_metrics(ca.history, 200, 200 + duration)
        
        results.append({
            'radius': radius,
            'intensity': intensity,
            'response': response,
            'stability': metrics['stability_score'],
            'reversibility': metrics['reversibility_score']
        })

df = pd.DataFrame(results)

# Calculate global correlation
corr, pval = pearsonr(df['response'], df['stability'])
print(f"\n✓ Global correlation: ρ = {corr:.3f}, p = {pval:.2e}")

# Create figure
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

# Panel A: Response heatmap
ax1 = fig.add_subplot(gs[0, 0])
pivot_response = df.pivot_table(values='response', index='intensity', columns='radius')
sns.heatmap(pivot_response, annot=True, fmt='.1f', cmap='RdYlGn_r', 
           ax=ax1, cbar_kws={'label': 'Response (%)'}, vmin=0, vmax=100)
ax1.set_title('A) Tumor Response Across Parameter Space', fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel('Tumor Radius (initial cells)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Therapy Intensity', fontsize=12, fontweight='bold')

# Panel B: Stability heatmap
ax2 = fig.add_subplot(gs[0, 1])
pivot_stability = df.pivot_table(values='stability', index='intensity', columns='radius')
sns.heatmap(pivot_stability, annot=True, fmt='.3f', cmap='RdYlGn', 
           ax=ax2, cbar_kws={'label': 'Stability Score'}, vmin=0.35, vmax=0.55)
ax2.set_title('B) Intervention Stability Across Parameter Space', fontsize=14, fontweight='bold', pad=15)
ax2.set_xlabel('Tumor Radius (initial cells)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Therapy Intensity', fontsize=12, fontweight='bold')

# Panel C: Reversibility heatmap
ax3 = fig.add_subplot(gs[1, 0])
pivot_reversibility = df.pivot_table(values='reversibility', index='intensity', columns='radius')
sns.heatmap(pivot_reversibility, annot=True, fmt='.3f', cmap='RdYlGn', 
           ax=ax3, cbar_kws={'label': 'Reversibility'}, vmin=0, vmax=1)
ax3.set_title('C) Reversibility Across Parameter Space', fontsize=14, fontweight='bold', pad=15)
ax3.set_xlabel('Tumor Radius (initial cells)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Therapy Intensity', fontsize=12, fontweight='bold')

# Panel D: Global scatter plot
ax4 = fig.add_subplot(gs[1, 1])
scatter = ax4.scatter(df['response'], df['stability'], 
                     c=df['intensity'], s=150, alpha=0.7, 
                     cmap='viridis', edgecolors='black', linewidth=1)

# Regression line
z = np.polyfit(df['response'], df['stability'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['response'].min(), df['response'].max(), 100)
ax4.plot(x_line, p(x_line), 'r--', linewidth=3, alpha=0.8, 
        label=f'Linear fit (ρ={corr:.3f}, p={pval:.2e})')

ax4.set_xlabel('Response (%)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Stability', fontsize=12, fontweight='bold')
ax4.set_title('D) Global Correlation: Response vs Stability', fontsize=14, fontweight='bold', pad=15)
ax4.grid(True, alpha=0.3)
ax4.legend(fontsize=10, loc='upper right')

# Colorbar on the right side
cbar = plt.colorbar(scatter, ax=ax4, pad=0.02)
cbar.set_label('Therapy Intensity', fontsize=10, fontweight='bold')

# Add text box with statistics - position lower left to avoid legend
ax4.text(0.05, 0.25, f'N = {len(df)} configs\nρ = {corr:.3f}\np = {pval:.2e}', 
        transform=ax4.transAxes, fontsize=10, fontweight='bold',
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9, edgecolor='black', linewidth=1.5))

plt.suptitle('Parameter Space Analysis: Universal Negative Correlation', 
            fontsize=17, fontweight='bold', y=0.98)

plt.savefig('images/figure6_parameter_space.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n✓ Figure 6 saved: images/figure6_parameter_space.png")
plt.close()
