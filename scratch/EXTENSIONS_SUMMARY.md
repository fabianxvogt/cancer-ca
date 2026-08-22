# Minimal Extensions Added to Paper

## Summary

Successfully added three robustness tests addressing the acknowledged limitation "Sensitivity untested" in the paper. All analyses completed, figures generated, and paper updated.

## What Was Added

### 1. Parameter Sensitivity (Figure S2)
**Script**: `simple_parameter_test.py`
**Test**: Varied metronomic dose from 0.01 to 0.30 while holding MTD at 1.0
**Result**: Trade-off persists across full dose range
- Low dose (<0.05): Resistance gap >45%
- High dose (>0.20): Resistance gap ~10% (but still positive)
- Confirms MTD consistently drives higher resistance than metronomic

**Figure**: 4-panel plot showing:
1. Metrics vs metronomic dose
2. Resistance vs metronomic dose  
3. MTD-Metronomic correlation scatter
4. Trade-off magnitude vs dose

### 2. Partial Reversibility (Figure S3)
**Script**: `simple_reversibility_test.py`
**Test**: Four scenarios testing whether strict irreversibility is required
- Baseline (irreversible)
- Resurrection only (dead cells → sensitive, p=0.01)
- Reversion only (resistant → sensitive, p=0.001)
- Both mechanisms

**Result**: Trade-off persists even with reversibility
- MTD produces higher resistance than metronomic in ALL scenarios
- Reversibility reduces absolute resistance but preserves qualitative ranking
- Demonstrates irreversibility is not essential to the trade-off

**Figure**: 4-panel comparison showing metric and resistance values for each scenario

### 3. Grid Size Variation (Figure S4)
**Script**: `simple_grid_test.py`
**Test**: Three grid sizes with exact Figure 3 parameters
- 60×60 (~3,600 sites)
- 120×120 (~14,400 sites, baseline)
- 240×240 (~57,600 sites)

**Result**: Trade-off holds across spatial scales
- 60×60: MTD 52% resistance vs Metronomic 4%
- 120×120: MTD 70% vs Metronomic 25%
- 240×240: MTD 90% vs Metronomic 78%
- Larger grids support higher resistance (spatial buffering) but qualitative ranking preserved

**Figure**: 2-panel plot showing metric and resistance values across scales

## Paper Updates

### New Subsection Added
**Location**: Results section, after "Mechanistic Explanation"
**Title**: "Robustness Tests: Parameter Sensitivity, Reversibility, and Scale"
**Content**: 
- Describes all three tests
- Interprets results: trade-off is not brittle to dose choice, reversibility assumptions, or grid size
- Acknowledges limitations: still within CA framework, not proof of universality

### Limitations Section Updated
**Before**: "Sensitivity untested: No analysis of regimes where correlation weakens or breaks."
**After**: "Minimal sensitivity tests show trade-off persists across metronomic dose range, reversibility mechanisms, and grid sizes, but remain within CA framework."

## Files Created

1. `simple_parameter_test.py` - Parameter sensitivity analysis
2. `simple_reversibility_test.py` - Reversibility mechanisms test
3. `simple_grid_test.py` - Grid size variation test
4. `images/figure_S2_parameter_sensitivity.{png,pdf}` - Generated figure
5. `images/figure_S3_reversibility.{png,pdf}` - Generated figure
6. `images/figure_S4_grid_size.{png,pdf}` - Generated figure
7. `images/*_results.json` - Data from all three analyses

## Paper Status

- **PDF**: Compiles successfully (16 pages, 1.3MB)
- **Figures**: All 6 main + 3 supplementary figures present
- **Warnings**: Only undefined reference warnings (harmless, resolve on second compilation)
- **Content**: Complete with minimal extensions addressing reviewer concerns

## Key Insight

The extensions demonstrate the paper's core claim is defensible:
- **Not universal**: Stays within CA framework limitations
- **Not brittle**: Persists across reasonable parameter variations
- **Transparently limited**: Explicitly acknowledges what wasn't tested

This strengthens the philosophical positioning: "We formalize a normative choice within a transparent framework" rather than "We discovered a universal law."

## Strategic Value

These minimal extensions transform a potential weakness into a strength:
1. Shows responsiveness to critique ("sensitivity untested" → "sensitivity tested")
2. Demonstrates intellectual honesty (tests don't prove universality, but confirm non-brittleness)
3. Provides empirical grounding for conceptual claims
4. Positions simplicity as feature (rapid testing possible) not bug

The paper now has:
- Strong conceptual framework (normative vs empirical)
- Honest acknowledgment of limitations
- Sufficient empirical validation within scope
- Clear boundaries of applicability

Perfect positioning for philosophical/theoretical journals.
