"""
Debug: Why are so many cells dead BEFORE therapy even starts?
"""

import numpy as np
from tumor_ca import AdvancedTumorCA

ca = AdvancedTumorCA(size=150, seed=42)
ca.initialize_tumor(radius=35, normal_cells=False)

print("Tracking cell counts every 10 steps:")
print(f"{'Step':<8} {'Sensitive':<12} {'Resistant':<12} {'Dead':<12} {'% Dead':<10}")
print("-" * 70)

for step in range(200):  # Up to therapy start
    ca.therapy = np.zeros((150, 150))
    
    if step % 10 == 0:
        sensitive = np.sum(ca.grid == 2)
        resistant = np.sum(ca.grid == 3)
        dead = np.sum(ca.grid == 4)
        total = 150 * 150
        pct_dead = dead / total * 100
        
        print(f"{step:<8} {sensitive:<12} {resistant:<12} {dead:<12} {pct_dead:>6.1f}%")
    
    ca.step()

print("\n" + "="*70)
print("ANALYSIS:")
print("="*70)
print("Dead cells are accumulating even WITHOUT therapy!")
print("Likely causes:")
print("  1. Starvation (nutrient depletion)")
print("  2. Natural death rate (if any)")
print("  3. Overcrowding effects")
print("\nChecking nutrient levels at t=150:")
ca2 = AdvancedTumorCA(size=150, seed=42)
ca2.initialize_tumor(radius=35, normal_cells=False)
for _ in range(150):
    ca2.therapy = np.zeros((150, 150))
    ca2.step()

tumor_mask = (ca2.grid == 2) | (ca2.grid == 3)
avg_nutrients_in_tumor = np.mean(ca2.nutrients[tumor_mask])
min_nutrients_in_tumor = np.min(ca2.nutrients[tumor_mask])
print(f"\nAverage nutrients in tumor region: {avg_nutrients_in_tumor:.3f}")
print(f"Minimum nutrients in tumor region: {min_nutrients_in_tumor:.3f}")
print(f"Starvation threshold: {ca2.theta_starve:.3f}")

if min_nutrients_in_tumor < ca2.theta_starve:
    print("\n⚠️  STARVATION IS HAPPENING! Cells are dying from nutrient depletion.")
else:
    print("\n✓ Nutrients adequate, starvation not the issue.")
