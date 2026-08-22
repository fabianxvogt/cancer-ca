"""
Intervention Stability Metrics
==============================

ZENTRALE THESE:
In irreduziblen evolutionären Systemen ist jede Therapie, die auf 
terminale Zustände (Heilung, Eliminierung) abzielt, strukturell instabil.

Die richtige Zielgröße ist nicht Response, sondern Interventionsstabilität.

Definitionen:
-------------
1. Regime Stability: Zeit bis qualitiativer Phasenübergang
2. Structural Entropy: Zunahme der Unordnung im System
3. Reversibility Loss: Verlust kontrollierbarer Zustände
4. Control Horizon: Zeitfenster effektiver Intervention
"""

import numpy as np
from scipy.stats import entropy
from collections import deque


class StabilityMetrics:
    """
    Messung von Interventionsstabilität statt Response
    """
    
    @staticmethod
    def detect_regime_change(history, window=20, threshold=0.3):
        """
        Erkenne qualitative Phasenübergänge
        
        Ein Regime-Change ist definiert als:
        - Plötzliche Änderung der Wachstumsrate
        - Qualitative Änderung der Populationsdynamik
        - Übergang zu dominanter Resistenz
        
        Returns
        -------
        regime_changes : list of int
            Zeitpunkte der Regime-Changes
        stability_duration : int
            Zeit bis zum ersten kritischen Übergang
        """
        total_tumor = np.array(history['sensitive']) + np.array(history['resistant'])
        
        if len(total_tumor) < window * 2:
            return [], len(total_tumor)
        
        regime_changes = []
        
        # Gleitende Wachstumsrate
        growth_rates = []
        for i in range(window, len(total_tumor)):
            before = np.mean(total_tumor[i-window:i])
            after = total_tumor[i]
            if before > 0:
                rate = (after - before) / before
                growth_rates.append(rate)
            else:
                growth_rates.append(0)
        
        # Erkenne sprunghafte Änderungen
        for i in range(1, len(growth_rates)):
            if abs(growth_rates[i] - growth_rates[i-1]) > threshold:
                regime_changes.append(i + window)
        
        # Resistenz-Dominanz (kritischer Übergang)
        resistant_fraction = np.array(history['resistant']) / (total_tumor + 1)
        for i in range(len(resistant_fraction)):
            if resistant_fraction[i] > 0.7:  # >70% resistent
                if i not in regime_changes:
                    regime_changes.append(i)
                break
        
        # Erste kritische Änderung = Ende der Stabilität
        stability_duration = regime_changes[0] if regime_changes else len(total_tumor)
        
        return regime_changes, stability_duration
    
    @staticmethod
    def structural_entropy_trajectory(history):
        """
        Miss Zunahme der strukturellen Unordnung
        
        Niedrige Entropie = System vorhersagbar/kontrollierbar
        Hohe Entropie = System chaotisch/unkontrollierbar
        
        Returns
        -------
        entropy_increase : float
            Rate der Entropie-Zunahme (instabil wenn > 0)
        final_entropy : float
            Finale Entropie
        """
        entropies = np.array(history['entropy'])
        
        if len(entropies) < 10:
            return 0, entropies[-1] if len(entropies) > 0 else 0
        
        # Linearer Fit über zweite Hälfte (post-Intervention)
        mid = len(entropies) // 2
        t = np.arange(len(entropies[mid:]))
        if len(t) > 5:
            coeffs = np.polyfit(t, entropies[mid:], 1)
            entropy_increase = coeffs[0]  # Steigung
        else:
            entropy_increase = 0
        
        return entropy_increase, entropies[-1]
    
    @staticmethod
    def reversibility_loss(history, therapy_start, therapy_end):
        """
        Miss Verlust reversibler Zustände
        
        Ein System ist reversibel, wenn:
        - Nach Therapiestopp Rückkehr zu vorherigem Regime möglich
        - Keine permanente qualitative Änderung
        
        Irreversibilität = Stabilitätsverlust
        
        Returns
        -------
        reversibility_score : float
            0 = vollständig irreversibel
            1 = vollständig reversibel
        """
        if therapy_end >= len(history['sensitive']):
            return 0.5  # Noch keine Daten
        
        # Pre-Therapie Zustand
        pre_sensitive = history['sensitive'][therapy_start-10:therapy_start]
        pre_resistant = history['resistant'][therapy_start-10:therapy_start]
        pre_ratio = np.mean(pre_resistant) / (np.mean(pre_sensitive) + np.mean(pre_resistant) + 1)
        
        # Post-Therapie Zustand (nach Erholung)
        recovery_window = min(30, len(history['sensitive']) - therapy_end)
        if recovery_window < 5:
            return 0.5
        
        post_sensitive = history['sensitive'][therapy_end:therapy_end+recovery_window]
        post_resistant = history['resistant'][therapy_end:therapy_end+recovery_window]
        post_ratio = np.mean(post_resistant) / (np.mean(post_sensitive) + np.mean(post_resistant) + 1)
        
        # Reversibilität: Wie ähnlich ist post zu pre?
        ratio_change = abs(post_ratio - pre_ratio)
        reversibility_score = 1 / (1 + ratio_change * 10)  # Normalisiert
        
        return reversibility_score
    
    @staticmethod
    def control_horizon(history, intervention_start, control_threshold=0.2):
        """
        Miss wie lange Intervention effektiv kontrolliert
        
        Control Horizon = Zeit, in der Intervention messbare Wirkung hat
        
        Kurzer Horizont = instabile Kontrolle
        Langer Horizont = stabile Kontrolle
        
        Returns
        -------
        horizon : int
            Anzahl Schritte effektiver Kontrolle
        """
        total_tumor = np.array(history['sensitive']) + np.array(history['resistant'])
        
        if intervention_start >= len(total_tumor):
            return 0
        
        baseline = total_tumor[intervention_start]
        
        # Finde Zeitpunkt, wo Tumorgröße wieder >80% Baseline
        for t in range(intervention_start + 1, len(total_tumor)):
            if total_tumor[t] > baseline * 0.8:
                return t - intervention_start
        
        return len(total_tumor) - intervention_start
    
    @staticmethod
    def compute_all_metrics(history, therapy_start=100, therapy_end=150):
        """
        Berechne alle Stabilitätsmetriken
        
        Returns
        -------
        metrics : dict
            Alle Stabilitätsmetriken
        """
        regime_changes, stability_duration = StabilityMetrics.detect_regime_change(history)
        entropy_rate, final_entropy = StabilityMetrics.structural_entropy_trajectory(history)
        reversibility = StabilityMetrics.reversibility_loss(history, therapy_start, therapy_end)
        horizon = StabilityMetrics.control_horizon(history, therapy_start)
        
        return {
            'regime_changes': regime_changes,
            'stability_duration': stability_duration,
            'entropy_increase_rate': entropy_rate,
            'final_entropy': final_entropy,
            'reversibility_score': reversibility,
            'control_horizon': horizon,
            # Composite Stability Score
            'stability_score': (
                (stability_duration / len(history['sensitive'])) * 0.3 +
                (1 / (1 + abs(entropy_rate))) * 0.2 +
                reversibility * 0.3 +
                (horizon / 100) * 0.2
            )
        }


