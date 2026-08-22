"""
New approach: Measure resistance DURING therapy, not at the end
Also test with larger initial tumors to maintain bigger populations
"""

import numpy as np
from tumor_ca import AdvancedTumorCA

def test_therapy_v2(mutation_rate, mtd_intensity, metro_intensity, initial_radius):
    """Test measuring resistance during therapy phase"""
    
    print(f"\n{'='*80}")
    print(f"Testing: mutation={mutation_rate}, MTD={mtd_intensity}, Metro={metro_intensity}, radius={initial_radius}")
    print(f"{'='*80}")
    
    # MTD test
    ca_mtd = AdvancedTumorCA(size=150, seed=42)
    ca_mtd.local_mutation_rate[:] = mutation_rate
    ca_mtd.initialize_tumor(radius=initial_radius, normal_cells=False)
    
    mtd_resistance_during = []
    mtd_populations = []
    
    for step in range(500):
        if step >= 200 and step < 280:
            ca_mtd.therapy = np.ones((150, 150)) * mtd_intensity
        else:
            ca_mtd.therapy = np.zeros((150, 150))
        ca_mtd.step()
        
        # Track during therapy
        if step >= 200 and step <= 280:
            total = ca_mtd.history['sensitive'][step] + ca_mtd.history['resistant'][step]
            if total > 0:
                res_pct = (ca_mtd.history['resistant'][step] / total) * 100
                mtd_resistance_during.append(res_pct)
                mtd_populations.append(total)
    
    # Metronomic test
    ca_metro = AdvancedTumorCA(size=150, seed=42)
    ca_metro.local_mutation_rate[:] = mutation_rate
    ca_metro.initialize_tumor(radius=initial_radius, normal_cells=False)
    
    metro_resistance_during = []
    metro_populations = []
    
    for step in range(500):
        if step >= 200 and step < 450:
            ca_metro.therapy = np.ones((150, 150)) * metro_intensity
        else:
            ca_metro.therapy = np.zeros((150, 150))
        ca_metro.step()
        
        # Track during mid-late therapy
        if step >= 300 and step <= 400:
            total = ca_metro.history['sensitive'][step] + ca_metro.history['resistant'][step]
            if total > 0:
                res_pct = (ca_metro.history['resistant'][step] / total) * 100
                metro_resistance_during.append(res_pct)
                metro_populations.append(total)
    
    # Average resistance DURING therapy
    mtd_avg_resistance = np.mean(mtd_resistance_during) if mtd_resistance_during else 0
    mtd_avg_pop = np.mean(mtd_populations) if mtd_populations else 0
    
    metro_avg_resistance = np.mean(metro_resistance_during) if metro_resistance_during else 0
    metro_avg_pop = np.mean(metro_populations) if metro_populations else 0
    
    # Get final states
    mtd_final_pop = ca_mtd.history['sensitive'][-1] + ca_mtd.history['resistant'][-1]
    metro_final_pop = ca_metro.history['sensitive'][-1] + ca_metro.history['resistant'][-1]
    
    print(f"\nMTD Results:")
    print(f"  Avg population during therapy: {mtd_avg_pop:.0f}")
    print(f"  Final population: {mtd_final_pop:.0f}")
    print(f"  Avg resistance DURING therapy: {mtd_avg_resistance:.1f}%")
    print(f"  Target: 85% | Diff: {abs(85 - mtd_avg_resistance):.1f}%")
    
    print(f"\nMetronomic Results:")
    print(f"  Avg population during therapy: {metro_avg_pop:.0f}")
    print(f"  Final population: {metro_final_pop:.0f}")
    print(f"  Avg resistance DURING therapy: {metro_avg_resistance:.1f}%")
    print(f"  Target: 25% | Diff: {abs(25 - metro_avg_resistance):.1f}%")
    
    # Score
    score = abs(85 - mtd_avg_resistance) + abs(25 - metro_avg_resistance)
    
    # Penalty for small populations
    if mtd_avg_pop < 500:
        score += 50
    if metro_avg_pop < 1000:
        score += 50
    
    print(f"\nScore (lower is better): {score:.1f}")
    
    return {
        'mutation_rate': mutation_rate,
        'mtd_intensity': mtd_intensity,
        'metro_intensity': metro_intensity,
        'radius': initial_radius,
        'mtd_resistance': mtd_avg_resistance,
        'metro_resistance': metro_avg_resistance,
        'mtd_population': mtd_avg_pop,
        'metro_population': metro_avg_pop,
        'score': score
    }


print("PARAMETER SWEEP V2: Measuring resistance DURING therapy")
print("Target: MTD=85% during therapy, Metronomic=25% during therapy")
print("Larger tumors for bigger populations\n")

results = []

# Test with larger initial tumors and different parameters
for radius in [25, 30]:
    for mutation in [0.0005, 0.001, 0.0015]:
        for mtd_int in [0.30, 0.35, 0.40]:
            for metro_int in [0.05, 0.06, 0.07]:
                result = test_therapy_v2(mutation, mtd_int, metro_int, radius)
                results.append(result)

# Find best result
results.sort(key=lambda x: x['score'])

print("\n\n" + "="*80)
print("TOP 5 BEST PARAMETER COMBINATIONS:")
print("="*80)

for i, r in enumerate(results[:5]):
    print(f"\n#{i+1} - Score: {r['score']:.1f}")
    print(f"  Initial radius: {r['radius']}")
    print(f"  Mutation rate: {r['mutation_rate']}")
    print(f"  MTD intensity: {r['mtd_intensity']}")
    print(f"  Metronomic intensity: {r['metro_intensity']}")
    print(f"  MTD: {r['mtd_resistance']:.1f}% resistance, {r['mtd_population']:.0f} cells avg")
    print(f"  Metronomic: {r['metro_resistance']:.1f}% resistance, {r['metro_population']:.0f} cells avg")
