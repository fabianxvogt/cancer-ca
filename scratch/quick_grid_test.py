"""
Quick Grid Size Test - Simplified version for rapid validation
Tests 3 grid sizes with only 5 intensity levels each
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from scipy.stats import pearsonr, entropy
import seaborn as sns
import json

sns.set_style("whitegrid")

def calculate_response_diversity(population, sensitive_state=2, resistant_state=3):
    """Calculate response diversity metric."""
    n_sensitive = np.sum(population == sensitive_state)
    n_resistant = np.sum(population == resistant_state)
    total = n_sensitive + n_resistant
    
    if total == 0:
        return 0.0
    
    p_sensitive = n_sensitive / total
    p_resistant = n_resistant / total
    
    probs = [p for p in [p_sensitive, p_resistant] if p > 0]
    if len(probs) == 0:
        return 0.0
    return entropy(probs, base=2)

def run_one_trial(size, therapy_intensity, protocol_type):
    """Run a single trial."""
    ca = AdvancedTumorCA(size=size)
    ca.initialize_tumor(radius=int(size/4))
    
    for t in range(500):
        if protocol_type == "MTD":
            ca.therapy = np.ones((size, size)) * (therapy_intensity if 200 <= t < 400 else 0.0)
        else:  # Metronomic
            ca.therapy = np.ones((size, size)) * (therapy_intensity * 0.5 if 200 <= t < 450 else 0.0)
        ca.step()
    
    # Check if population survived
    total = np.sum((ca.grid == 2) | (ca.grid == 3))
    if total < 10:
        return None
    
    metric = calculate_response_diversity(ca.grid)
    resistant_frac = np.sum(ca.grid == 3) / max(1, total)
    
    return {'metric': metric, 'resistant_frac': resistant_frac}

# Quick test: 3 sizes × 5 intensities × 2 protocols
sizes = [60, 120, 240]
intensities = [0.2, 0.4, 0.6, 0.8, 1.0]

results = []

for size in sizes:
    print(f"\n Testing {size}×{size}")
    for intensity in intensities:
        print(f"  Intensity {intensity}")
        
        mtd = run_one_trial(size, intensity, "MTD")
        metro = run_one_trial(size, intensity, "Metronomic")
        
        if mtd and metro:
            results.append({
                'size': size,
                'intensity': intensity,
                'mtd_metric': mtd['metric'],
                'metro_metric': metro['metric'],
                'mtd_resistance': mtd['resistant_frac'],
                'metro_resistance': metro['resistant_frac']
            })

# Save
with open('images/grid_size_results.json', 'w') as f:
    json.dump({'results': results}, f, indent=2)

# Calculate correlations per size
correlations = []
for size in sizes:
    size_data = [r for r in results if r['size'] == size]
    if len(size_data) >= 3:
        mtd_metrics = [r['mtd_metric'] for r in size_data]
        metro_metrics = [r['metro_metric'] for r in size_data]
        if len(set(mtd_metrics)) > 1:
            rho, p = pearsonr(mtd_metrics, metro_metrics)
            correlations.append({'size': size, 'rho': rho, 'p': p, 'n': len(size_data)})
            print(f"\n{size}×{size}: ρ={rho:.4f}, p={p:.2e}, n={len(size_data)}")

# Quick plot
fig, axes = plt.subplots(1, 4, figsize=(16, 4))

for idx, size in enumerate(sizes):
    ax = axes[idx]
    size_data = [r for r in results if r['size'] == size]
    if size_data:
        mtd = [r['mtd_metric'] for r in size_data]
        metro = [r['metro_metric'] for r in size_data]
        ax.scatter(mtd, metro, s=80, alpha=0.7)
        ax.set_xlabel('MTD Metric')
        ax.set_ylabel('Metronomic Metric')
        ax.set_title(f'{size}×{size}')
        ax.grid(True, alpha=0.3)
        
        # Add correlation
        corr = next((c for c in correlations if c['size'] == size), None)
        if corr:
            ax.text(0.05, 0.95, f"ρ={corr['rho']:.3f}\\np={corr['p']:.1e}",
                   transform=ax.transAxes, va='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot 4: Correlation vs size
ax = axes[3]
if correlations:
    sizes_plot = [c['size'] for c in correlations]
    rhos_plot = [c['rho'] for c in correlations]
    ax.plot(sizes_plot, rhos_plot, 'o-', markersize=10, linewidth=2)
    ax.set_xlabel('Grid Size')
    ax.set_ylabel('Correlation (ρ)')
    ax.set_title('Scale Dependence')
    ax.set_xticks(sizes_plot)
    ax.axhline(0, color='k', linestyle='--', alpha=0.3)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('images/figure_S4_grid_size.png', dpi=300, bbox_inches='tight')
plt.savefig('images/figure_S4_grid_size.pdf', bbox_inches='tight')
print("\n✓ Saved Figure S4")
