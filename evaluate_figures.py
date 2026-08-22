"""
Evaluate Figure Quality - Actually CHECK the numbers!
"""

import numpy as np
from tumor_ca import AdvancedTumorCA

def run_and_evaluate(seed=42):
    """Run simulations and return actual measurements"""
    
    print(f"\n{'='*80}")
    print(f"EVALUATION RUN (seed={seed})")
    print(f"{'='*80}")
    
    # MTD simulation
    ca_mtd = AdvancedTumorCA(size=120, seed=seed)
    ca_mtd.initialize_tumor(radius=30, normal_cells=False)  # Increased from 20
    
    for step in range(500):
        if step >= 200 and step < 280:
            ca_mtd.therapy = np.ones((120, 120)) * 0.35  # Match figure script
        else:
            ca_mtd.therapy = np.zeros((120, 120))
        ca_mtd.step()
    
    # Metronomic simulation
    ca_metro = AdvancedTumorCA(size=120, seed=seed)
    ca_metro.initialize_tumor(radius=30, normal_cells=False)  # Increased from 20
    
    for step in range(500):
        if step >= 200 and step < 450:
            ca_metro.therapy = np.ones((120, 120)) * 0.02  # Match figure script
        else:
            ca_metro.therapy = np.zeros((120, 120))
        ca_metro.step()
    
    # MEASURE ACTUAL VALUES
    results = {}
    
    # MTD measurements
    mtd_sens_280 = ca_mtd.history['sensitive'][280]
    mtd_res_280 = ca_mtd.history['resistant'][280]
    mtd_total_280 = mtd_sens_280 + mtd_res_280
    mtd_resistance_280 = (mtd_res_280 / mtd_total_280 * 100) if mtd_total_280 > 0 else 0
    
    mtd_sens_final = ca_mtd.history['sensitive'][-1]
    mtd_res_final = ca_mtd.history['resistant'][-1]
    mtd_total_final = mtd_sens_final + mtd_res_final
    mtd_resistance_final = (mtd_res_final / mtd_total_final * 100) if mtd_total_final > 0 else 0
    
    # Resistance at therapy start (t=200)
    mtd_sens_200 = ca_mtd.history['sensitive'][200]
    mtd_res_200 = ca_mtd.history['resistant'][200]
    mtd_total_200 = mtd_sens_200 + mtd_res_200
    mtd_resistance_200 = (mtd_res_200 / mtd_total_200 * 100) if mtd_total_200 > 0 else 0
    
    # Metronomic measurements
    metro_sens_350 = ca_metro.history['sensitive'][350]
    metro_res_350 = ca_metro.history['resistant'][350]
    metro_total_350 = metro_sens_350 + metro_res_350
    metro_resistance_350 = (metro_res_350 / metro_total_350 * 100) if metro_total_350 > 0 else 0
    
    metro_sens_final = ca_metro.history['sensitive'][-1]
    metro_res_final = ca_metro.history['resistant'][-1]
    metro_total_final = metro_sens_final + metro_res_final
    metro_resistance_final = (metro_res_final / metro_total_final * 100) if metro_total_final > 0 else 0
    
    print("\nMTD RESULTS:")
    print(f"  At therapy start (t=200):  {mtd_total_200:>5.0f} cells, {mtd_resistance_200:5.1f}% resistant")
    print(f"  At therapy end (t=280):    {mtd_total_280:>5.0f} cells, {mtd_resistance_280:5.1f}% resistant")
    print(f"  Final (t=500):             {mtd_total_final:>5.0f} cells, {mtd_resistance_final:5.1f}% resistant")
    print(f"  TARGET: ~85% resistant with >500 cells remaining")
    print(f"  ✓ Population survived: {mtd_total_280 >= 500}")
    print(f"  ✓ Resistance 80-90%: {80 <= mtd_resistance_280 <= 90}")
    
    print("\nMETRONOMIC RESULTS:")
    print(f"  During therapy (t=350):    {metro_total_350:>5.0f} cells, {metro_resistance_350:5.1f}% resistant")
    print(f"  Final (t=500):             {metro_total_final:>5.0f} cells, {metro_resistance_final:5.1f}% resistant")
    print(f"  TARGET: ~25% resistant with >1000 cells remaining")
    print(f"  ✓ Population survived: {metro_total_350 >= 1000}")
    print(f"  ✓ Resistance 20-30%: {20 <= metro_resistance_350 <= 30}")
    
    # Check Figure 4 snapshots
    print("\nFIGURE 4 SNAPSHOTS:")
    ca_fig4 = AdvancedTumorCA(size=120, seed=seed)
    ca_fig4.initialize_tumor(radius=30, normal_cells=False)  # Increased from 20
    
    snapshots = {}
    for step in range(500):
        if step >= 200 and step < 280:
            ca_fig4.therapy = np.ones((120, 120)) * 0.35  # Match figure script
        else:
            ca_fig4.therapy = np.zeros((120, 120))
        
        if step in [0, 150, 200, 250, 280, 350, 450]:
            sens = np.sum(ca_fig4.grid == 2)
            res = np.sum(ca_fig4.grid == 3)
            dead = np.sum(ca_fig4.grid == 4)
            total = sens + res
            res_pct = (res / total * 100) if total > 0 else 0
            print(f"  t={step:>3}: Total={total:>5}, Sensitive={sens:>4}, Resistant={res:>4}, Dead={dead:>5}, Res%={res_pct:5.1f}%")
            
        ca_fig4.step()
    
    # Overall score
    mtd_score = abs(85 - mtd_resistance_280)
    metro_score = abs(25 - metro_resistance_350)
    pop_penalty = 0
    if mtd_total_280 < 500:
        pop_penalty += 100
    if metro_total_350 < 1000:
        pop_penalty += 100
    
    total_score = mtd_score + metro_score + pop_penalty
    
    print(f"\nOVERALL SCORE: {total_score:.1f} (lower is better)")
    print(f"  MTD diff from 85%: {mtd_score:.1f}")
    print(f"  Metro diff from 25%: {metro_score:.1f}")
    print(f"  Population penalty: {pop_penalty}")
    
    return {
        'mtd_resistance_280': mtd_resistance_280,
        'mtd_population_280': mtd_total_280,
        'metro_resistance_350': metro_resistance_350,
        'metro_population_350': metro_total_350,
        'score': total_score
    }


