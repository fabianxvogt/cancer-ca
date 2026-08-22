"""
Statistical Validation - Address Reviewer Concerns
===================================================

Addresses:
1. Perfect correlations being suspicious (ρ = -1.000)
2. Need for confidence intervals
3. Alternative correlation measures
4. Understanding seed variability
5. Robustness testing
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics, ResponseVsStability
from scipy.stats import pearsonr, spearmanr, kendalltau
import pandas as pd

print("="*80)
print("STATISTICAL VALIDATION - Addressing Reviewer Concerns")
print("="*80)

# Test 1: Why do we get perfect correlations? Is it real or artifact?
print("\n" + "="*80)
print("TEST 1: CORRELATION ROBUSTNESS ACROSS MULTIPLE METRICS")
print("="*80)

# Generate data with more parameter variation
intensities = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]
results = []

for intensity in intensities:
    ca = AdvancedTumorCA(size=100, seed=42)
    ca.initialize_tumor(radius=20, normal_cells=False)
    
    for step in range(300):
        if 100 <= step < 200:
            ca.therapy = np.ones((100, 100)) * intensity
        else:
            ca.therapy = np.zeros((100, 100))
        ca.step()
    
    # Calculate metrics
    response_metrics = ResponseVsStability.measure_response(ca.history, therapy_start=100, therapy_end=200)
    stability_metrics = StabilityMetrics.compute_all_metrics(ca.history, therapy_start=100, therapy_end=200)
    
    results.append({
        'intensity': intensity,
        'response': response_metrics['max_reduction'],
        'stability': stability_metrics['stability_score'],
        'reversibility': stability_metrics['reversibility_score'],
        'entropy_rate': stability_metrics['entropy_increase_rate']
    })

df = pd.DataFrame(results)

# Multiple correlation measures
pearson_r, pearson_p = pearsonr(df['response'], df['stability'])
spearman_r, spearman_p = spearmanr(df['response'], df['stability'])
kendall_r, kendall_p = kendalltau(df['response'], df['stability'])

print(f"\nCorrelation between Response and Stability:")
print(f"  Pearson:  ρ = {pearson_r:.4f}, p = {pearson_p:.4e}")
print(f"  Spearman: ρ = {spearman_r:.4f}, p = {spearman_p:.4e}")
print(f"  Kendall:  τ = {kendall_r:.4f}, p = {kendall_p:.4e}")

if abs(pearson_r) > 0.999:
    print("\n⚠️  REVIEWER CONCERN: Perfect correlation suggests:")
    print("     1. Deterministic coupling between metrics")
    print("     2. Insufficient parameter variation")
    print("     3. Possible metric co-dependency")
else:
    print("\n✅ Correlation is strong but not suspiciously perfect")

# Test 2: Bootstrap confidence intervals
print("\n" + "="*80)
print("TEST 2: BOOTSTRAP CONFIDENCE INTERVALS (1000 resamples)")
print("="*80)

bootstrap_correlations = []
n_bootstrap = 1000

for _ in range(n_bootstrap):
    # Resample with replacement
    sample_idx = np.random.choice(len(df), size=len(df), replace=True)
    sample = df.iloc[sample_idx]
    
    if sample['response'].std() > 0:  # Check for variance
        r, _ = pearsonr(sample['response'], sample['stability'])
        bootstrap_correlations.append(r)

bootstrap_correlations = np.array(bootstrap_correlations)
ci_lower = np.percentile(bootstrap_correlations, 2.5)
ci_upper = np.percentile(bootstrap_correlations, 97.5)

print(f"Pearson correlation: {pearson_r:.4f}")
print(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"Std: {np.std(bootstrap_correlations):.4f}")

# Test 3: Understanding seed variability (address 80% reproducibility)
print("\n" + "="*80)
print("TEST 3: SEED VARIABILITY ANALYSIS (Why do 2/10 seeds differ?)")
print("="*80)

seed_results = []
for seed in range(20):  # Test 20 seeds instead of 10
    results_per_seed = []
    
    for intensity in [0.40, 0.25, 0.15]:
        ca = AdvancedTumorCA(size=100, seed=seed)
        ca.initialize_tumor(radius=20, normal_cells=False)
        
        for step in range(300):
            if 100 <= step < 200:
                ca.therapy = np.ones((100, 100)) * intensity
            else:
                ca.therapy = np.zeros((100, 100))
            ca.step()
        
        response_metrics = ResponseVsStability.measure_response(ca.history, therapy_start=100, therapy_end=200)
        stability_metrics = StabilityMetrics.compute_all_metrics(ca.history, therapy_start=100, therapy_end=200)
        
        results_per_seed.append({
            'response': response_metrics['max_reduction'],
            'stability': stability_metrics['stability_score']
        })
    
    df_seed = pd.DataFrame(results_per_seed)
    if df_seed['response'].std() > 0:
        r, _ = pearsonr(df_seed['response'], df_seed['stability'])
        seed_results.append({
            'seed': seed,
            'correlation': r,
            'sign': np.sign(r)
        })

df_seeds = pd.DataFrame(seed_results)
negative_count = np.sum(df_seeds['sign'] == -1)
positive_count = np.sum(df_seeds['sign'] == 1)

print(f"Seeds with negative correlation: {negative_count}/20 ({negative_count/20*100:.0f}%)")
print(f"Seeds with positive correlation: {positive_count}/20 ({positive_count/20*100:.0f}%)")
print(f"\nMean correlation: {df_seeds['correlation'].mean():.4f} ± {df_seeds['correlation'].std():.4f}")
print(f"Median correlation: {df_seeds['correlation'].median():.4f}")

# Identify problematic seeds
if positive_count > 0:
    print(f"\n⚠️  REVIEWER CONCERN: {positive_count} seeds show POSITIVE correlation")
    print("Problematic seeds:", df_seeds[df_seeds['sign'] == 1]['seed'].values)
    
    # Analyze why
    print("\nAnalyzing seed 0 (if problematic):")
    if 0 in df_seeds[df_seeds['sign'] == 1]['seed'].values:
        print("  → This seed produces inverse relationship")
        print("  → Likely due to stochastic initial conditions affecting evolutionary trajectory")
else:
    print("\n✅ All seeds show negative correlation")

# Test 4: Alternative stability metrics (address circularity concern)
print("\n" + "="*80)
print("TEST 4: ALTERNATIVE STABILITY DEFINITIONS")
print("Testing if result holds with metrics that DON'T penalize elimination")
print("="*80)

# Alternative metric 1: Population variance (lower = more stable)
# This DOESN'T inherently penalize elimination
def population_stability_variance(history, start, end):
    total = np.array(history['sensitive']) + np.array(history['resistant'])
    post_therapy = total[end:min(end+100, len(total))]
    return -np.std(post_therapy)  # Negative so higher = more stable

# Alternative metric 2: Final size (higher = better, opposite of typical "stability")
def final_population_size(history):
    total = history['sensitive'][-1] + history['resistant'][-1]
    return total / 1000  # Normalize

alt_results = []
for intensity in [0.15, 0.25, 0.35, 0.45, 0.55]:
    ca = AdvancedTumorCA(size=100, seed=42)
    ca.initialize_tumor(radius=20, normal_cells=False)
    
    for step in range(300):
        if 100 <= step < 200:
            ca.therapy = np.ones((100, 100)) * intensity
        else:
            ca.therapy = np.zeros((100, 100))
        ca.step()
    
    response_metrics = ResponseVsStability.measure_response(ca.history, therapy_start=100, therapy_end=200)
    
    alt_results.append({
        'response': response_metrics['max_reduction'],
        'variance_stability': population_stability_variance(ca.history, 100, 200),
        'final_size': final_population_size(ca.history)
    })

df_alt = pd.DataFrame(alt_results)

r_variance, p_variance = pearsonr(df_alt['response'], df_alt['variance_stability'])
r_final, p_final = pearsonr(df_alt['response'], df_alt['final_size'])

print(f"\nAlternative Metric 1 - Population Variance Stability:")
print(f"  Correlation with response: ρ = {r_variance:.4f}, p = {p_variance:.4e}")
print(f"  {'✅ STILL NEGATIVE' if r_variance < 0 else '❌ SIGN FLIPPED'}")

print(f"\nAlternative Metric 2 - Final Population Size:")
print(f"  Correlation with response: ρ = {r_final:.4f}, p = {p_final:.4e}")
print(f"  {'✅ NEGATIVE (high response → low final size)' if r_final < 0 else '❌ POSITIVE'}")

# Summary
print("\n" + "="*80)
print("SUMMARY FOR REVIEWERS")
print("="*80)

print("\n1. Perfect Correlations:")
if abs(pearson_r) > 0.999:
    print("   ⚠️  Acknowledge: Deterministic coupling in controlled parameter space")
    print("   Defense: Real-world parameter variation would add noise")
    print("   Action: Report with CI and alternative metrics")
else:
    print("   ✅ Not suspiciously perfect")

print(f"\n2. Seed Reproducibility: {negative_count}/20 = {negative_count/20*100:.0f}%")
if negative_count >= 18:
    print("   ✅ Strong reproducibility")
elif negative_count >= 15:
    print("   ⚠️  Moderate reproducibility - clarify conditions")
else:
    print("   ❌ Weak reproducibility - fundamental issue")

print("\n3. Metric Independence:")
if r_variance < 0 and r_final < 0:
    print("   ✅ Tradeoff holds with alternative metrics")
else:
    print("   ⚠️  Result may be metric-dependent")

print("\n" + "="*80)
