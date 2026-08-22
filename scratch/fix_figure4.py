"""
Fix Figure 4 - Test reduced therapy intensity to keep more cells alive
"""

import numpy as np
from tumor_ca import AdvancedTumorCA

print("="*80)
print("TESTING REDUCED THERAPY INTENSITY FOR FIGURE 4")
print("="*80)

# Test different intensities
intensities = [0.20, 0.25, 0.30]

for mtd_intensity in intensities:
    print(f"\n{'='*80}")
    print(f"Testing MTD intensity: {mtd_intensity}")
    print(f"{'='*80}")
    
    # Initialize CA - same as figure4
    ca = AdvancedTumorCA(size=150, seed=42)
    ca.initialize_tumor(radius=35, normal_cells=False)
    
    # Run simulation - same timeline as figure4
    for step in range(500):
        # MTD therapy phase (t=200 to 280) - with variable intensity
        if 200 <= step < 280:
            ca.therapy = np.ones((150, 150)) * mtd_intensity
        else:
            ca.therapy = np.zeros((150, 150))
        
        ca.step()
    
    # Check cell counts at key timepoints
    timepoints = [0, 150, 200, 250, 280, 350, 450]
    
    print(f"\nCell counts at key timepoints:")
    print(f"{'Time':<8} {'Sensitive':<12} {'Resistant':<12} {'Dead':<12} {'Total':<12} {'% Dead':<10}")
    print("-" * 80)
    
    total_grid_cells = 150 * 150
    
    for t_idx in timepoints:
        if t_idx < len(ca.history['sensitive']):
            sensitive = ca.history['sensitive'][t_idx]
            resistant = ca.history['resistant'][t_idx]
            
            # Count dead cells from grid
            dead_cells = np.sum(ca.grid == 3)  # State 3 = dead
            living = sensitive + resistant
            
            pct_dead = (dead_cells / total_grid_cells * 100)
            
            flag = ""
            if pct_dead > 80:
                flag = "❌ TOO MUCH GRAY!"
            elif pct_dead > 60:
                flag = "⚠️  Still quite gray"
            elif pct_dead < 50:
                flag = "✅ Good visibility"
            
            print(f"{t_idx:<8} {sensitive:<12} {resistant:<12} {dead_cells:<12} {living:<12} {pct_dead:>6.1f}%  {flag}")
    
    # Final assessment
    final_dead_pct = (np.sum(ca.grid == 3) / total_grid_cells * 100)
    final_living = ca.history['sensitive'][-1] + ca.history['resistant'][-1]
    final_res_pct = ca.history['resistant'][-1] / (final_living + 1) * 100
    
    print(f"\nFinal state:")
    print(f"  Living cells: {final_living}")
    print(f"  Dead cells: {np.sum(ca.grid == 3)} ({final_dead_pct:.1f}%)")
    print(f"  Resistance: {final_res_pct:.1f}%")
    
    if final_dead_pct < 50 and final_living > 300:
        print(f"\n✅ GOOD! This intensity ({mtd_intensity}) produces visible figures!")
    elif final_dead_pct < 70:
        print(f"\n⚠️  Better but still marginal (try even lower intensity)")
    else:
        print(f"\n❌ Still too much dead (need lower intensity)")

print(f"\n{'='*80}")
print("RECOMMENDATION:")
print("="*80)
print("Use the intensity that keeps dead cells < 50% with >300 living cells")
