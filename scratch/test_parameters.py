"""
Systematic Parameter Testing
Find the right parameters to achieve:
- MTD: ~85% resistance, population survives
- Metronomic: ~25% resistance, population survives
"""

import numpy as np
from tumor_ca import AdvancedTumorCA

def test_therapy(mutation_rate, mtd_intensity, metro_intensity, resistant_death_rate):
    """Test a specific parameter combination"""
    
    print(f"\n{'='*80}")
    print(f"Testing: mutation={mutation_rate}, MTD={mtd_intensity}, Metro={metro_intensity}, res_death={resistant_death_rate}")
    print(f"{'='*80}")
    
    # Temporarily modify the CA parameters
    original_mutation = 0.002
    
    # MTD test
    ca_mtd = AdvancedTumorCA(size=120, seed=42)
    ca_mtd.local_mutation_rate[:] = mutation_rate
    ca_mtd.initialize_tumor(radius=20, normal_cells=False)
    
    for step in range(500):
        if step >= 200 and step < 280:
            ca_mtd.therapy = np.ones((120, 120)) * mtd_intensity
        else:
            ca_mtd.therapy = np.zeros((120, 120))
        ca_mtd.step()
    
    # Get final MTD stats
    mtd_total = ca_mtd.history['sensitive'][-1] + ca_mtd.history['resistant'][-1]
    mtd_resistance_pct = 0
    if mtd_total > 0:
        mtd_resistance_pct = (ca_mtd.history['resistant'][-1] / mtd_total) * 100
    
    mtd_pop_at_therapy_end = ca_mtd.history['sensitive'][280] + ca_mtd.history['resistant'][280]
    
    # Metronomic test
    ca_metro = AdvancedTumorCA(size=120, seed=42)
    ca_metro.local_mutation_rate[:] = mutation_rate
    ca_metro.initialize_tumor(radius=20, normal_cells=False)
    
    for step in range(500):
        if step >= 200 and step < 450:
            ca_metro.therapy = np.ones((120, 120)) * metro_intensity
        else:
            ca_metro.therapy = np.zeros((120, 120))
        ca_metro.step()
    
    # Get final Metronomic stats
    metro_total = ca_metro.history['sensitive'][-1] + ca_metro.history['resistant'][-1]
    metro_resistance_pct = 0
    if metro_total > 0:
        metro_resistance_pct = (ca_metro.history['resistant'][-1] / metro_total) * 100
    
    metro_pop_during_therapy = ca_metro.history['sensitive'][350] + ca_metro.history['resistant'][350]
    
    print(f"\nMTD Results:")
    print(f"  Final population: {mtd_total}")
    print(f"  Population at therapy end (t=280): {mtd_pop_at_therapy_end}")
    print(f"  Final resistance: {mtd_resistance_pct:.1f}%")
    print(f"  Target: 85% | Diff: {abs(85 - mtd_resistance_pct):.1f}%")
    
    print(f"\nMetronomic Results:")
    print(f"  Final population: {metro_total}")
    print(f"  Population during therapy (t=350): {metro_pop_during_therapy}")
    print(f"  Final resistance: {metro_resistance_pct:.1f}%")
    print(f"  Target: 25% | Diff: {abs(25 - metro_resistance_pct):.1f}%")
    
    # Score this combination
    score = abs(85 - mtd_resistance_pct) + abs(25 - metro_resistance_pct)
    
    # Penalty for extinction
    if mtd_total < 100:
        score += 100
    if metro_total < 500:
        score += 100
    
    print(f"\nScore (lower is better): {score:.1f}")
    print(f"  MTD survived: {mtd_total >= 100}")
    print(f"  Metro survived: {metro_total >= 500}")
    
    return {
        'mutation_rate': mutation_rate,
        'mtd_intensity': mtd_intensity,
        'metro_intensity': metro_intensity,
        'resistant_death_rate': resistant_death_rate,
        'mtd_resistance': mtd_resistance_pct,
        'metro_resistance': metro_resistance_pct,
        'mtd_population': mtd_total,
        'metro_population': metro_total,
        'score': score
    }


print("PARAMETER SWEEP STARTING...")
print("Target: MTD=85% resistance, Metronomic=25% resistance")
print("Both populations must survive (>100 cells)\n")

results = []

# Test different mutation rates
for mutation in [0.001, 0.002, 0.003, 0.005]:
    # Test different MTD intensities
    for mtd_int in [0.35, 0.40, 0.45, 0.50]:
        # Test different Metronomic intensities
        for metro_int in [0.07, 0.08, 0.09, 0.10]:
            result = test_therapy(mutation, mtd_int, metro_int, 0.01)
            results.append(result)

# Find best result
results.sort(key=lambda x: x['score'])

print("\n\n" + "="*80)
print("TOP 5 BEST PARAMETER COMBINATIONS:")
print("="*80)

for i, r in enumerate(results[:5]):
    print(f"\n#{i+1} - Score: {r['score']:.1f}")
    print(f"  Mutation rate: {r['mutation_rate']}")
    print(f"  MTD intensity: {r['mtd_intensity']}")
    print(f"  Metronomic intensity: {r['metro_intensity']}")
    print(f"  MTD: {r['mtd_resistance']:.1f}% resistance, {r['mtd_population']:.0f} cells")
    print(f"  Metronomic: {r['metro_resistance']:.1f}% resistance, {r['metro_population']:.0f} cells")
