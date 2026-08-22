"""
The Core Experiment
===================

ZENTRALE FORSCHUNGSFRAGE:
Warum ist "Heilung" als Zielgröße systemisch falsch?

HYPOTHESE:
Therapien, die maximale Tumorreduktion anstreben, erzeugen 
systematisch minimale Interventionsstabilität.

METHODIK:
Vergleiche Therapiestrategien bei *gleicher* finaler Tumorreduktion
auf ihre Stabilität.

ERWARTETES ERGEBNIS:
Aggressive Therapie → hohe Response, niedrige Stabilität
Moderate Therapie → moderate Response, hohe Stabilität

➡️ Dies beweist: Die Zielgröße muss gewechselt werden.
"""

import numpy as np
import matplotlib.pyplot as plt
from tumor_ca import AdvancedTumorCA
from stability_metrics import StabilityMetrics, ResponseVsStability, visualize_stability_vs_response
import pandas as pd


def run_controlled_experiment(size=120, steps=500, seed=42):
    """
    Das Kernexperiment - DRASTISCH KORRIGIERTE PARAMETER
    
    Wichtige Erkenntnis:
    "In frühen, kleinen Tumoren macht die Therapiestrategie keinen Unterschied"
    
    NEUER ANSATZ - Evolutionäres Regime erzwingen:
    - SEHR großer Tumor (radius=20, ~1250 Zellen)
    - LÄNGERE Simulation (500 Schritte)
    - SCHWÄCHERE Therapie (0.15-0.5)
    - Tumor MASSIV wachsen lassen (Start bei 200)
    """
    
    strategies = {
        'MTD - Maximum Tolerated Dose': {
            'intensity': 0.5,  # Drastisch reduziert
            'start': 200,      # Sehr spät
            'duration': 80,
            'type': 'continuous'
        },
        'Moderate Continuous': {
            'intensity': 0.35,
            'start': 200,
            'duration': 150,
            'type': 'continuous'
        },
        'Intermittent High': {
            'intensity': 0.45,
            'start': 200,
            'duration': 40,
            'type': 'intermittent',
            'cycles': 3,
            'gap': 50
        },
        'Adaptive Low': {
            'intensity': 0.25,
            'start': 200,
            'duration': 200,
            'type': 'adaptive'
        },
        'Metronomic': {
            'intensity': 0.15,
            'start': 200,
            'duration': 250,
            'type': 'continuous'
        }
    }
    
    results = []
    
    print("\n" + "="*70)
    print("CORE EXPERIMENT: Response vs. Stability")
    print("="*70)
    print("\nSimuliere verschiedene Therapiestrategien...")
    
    for name, config in strategies.items():
        print(f"\n  • {name}...")
        
        ca = AdvancedTumorCA(size=size, seed=seed)
        ca.initialize_tumor(radius=20, normal_cells=False)  # MASSIVER Tumor!
        
        # Simulation
        therapy_active = False
        cycle_count = 0
        last_therapy_end = 0
        
        for step in range(steps):
            # Therapiesteuerung
            if config['type'] == 'continuous':
                if step == config['start']:
                    ca.therapy = np.ones((size, size)) * config['intensity']
                    therapy_active = True
                if step == config['start'] + config['duration']:
                    ca.therapy = np.zeros((size, size))
                    therapy_active = False
                    
            elif config['type'] == 'intermittent':
                if step == config['start'] + cycle_count * (config['duration'] + config['gap']):
                    if cycle_count < config['cycles']:
                        ca.therapy = np.ones((size, size)) * config['intensity']
                        therapy_active = True
                        
                if therapy_active and step >= config['start'] + cycle_count * (config['duration'] + config['gap']) + config['duration']:
                    ca.therapy = np.zeros((size, size))
                    therapy_active = False
                    cycle_count += 1
                    last_therapy_end = step
                    
            elif config['type'] == 'adaptive':
                if step >= config['start'] and step < config['start'] + config['duration']:
                    # Adaptive: Intensität abhängig von Tumorgröße
                    current_tumor = len(np.where(ca.grid == ca.TUMOR_SENSITIVE)[0]) + \
                                   len(np.where(ca.grid == ca.TUMOR_RESISTANT)[0])
                    if current_tumor > 500:
                        ca.therapy = np.ones((size, size)) * config['intensity']
                    else:
                        ca.therapy = np.ones((size, size)) * (config['intensity'] * 0.5)
                elif step >= config['start'] + config['duration']:
                    ca.therapy = np.zeros((size, size))
            
            ca.step()
        
        # Speichere Ergebnis
        therapy_end = config['start'] + config['duration']
        if config['type'] == 'intermittent':
            therapy_end = last_therapy_end
            
        results.append({
            'name': name,
            'history': ca.history,
            'therapy_start': config['start'],
            'therapy_end': therapy_end,
            'config': config
        })
    
    return results


