# Coating Performance Decision-Support Tool

Python-based decision-support framework linking:

- Experimental coating metrics (wear + adhesion)
- Real machining force signals (ORNL dataset)

to produce severity-dependent coating risk ranking.

## Pipeline
1. CRI (Coating Robustness Index)
2. MSI (Machining Severity Index)
3. Risk Matrix (MSI / CRI)

Outputs:
- coating_robustness_index.csv
- machining_severity_index.csv
- risk_matrix.csv
- heatmap plots

This is a severity-normalized comparative coating performance model.
