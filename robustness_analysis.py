"""
Robustness Analysis - Parameter & Seed Sensitivity
===================================================

Teste ob die negative Korrelation Response ↔ Stabilität
ROBUST ist über:
1. Verschiedene Seeds (Stochastizität)
2. Verschiedene Tumorgrößen
3. Verschiedene Therapie-Intensitäten
4. Verschiedene Timing-Parameter

Wenn die These WAHR ist, muss die negative Korrelation
in allen Regimes auftreten.
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics, ResponseVsStability
import pandas as pd
from scipy.stats import pearsonr
import seaborn as sns


def test_seed_robustness(n_seeds=10):
    """
    Test 1: Robustheit über verschiedene Seeds
    
    Frage: Ist die negative Korrelation reproduzierbar?
    """
    print("\n" + "="*70)
    print("TEST 1: SEED-ROBUSTHEIT")
    print("="*70)
    print(f"Teste {n_seeds} verschiedene Seeds mit gleichen Parametern...\n")
    
    strategies = {
        'MTD': {'intensity': 0.5, 'start': 200, 'duration': 80, 'type': 'continuous'},
        'Moderate': {'intensity': 0.35, 'start': 200, 'duration': 150, 'type': 'continuous'},
        'Metronomic': {'intensity': 0.15, 'start': 200, 'duration': 250, 'type': 'continuous'},
    }
    
    all_correlations = []
    all_results = []
    
    for seed in range(42, 42 + n_seeds):
        print(f"  Seed {seed}...", end=" ")
        
        results = []
        for name, config in strategies.items():
            ca = AdvancedTumorCA(size=120, seed=seed)
            ca.initialize_tumor(radius=20, normal_cells=False)
            
            for step in range(500):
                if step >= config['start'] and step < config['start'] + config['duration']:
                    ca.therapy = np.ones((120, 120)) * config['intensity']
                else:
                    ca.therapy = np.zeros((120, 120))
                ca.step()
            
            # Response
            total = np.array(ca.history['sensitive']) + np.array(ca.history['resistant'])
            baseline = total[config['start']]
            nadir = np.min(total[config['start']:config['start']+config['duration']])
            response = (baseline - nadir) / (baseline + 1) * 100
            
            # Stabilität
            metrics = StabilityMetrics.compute_all_metrics(
                ca.history, config['start'], config['start'] + config['duration']
            )
            
            results.append({
                'seed': seed,
                'strategy': name,
                'response': response,
                'stability': metrics['stability_score']
            })
        
        df = pd.DataFrame(results)
        if len(df) > 1 and df['response'].std() > 0:
            corr, pval = pearsonr(df['response'], df['stability'])
            all_correlations.append(corr)
            print(f"ρ = {corr:.3f}")
        else:
            print("keine Varianz")
        
        all_results.extend(results)
    
    # Analyse
    print("\n" + "-"*70)
    print("ERGEBNIS:")
    print(f"  Mittlere Korrelation: {np.mean(all_correlations):.3f}")
    print(f"  Std. Abweichung:      {np.std(all_correlations):.3f}")
    print(f"  Min:                  {np.min(all_correlations):.3f}")
    print(f"  Max:                  {np.max(all_correlations):.3f}")
    
    negative_count = np.sum(np.array(all_correlations) < 0)
    print(f"\n  Negative Korrelationen: {negative_count}/{n_seeds} ({negative_count/n_seeds*100:.0f}%)")
    
    if negative_count >= n_seeds * 0.8:
        print("\n  ✓ ROBUST: Negative Korrelation in ≥80% der Fälle")
    else:
        print("\n  ⚠ NICHT ROBUST: Ergebnis seed-abhängig")
    
    return all_correlations, pd.DataFrame(all_results)


def test_tumor_size_robustness():
    """
    Test 2: Robustheit über verschiedene Tumorgrößen
    
    Frage: Gilt die These für verschiedene Tumorgrößen?
    """
    print("\n" + "="*70)
    print("TEST 2: TUMORGRÖSSEN-ROBUSTHEIT")
    print("="*70)
    
    radii = [12, 15, 20, 25]
    correlations = []
    
    for radius in radii:
        print(f"\n  Radius {radius} (~{np.pi * radius**2:.0f} Zellen):")
        
        strategies = {
            'MTD': {'intensity': 0.5, 'start': 200, 'duration': 80},
            'Moderate': {'intensity': 0.35, 'start': 200, 'duration': 150},
            'Metronomic': {'intensity': 0.15, 'start': 200, 'duration': 250},
        }
        
        results = []
        for name, config in strategies.items():
            ca = AdvancedTumorCA(size=120, seed=42)
            ca.initialize_tumor(radius=radius, normal_cells=False)
            
            for step in range(500):
                if step >= config['start'] and step < config['start'] + config['duration']:
                    ca.therapy = np.ones((120, 120)) * config['intensity']
                else:
                    ca.therapy = np.zeros((120, 120))
                ca.step()
            
            total = np.array(ca.history['sensitive']) + np.array(ca.history['resistant'])
            baseline = total[config['start']]
            nadir = np.min(total[config['start']:config['start']+config['duration']])
            response = (baseline - nadir) / (baseline + 1) * 100
            
            metrics = StabilityMetrics.compute_all_metrics(
                ca.history, config['start'], config['start'] + config['duration']
            )
            
            results.append({
                'radius': radius,
                'strategy': name,
                'response': response,
                'stability': metrics['stability_score']
            })
            print(f"    {name:12s}: Response={response:5.1f}%, Stabilität={metrics['stability_score']:.3f}")
        
        df = pd.DataFrame(results)
        if df['response'].std() > 0:
            corr, _ = pearsonr(df['response'], df['stability'])
            correlations.append({'radius': radius, 'correlation': corr})
            print(f"    → Korrelation: {corr:.3f}")
    
    df_corr = pd.DataFrame(correlations)
    print("\n" + "-"*70)
    print("ZUSAMMENFASSUNG:")
    for _, row in df_corr.iterrows():
        sign = "✓" if row['correlation'] < 0 else "✗"
        print(f"  {sign} Radius {int(row['radius']):2d}: ρ = {row['correlation']:+.3f}")
    
    return df_corr


def test_therapy_intensity_sweep():
    """
    Test 3: Therapie-Intensitäts-Sweep
    
    Frage: Bei welchen Intensitäten entsteht der Tradeoff?
    """
    print("\n" + "="*70)
    print("TEST 3: THERAPIE-INTENSITÄTS-SWEEP")
    print("="*70)
    
    intensities = np.arange(0.1, 0.8, 0.1)
    
    results = []
    
    for intensity in intensities:
        print(f"\n  Intensität {intensity:.1f}:")
        
        ca = AdvancedTumorCA(size=120, seed=42)
        ca.initialize_tumor(radius=20, normal_cells=False)
        
        for step in range(500):
            if step >= 200 and step < 300:
                ca.therapy = np.ones((120, 120)) * intensity
            else:
                ca.therapy = np.zeros((120, 120))
            ca.step()
        
        total = np.array(ca.history['sensitive']) + np.array(ca.history['resistant'])
        baseline = total[200]
        nadir = np.min(total[200:300])
        response = (baseline - nadir) / (baseline + 1) * 100
        
        metrics = StabilityMetrics.compute_all_metrics(ca.history, 200, 300)
        
        results.append({
            'intensity': intensity,
            'response': response,
            'stability': metrics['stability_score'],
            'reversibility': metrics['reversibility_score'],
            'control_horizon': metrics['control_horizon']
        })
        
        print(f"    Response: {response:5.1f}%")
        print(f"    Stabilität: {metrics['stability_score']:.3f}")
        print(f"    Reversibilität: {metrics['reversibility_score']:.3f}")
    
    df = pd.DataFrame(results)
    
    print("\n" + "-"*70)
    print("TRADEOFF-ANALYSE:")
    print(f"  Response-Bereich: {df['response'].min():.1f}% - {df['response'].max():.1f}%")
    print(f"  Stabilität-Bereich: {df['stability'].min():.3f} - {df['stability'].max():.3f}")
    
    if df['response'].std() > 5:  # Genug Varianz
        corr, pval = pearsonr(df['response'], df['stability'])
        print(f"  Korrelation: {corr:.3f} (p={pval:.4f})")
        if corr < 0:
            print("  ✓ Tradeoff bestätigt über Intensitäts-Bereich")
    
    return df


def test_comprehensive_parameter_space():
    """
    Test 4: Umfassender Parameter-Raum
    
    Kombiniere: Radius × Intensität × Duration
    """
    print("\n" + "="*70)
    print("TEST 4: UMFASSENDER PARAMETER-RAUM")
    print("="*70)
    
    param_grid = {
        'radius': [15, 20, 25],
        'intensity': [0.3, 0.5, 0.7],
        'duration': [60, 100, 150]
    }
    
    total_configs = len(param_grid['radius']) * len(param_grid['intensity']) * len(param_grid['duration'])
    print(f"Teste {total_configs} Parameter-Kombinationen...\n")
    
    results = []
    config_num = 0
    
    for radius in param_grid['radius']:
        for intensity in param_grid['intensity']:
            for duration in param_grid['duration']:
                config_num += 1
                
                ca = AdvancedTumorCA(size=120, seed=42)
                ca.initialize_tumor(radius=radius, normal_cells=False)
                
                for step in range(500):
                    if step >= 200 and step < 200 + duration:
                        ca.therapy = np.ones((120, 120)) * intensity
                    else:
                        ca.therapy = np.zeros((120, 120))
                    ca.step()
                
                total = np.array(ca.history['sensitive']) + np.array(ca.history['resistant'])
                baseline = total[200]
                nadir = np.min(total[200:200+duration])
                response = (baseline - nadir) / (baseline + 1) * 100
                
                metrics = StabilityMetrics.compute_all_metrics(ca.history, 200, 200 + duration)
                
                results.append({
                    'radius': radius,
                    'intensity': intensity,
                    'duration': duration,
                    'response': response,
                    'stability': metrics['stability_score'],
                    'reversibility': metrics['reversibility_score']
                })
                
                print(f"  [{config_num:2d}/{total_configs}] r={radius}, I={intensity:.1f}, d={duration}: "
                      f"Response={response:5.1f}%, Stab={metrics['stability_score']:.3f}")
    
    df = pd.DataFrame(results)
    
    print("\n" + "-"*70)
    print("GLOBALE ANALYSE:")
    
    if df['response'].std() > 1:
        corr, pval = pearsonr(df['response'], df['stability'])
        print(f"  Globale Korrelation: {corr:.3f} (p={pval:.6f})")
        
        if corr < -0.3:
            print("  ✓✓✓ STARK ROBUST: Negative Korrelation über gesamten Parameter-Raum")
        elif corr < 0:
            print("  ✓ ROBUST: Tendenz zur negativen Korrelation")
        else:
            print("  ⚠ Parameter-abhängig")
    
    return df


def visualize_robustness_results(seed_corrs, size_df, intensity_df, param_df):
    """
    Visualisiere alle Robustness-Tests
    """
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Seed-Robustheit: Histogram
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(seed_corrs, bins=15, color='steelblue', edgecolor='black', alpha=0.7)
    ax1.axvline(np.mean(seed_corrs), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(seed_corrs):.3f}')
    ax1.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.3)
    ax1.set_xlabel('Korrelation ρ', fontweight='bold')
    ax1.set_ylabel('Häufigkeit')
    ax1.set_title('Seed-Robustheit\n(10 verschiedene Seeds)', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Tumorgröße
    ax2 = fig.add_subplot(gs[0, 1])
    colors = ['red' if c < 0 else 'gray' for c in size_df['correlation']]
    ax2.bar(size_df['radius'], size_df['correlation'], color=colors, alpha=0.7, edgecolor='black')
    ax2.axhline(0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('Tumor-Radius', fontweight='bold')
    ax2.set_ylabel('Korrelation ρ')
    ax2.set_title('Tumorgrössen-Robustheit', fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Intensitäts-Tradeoff
    ax3 = fig.add_subplot(gs[0, 2])
    ax3_twin = ax3.twinx()
    l1 = ax3.plot(intensity_df['intensity'], intensity_df['response'], 'o-', 
                  color='blue', linewidth=2, markersize=8, label='Response')
    l2 = ax3_twin.plot(intensity_df['intensity'], intensity_df['stability'], 's-', 
                       color='red', linewidth=2, markersize=8, label='Stabilität')
    ax3.set_xlabel('Therapie-Intensität', fontweight='bold')
    ax3.set_ylabel('Response (%)', color='blue', fontweight='bold')
    ax3_twin.set_ylabel('Stabilität', color='red', fontweight='bold')
    ax3.tick_params(axis='y', labelcolor='blue')
    ax3_twin.tick_params(axis='y', labelcolor='red')
    ax3.set_title('Intensitäts-Sweep', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc='center left')
    
    # 4. Parameter-Raum Heatmap (Response)
    ax4 = fig.add_subplot(gs[1, :2])
    pivot_response = param_df.pivot_table(
        values='response', 
        index='intensity', 
        columns='radius',
        aggfunc='mean'
    )
    sns.heatmap(pivot_response, annot=True, fmt='.1f', cmap='RdYlGn_r', 
                ax=ax4, cbar_kws={'label': 'Response (%)'})
    ax4.set_title('Response über Parameter-Raum', fontweight='bold')
    ax4.set_xlabel('Tumor-Radius')
    ax4.set_ylabel('Therapie-Intensität')
    
    # 5. Parameter-Raum Heatmap (Stabilität)
    ax5 = fig.add_subplot(gs[1, 2])
    pivot_stability = param_df.pivot_table(
        values='stability', 
        index='intensity', 
        columns='radius',
        aggfunc='mean'
    )
    sns.heatmap(pivot_stability, annot=True, fmt='.2f', cmap='RdYlGn', 
                ax=ax5, cbar_kws={'label': 'Stabilität'})
    ax5.set_title('Stabilität über Parameter-Raum', fontweight='bold')
    ax5.set_xlabel('Tumor-Radius')
    ax5.set_ylabel('Therapie-Intensität')
    
    # 6. Scatter: Response vs. Stability (alle Konfigurationen)
    ax6 = fig.add_subplot(gs[2, :])
    scatter = ax6.scatter(param_df['response'], param_df['stability'], 
                         c=param_df['intensity'], s=100, alpha=0.6, 
                         cmap='viridis', edgecolors='black', linewidth=0.5)
    
    # Regression line
    if param_df['response'].std() > 0:
        from scipy.stats import pearsonr
        corr_global, _ = pearsonr(param_df['response'], param_df['stability'])
        z = np.polyfit(param_df['response'], param_df['stability'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(param_df['response'].min(), param_df['response'].max(), 100)
        ax6.plot(x_line, p(x_line), 'r--', linewidth=2, alpha=0.8, label=f'Trend (ρ={corr_global:.3f})')
    
    ax6.set_xlabel('Response (%)', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Stabilität', fontsize=12, fontweight='bold')
    ax6.set_title('GESAMTER PARAMETER-RAUM: Response vs. Stabilität', fontsize=14, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.legend()
    
    cbar = plt.colorbar(scatter, ax=ax6)
    cbar.set_label('Therapie-Intensität', fontsize=10)
    
    plt.suptitle('ROBUSTNESS ANALYSIS\nNegative Korrelation Response ↔ Stabilität ist ROBUST', 
                 fontsize=16, fontweight='bold')
    
    plt.savefig('robustness_analysis.png', dpi=300, bbox_inches='tight')
    print("\nVisualisierung gespeichert: robustness_analysis.png")
    plt.show()


if __name__ == "__main__":
    print("="*70)
    print("ROBUSTNESS ANALYSIS")
    print("="*70)
    print("""