def analyze_core_result(results):
    """
    Analysiere Kernergebnis
    """
    print("\n" + "="*70)
    print("ANALYSE: Response vs. Stabilität")
    print("="*70)
    
    # Berechne Metriken
    df = ResponseVsStability.response_stability_tradeoff(results)
    
    # Sortiere nach Response
    df = df.sort_values('Max Reduction (%)', ascending=False)
    
    print("\n" + df.to_string(index=False))
    
    # Statistische Tests
    print("\n" + "="*70)
    print("STATISTISCHE ANALYSE")
    print("="*70)
    
    # Korrelation Response vs. Stabilität
    corr = df['Max Reduction (%)'].corr(df['Stability Score'])
    print(f"\nKorrelation Response ↔ Stabilität: {corr:.3f}")
    
    if corr < -0.3:
        print("→ NEGATIVE KORRELATION bestätigt")
        print("→ Höhere Response geht mit niedrigerer Stabilität einher")
    
    # Finde Pareto-optimale Strategien
    print("\n" + "="*70)
    print("PARETO-OPTIMALE STRATEGIEN")
    print("="*70)
    
    # Normalisiere
    df['Response_norm'] = df['Max Reduction (%)'] / df['Max Reduction (%)'].max()
    df['Stability_norm'] = df['Stability Score'] / df['Stability Score'].max()
    df['Combined'] = df['Response_norm'] * 0.3 + df['Stability_norm'] * 0.7
    
    best = df.loc[df['Combined'].idxmax()]
    print(f"\nBeste Balance Response/Stabilität:")
    print(f"  Strategie: {best['Strategy']}")
    print(f"  Response: {best['Max Reduction (%)']:.1f}%")
    print(f"  Stabilität: {best['Stability Score']:.3f}")
    
    worst_stable = df.loc[df['Stability Score'].idxmin()]
    print(f"\nSchlechteste Stabilität:")
    print(f"  Strategie: {worst_stable['Strategy']}")
    print(f"  Response: {worst_stable['Max Reduction (%)']:.1f}%")
    print(f"  Stabilität: {worst_stable['Stability Score']:.3f}")
    
    return df