# Run multiple times to check consistency
print("="*80)
print("TESTING MULTIPLE SEEDS TO CHECK CONSISTENCY")
print("="*80)

results = []
for seed in [42, 123, 456]:
    result = run_and_evaluate(seed)
    results.append(result)

print("\n" + "="*80)
print("SUMMARY ACROSS SEEDS:")
print("="*80)
mtd_res_avg = np.mean([r['mtd_resistance_280'] for r in results])
mtd_pop_avg = np.mean([r['mtd_population_280'] for r in results])
metro_res_avg = np.mean([r['metro_resistance_350'] for r in results])
metro_pop_avg = np.mean([r['metro_population_350'] for r in results])

print(f"\nMTD averages:")
print(f"  Resistance at therapy end: {mtd_res_avg:.1f}% (target: 85%)")
print(f"  Population at therapy end: {mtd_pop_avg:.0f} (target: >500)")

print(f"\nMetronomic averages:")
print(f"  Resistance during therapy: {metro_res_avg:.1f}% (target: 25%)")
print(f"  Population during therapy: {metro_pop_avg:.0f} (target: >1000)")

print(f"\nAverage score: {np.mean([r['score'] for r in results]):.1f}")

# Pass/Fail
mtd_pass = 80 <= mtd_res_avg <= 90 and mtd_pop_avg >= 500
metro_pass = 20 <= metro_res_avg <= 30 and metro_pop_avg >= 1000

print("\n" + "="*80)
if mtd_pass and metro_pass:
    print("✅ FIGURES ARE GOOD! Both MTD and Metronomic meet targets!")
else:
    print("❌ FIGURES NEED MORE WORK!")
    if not mtd_pass:
        print(f"   MTD: resistance={mtd_res_avg:.1f}% (need 80-90%), pop={mtd_pop_avg:.0f} (need >500)")
    if not metro_pass:
        print(f"   Metronomic: resistance={metro_res_avg:.1f}% (need 20-30%), pop={metro_pop_avg:.0f} (need >1000)")
print("="*80)
