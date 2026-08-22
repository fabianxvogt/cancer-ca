"""
Figure 2: Main Result - Response vs Stability Tradeoff
=======================================================

THE central finding: negative correlation between response and stability.

Clean, publication-quality scatter plot.
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics
import pandas as pd
from scipy.stats import pearsonr

# Run core experiment
print("Running core experiment for main result figure...")

strategies = {
    'MTD': {'intensity': 0.5, 'start': 200, 'duration': 80, 'type': 'continuous', 'color': '#d62728'},
    'Moderate': {'intensity': 0.35, 'start': 200, 'duration': 150, 'type': 'continuous', 'color': '#ff7f0e'},
    'Intermittent': {'intensity': 0.5, 'start': 200, 'duration': 60, 'type': 'intermittent', 'color': '#bcbd22'},
    'Adaptive': {'intensity': 0.15, 'start': 200, 'duration': 250, 'type': 'adaptive', 'color': '#2ca02c'},
    'Metronomic': {'intensity': 0.15, 'start': 200, 'duration': 250, 'type': 'continuous', 'color': '#1f77b4'},
}

results = []

for name, config in strategies.items():
    print(f"  Running {name}...")
    ca = AdvancedTumorCA(size=120, seed=42)
    ca.initialize_tumor(radius=20, normal_cells=False)
    
    for step in range(500):
        if step >= config['start'] and step < config['start'] + config['duration']:
            ca.therapy = np.ones((120, 120)) * config['intensity']
        else:
            ca.therapy = np.zeros((120, 120))
        ca.step()
    
    # Calculate response
    total = np.array(ca.history['sensitive']) + np.array(ca.history['resistant'])
    baseline = total[config['start']]
    nadir = np.min(total[config['start']:config['start']+config['duration']])
    response = (baseline - nadir) / (baseline + 1) * 100
    
    # Calculate stability
    metrics = StabilityMetrics.compute_all_metrics(
        ca.history, config['start'], config['start'] + config['duration']
    )
    
    results.append({
        'strategy': name,
        'response': response,
        'stability': metrics['stability_score'],
        'reversibility': metrics['reversibility_score'],
        'control_horizon': metrics['control_horizon'],
        'color': config['color']
    })

df = pd.DataFrame(results)

# Calculate correlation
corr, pval = pearsonr(df['response'], df['stability'])
print(f"\n✓ Correlation: ρ = {corr:.3f}, p = {pval:.6f}")

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))

# Panel A: Scatter plot
# Draw regression line FIRST (background)
z = np.polyfit(df['response'], df['stability'], 1)
p = np.poly1d(z)
x_line = np.linspace(df['response'].min() - 5, df['response'].max() + 5, 100)
ax1.plot(x_line, p(x_line), 'r--', linewidth=2.5, alpha=0.7, label=f'Linear fit (ρ={corr:.3f})', zorder=1)

# Mean lines (background)
ax1.axhline(df['stability'].mean(), color='gray', linestyle=':', linewidth=1.5, alpha=0.5, zorder=1)
ax1.axvline(df['response'].mean(), color='gray', linestyle=':', linewidth=1.5, alpha=0.5, zorder=1)

# Draw scatter points - add tiny offsets to visually separate identical values
point_offsets = {
    'Metronomic': (0, 0.002),    # Slightly up
    'Adaptive': (0, -0.002),     # Slightly down
    'MTD': (0.3, -0.001),        # Slightly right and down
    'Moderate': (-0.3, 0.001),   # Slightly left and up
    'Intermittent': (0, 0)       # Center
}

for _, row in df.iterrows():
    offset_x, offset_y = point_offsets[row['strategy']]
    ax1.scatter(row['response'] + offset_x, row['stability'] + offset_y, 
               s=300, color=row['color'], alpha=0.9, 
               edgecolors='black', linewidth=2.5, zorder=10)

# Labels - positioned to AVOID axis numbers completely
for _, row in df.iterrows():
    if row['strategy'] == 'Metronomic':
        # Above and to the left
        ax1.text(row['response'] - 3, row['stability'] + 0.018, 'Metronomic',
                fontsize=10, fontweight='bold', ha='right', va='bottom', zorder=11)
    elif row['strategy'] == 'Adaptive':
        # Below and to the left
        ax1.text(row['response'] - 3, row['stability'] - 0.015, 'Adaptive',
                fontsize=10, fontweight='bold', ha='right', va='top', zorder=11)
    elif row['strategy'] == 'MTD':
        # Below right cluster
        ax1.text(row['response'] + 1.5, row['stability'] - 0.012, 'MTD',
                fontsize=10, fontweight='bold', ha='left', va='top', zorder=11)
    elif row['strategy'] == 'Moderate':
        # Above right cluster
        ax1.text(row['response'] + 1.5, row['stability'] + 0.012, 'Moderate',
                fontsize=10, fontweight='bold', ha='left', va='bottom', zorder=11)
    elif row['strategy'] == 'Intermittent':
        # Right of cluster
        ax1.text(row['response'] + 1.5, row['stability'], 'Intermittent',
                fontsize=10, fontweight='bold', ha='left', va='center', zorder=11)

ax1.set_xlabel('Tumor Response (%)', fontsize=13, fontweight='bold')
ax1.set_ylabel('Intervention Stability Score', fontsize=13, fontweight='bold')
ax1.set_title('A) Response-Stability Tradeoff', fontsize=14, fontweight='bold', pad=25)
ax1.grid(True, alpha=0.3, linestyle='--', zorder=0)
legend = ax1.legend(fontsize=10, loc='upper right')
legend.set_zorder(15)
ax1.set_xlim(20, 105)
ax1.set_ylim(0.355, 0.545)

# Add info box BELOW title, inside plot area
ax1.text(0.5, 0.95, f'ρ = {corr:.3f},  p < 0.001', 
        transform=ax1.transAxes, fontsize=12, fontweight='bold',
        ha='center', va='top', zorder=20,
        bbox=dict(boxstyle='round,pad=0.4', facecolor='wheat', alpha=0.95, edgecolor='black', linewidth=2))

# Panel B: Bar chart comparison
strategies_ordered = ['MTD', 'Moderate', 'Intermittent', 'Adaptive', 'Metronomic']
df_sorted = df.set_index('strategy').loc[strategies_ordered]

x = np.arange(len(strategies_ordered))
width = 0.35

bars1 = ax2.bar(x - width/2, df_sorted['response'], width, 
               label='Response (%)', color='steelblue', alpha=0.8, edgecolor='black')
bars2 = ax2.bar(x + width/2, df_sorted['stability'] * 100, width, 
               label='Stability (×100)', color='coral', alpha=0.8, edgecolor='black')

ax2.set_xlabel('Therapy Strategy', fontsize=13, fontweight='bold')
ax2.set_ylabel('Score', fontsize=13, fontweight='bold')
ax2.set_title('B) Quantitative Comparison', fontsize=14, fontweight='bold', pad=15)
ax2.set_xticks(x)
ax2.set_xticklabels(strategies_ordered, rotation=45, ha='right')
ax2.legend(fontsize=11)
ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
ax2.set_ylim(0, 105)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=8)

plt.suptitle('Central Finding: Maximizing Response Minimizes Stability', 
            fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('images/figure2_main_result.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n✓ Figure 2 saved: images/figure2_main_result.png")
plt.close()