class ResponseVsStability:
    """
    Zentrale Analyse: Response ≠ Stabilität
    
    Zeige, dass Therapien mit gleicher Tumorreduktion
    dramatisch unterschiedliche Stabilität haben können.
    """
    
    @staticmethod
    def measure_response(history, therapy_start, therapy_end):
        """
        Miss traditionelle Response-Metriken
        
        Returns
        -------
        max_reduction : float
            Maximale Tumorreduktion (%)
        final_tumor_burden : int
            Finale Tumorgröße
        """
        total_tumor = np.array(history['sensitive']) + np.array(history['resistant'])
        
        baseline = total_tumor[therapy_start]
        nadir = np.min(total_tumor[therapy_start:therapy_end+20])
        final = total_tumor[-1]
        
        max_reduction = (baseline - nadir) / (baseline + 1) * 100
        
        return {
            'max_reduction': max_reduction,
            'final_tumor_burden': final,
            'nadir': nadir
        }
    
    @staticmethod
    def response_stability_tradeoff(ca_results):
        """
        Analysiere Tradeoff zwischen Response und Stabilität
        
        Parameters
        ----------
        ca_results : list of dict
            Ergebnisse verschiedener Therapiestrategien
            Jedes dict: {'name', 'history', 'therapy_start', 'therapy_end'}
        
        Returns
        -------
        analysis : pd.DataFrame
            Vergleich Response vs. Stabilität
        """
        import pandas as pd
        
        results = []
        
        for result in ca_results:
            response = ResponseVsStability.measure_response(
                result['history'],
                result['therapy_start'],
                result['therapy_end']
            )
            
            stability = StabilityMetrics.compute_all_metrics(
                result['history'],
                result['therapy_start'],
                result['therapy_end']
            )
            
            results.append({
                'Strategy': result['name'],
                'Max Reduction (%)': response['max_reduction'],
                'Final Tumor': response['final_tumor_burden'],
                'Stability Score': stability['stability_score'],
                'Control Horizon': stability['control_horizon'],
                'Reversibility': stability['reversibility_score'],
                'Entropy Rate': stability['entropy_increase_rate']
            })
        
        return pd.DataFrame(results)


