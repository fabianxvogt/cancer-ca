# Committed manuscript figure assets

## Inventory status

The six main figures and three supplementary figures included by `paper.tex` are
committed in this folder. The committed `figure_S1_metric_dependence.py` source is
separate exploratory source: it is not rendered, has no committed result table, and
is not listed as a paper asset. The dual-metric roadmap item remains open.

## Figure Overview

| # | Filename | Purpose | Status |
|---|----------|---------|--------|
| 1 | `figure1_concept.png` | Conceptual framework (therapy as rule operator) | ✓ Ready |
| 2 | `figure2_main_result.png` | **MAIN RESULT**: response versus controllability-based stability | ✓ Ready |
| 3 | `figure3_temporal_dynamics.png` | MTD vs Metronomic temporal comparison | ✓ Ready |
| 4 | `figure4_spatial_evolution.png` | Spatial evolutionary regime shift visualization | ✓ Ready |
| 5 | `figure5_robustness.png` | Seed/size/intensity robustness | ✓ Ready |
| 6 | `figure6_parameter_space.png` | Global parameter space | ✓ Ready |

## Supplementary Figures

| # | Filename | Purpose | Status |
|---|----------|---------|--------|
| S2 | `figure_S2_parameter_sensitivity.png` | Metronomic-dose sensitivity | ✓ Included in `paper.tex` |
| S3 | `figure_S3_reversibility.png` | Partial-reversibility scenarios | ✓ Included in `paper.tex` |
| S4 | `figure_S4_grid_size.png` | Finite-size effects | ✓ Included in `paper.tex` |

## LaTeX Integration

The paper (`paper.tex`) has been updated with:
- Correct image paths (`images/figureX_...png`)
- Detailed captions for all figures
- Proper figure references in text

## Compile the draft with figures

```bash
# Run from the project root.
pdflatex paper.tex
pdflatex paper.tex  # Run twice for references
```

The PDF will automatically include the six main figures and the three
supplementary figures listed above.

## Figure Generation Scripts

Each figure has its own standalone Python script:

```bash
# Regenerate individual figures:
python figure1_concept.py
python figure2_main_result.py
python figure3_temporal_dynamics.py
python figure4_spatial_evolution.py
python figure5_robustness.py
python figure6_parameter_space.py
```

## Scope note

This file records committed assets and manuscript inclusion status only. Reported
scientific values remain in `README.md` and `paper.tex`; the current owner review
does not promote the exploratory dual-metric source to a figure.

## What Changed from Original Images:

**OLD (combined images):**
- `response_vs_stability.png` - Too dense, 6 panels crammed together
- `robustness_analysis.png` - 6 panels, hard to read
- `detailed_trajectories.png` - Missing

**NEW (focused images):**
1. ✓ Conceptual schematic (new, didn't exist before)
2. ✓ Main result only (2 panels, clean)
3. ✓ Temporal dynamics only (3×2 grid, focused)
4. ✓ Spatial evolution only (7 snapshots, clear story)
5. ✓ Robustness only (3 panels, robustness summary)
6. ✓ Parameter space only (4 panels, global view)

## File Sizes:

Total: ~2 MB (well within journal limits)
- Each figure: 200-500 KB
- All vector-ready, publication quality

## Next steps

1. **View the figures** - Check if they look good visually
2. **Compile paper.tex** - See integrated PDF
3. **Adjust captions** - Fine-tune descriptions if needed
4. Review publication venue and any future figure changes against `ROADMAP.md`

---

**Inventory reconciled:** 2026-08-25
**Project status:** manuscript draft; publication venue remains open in `ROADMAP.md`