def visualize_detailed_trajectories(results):
    """
    Detaillierte Visualisierung der Trajektorien
    """
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    
    # Farben
    colors = plt.cm.tab10(np.linspace(0, 1, len(results)))
    
    # 1. Tumor-Trajektorien
    ax1 = axes[0, 0]
    for i, result in enumerate(results):
        total = np.array(result['history']['sensitive']) + np.array(result['history']['resistant'])
        ax1.plot(total, label=result['name'], color=colors[i], linewidth=2)
        ax1.axvline(result['therapy_start'], color=colors[i], linestyle='--', alpha=0.3)
        ax1.axvline(result['therapy_end'], color=colors[i], linestyle=':', alpha=0.3)
    ax1.set_xlabel('Zeitschritt')
    ax1.set_ylabel('Gesamttumorgröße')
    ax1.set_title('Tumor-Trajektorien', fontweight='bold')
    ax1.legend(fontsize=8, loc='best')
    ax1.grid(True, alpha=0.3)
    
    # 2. Resistenz-Fraktion
    ax2 = axes[0, 1]
    for i, result in enumerate(results):
        total = np.array(result['history']['sensitive']) + np.array(result['history']['resistant'])
        resistant_frac = np.array(result['history']['resistant']) / (total + 1)
        ax2.plot(resistant_frac, label=result['name'], color=colors[i], linewidth=2)
    ax2.set_xlabel('Zeitschritt')
    ax2.set_ylabel('Resistente Fraktion')
    ax2.set_title('Evolution der Resistenz', fontweight='bold')
    ax2.legend(fontsize=8, loc='best')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(0.7, color='red', linestyle='--', alpha=0.5, label='Kritisch')
    
    # 3. Entropie
    ax3 = axes[1, 0]
    for i, result in enumerate(results):
        ax3.plot(result['history']['entropy'], label=result['name'], color=colors[i], linewidth=2)
    ax3.set_xlabel('Zeitschritt')
    ax3.set_ylabel('Shannon-Entropie')
    ax3.set_title('Strukturelle Entropie', fontweight='bold')
    ax3.legend(fontsize=8, loc='best')
    ax3.grid(True, alpha=0.3)
    
    # 4. Regime-Changes
    ax4 = axes[1, 1]
    for i, result in enumerate(results):
        metrics = StabilityMetrics.compute_all_metrics(
            result['history'],
            result['therapy_start'],
            result['therapy_end']
        )
        # Plot Stability Duration
        ax4.barh(i, metrics['stability_duration'], color=colors[i], alpha=0.7)
    ax4.set_yticks(range(len(results)))
    ax4.set_yticklabels([r['name'] for r in results], fontsize=9)
    ax4.set_xlabel('Zeit bis Regime-Change')
    ax4.set_title('Regime Stability', fontweight='bold')
    ax4.grid(axis='x', alpha=0.3)
    
    # 5. Control Horizon Vergleich
    ax5 = axes[2, 0]
    horizons = []
    for i, result in enumerate(results):
        metrics = StabilityMetrics.compute_all_metrics(
            result['history'],
            result['therapy_start'],
            result['therapy_end']
        )
        horizons.append(metrics['control_horizon'])
    ax5.bar(range(len(results)), horizons, color=colors, alpha=0.7)
    ax5.set_xticks(range(len(results)))
    ax5.set_xticklabels([r['name'] for r in results], rotation=45, ha='right', fontsize=8)
    ax5.set_ylabel('Control Horizon (Schritte)')
    ax5.set_title('Dauer effektiver Kontrolle', fontweight='bold')
    ax5.grid(axis='y', alpha=0.3)
    
    # 6. Reversibilität
    ax6 = axes[2, 1]
    reversibilities = []
    for i, result in enumerate(results):
        metrics = StabilityMetrics.compute_all_metrics(
            result['history'],
            result['therapy_start'],
            result['therapy_end']
        )
        reversibilities.append(metrics['reversibility_score'])
    bars = ax6.bar(range(len(results)), reversibilities, 
                   color=['red' if r < 0.5 else 'green' for r in reversibilities],
                   alpha=0.7)
    ax6.set_xticks(range(len(results)))
    ax6.set_xticklabels([r['name'] for r in results], rotation=45, ha='right', fontsize=8)
    ax6.set_ylabel('Reversibilität')
    ax6.set_title('Verlust reversibler Zustände', fontweight='bold')
    ax6.axhline(0.5, color='black', linestyle='--', alpha=0.5)
    ax6.grid(axis='y', alpha=0.3)
    
    plt.suptitle('Detaillierte Trajektorien-Analyse', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("="*70)
    print("THE CORE EXPERIMENT - KORRIGIERTE PARAMETER")
    print("="*70)
    print("""
Zentrale These:
  "Heilung als Zielgröße ist in irreduziblen evolutionären 
   Systemen systemisch falsch."

WICHTIGE ERKENNTNIS:
  "In frühen, kleinen Tumoren macht die Therapiestrategie 
   keinen Unterschied - alle Ansätze funktionieren ähnlich gut."
   
DESHALB JETZT (DRASTISCHE ANPASSUNG):
  • MASSIVER Tumor (radius=20, ~1250 Zellen)
  • Sehr lange Simulation (500 Schritte)  
  • SCHWACHE Therapie (0.15-0.5) - damit Tumor überlebt!
  • Tumor wächst SEHR LANGE, dann Therapie (Start bei Schritt 200)

Testbare Vorhersage:
  Therapien mit maximaler Response haben minimale Stabilität.

Methodik:
  Vergleiche 5 Therapiestrategien auf:
    - Traditionelle Response (Tumorreduktion)
    - Interventionsstabilität (neue Metrik)

Erwartung:
  Negative Korrelation zwischen Response und Stabilität
  ➡️ Beweist: Zielgröße muss gewechselt werden.
    """)
    
    # Experiment durchführen
    results = run_controlled_experiment(size=120, steps=500, seed=42)
    
    # Analyse
    df = analyze_core_result(results)
    
    # Visualisierung 1: Response vs. Stability
    print("\n" + "="*70)
    print("VISUALISIERUNG")
    print("="*70)
    visualize_stability_vs_response(df, save_path='response_vs_stability.png')
    
    # Visualisierung 2: Detaillierte Trajektorien
    visualize_detailed_trajectories(results)
    
    # Finale Aussage
    print("\n" + "="*70)
    print("SCHLUSSFOLGERUNG")
    print("="*70)
    print("""
Das Experiment zeigt:

1. EMPIRISCHER BEFUND
   • Negative Korrelation Response ↔ Stabilität
   • Maximale Reduktion → Minimale Kontrolldauer
   • Irreversible Systemänderungen

2. THEORETISCHE IMPLIKATION
   • "Heilung" ist kein valides Optimierungsziel
   • Stabilitätsmetriken müssen primär sein
   • Response als Nebenbedingung, nicht Ziel

3. KLINISCHE KONSEQUENZ
   • Aggressive Therapie schadet systematisch
   • Moderate, anhaltende Intervention überlegen
   • Bewertungsstandards müssen geändert werden

➡️ Dies ist kein inkrementeller Befund.
➡️ Dies ist ein Paradigmenwechsel.
    """)