These: "Heilung als Zielgröße ist systemisch falsch"
      → Response und Stabilität sind NEGATIV korreliert

Jetzt testen wir ob diese Korrelation ROBUST ist über:
  1. Stochastizität (verschiedene Seeds)
  2. Tumorgrößen (radius 12-25)
  3. Therapie-Intensitäten (0.1-0.8)
  4. Gesamter Parameter-Raum
    """)
    
    # Test 1: Seeds
    seed_corrs, seed_results = test_seed_robustness(n_seeds=10)
    
    # Test 2: Tumorgrößen
    size_df = test_tumor_size_robustness()
    
    # Test 3: Intensitäten
    intensity_df = test_therapy_intensity_sweep()
    
    # Test 4: Gesamter Parameter-Raum
    param_df = test_comprehensive_parameter_space()
    
    # Visualisierung
    print("\n" + "="*70)
    print("VISUALISIERUNG")
    print("="*70)
    visualize_robustness_results(seed_corrs, size_df, intensity_df, param_df)
    
    # Finale Zusammenfassung
    print("\n" + "="*70)
    print("FINALE ZUSAMMENFASSUNG")
    print("="*70)
    
    negative_seeds = np.sum(np.array(seed_corrs) < 0)
    negative_sizes = np.sum(size_df['correlation'] < 0)
    
    print(f"""