def visualize_stability_vs_response(df, save_path=None):
    """
    Visualisiere das zentrale Argument
    
    Zeige: Maximale Response → Minimale Stabilität
    """
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Response vs. Stability
    ax1 = axes[0, 0]
    ax1.scatter(df['Max Reduction (%)'], df['Stability Score'], 
                s=200, alpha=0.7, c=df.index, cmap='viridis')
    for i, row in df.iterrows():
        ax1.annotate(row['Strategy'], 
                    (row['Max Reduction (%)'], row['Stability Score']),
                    fontsize=9, ha='center')
    ax1.set_xlabel('Maximale Tumorreduktion (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Stabilitätsscore', fontsize=12, fontweight='bold')
    ax1.set_title('KERNBEFUND: Response ≠ Stabilität', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=df['Stability Score'].mean(), color='r', linestyle='--', 
                label='Mittlere Stabilität', alpha=0.5)
    ax1.legend()
    
    # 2. Control Horizon
    ax2 = axes[0, 1]
    bars = ax2.barh(df['Strategy'], df['Control Horizon'], color='steelblue', alpha=0.7)
    ax2.set_xlabel('Control Horizon (Zeitschritte)', fontsize=12)
    ax2.set_title('Dauer effektiver Kontrolle', fontsize=12, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # 3. Reversibilität
    ax3 = axes[1, 0]
    colors = ['red' if x < 0.5 else 'green' for x in df['Reversibility']]
    ax3.barh(df['Strategy'], df['Reversibility'], color=colors, alpha=0.7)
    ax3.set_xlabel('Reversibilität (0=irreversibel, 1=reversibel)', fontsize=12)
    ax3.set_title('Verlust reversibler Zustände', fontsize=12, fontweight='bold')
    ax3.axvline(x=0.5, color='black', linestyle='--', alpha=0.5)
    ax3.grid(axis='x', alpha=0.3)
    
    # 4. Finale Tumorgröße vs. Stabilität
    ax4 = axes[1, 1]
    ax4.scatter(df['Final Tumor'], df['Stability Score'],
                s=200, alpha=0.7, c=df.index, cmap='viridis')
    for i, row in df.iterrows():
        ax4.annotate(row['Strategy'], 
                    (row['Final Tumor'], row['Stability Score']),
                    fontsize=9, ha='center')
    ax4.set_xlabel('Finale Tumorgröße', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Stabilitätsscore', fontsize=12, fontweight='bold')
    ax4.set_title('Größe ist nicht Kontrolle', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle(
        'INTERVENTION STABILITY > RESPONSE\n' +
        'Heilung als Zielgröße ist systemisch falsch',
        fontsize=16, fontweight='bold'
    )
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.show()


if __name__ == "__main__":
    print("="*70)
    print("STABILITY METRICS MODULE")
    print("="*70)
    print("""
Dieses Modul implementiert die zentrale These:

    "In irreduziblen evolutionären Systemen ist jede Therapie,
     die auf terminale Zustände abzielt, strukturell instabil."

Metriken:
---------
1. Regime Stability     → Zeit bis Phasenübergang
2. Structural Entropy   → Zunahme der Unordnung
3. Reversibility Loss   → Verlust kontrollierbarer Zustände
4. Control Horizon      → Dauer effektiver Intervention

➡️ Die richtige Zielgröße ist STABILITÄT, nicht RESPONSE.
    """)
