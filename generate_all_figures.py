"""
Master Script: Generate All Publication Figures
================================================

Runs all figure generation scripts in sequence.

Usage:
    python generate_all_figures.py
"""

import subprocess
import time

figures = [
    ('figure1_concept.py', 'Conceptual Framework'),
    ('figure2_main_result.py', 'Main Result'),
    ('figure3_temporal_dynamics.py', 'Temporal Dynamics'),
    ('figure4_spatial_evolution.py', 'Spatial Evolution'),
    ('figure5_robustness.py', 'Robustness Analysis'),
    ('figure6_parameter_space.py', 'Parameter Space'),
]

print("="*70)
print("GENERATING ALL PUBLICATION FIGURES")
print("="*70)
print(f"\nTotal: {len(figures)} figures\n")

start_time = time.time()

for idx, (script, description) in enumerate(figures, 1):
    print(f"\n{'='*70}")
    print(f"FIGURE {idx}/{len(figures)}: {description}")
    print(f"Script: {script}")
    print(f"{'='*70}\n")
    
    fig_start = time.time()
    
    try:
        result = subprocess.run(['python', script], 
                              capture_output=False, 
                              text=True, 
                              check=True)
        fig_time = time.time() - fig_start
        print(f"\n✓ Figure {idx} complete ({fig_time:.1f}s)")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Figure {idx} FAILED!")
        print(f"Error: {e}")
        break

total_time = time.time() - start_time

print("\n" + "="*70)
print("ALL FIGURES GENERATED!")
print("="*70)
print(f"\nTotal time: {total_time:.1f}s")
print(f"\nFigures saved in: images/")
print("\nGenerated files:")
print("  - figure1_concept.png")
print("  - figure2_main_result.png")
print("  - figure3_temporal_dynamics.png")
print("  - figure4_spatial_evolution.png")
print("  - figure5_robustness.png")
print("  - figure6_parameter_space.png")
print("\nYou can now:")
print("  1. Screenshot these figures")
print("  2. Place them in images/ folder")
print("  3. Compile paper.tex to PDF")
print("\nDone!")
