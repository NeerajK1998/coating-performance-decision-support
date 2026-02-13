import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

FILE_PATH = "/Users/neerajkulkarni/Documents/Personal/Thesis R/Complete Analysis .xlsx"
WEAR_SHEET = "Wear Rate"
ADH_SHEET  = "Adhesion"

OUT_DIR = Path("07_outputs")
PLOT_DIR = OUT_DIR / "plots"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

W_WEAR = 0.6
W_ADH  = 0.4
ADH_GATE_THRESH = 0.30

def minmax01(series: pd.Series) -> pd.Series:
    s = series.astype(float)
    denom = (s.max() - s.min())
    if denom == 0:
        return pd.Series(np.ones(len(s)), index=s.index)
    return (s - s.min()) / denom

def main():
    wear = pd.read_excel(FILE_PATH, sheet_name=WEAR_SHEET)
    adh  = pd.read_excel(FILE_PATH, sheet_name=ADH_SHEET)

    wear_cols = [c for c in wear.columns if isinstance(c, str) and c.strip().startswith("M")]
    if not wear_cols:
        raise ValueError(f"No wear measurement columns found. Columns: {list(wear.columns)}")

    wear = wear.rename(columns={wear.columns[0]: "Sample Num"})
    wear["Sample Num"] = wear["Sample Num"].astype(str).str.strip()
    wear["Wear_Avg"] = wear[wear_cols].apply(pd.to_numeric, errors="coerce").mean(axis=1)
    wear_small = wear[["Sample Num", "Wear_Avg"]].dropna()

    if "Sample Num" not in adh.columns:
        adh = adh.rename(columns={adh.columns[0]: "Sample Num"})
    adh["Sample Num"] = adh["Sample Num"].astype(str).str.strip()

    possible = [c for c in adh.columns if "Avg" in str(c) and "Adhesion" in str(c)]
    if not possible:
        raise ValueError(f"Could not find 'Avg Adhesion' column. Columns: {list(adh.columns)}")
    avg_adh_col = possible[0]

    adh_small = adh[["Sample Num", avg_adh_col]].copy().dropna()
    adh_small = adh_small.rename(columns={avg_adh_col: "Adhesion_Avg"})

    df = pd.merge(wear_small, adh_small, on="Sample Num", how="inner")

    df["WRS"] = 1.0 - minmax01(df["Wear_Avg"])
    df["AS"]  = minmax01(df["Adhesion_Avg"])

    df["CRI"] = W_WEAR * df["WRS"] + W_ADH * df["AS"]
    gate = (df["AS"] / ADH_GATE_THRESH).clip(upper=1.0)
    df["CRI_final"] = df["CRI"] * gate

    df = df.sort_values("CRI_final", ascending=False).reset_index(drop=True)
    df["Rank"] = np.arange(1, len(df) + 1)

    out_csv = OUT_DIR / "coating_robustness_index.csv"
    df.to_csv(out_csv, index=False)

    plt.figure()
    plt.bar(df["Sample Num"], df["CRI_final"])
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("CRI_final (combined wear + adhesion)")
    plt.title("Coating Robustness Index (fixed coating; substrate-driven)")
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "cri_ranking.png", dpi=200)
    plt.close()

    plt.figure()
    sc = plt.scatter(df["Wear_Avg"], df["Adhesion_Avg"], c=df["CRI_final"])
    plt.xlabel("Wear_Avg (lower is better)")
    plt.ylabel("Adhesion_Avg (higher is better)")
    plt.title("Wear vs Adhesion (color = CRI_final)")
    plt.colorbar(sc, label="CRI_final")
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "wear_vs_adhesion_cri.png", dpi=200)
    plt.close()

    print("\n✅ Done.")
    print(f"Saved: {out_csv}")
    print("\nTop 5 by CRI_final:")
    print(df[['Rank','Sample Num','Wear_Avg','Adhesion_Avg','CRI_final']].head(5))

if __name__ == "__main__":
    main()
