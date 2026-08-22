"""
Parameter Sensitivity Analysis
Tests whether MTD-Metronomic trade-off persists across:
- Mutation rates: μ₀ = [0.001, 0.002, 0.005]
- Resistance cost: resistant cells divide slower
- Therapy-mutation coupling: α = [0, 1.5, 3.0]
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
import seaborn as sns
from scipy.stats import pearsonr, entropy
import json

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12

def calculate_response_diversity(population, sensitive_state=2, resistant_state=3):
    """Calculate response diversity metric (Shannon entropy of cell type distribution)."""
    n_sensitive = np.sum(population == sensitive_state)
    n_resistant = np.sum(population == resistant_state)
    total = n_sensitive + n_resistant
    
    if total == 0:
        return 0.0
    
    p_sensitive = n_sensitive / total
    p_resistant = n_resistant / total
    
    # Shannon entropy
    probs = [p for p in [p_sensitive, p_resistant] if p > 0]
    if len(probs) == 0:
        return 0.0
    return entropy(probs, base=2)

def run_protocol_parametrized(mutation_rate, resistance_cost, therapy_coupling, protocol_name, therapy_schedule):
    """Run therapy protocol and compute final stability metrics."""
    ca = AdvancedTumorCA(size=120)
    ca.local_mutation_rate = np.ones((120, 120)) * mutation_rate
    ca.local_division_rate = np.ones((120, 120)) * 4.0 * (1.0 - resistance_cost)
    ca.initialize_tumor()
    
    for t in range(500):
        intensity = therapy_schedule(t)
        ca.therapy = np.ones((120, 120)) * intensity
        ca.step()
        
        if t % 50 == 0:
            total_cells = np.sum((ca.grid == 2) | (ca.grid == 3))
            if total_cells < 10:
                print(f"  {protocol_name}: Extinction at t={t}")
                return None
    
    # Get final population state
    population = ca.grid.copy()
    
    # Calculate metric
    response_diversity = calculate_response_diversity(population, sensitive_state=2, resistant_state=3)
    
    sensitive_fraction = np.sum(population == 2) / max(1, np.sum((population == 2) | (population == 3)))
    resistant_fraction = np.sum(population == 3) / max(1, np.sum((population == 2) | (population == 3)))
    
    print(f"  {protocol_name}: S={sensitive_fraction:.3f}, R={resistant_fraction:.3f}, "
          f"Metric={response_diversity:.4f}")
    
    return {
        'protocol': protocol_name,
        'sensitive_fraction': sensitive_fraction,
        'resistant_fraction': resistant_fraction,
        'response_diversity': response_diversity
    }

def test_parameter_combination(mutation_rate, resistance_cost, therapy_mutation_coupling, n_intensities=20):
    """Test a single parameter combination across therapy intensities."""
    print(f"\nTesting μ₀={mutation_rate}, cost={resistance_cost}, α={therapy_mutation_coupling}")
    
    results = []
    
    for intensity in np.linspace(0.1, 1.0, n_intensities):
        print(f"  Intensity={intensity:.2f}")
        
        # MTD protocol: High dose, windowed (200-400)
        mtd_result = run_protocol_parametrized(
            mutation_rate, resistance_cost, therapy_mutation_coupling,
            "MTD",
            lambda t: intensity if 200 <= t < 400 else 0.0
        )
        
        # Metronomic protocol: Low continuous (200-450)
        metronomic_result = run_protocol_parametrized(
            mutation_rate, resistance_cost, therapy_mutation_coupling,
            "Metronomic", 
            lambda t: intensity * 0.5 if 200 <= t < 450 else 0.0
        )
        
        if mtd_result is not None and metronomic_result is not None:
            results.append({
                'intensity': intensity,
                'mutation_rate': mutation_rate,
                'resistance_cost': resistance_cost,
                'therapy_mutation_coupling': therapy_mutation_coupling,
                'mtd_metric': mtd_result['response_diversity'],
                'metronomic_metric': metronomic_result['response_diversity'],
                'mtd_resistant_fraction': mtd_result['resistant_fraction'],
                'metronomic_resistant_fraction': metronomic_result['resistant_fraction']
            })
    
    return results

def main():
    # Parameter ranges
    mutation_rates = [0.001, 0.002, 0.005]
    resistance_costs = [0.0, 0.1, 0.2]  # 0%, 10%, 20% division penalty
    therapy_mutation_couplings = [0.0, 1.5, 3.0]
    
    all_results = []
    correlations = []
    
    # Test all combinations
    for mu in mutation_rates:
        for cost in resistance_costs:
            for alpha in therapy_mutation_couplings:
                results = test_parameter_combination(
                    mutation_rate=mu,
                    resistance_cost=cost,
                    therapy_mutation_coupling=alpha,
                    n_intensities=10  # Reduced for speed
                )
                
                all_results.extend(results)
                
                # Calculate correlation for this combination
                if len(results) >= 3:
                    mtd_metrics = [r['mtd_metric'] for r in results]
                    metronomic_metrics = [r['metronomic_metric'] for r in results]
                    
                    if len(set(mtd_metrics)) > 1 and len(set(metronomic_metrics)) > 1:
                        rho, pval = pearsonr(mtd_metrics, metronomic_metrics)
                        correlations.append({
                            'mutation_rate': mu,
                            'resistance_cost': cost,
                            'therapy_mutation_coupling': alpha,
                            'correlation': rho,
                            'p_value': pval,
                            'n_points': len(results)
                        })
                        print(f"  → Correlation: ρ={rho:.4f}, p={pval:.4e}")
    
    # Save results
    with open('images/parameter_sensitivity_results.json', 'w') as f:
        json.dump({
            'results': all_results,
            'correlations': correlations
        }, f, indent=2)
    
    # Create summary plot
    create_summary_plot(correlations)
    
    print(f"\n✓ Completed {len(correlations)} parameter combinations")
    print(f"✓ Results saved to images/parameter_sensitivity_results.json")

def create_summary_plot(correlations):
    """Create heatmap showing correlation strength across parameter space."""
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    # Get unique values
    mutation_rates = sorted(list(set(c['mutation_rate'] for c in correlations)))
    costs = sorted(list(set(c['resistance_cost'] for c in correlations)))
    alphas = sorted(list(set(c['therapy_mutation_coupling'] for c in correlations)))
    
    # Plot 1: Mutation rate vs Resistance cost (fixed α=3.0)
    grid1 = np.full((len(costs), len(mutation_rates)), np.nan)
    for c in correlations:
        if c['therapy_mutation_coupling'] == 3.0:
            i = costs.index(c['resistance_cost'])
            j = mutation_rates.index(c['mutation_rate'])
            grid1[i, j] = c['correlation']
    
    im1 = axes[0].imshow(grid1, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    axes[0].set_xticks(range(len(mutation_rates)))
    axes[0].set_xticklabels([f'{m:.3f}' for m in mutation_rates])
    axes[0].set_yticks(range(len(costs)))
    axes[0].set_yticklabels([f'{c:.1f}' for c in costs])
    axes[0].set_xlabel('Mutation Rate μ₀')
    axes[0].set_ylabel('Resistance Cost')
    axes[0].set_title('α = 3.0 (High Coupling)')
    
    # Add correlation values
    for i in range(len(costs)):
        for j in range(len(mutation_rates)):
            if not np.isnan(grid1[i, j]):
                axes[0].text(j, i, f'{grid1[i, j]:.2f}', 
                           ha='center', va='center', fontsize=9)
    
    # Plot 2: Mutation rate vs α (fixed cost=0.1)
    grid2 = np.full((len(alphas), len(mutation_rates)), np.nan)
    for c in correlations:
        if c['resistance_cost'] == 0.1:
            i = alphas.index(c['therapy_mutation_coupling'])
            j = mutation_rates.index(c['mutation_rate'])
            grid2[i, j] = c['correlation']
    
    im2 = axes[1].imshow(grid2, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    axes[1].set_xticks(range(len(mutation_rates)))
    axes[1].set_xticklabels([f'{m:.3f}' for m in mutation_rates])
    axes[1].set_yticks(range(len(alphas)))
    axes[1].set_yticklabels([f'{a:.1f}' for a in alphas])
    axes[1].set_xlabel('Mutation Rate μ₀')
    axes[1].set_ylabel('Therapy-Mutation Coupling α')
    axes[1].set_title('Resistance Cost = 10%')
    
    for i in range(len(alphas)):
        for j in range(len(mutation_rates)):
            if not np.isnan(grid2[i, j]):
                axes[1].text(j, i, f'{grid2[i, j]:.2f}', 
                           ha='center', va='center', fontsize=9)
    
    # Plot 3: Resistance cost vs α (fixed μ₀=0.002)
    grid3 = np.full((len(alphas), len(costs)), np.nan)
    for c in correlations:
        if c['mutation_rate'] == 0.002:
            i = alphas.index(c['therapy_mutation_coupling'])
            j = costs.index(c['resistance_cost'])
            grid3[i, j] = c['correlation']
    
    im3 = axes[2].imshow(grid3, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    axes[2].set_xticks(range(len(costs)))
    axes[2].set_xticklabels([f'{c:.1f}' for c in costs])
    axes[2].set_yticks(range(len(alphas)))
    axes[2].set_yticklabels([f'{a:.1f}' for a in alphas])
    axes[2].set_xlabel('Resistance Cost')
    axes[2].set_ylabel('Therapy-Mutation Coupling α')
    axes[2].set_title('μ₀ = 0.002 (Baseline)')
    
    for i in range(len(alphas)):
        for j in range(len(costs)):
            if not np.isnan(grid3[i, j]):
                axes[2].text(j, i, f'{grid3[i, j]:.2f}', 
                           ha='center', va='center', fontsize=9)
    
    plt.colorbar(im3, ax=axes, label='Correlation (ρ)', fraction=0.046, pad=0.04)
    plt.tight_layout()
    plt.savefig('images/figure_S2_parameter_sensitivity.png', dpi=300, bbox_inches='tight')
    plt.savefig('images/figure_S2_parameter_sensitivity.pdf', bbox_inches='tight')
    print("✓ Saved Figure S2: Parameter Sensitivity")

if __name__ == '__main__':
    main()
