"""
Evaluate Figure 6 - Parameter Space Analysis
Check if the correlation and values are correct
"""

import numpy as np
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics, ResponseVsStability

print("="*80)
print("FIGURE 6 EVALUATION - Parameter Space Analysis")
print("="*80)

# Test parameters from the grid
test_cases = [
    {'intensity': 0.2, 'radius': 12, 'name': 'Low intensity, small tumor'},
    {'intensity': 0.4, 'radius': 20, 'name': 'Medium intensity, medium tumor'},
    {'intensity': 0.6, 'radius': 20, 'name': 'High intensity, medium tumor'},
]

results = []

for case in test_cases:
    print(f"\n{'='*80}")
    print(f"Testing: {case['name']}")
    print(f"  Therapy intensity: {case['intensity']}")
    print(f"  Tumor radius: {case['radius']}")
    print('='*80)
    
    ca = AdvancedTumorCA(size=100, seed=42)
    ca.initialize_tumor(radius=case['radius'], normal_cells=False)
    
    for step in range(300):
        if step >= 100 and step < 180:
            ca.therapy = np.ones((100, 100)) * case['intensity']
        else:
            ca.therapy = np.zeros((100, 100))
        ca.step()
    
    # Calculate metrics using the correct classes
    response_metrics = ResponseVsStability.measure_response(ca.history, therapy_start=100, therapy_end=150)
    response = response_metrics['max_reduction']
    reversibility = StabilityMetrics.reversibility_loss(ca.history, therapy_start=100, therapy_end=150)
    
    # Compute all stability metrics
    all_metrics = StabilityMetrics.compute_all_metrics(ca.history, therapy_start=100, therapy_end=150)
    stability = all_metrics.get('stability_score', 0)
    
    print(f"\nResults:")
    print(f"  Response:      {response:6.1f}%")
    print(f"  Stability:     {stability:6.3f}")
    print(f"  Reversibility: {reversibility:6.3f}")
    
    results.append({
        'intensity': case['intensity'],
        'radius': case['radius'],
        'response': response,
        'stability': stability,
        'reversibility': reversibility
    })

# Check correlation
print("\n" + "="*80)
print("CORRELATION CHECK:")
print("="*80)

responses = [r['response'] for r in results]
stabilities = [r['stability'] for r in results]

if len(responses) > 1 and np.std(responses) > 0 and np.std(stabilities) > 0:
    correlation = np.corrcoef(responses, stabilities)[0, 1]
    print(f"Response vs Stability correlation: ρ = {correlation:.3f}")
    
    if correlation < -0.5:
        print("✅ GOOD! Negative correlation as expected (high response → low stability)")
    elif correlation > 0.5:
        print("❌ PROBLEM! Positive correlation (should be negative!)")
    else:
        print("⚠️  WARNING! Weak correlation (expected strong negative)")
else:
    print("⚠️  Cannot calculate correlation (not enough variation in data)")

# Print summary table
print("\n" + "="*80)
print("SUMMARY TABLE:")
print("="*80)
print(f"{'Intensity':<12} {'Radius':<10} {'Response':<12} {'Stability':<12} {'Reversibility':<15}")
print("-" * 80)
for r in results:
    print(f"{r['intensity']:<12.1f} {r['radius']:<10} {r['response']:<12.1f} {r['stability']:<12.3f} {r['reversibility']:<15.3f}")

# Check specific values
print("\n" + "="*80)
print("VALUE CHECK:")
print("="*80)

issues = []

for r in results:
    if r['response'] < 0 or r['response'] > 100:
        issues.append(f"Response {r['response']:.1f}% out of valid range (0-100%)")
    if r['stability'] < 0 or r['stability'] > 1:
        issues.append(f"Stability {r['stability']:.3f} out of valid range (0-1)")
    if r['reversibility'] < 0 or r['reversibility'] > 1:
        issues.append(f"Reversibility {r['reversibility']:.3f} out of valid range (0-1)")

if issues:
    print("❌ PROBLEMS FOUND:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ All values in valid ranges!")

print("\n" + "="*80)
print("EXPECTED BEHAVIOR:")
print("="*80)
print("1. Higher therapy intensity → Higher response (more cells killed)")
print("2. Higher response → Lower stability (more evolutionary disruption)")
print("3. Therefore: ρ(response, stability) should be NEGATIVE")
print("4. Reversibility should be HIGH when therapy is gentle, LOW when aggressive")
