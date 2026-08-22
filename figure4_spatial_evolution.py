"""
Figure 4: Spatial Evolution Under MTD
======================================

Shows the spatial dynamics of evolutionary regime shift.

Snapshots at key timepoints showing:
- Initial tumor (pre-therapy)
- During therapy (population collapse)
- Post-therapy (resistant takeover)
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from matplotlib.colors import ListedColormap, BoundaryNorm

print("Running MTD simulation for spatial evolution...")

ca = AdvancedTumorCA(size=150, seed=42)
ca.initialize_tumor(radius=35, normal_cells=False)  # Larger grid and tumor

# Store snapshots
snapshots = {}
snapshot_times = [0, 150, 200, 250, 280, 350, 450]
snapshot_labels = ['Initial', 'Pre-therapy', 'Therapy Start', 'Mid-therapy', 'Therapy End', 'Recovery', 'Final']

for step in range(500):
    if step >= 200 and step < 250:  # Shortened from 280 to prevent too many dead cells
        ca.therapy = np.ones((150, 150)) * 0.12  # Further reduced to keep dead cells ~30-40%
    else:
        ca.therapy = np.zeros((150, 150))
    
    if step in snapshot_times:
        snapshots[step] = ca.grid.copy()
    
    ca.step()

# Create figure
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.flatten()

# Create custom colormap with explicit normalization
colors = ['white', '#90EE90', '#FFB6C1', '#8B008B', 'dimgray']  # 0=Empty, 1=Normal, 2=Sensitive, 3=Resistant, 4=Dead
cmap = ListedColormap(colors)
bounds = [0, 1, 2, 3, 4, 5]
norm = BoundaryNorm(bounds, cmap.N)

# Also need to map state values correctly
# In tumor_ca.py: EMPTY=0, NORMAL=1, TUMOR_SENSITIVE=2, TUMOR_RESISTANT=3, DEAD=4

for idx, (step, label) in enumerate(zip(snapshot_times, snapshot_labels)):
    ax = axes[idx]
    
    # Get grid and check values
    grid = snapshots[step]
    unique_vals = np.unique(grid)
    print(f"t={step}: Unique values in grid: {unique_vals}")
    
    # Plot grid with explicit boundary normalization
    im = ax.imshow(grid, cmap=cmap, norm=norm, interpolation='nearest')
    
    # Count cells
    grid = snapshots[step]
    n_sensitive = np.sum(grid == 2)
    n_resistant = np.sum(grid == 3)
    total = n_sensitive + n_resistant
    res_frac = n_resistant / (total + 1) * 100 if total > 0 else 0
    
    ax.set_title(f't={step}: {label}\n'
                f'Total: {total:,} | Resistant: {res_frac:.1f}%',
                fontsize=11, fontweight='bold')
    ax.axis('off')
    
    # Add border for therapy period
    if 200 <= step < 250:  # Updated therapy duration
        for spine in ['top', 'bottom', 'left', 'right']:
            ax.spines[spine].set_visible(True)
            ax.spines[spine].set_color('blue')
            ax.spines[spine].set_linewidth(4)

# Hide last axis (7 snapshots, 8 subplots)
axes[7].axis('off')

# Add colorbar legend
cbar_ax = fig.add_axes([0.75, 0.15, 0.15, 0.03])
cbar = plt.colorbar(im, cax=cbar_ax, orientation='horizontal', ticks=[0, 1, 2, 3, 4])
cbar.set_label('Cell State', fontsize=10, fontweight='bold')
cbar.ax.set_xticklabels(['Empty', 'Normal', 'Sensitive', 'Resistant', 'Dead'], fontsize=8, rotation=0)

# Add annotations
fig.text(0.05, 0.95, 'Blue border = Therapy active (t=200-250)', 
        fontsize=11, fontweight='bold', color='blue',
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.suptitle('Spatial Evolution: MTD Induces Irreversible Evolutionary Regime Shift', 
            fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('images/figure4_spatial_evolution.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n✓ Figure 4 saved: images/figure4_spatial_evolution.png")
plt.close()
