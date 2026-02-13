import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

OUT_DIR = Path("07_outputs")
PLOT_DIR = OUT_DIR / "plots"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

MSI_PATH = OUT_DIR / "machining_severity_index.csv"
CRI_PATH = OUT_DIR / "coating_robustness_index.csv"

def main():
    msi = pd.read_csv(MSI_PATH)
    cri = pd.read_csv(CRI_PATH)

    # Basic checks
    if "MSI" not in msi.columns:
        raise ValueError(f"MSI column not found in {MSI_PATH}")
    if "CRI_final" not in cri.columns:
        raise ValueError(f"CRI_final column not found in {CRI_PATH}")
    if "Sample Num" not in cri.columns:
        raise ValueError("Sample Num not found in CRI file")

    # MSI scenarios from distribution
    msi_vals = msi["MSI"].dropna().astype(float).to_numpy()
    low, med, high = np.quantile(msi_vals, [0.25, 0.50, 0.75])

    scenarios = pd.DataFrame({
        "Scenario": ["Low (P25)", "Medium (P50)", "High (P75)"],
        "MSI_value": [low, med, high]
    })

    # Risk matrix: for each substrate, compute risk under each scenario
    base = cri[["Sample Num", "CRI_final", "Wear_Avg", "Adhesion_Avg"]].copy()
    base["CRI_final"] = base["CRI_final"].astype(float)

    risk_rows = []
    for _, sc in scenarios.iterrows():
        m = float(sc["MSI_value"])
        tmp = base.copy()
        tmp["Scenario"] = sc["Scenario"]
        tmp["MSI_value"] = m
        tmp["Risk"] = m / (tmp["CRI_final"] + 1e-12)
        risk_rows.append(tmp)

    risk_long = pd.concat(risk_rows, ignore_index=True)

    # Wide matrix for readability
    risk_wide = risk_long.pivot(index="Sample Num", columns="Scenario", values="Risk").reset_index()

    # Rank by worst-case risk (High scenario)
    risk_wide["WorstCaseRisk"] = risk_wide[["Low (P25)", "Medium (P50)", "High (P75)"]].max(axis=1)
    risk_wide = risk_wide.sort_values("WorstCaseRisk", ascending=True).reset_index(drop=True)
    risk_wide["Rank"] = np.arange(1, len(risk_wide) + 1)

    out_csv = OUT_DIR / "risk_matrix.csv"
    risk_wide.to_csv(out_csv, index=False)

    # Heatmap plot (matplotlib only)
    heat = risk_wide.set_index("Sample Num")[["Low (P25)", "Medium (P50)", "High (P75)"]]
    plt.figure(figsize=(8, max(4, 0.35 * len(heat))))
    plt.imshow(heat.values, aspect="auto")
    plt.yticks(range(len(heat.index)), heat.index)
    plt.xticks(range(heat.shape[1]), heat.columns, rotation=30, ha="right")
    plt.colorbar(label="Risk = MSI / CRI_final")
    plt.title("Risk Matrix (lower is better)")
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "risk_matrix_heatmap.png", dpi=200)
    plt.close()

    # Print top 5 safest by worst-case risk
    print("\n✅ Risk matrix generated.")
    print(f"Saved: {out_csv}")
    print(f"Plot: {PLOT_DIR / 'risk_matrix_heatmap.png'}")
    print("\nTop 5 safest substrates (lowest worst-case risk):")
    print(risk_wide[["Rank", "Sample Num", "Low (P25)", "Medium (P50)", "High (P75)", "WorstCaseRisk"]].head(5).to_string(index=False))

    print("\nMSI scenario values:")
    print(scenarios.to_string(index=False))

if __name__ == "__main__":
    main()