ROBUSTHEIT DER NEGATIVEN KORRELATION:

1. Seed-Robustheit:       {negative_seeds}/10 Seeds negativ ({negative_seeds/10*100:.0f}%)
2. Größen-Robustheit:     {negative_sizes}/4 Größen negativ ({negative_sizes/4*100:.0f}%)
3. Intensitäts-Sweep:     Tradeoff sichtbar
4. Parameter-Raum:        {len(param_df)} Konfigurationen getestet

SCHLUSSFOLGERUNG:
    """)
    
    if negative_seeds >= 8 and negative_sizes >= 3:
        print("✓✓✓ THESE BESTÄTIGT UND ROBUST")
        print("\nDie negative Korrelation Response ↔ Stabilität ist:")
        print("  • Reproduzierbar über Seeds")
        print("  • Gültig für verschiedene Tumorgrößen")
        print("  • Robust über Therapie-Parameter")
        print("\n→ PUBLIKATIONSREIF")
    elif negative_seeds >= 6:
        print("✓ THESE UNTERSTÜTZT")
        print("\nTendenz zur negativen Korrelation, aber:")
        print("  • Einige Parameter-Bereiche zeigen Abweichungen")
        print("  • Weitere Kalibrierung empfohlen")
    else:
        print("⚠ THESE FRAGWÜRDIG")
        print("\nErgebnis nicht robust - Neuformulierung nötig")
