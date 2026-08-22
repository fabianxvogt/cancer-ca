"""
Figure 1: Conceptual Framework
==============================

Schematic showing difference between:
A) Traditional view: Therapy as cell killer
B) Our view: Therapy as rule operator

This is a conceptual diagram, not a simulation.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: Traditional View
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 10)
ax1.axis('off')
ax1.set_title('A) Traditional Paradigm:\nTherapy as Environmental Perturbation', 
              fontsize=14, fontweight='bold', pad=20)

# Tumor (state) - larger, more prominent
tumor_box = FancyBboxPatch((0.8, 5.8), 3.4, 2.4, boxstyle="round,pad=0.15", 
                           edgecolor='darkred', facecolor='#FFB6C6', linewidth=4)
ax1.add_patch(tumor_box)
ax1.text(2.5, 7, 'Tumor\nState', ha='center', va='center', 
         fontsize=12, fontweight='bold', color='darkred')

# Therapy arrow (kills cells) - thicker, more visible
arrow1 = FancyArrowPatch((2.5, 5.3), (2.5, 3.8), 
                        arrowstyle='->,head_width=0.6,head_length=0.8', 
                        mutation_scale=30, linewidth=4, color='#0066CC')
ax1.add_patch(arrow1)
ax1.text(4.2, 4.5, 'Therapy\n(kills cells)', ha='left', va='center', 
         fontsize=11, color='#0066CC', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7, edgecolor='#0066CC', linewidth=2))

# Smaller tumor (reduced state)
small_tumor = FancyBboxPatch((1.3, 1.2), 2.4, 1.8, boxstyle="round,pad=0.15", 
                            edgecolor='darkred', facecolor='#FFB6C6', linewidth=4)
ax1.add_patch(small_tumor)
ax1.text(2.5, 2.1, 'Reduced\nTumor', ha='center', va='center', 
         fontsize=11, fontweight='bold', color='darkred')

# Key assumption box - more professional
assumption_box = FancyBboxPatch((5.2, 0.8), 4, 3, boxstyle="round,pad=0.15", 
                               edgecolor='#555555', facecolor='#F0F0F0', linewidth=3, linestyle='-')
ax1.add_patch(assumption_box)
ax1.text(7.2, 3.2, 'Assumptions:', ha='center', fontsize=11, fontweight='bold', color='#333333')
ax1.text(7.2, 2.6, '✓ Rules unchanged', ha='center', fontsize=10, color='#006400')
ax1.text(7.2, 2.1, '✓ Reversible', ha='center', fontsize=10, color='#006400')
ax1.text(7.2, 1.6, '✓ Smaller = Better', ha='center', fontsize=10, color='#006400')
ax1.text(7.2, 1.1, '(All FALSE!)', ha='center', fontsize=9, fontweight='bold', 
         color='red', style='italic')

# Panel B: Our View
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 10)
ax2.axis('off')
ax2.set_title('B) Evolutionary Paradigm:\nTherapy as Rule Operator', 
              fontsize=14, fontweight='bold', pad=20)

# Initial state
init_box = FancyBboxPatch((1, 7.5), 2.5, 1.5, boxstyle="round,pad=0.1", 
                         edgecolor='darkred', facecolor='lightcoral', linewidth=3)
ax2.add_patch(init_box)
ax2.text(2.25, 8.25, 'State₀', ha='center', va='center', fontsize=11, fontweight='bold')

# Rules box initial
rules_box1 = FancyBboxPatch((4.2, 7.5), 2.5, 1.5, boxstyle="round,pad=0.05", 
                           edgecolor='green', facecolor='lightgreen', linewidth=2)
ax2.add_patch(rules_box1)
ax2.text(5.45, 8.6, 'Rules₀:', ha='center', fontsize=9, fontweight='bold')
ax2.text(5.45, 8.2, 'μ = low', ha='center', fontsize=8)
ax2.text(5.45, 7.85, 'competition = high', ha='center', fontsize=8)

# Therapy arrow (modifies rules AND state)
therapy_arrow1 = FancyArrowPatch((2.25, 7), (2.25, 5.5), 
                                arrowstyle='->', mutation_scale=25, linewidth=3, color='red')
ax2.add_patch(therapy_arrow1)
therapy_arrow2 = FancyArrowPatch((5.45, 7), (5.45, 5.5), 
                                arrowstyle='->', mutation_scale=25, linewidth=3, color='red')
ax2.add_patch(therapy_arrow2)
ax2.text(7.5, 6.2, 'Therapy\n(rewrites rules)', ha='center', va='center', 
         fontsize=10, color='red', fontweight='bold')

# Final state (different)
final_box = FancyBboxPatch((1, 3.5), 2.5, 1.5, boxstyle="round,pad=0.1", 
                          edgecolor='purple', facecolor='plum', linewidth=3)
ax2.add_patch(final_box)
ax2.text(2.25, 4.25, 'State₁\n(resistant)', ha='center', va='center', fontsize=10, fontweight='bold')

# Rules box final (CHANGED)
rules_box2 = FancyBboxPatch((4.2, 3.5), 2.5, 1.5, boxstyle="round,pad=0.05", 
                           edgecolor='darkgreen', facecolor='yellow', linewidth=3, linestyle='--')
ax2.add_patch(rules_box2)
ax2.text(5.45, 4.6, 'Rules₁:', ha='center', fontsize=9, fontweight='bold', color='red')
ax2.text(5.45, 4.2, 'μ = HIGH', ha='center', fontsize=8, color='red')
ax2.text(5.45, 3.85, 'competition = LOW', ha='center', fontsize=8, color='red')

# Key insight box
insight_box = FancyBboxPatch((0.5, 0.3), 6.5, 2.2, boxstyle="round,pad=0.1", 
                            edgecolor='darkred', facecolor='mistyrose', linewidth=3)
ax2.add_patch(insight_box)
ax2.text(3.75, 2, 'Key Insight:', ha='center', fontsize=11, fontweight='bold', color='darkred')
ax2.text(3.75, 1.5, '• Therapy changes mutation rate μ(x,y,t)', ha='center', fontsize=9)
ax2.text(3.75, 1.1, '• Creates niches for resistant cells', ha='center', fontsize=9)
ax2.text(3.75, 0.7, '• IRREVERSIBLE regime shift', ha='center', fontsize=9, fontweight='bold')

# Add big annotation
ax2.text(9, 5, '≠', fontsize=80, ha='center', va='center', color='red', alpha=0.3)

plt.suptitle('Therapy as Rule Operator: Beyond State-Space Perturbation', 
             fontsize=16, fontweight='bold', y=0.98)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('images/figure1_concept.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Figure 1 saved: images/figure1_concept.png")
plt.close()
