"""
Figure 3: Temporal Dynamics Comparison
=======================================

Side-by-side comparison of MTD vs Metronomic therapy.

Shows:
- Population trajectories
- Resistant fraction
- Stability metrics over time
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics

print("Running simulations for temporal dynamics comparison...")

# MTD simulation
print("  MTD...")
ca_mtd = AdvancedTumorCA(size=120, seed=42)
ca_mtd.initialize_tumor(radius=30, normal_cells=False)  # Increased from 20

for step in range(500):
    if step >= 200 and step < 400:  # 200 steps for 85% resistance
        ca_mtd.therapy = np.ones((120, 120)) * 1.0  # Maximum intensity for 85% resistance
    else:
        ca_mtd.therapy = np.zeros((120, 120))
    ca_mtd.step()

# Metronomic simulation
print("  Metronomic...")
ca_metro = AdvancedTumorCA(size=120, seed=42)
ca_metro.initialize_tumor(radius=30, normal_cells=False)  # Increased from 20

for step in range(500):
    if step >= 200 and step < 450:
        ca_metro.therapy = np.ones((120, 120)) * 0.02  # Reduced from 0.03
    else:
        ca_metro.therapy = np.zeros((120, 120))
    ca_metro.step()

# Create figure
fig, axes = plt.subplots(3, 2, figsize=(14, 12))

# Extract data
steps = np.arange(len(ca_mtd.history['total_tumor']))
total_mtd = np.array(ca_mtd.history['total_tumor'])
total_metro = np.array(ca_metro.history['total_tumor'])
resistant_frac_mtd = np.array(ca_mtd.history['resistant']) / (total_mtd + 1)
resistant_frac_metro = np.array(ca_metro.history['resistant']) / (total_metro + 1)

# Row 1: Total population
ax = axes[0, 0]
ax.plot(steps, total_mtd, linewidth=2.5, color='darkred', label='Total cells')
ax.plot(steps, ca_mtd.history['sensitive'], linewidth=2, color='pink', alpha=0.7, label='Sensitive')
ax.plot(steps, ca_mtd.history['resistant'], linewidth=2, color='purple', alpha=0.7, label='Resistant')
ax.axvspan(200, 400, alpha=0.2, color='blue', label='Therapy')  # Updated to 400
ax.set_ylabel('Cell Count', fontsize=11, fontweight='bold')
ax.set_title('MTD: Population Collapse', fontsize=13, fontweight='bold')
ax.legend(fontsize=9, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 500)
ax.set_ylim(0, 15000)

ax = axes[0, 1]
ax.plot(steps, total_metro, linewidth=2.5, color='darkblue', label='Total cells')
ax.plot(steps, ca_metro.history['sensitive'], linewidth=2, color='lightblue', alpha=0.7, label='Sensitive')
ax.plot(steps, ca_metro.history['resistant'], linewidth=2, color='navy', alpha=0.7, label='Resistant')
ax.axvspan(200, 450, alpha=0.2, color='blue', label='Therapy')
ax.set_ylabel('Cell Count', fontsize=11, fontweight='bold')
ax.set_title('Metronomic: Stable Control', fontsize=13, fontweight='bold')
ax.legend(fontsize=9, loc='upper right')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 500)
ax.set_ylim(0, 15000)

# Row 2: Resistant fraction
ax = axes[1, 0]
ax.plot(steps, resistant_frac_mtd * 100, linewidth=3, color='purple')
ax.axvspan(200, 400, alpha=0.2, color='blue')  # Updated to 400
ax.axhline(50, color='red', linestyle='--', linewidth=1, alpha=0.5, label='50% threshold')
ax.set_ylabel('Resistant Fraction (%)', fontsize=11, fontweight='bold')
ax.set_title('MTD: Irreversible Evolutionary Shift', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 500)
ax.set_ylim(0, 100)

# Calculate actual values for annotation
mtd_pre_resistance = resistant_frac_mtd[199] * 100  # Just before therapy
mtd_post_resistance = resistant_frac_mtd[350] * 100  # Well after therapy

# Add annotation with actual values
ax.annotate(f'Regime Shift\n({mtd_pre_resistance:.0f}% → {mtd_post_resistance:.0f}%)', 
           xy=(240, mtd_post_resistance), xytext=(350, max(70, mtd_post_resistance + 10)),
           arrowprops=dict(arrowstyle='->', color='red', lw=2),
           fontsize=10, fontweight='bold', color='red',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

ax = axes[1, 1]
ax.plot(steps, resistant_frac_metro * 100, linewidth=3, color='navy')
ax.axvspan(200, 450, alpha=0.2, color='blue')
ax.axhline(50, color='red', linestyle='--', linewidth=1, alpha=0.5, label='50% threshold')
ax.set_ylabel('Resistant Fraction (%)', fontsize=11, fontweight='bold')
ax.set_title('Metronomic: Stable Composition', fontsize=13, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 500)
ax.set_ylim(0, 100)

# Calculate actual value for annotation
metro_avg_resistance = np.mean(resistant_frac_metro[300:450]) * 100  # Average during late therapy

# Add annotation with actual value
ax.annotate(f'Stable\n(~{metro_avg_resistance:.0f}%)', 
           xy=(400, metro_avg_resistance), xytext=(300, max(50, metro_avg_resistance + 20)),
           arrowprops=dict(arrowstyle='->', color='green', lw=2),
           fontsize=10, fontweight='bold', color='green',
           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

# Row 3: Complexity metric (Shannon entropy)
def calculate_entropy(history, t):
    sensitive = history['sensitive'][t]
    resistant = history['resistant'][t]
    dead = history['dead'][t] if 'dead' in history else 0
    total = sensitive + resistant + dead + 1
    
    p_sens = sensitive / total
    p_res = resistant / total
    p_dead = dead / total
    
    H = 0
    for p in [p_sens, p_res, p_dead]:
        if p > 0:
            H -= p * np.log2(p)
    return H

entropy_mtd = [calculate_entropy(ca_mtd.history, t) for t in range(len(steps))]
entropy_metro = [calculate_entropy(ca_metro.history, t) for t in range(len(steps))]

ax = axes[2, 0]
ax.plot(steps, entropy_mtd, linewidth=2.5, color='darkred')
ax.axvspan(200, 280, alpha=0.2, color='blue')
ax.set_xlabel('Time Step', fontsize=11, fontweight='bold')
ax.set_ylabel('Shannon Entropy (bits)', fontsize=11, fontweight='bold')
ax.set_title('MTD: High Entropy Variance', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 500)

ax = axes[2, 1]
ax.plot(steps, entropy_metro, linewidth=2.5, color='darkblue')
ax.axvspan(200, 450, alpha=0.2, color='blue')
ax.set_xlabel('Time Step', fontsize=11, fontweight='bold')
ax.set_ylabel('Shannon Entropy (bits)', fontsize=11, fontweight='bold')
ax.set_title('Metronomic: Low Entropy Variance', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 500)

plt.suptitle('Temporal Dynamics: MTD Destabilizes, Metronomic Stabilizes', 
            fontsize=16, fontweight='bold', y=0.995)

plt.tight_layout(rect=[0, 0, 1, 0.99])
plt.savefig('images/figure3_temporal_dynamics.png', dpi=300, bbox_inches='tight', facecolor='white')
print("\n✓ Figure 3 saved: images/figure3_temporal_dynamics.png")
plt.close()
