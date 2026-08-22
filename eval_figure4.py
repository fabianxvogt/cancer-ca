"""
Evaluate Figure 4 - Check if cells are actually visible or all gray/dead
"""

import numpy as np
from tumor_ca import AdvancedTumorCA

print("="*80)
print("FIGURE 4 EVALUATION - Checking cell states at each snapshot")
print("="*80)

ca = AdvancedTumorCA(size=150, seed=42)
ca.initialize_tumor(radius=35, normal_cells=False)

snapshot_times = [0, 150, 200, 250, 280, 350, 450]
snapshots = {}

for step in range(500):
    if step >= 200 and step < 250:  # Match figure4 - shortened therapy
        ca.therapy = np.ones((150, 150)) * 0.12  # Match figure4
    else:
        ca.therapy = np.zeros((150, 150))
    
    if step in snapshot_times:
        # Count each cell type
        empty = np.sum(ca.grid == 0)
        normal = np.sum(ca.grid == 1)
        sensitive = np.sum(ca.grid == 2)
        resistant = np.sum(ca.grid == 3)
        dead = np.sum(ca.grid == 4)
        
        total_living = sensitive + resistant
        total_cells = empty + normal + sensitive + resistant + dead
        grid_size = 150 * 150
        
        res_pct = (resistant / total_living * 100) if total_living > 0 else 0
        
        print(f"\nt={step}:")
        print(f"  Empty:     {empty:>6} ({empty/grid_size*100:5.1f}%)")
        print(f"  Normal:    {normal:>6} ({normal/grid_size*100:5.1f}%)")
        print(f"  Sensitive: {sensitive:>6} ({sensitive/grid_size*100:5.1f}%) <- PINK")
        print(f"  Resistant: {resistant:>6} ({resistant/grid_size*100:5.1f}%) <- PURPLE")
        print(f"  Dead:      {dead:>6} ({dead/grid_size*100:5.1f}%) <- GRAY")
        print(f"  Total living: {total_living:>6}")
        print(f"  Resistance: {res_pct:5.1f}%")
        
        snapshots[step] = {
            'sensitive': sensitive,
            'resistant': resistant,
            'dead': dead,
            'total_living': total_living
        }
    
    ca.step()

# Analysis
print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)

issues = []

# Check if mostly dead
for t in snapshot_times:
    if t == 0:
        continue
    snap = snapshots[t]
    total = snap['sensitive'] + snap['resistant'] + snap['dead']
    if total > 0:
        dead_pct = snap['dead'] / total * 100
        if dead_pct > 80:
            issues.append(f"t={t}: {dead_pct:.1f}% dead (too much gray!)")

# Check if cells are visible
for t in snapshot_times:
    if t == 0:
        continue
    snap = snapshots[t]
    if snap['sensitive'] < 50 and snap['resistant'] < 50:
        issues.append(f"t={t}: Only {snap['sensitive']} pink + {snap['resistant']} purple cells (barely visible!)")

if issues:
    print("❌ PROBLEMS FOUND:")
    for issue in issues:
        print(f"  - {issue}")
    print("\nRECOMMENDATIONS:")
    print("  1. Reduce therapy intensity (currently 0.35)")
    print("  2. Increase division rate (currently 1.5)")
    print("  3. Further reduce death rate (currently 0.08)")
    print("  4. Use even larger initial tumor")
else:
    print("✅ Figure 4 looks good! Cells are visible and populations reasonable.")

# Check if colormap is working
print("\n" + "="*80)
print("COLORMAP CHECK:")
print("="*80)
print("Expected colors:")
print("  Pink (Sensitive):  Should see at t=0, t=150, t=200")
print("  Purple (Resistant): Should see at t=150, t=200, t=250, t=280+")
print("  Gray (Dead):       Should increase during therapy")
print("\nIf you see ALL GRAY, the colormap is broken or cells are all dead!")
