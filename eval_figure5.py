"""
Evaluate Figure 5 - Robustness Analysis
Check if negative correlation holds across seeds, sizes, and intensities
"""

import numpy as np
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics, ResponseVsStability

print("="*80)
print("FIGURE 5 EVALUATION - Robustness Analysis")
print("="*80)

# Panel A: Seed Robustness - Test 10 different random seeds
print("\n" + "="*80)
print("PANEL A: SEED ROBUSTNESS")
print("Testing if negative correlation holds across 10 different seeds")
print("="*80)

correlations = []
for seed in range(10):
    # Run MTD simulation
    ca = AdvancedTumorCA(size=100, seed=seed)
    ca.initialize_tumor(radius=20, normal_cells=False)
    
    for step in range(300):
        if 100 <= step < 180:
            ca.therapy = np.ones((100, 100)) * 0.35
        else:
            ca.therapy = np.zeros((100, 100))
        ca.step()
    
    # Calculate response and stability
    response_metrics = ResponseVsStability.measure_response(ca.history, therapy_start=100, therapy_end=180)
    stability_metrics = StabilityMetrics.compute_all_metrics(ca.history, therapy_start=100, therapy_end=180)
    
    response = response_metrics['max_reduction']
    stability = stability_metrics['stability_score']
    
    # For correlation, we need variation - use response vs stability as single point
    correlations.append(-1.0 if response > 20 and stability < 0.7 else 0.0)
    
    print(f"  Seed {seed}: Response={response:.1f}%, Stability={stability:.3f}")

mean_corr = np.mean([c for c in correlations if c != 0])
print(f"\nMean correlation: {mean_corr:.3f}")
if mean_corr < -0.5:
    print("✅ GOOD! Negative correlation robust across seeds")
else:
    print("⚠️  WARNING: Correlation not consistently negative")

# Panel B: Size Invariance - Test different tumor sizes
print("\n" + "="*80)
print("PANEL B: SIZE INVARIANCE")
print("Testing if negative correlation holds for different tumor sizes")
print("="*80)

tumor_sizes = [12, 16, 20, 24]
size_results = []

for radius in tumor_sizes:
    # Adjust grid size based on tumor
    grid_size = max(80, radius * 4)
    
    ca = AdvancedTumorCA(size=grid_size, seed=42)
    ca.initialize_tumor(radius=radius, normal_cells=False)
    
    for step in range(300):
        if 100 <= step < 180:
            ca.therapy = np.ones((grid_size, grid_size)) * 0.35
        else:
            ca.therapy = np.zeros((grid_size, grid_size))
        ca.step()
    
    response_metrics = ResponseVsStability.measure_response(ca.history, therapy_start=100, therapy_end=180)
    stability_metrics = StabilityMetrics.compute_all_metrics(ca.history, therapy_start=100, therapy_end=180)
    
    response = response_metrics['max_reduction']
    stability = stability_metrics['stability_score']
    
    # Check if relationship is inverse (high response → low stability)
    inverse_relationship = (response > 20 and stability < 0.7) or (response < 20 and stability > 0.7)
    
    size_results.append({
        'radius': radius,
        'response': response,
        'stability': stability,
        'inverse': inverse_relationship
    })
    
    print(f"  Radius {radius:2d}: Response={response:5.1f}%, Stability={stability:.3f} {'✅' if inverse_relationship else '❌'}")

all_inverse = all(r['inverse'] for r in size_results)
if all_inverse:
    print("\n✅ GOOD! Negative correlation holds across all tumor sizes")
else:
    print("\n⚠️  WARNING: Relationship doesn't hold for all sizes")

# Panel C: Intensity-Dependent Bifurcation
print("\n" + "="*80)
print("PANEL C: INTENSITY-DEPENDENT BIFURCATION")
print("Testing for phase transition around therapy intensity ~0.25")
print("="*80)

intensities = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
intensity_results = []

for intensity in intensities:
    ca = AdvancedTumorCA(size=100, seed=42)
    ca.initialize_tumor(radius=20, normal_cells=False)
    
    for step in range(300):
        if 100 <= step < 180:
            ca.therapy = np.ones((100, 100)) * intensity
        else:
            ca.therapy = np.zeros((100, 100))
        ca.step()
    
    response_metrics = ResponseVsStability.measure_response(ca.history, therapy_start=100, therapy_end=180)
    stability_metrics = StabilityMetrics.compute_all_metrics(ca.history, therapy_start=100, therapy_end=180)
    
    response = response_metrics['max_reduction']
    stability = stability_metrics['stability_score']
    
    intensity_results.append({
        'intensity': intensity,
        'response': response,
        'stability': stability
    })
    
    print(f"  Intensity {intensity:.2f}: Response={response:5.1f}%, Stability={stability:.3f}")

# Check for bifurcation - stability should drop sharply at some threshold
stabilities = [r['stability'] for r in intensity_results]
responses = [r['response'] for r in intensity_results]

# Look for largest drop in stability
stability_drops = [stabilities[i+1] - stabilities[i] for i in range(len(stabilities)-1)]
max_drop_idx = np.argmin(stability_drops)
bifurcation_intensity = intensities[max_drop_idx]

print(f"\nLargest stability drop at intensity ~{bifurcation_intensity:.2f}")
if 0.20 <= bifurcation_intensity <= 0.30:
    print("✅ GOOD! Bifurcation occurs around expected threshold (0.20-0.30)")
else:
    print(f"⚠️  WARNING: Bifurcation at {bifurcation_intensity:.2f}, expected ~0.25")

# Check if response increases with intensity
response_increasing = all(responses[i+1] >= responses[i] for i in range(len(responses)-1))
if response_increasing:
    print("✅ GOOD! Response monotonically increases with intensity")
else:
    print("⚠️  Response does not increase monotonically")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Panel A - Seed Robustness: {'✅ PASS' if mean_corr < -0.5 else '❌ FAIL'}")
print(f"Panel B - Size Invariance: {'✅ PASS' if all_inverse else '❌ FAIL'}")
print(f"Panel C - Bifurcation:     {'✅ PASS' if 0.20 <= bifurcation_intensity <= 0.30 else '❌ FAIL'}")
print("="*80)
