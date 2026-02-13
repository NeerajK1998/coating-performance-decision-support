import re
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

CUTTING_ROOT = Path("01_data/ornl_raw/Cutting data")
OUT_DIR = Path("07_outputs")
PLOT_DIR = OUT_DIR / "plots"
OUT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

def parse_meta_from_path(p: Path) -> dict:
    s = str(p)
    rpm = None
    setup = None
    cut = None
    pas = None

    m = re.search(r"Spindle Velocity\s*=\s*\+?(\d+)\s*rpm", s)
    if m: rpm = int(m.group(1))

    m = re.search(r"Setup\s*(\d+)", s)
    if m: setup = int(m.group(1))

    m = re.search(r"Cutting,\s*Setup\s*\d+,\s*Pass\s*(\d+)", s)
    if m: pas = int(m.group(1))

    m = re.search(r"Cut\s*(\d+)", s)
    if m: cut = int(m.group(1))

    return {"rpm": rpm, "setup": setup, "cut": cut, "pass": pas}

def load_pass_txt(p: Path) -> pd.DataFrame:
    """
    Pass files have a text header then a CSV table:
    Point, Time(s), Ch1(N), Ch2(N), Ch3(N)
    We extract forces from the last 3 columns.
    """
    # Find the header row that starts with "Point"
    with p.open("r", errors="ignore") as f:
        lines = f.readlines()

    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Point"):
            start_idx = i
            break

    if start_idx is None:
        raise ValueError("Could not find CSV header row starting with 'Point'")

    # Read CSV from that header row onward
    df = pd.read_csv(
        p,
        skiprows=start_idx,
        sep=",",
        engine="python"
    )

    # Clean column names
    df.columns = [c.strip() for c in df.columns]

    if df.shape[1] < 5:
        raise ValueError(f"Expected >=5 columns, got {df.shape[1]}: {df.columns.tolist()}")

    # Force columns are the last 3 columns
    force = df.iloc[:, -3:].apply(pd.to_numeric, errors="coerce").dropna()
    force.columns = ["Fx", "Fy", "Fz"]
    return force

def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x))))

def main():
    pass_files = sorted(CUTTING_ROOT.rglob("Pass *.txt"))
    if not pass_files:
        raise FileNotFoundError(f"No Pass *.txt files found under: {CUTTING_ROOT}")

    rows = []
    for p in pass_files:
        meta = parse_meta_from_path(p)
        try:
            f = load_pass_txt(p)
        except Exception as e:
            # Skip problematic files but log
            rows.append({**meta, "file": str(p), "error": str(e)})
            continue

        # Force magnitude over time
        Fx = f["Fx"].to_numpy()
        Fy = f["Fy"].to_numpy()
        Fz = f["Fz"].to_numpy()
        Fmag = np.sqrt(Fx**2 + Fy**2 + Fz**2)

        Fx_rms = rms(Fx); Fy_rms = rms(Fy); Fz_rms = rms(Fz)
        F_rms  = rms(Fmag)
        F_peak = float(np.nanmax(np.abs(Fmag)))
        crest  = float(F_peak / (F_rms + 1e-12))

        rows.append({
            **meta,
            "file": str(p),
            "Fx_rms": Fx_rms,
            "Fy_rms": Fy_rms,
            "Fz_rms": Fz_rms,
            "F_rms": F_rms,
            "F_peak": F_peak,
            "crest_factor": crest,
            "error": ""
        })

    df = pd.DataFrame(rows)

    # Separate good rows
    good = df[df["error"].fillna("") == ""].copy()
    if good.empty:
        raise RuntimeError("All Pass files failed to parse. Check file format.")

    # MSI v1: normalized combination of F_rms and crest_factor
    def norm01(s: pd.Series) -> pd.Series:
        s = s.astype(float)
        denom = (s.max() - s.min())
        if denom == 0:
            return pd.Series(np.ones(len(s)), index=s.index)
        return (s - s.min()) / denom

    good["F_rms_n"] = norm01(good["F_rms"])
    good["crest_n"] = norm01(good["crest_factor"])
    good["MSI"] = 0.7 * good["F_rms_n"] + 0.3 * good["crest_n"]

    out_csv = OUT_DIR / "machining_severity_index.csv"
    good.sort_values("MSI", ascending=False).to_csv(out_csv, index=False)

    # Plot MSI distribution
    plt.figure()
    plt.hist(good["MSI"].to_numpy(), bins=30)
    plt.xlabel("MSI (Machining Severity Index)")
    plt.ylabel("Count")
    plt.title("MSI distribution (from Pass force data)")
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "msi_distribution.png", dpi=200)
    plt.close()

    # Plot MSI vs rpm (if rpm available)
    if good["rpm"].notna().any():
        plt.figure()
        plt.scatter(good["rpm"], good["MSI"])
        plt.xlabel("Spindle speed (rpm)")
        plt.ylabel("MSI")
        plt.title("MSI vs spindle speed")
        plt.tight_layout()
        plt.savefig(PLOT_DIR / "msi_vs_rpm.png", dpi=200)
        plt.close()

    print("\n✅ MSI computed.")
    print(f"Saved: {out_csv}")
    print("Top 5 most severe passes:")
    cols = ["rpm","setup","pass","F_rms","F_peak","crest_factor","MSI","file"]
    print(good.sort_values("MSI", ascending=False)[cols].head(5).to_string(index=False))

    # Also save parse errors if any
    bad = df[df["error"].fillna("") != ""].copy()
    if not bad.empty:
        bad.to_csv(OUT_DIR / "msi_parse_errors.csv", index=False)
        print(f"\n⚠️ Some files could not be parsed. See: {OUT_DIR / 'msi_parse_errors.csv'}")

if __name__ == "__main__":
    main()
