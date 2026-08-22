"""
Evaluate Figure 3 - Test until we get the right dynamics
"""

import numpy as np
from tumor_ca import AdvancedTumorCA

print("="*80)
print("FIGURE 3 EVALUATION - Testing MTD vs Metronomic")
print("="*80)

# MTD simulation
print("\nRunning MTD simulation...")
ca_mtd = AdvancedTumorCA(size=120, seed=42)
ca_mtd.initialize_tumor(radius=30, normal_cells=False)

for step in range(500):
    if step >= 200 and step < 400:
        ca_mtd.therapy = np.ones((120, 120)) * 1.0
    else:
        ca_mtd.therapy = np.zeros((120, 120))
    ca_mtd.step()

# Metronomic simulation
print("Running Metronomic simulation...")
ca_metro = AdvancedTumorCA(size=120, seed=42)
ca_metro.initialize_tumor(radius=30, normal_cells=False)

for step in range(500):
    if step >= 200 and step < 450:
        ca_metro.therapy = np.ones((120, 120)) * 0.02
    else:
        ca_metro.therapy = np.zeros((120, 120))
    ca_metro.step()

# Analyze results
print("\n" + "="*80)
print("MTD RESULTS:")
print("="*80)

mtd_total = np.array(ca_mtd.history['sensitive']) + np.array(ca_mtd.history['resistant'])
mtd_res_frac = np.array(ca_mtd.history['resistant']) / (mtd_total + 1)

print(f"Pre-therapy (t=199):")
print(f"  Total: {mtd_total[199]}")
print(f"  Resistance: {mtd_res_frac[199]*100:.1f}%")

print(f"\nEnd of therapy (t=399):")
print(f"  Total: {mtd_total[399]}")
print(f"  Resistance: {mtd_res_frac[399]*100:.1f}%")

print(f"\nPost-therapy (t=450):")
print(f"  Total: {mtd_total[450]}")
print(f"  Resistance: {mtd_res_frac[450]*100:.1f}%")

print(f"\nFinal (t=499):")
print(f"  Total: {mtd_total[499]}")
print(f"  Resistance: {mtd_res_frac[499]*100:.1f}%")

print("\n" + "="*80)
print("METRONOMIC RESULTS:")
print("="*80)

metro_total = np.array(ca_metro.history['sensitive']) + np.array(ca_metro.history['resistant'])
metro_res_frac = np.array(ca_metro.history['resistant']) / (metro_total + 1)

print(f"Pre-therapy (t=199):")
print(f"  Total: {metro_total[199]}")
print(f"  Resistance: {metro_res_frac[199]*100:.1f}%")

print(f"\nMid-therapy (t=325):")
print(f"  Total: {metro_total[325]}")
print(f"  Resistance: {metro_res_frac[325]*100:.1f}%")

print(f"\nEnd of therapy (t=449):")
print(f"  Total: {metro_total[449]}")
print(f"  Resistance: {metro_res_frac[449]*100:.1f}%")

print(f"\nFinal (t=499):")
print(f"  Total: {metro_total[499]}")
print(f"  Resistance: {metro_res_frac[499]*100:.1f}%")

# Assessment
print("\n" + "="*80)
print("ASSESSMENT:")
print("="*80)

mtd_final_res = mtd_res_frac[450] * 100
metro_avg_res = np.mean(metro_res_frac[300:450]) * 100

print(f"MTD final resistance: {mtd_final_res:.1f}%")
print(f"Metronomic avg resistance: {metro_avg_res:.1f}%")

if mtd_final_res < 75:
    print(f"❌ MTD resistance too low ({mtd_final_res:.1f}% < 75%)")
    print("   Need: Higher intensity OR longer duration OR lower resistant cell death rate")
elif mtd_final_res > 90:
    print(f"❌ MTD resistance too high ({mtd_final_res:.1f}% > 90%)")
    print("   Need: Lower intensity OR shorter duration")
else:
    print(f"✅ MTD resistance in target range (75-90%)")

if metro_avg_res < 15:
    print(f"❌ Metronomic resistance too low ({metro_avg_res:.1f}% < 15%)")
    print("   Need: Higher intensity OR different selection dynamics")
elif metro_avg_res > 40:
    print(f"❌ Metronomic resistance too high ({metro_avg_res:.1f}% > 40%)")
    print("   Need: Lower intensity")
else:
    print(f"✅ Metronomic resistance in target range (15-40%)")

if mtd_final_res > metro_avg_res + 20:
    print(f"✅ Clear difference: MTD {mtd_final_res:.1f}% vs Metronomic {metro_avg_res:.1f}%")
else:
    print(f"⚠️  Difference too small: MTD {mtd_final_res:.1f}% vs Metronomic {metro_avg_res:.1f}%")
