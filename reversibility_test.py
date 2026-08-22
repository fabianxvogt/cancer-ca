"""
Partial Reversibility Test
Tests whether MTD-Metronomic trade-off persists when:
1. Dead cells can resurrect (p_resurrect = 0.01)
2. Resistant cells can revert to sensitive (p_revert = 0.001)
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
import seaborn as sns
from scipy.stats import pearsonr, entropy
import json

sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10

class ReversibleTumorCA(AdvancedTumorCA):
    """Extended CA with reversibility mechanisms."""
    
    def __init__(self, *args, resurrection_prob=0.0, reversion_prob=0.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.resurrection_prob = resurrection_prob
        self.reversion_prob = reversion_prob
    
    def step(self):
        """Override step to add reversibility."""
        # First, normal CA step
        super().step()
        
        # Then apply reversibility mechanisms
        if self.resurrection_prob > 0:
            self._apply_resurrection()
        
        if self.reversion_prob > 0:
            self._apply_reversion()
    
    def _apply_resurrection(self):
        """Dead cells can spontaneously resurrect to sensitive state."""
        dead_mask = (self.grid == 4)
        resurrect_mask = dead_mask & (np.random.random(self.grid.shape) < self.resurrection_prob)
        
        # Resurrect to sensitive state
        self.grid[resurrect_mask] = 2
        
        # Reset their age
        self.dead_age[resurrect_mask] = 0
        
        if np.sum(resurrect_mask) > 0:
            print(f"  Resurrected {np.sum(resurrect_mask)} dead cells")
    
    def _apply_reversion(self):
        """Resistant cells can revert to sensitive state."""
        resistant_mask = (self.grid == 3)
        revert_mask = resistant_mask & (np.random.random(self.grid.shape) < self.reversion_prob)
        
        # Revert to sensitive
        self.grid[revert_mask] = 2
        
        if np.sum(revert_mask) > 0:
            print(f"  Reverted {np.sum(revert_mask)} resistant cells to sensitive")

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

def run_protocol_reversible(resurrection_prob, reversion_prob, protocol_name, therapy_schedule):
    """Run therapy protocol and compute final stability metrics."""
    ca = ReversibleTumorCA(
        size=120,
        resurrection_prob=resurrection_prob,
        reversion_prob=reversion_prob
    )
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
    
    population = ca.grid.copy()
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

def test_reversibility_scenario(resurrection_prob, reversion_prob, n_intensities=15):
    """Test a specific reversibility scenario."""
    print(f"\nTesting resurrection={resurrection_prob}, reversion={reversion_prob}")
    
    results = []
    
    for intensity in np.linspace(0.1, 1.0, n_intensities):
        print(f"  Intensity={intensity:.2f}")
        
        # MTD: High dose, windowed (200-400)
        mtd_result = run_protocol_reversible(
            resurrection_prob, reversion_prob,
            "MTD", 
            lambda t: intensity if 200 <= t < 400 else 0.0
        )
        
        # Metronomic: Low continuous (200-450)
        metronomic_result = run_protocol_reversible(
            resurrection_prob, reversion_prob,
            "Metronomic", 
            lambda t: intensity * 0.5 if 200 <= t < 450 else 0.0
        )
        
        if mtd_result is not None and metronomic_result is not None:
            results.append({
                'intensity': intensity,
                'resurrection_prob': resurrection_prob,
                'reversion_prob': reversion_prob,
                'mtd_metric': mtd_result['response_diversity'],
                'metronomic_metric': metronomic_result['response_diversity'],
                'mtd_resistant_fraction': mtd_result['resistant_fraction'],
                'metronomic_resistant_fraction': metronomic_result['resistant_fraction']
            })
    
    return results

def main():
    # Test scenarios
    scenarios = [
        {'resurrection_prob': 0.0, 'reversion_prob': 0.0, 'label': 'Baseline (Irreversible)'},
        {'resurrection_prob': 0.01, 'reversion_prob': 0.0, 'label': 'Resurrection Only'},
        {'resurrection_prob': 0.0, 'reversion_prob': 0.001, 'label': 'Reversion Only'},
        {'resurrection_prob': 0.01, 'reversion_prob': 0.001, 'label': 'Both Mechanisms'},
    ]
    
    all_results = []
    correlations = []
    
    for scenario in scenarios:
        results = test_reversibility_scenario(
            resurrection_prob=scenario['resurrection_prob'],
            reversion_prob=scenario['reversion_prob'],
            n_intensities=10
        )
        
        all_results.extend(results)
        
        # Calculate correlation
        if len(results) >= 3:
            mtd_metrics = [r['mtd_metric'] for r in results]
            metronomic_metrics = [r['metronomic_metric'] for r in results]
            
            if len(set(mtd_metrics)) > 1 and len(set(metronomic_metrics)) > 1:
                rho, pval = pearsonr(mtd_metrics, metronomic_metrics)
                correlations.append({
                    **scenario,
                    'correlation': rho,
                    'p_value': pval,
                    'n_points': len(results)
                })
                print(f"  → Correlation: ρ={rho:.4f}, p={pval:.4e}")
    
    # Save results
    with open('images/reversibility_results.json', 'w') as f:
        json.dump({
            'results': all_results,
            'correlations': correlations
        }, f, indent=2)
    
    # Create visualization
    create_reversibility_plot(all_results, correlations)
    
    print(f"\n✓ Completed {len(scenarios)} reversibility scenarios")
    print(f"✓ Results saved to images/reversibility_results.json")

def create_reversibility_plot(results, correlations):
    """Create comparison plot across reversibility scenarios."""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    scenarios = [
        {'resurrection_prob': 0.0, 'reversion_prob': 0.0, 'label': 'Baseline\n(Irreversible)'},
        {'resurrection_prob': 0.01, 'reversion_prob': 0.0, 'label': 'Resurrection\nOnly'},
        {'resurrection_prob': 0.0, 'reversion_prob': 0.001, 'label': 'Reversion\nOnly'},
        {'resurrection_prob': 0.01, 'reversion_prob': 0.001, 'label': 'Both\nMechanisms'},
    ]
    
    for idx, scenario in enumerate(scenarios):
        ax = axes[idx // 2, idx % 2]
        
        # Filter results for this scenario
        scenario_results = [
            r for r in results 
            if r['resurrection_prob'] == scenario['resurrection_prob'] 
            and r['reversion_prob'] == scenario['reversion_prob']
        ]
        
        if scenario_results:
            mtd_metrics = [r['mtd_metric'] for r in scenario_results]
            metronomic_metrics = [r['metronomic_metric'] for r in scenario_results]
            
            # Scatter plot
            ax.scatter(mtd_metrics, metronomic_metrics, alpha=0.7, s=60)
            
            # Linear fit
            if len(mtd_metrics) > 1:
                z = np.polyfit(mtd_metrics, metronomic_metrics, 1)
                p = np.poly1d(z)
                x_line = np.linspace(min(mtd_metrics), max(mtd_metrics), 100)
                ax.plot(x_line, p(x_line), 'r--', alpha=0.5, linewidth=2)
            
            # Find correlation for this scenario
            corr_data = next((c for c in correlations 
                            if c['resurrection_prob'] == scenario['resurrection_prob']
                            and c['reversion_prob'] == scenario['reversion_prob']), None)
            
            if corr_data:
                ax.text(0.05, 0.95, f"ρ = {corr_data['correlation']:.4f}\np < {corr_data['p_value']:.1e}",
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_xlabel('MTD Metric (Response Diversity)')
            ax.set_ylabel('Metronomic Metric (Response Diversity)')
            ax.set_title(scenario['label'])
            ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('images/figure_S3_reversibility.png', dpi=300, bbox_inches='tight')
    plt.savefig('images/figure_S3_reversibility.pdf', bbox_inches='tight')
    print("✓ Saved Figure S3: Reversibility Test")

if __name__ == '__main__':
    main()
