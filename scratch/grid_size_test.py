"""
Grid Size Variation Analysis
Tests whether MTD-Metronomic trade-off persists across different grid sizes:
- 60×60 (small)
- 120×120 (baseline)
- 240×240 (large)

Goal: Confirm results are not finite-size artifacts.
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
import seaborn as sns
from scipy.stats import pearsonr, entropy
import json
import time

sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10

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

def run_protocol(size, protocol_name, therapy_schedule, max_steps=500):
    """Run therapy protocol and compute final stability metrics."""
    ca = AdvancedTumorCA(size=size)
    ca.initialize_tumor()
    
    for t in range(max_steps):
        intensity = therapy_schedule(t)
        ca.therapy = np.ones((size, size)) * intensity
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

def test_grid_size(size, n_intensities=15):
    """Test a specific grid size across therapy intensities."""
    print(f"\n{'='*60}")
    print(f"Testing grid size: {size}×{size}")
    print(f"{'='*60}")
    
    results = []
    start_time = time.time()
    
    for intensity in np.linspace(0.1, 1.0, n_intensities):
        print(f"\n  Intensity={intensity:.2f}")
        
        # MTD: High dose, windowed therapy (200-400)
        mtd_result = run_protocol(
            size, "MTD", 
            lambda t: intensity if 200 <= t < 400 else 0.0
        )
        
        # Metronomic: Low continuous dose (200-450)
        metronomic_result = run_protocol(
            size, "Metronomic", 
            lambda t: intensity * 0.5 if 200 <= t < 450 else 0.0
        )
        
        if mtd_result is not None and metronomic_result is not None:
            results.append({
                'intensity': intensity,
                'grid_size': size,
                'mtd_metric': mtd_result['response_diversity'],
                'metronomic_metric': metronomic_result['response_diversity'],
                'mtd_resistant_fraction': mtd_result['resistant_fraction'],
                'metronomic_resistant_fraction': metronomic_result['resistant_fraction']
            })
    
    elapsed = time.time() - start_time
    print(f"\n  Grid {size}×{size} completed in {elapsed:.1f} seconds")
    
    return results

def main():
    # Test different grid sizes
    grid_sizes = [60, 120, 240]
    
    all_results = []
    correlations = []
    
    for size in grid_sizes:
        # Adjust n_intensities based on size to manage computation time
        n_intensities = 15 if size <= 120 else 10
        
        results = test_grid_size(size, n_intensities=n_intensities)
        all_results.extend(results)
        
        # Calculate correlation for this grid size
        if len(results) >= 3:
            mtd_metrics = [r['mtd_metric'] for r in results]
            metronomic_metrics = [r['metronomic_metric'] for r in results]
            
            if len(set(mtd_metrics)) > 1 and len(set(metronomic_metrics)) > 1:
                rho, pval = pearsonr(mtd_metrics, metronomic_metrics)
                correlations.append({
                    'grid_size': size,
                    'correlation': rho,
                    'p_value': pval,
                    'n_points': len(results),
                    'mean_mtd_metric': np.mean(mtd_metrics),
                    'mean_metronomic_metric': np.mean(metronomic_metrics),
                    'mtd_metric_std': np.std(mtd_metrics),
                    'metronomic_metric_std': np.std(metronomic_metrics)
                })
                print(f"\n  → Correlation for {size}×{size}: ρ={rho:.4f}, p={pval:.4e}")
    
    # Save results
    with open('images/grid_size_results.json', 'w') as f:
        json.dump({
            'results': all_results,
            'correlations': correlations
        }, f, indent=2)
    
    # Create visualization
    create_grid_size_plot(all_results, correlations)
    
    print(f"\n{'='*60}")
    print(f"✓ Completed {len(grid_sizes)} grid sizes")
    print(f"✓ Results saved to images/grid_size_results.json")
    print(f"{'='*60}")

def create_grid_size_plot(results, correlations):
    """Create comparison plot across grid sizes."""
    
    fig = plt.figure(figsize=(15, 5))
    
    # Get unique grid sizes
    grid_sizes = sorted(list(set(r['grid_size'] for r in results)))
    
    # Plot 1: Scatter plots for each grid size
    for idx, size in enumerate(grid_sizes):
        ax = plt.subplot(1, 4, idx + 1)
        
        # Filter results for this grid size
        size_results = [r for r in results if r['grid_size'] == size]
        
        if size_results:
            mtd_metrics = [r['mtd_metric'] for r in size_results]
            metronomic_metrics = [r['metronomic_metric'] for r in size_results]
            
            # Scatter plot
            ax.scatter(mtd_metrics, metronomic_metrics, alpha=0.7, s=60)
            
            # Linear fit
            if len(mtd_metrics) > 1:
                z = np.polyfit(mtd_metrics, metronomic_metrics, 1)
                p = np.poly1d(z)
                x_line = np.linspace(min(mtd_metrics), max(mtd_metrics), 100)
                ax.plot(x_line, p(x_line), 'r--', alpha=0.5, linewidth=2)
            
            # Find correlation
            corr_data = next((c for c in correlations if c['grid_size'] == size), None)
            
            if corr_data:
                ax.text(0.05, 0.95, f"ρ = {corr_data['correlation']:.4f}\np < {corr_data['p_value']:.1e}",
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_xlabel('MTD Metric')
            ax.set_ylabel('Metronomic Metric')
            ax.set_title(f'{size}×{size} Grid')
            ax.grid(True, alpha=0.3)
    
    # Plot 4: Correlation strength vs grid size
    ax4 = plt.subplot(1, 4, 4)
    
    sizes = [c['grid_size'] for c in correlations]
    rhos = [c['correlation'] for c in correlations]
    
    ax4.plot(sizes, rhos, 'o-', markersize=10, linewidth=2)
    ax4.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax4.set_xlabel('Grid Size')
    ax4.set_ylabel('Correlation (ρ)')
    ax4.set_title('Correlation vs Grid Size')
    ax4.set_xticks(sizes)
    ax4.set_xticklabels([f'{s}×{s}' for s in sizes], rotation=45)
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(-1.05, 1.05)
    
    plt.tight_layout()
    plt.savefig('images/figure_S4_grid_size.png', dpi=300, bbox_inches='tight')
    plt.savefig('images/figure_S4_grid_size.pdf', bbox_inches='tight')
    print("✓ Saved Figure S4: Grid Size Variation")

if __name__ == '__main__':
    main()
